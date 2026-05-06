"""Optional LLM-assisted SCR annotation.

This script reads rule-enriched skills, asks an OpenAI-compatible chat model to
produce SCR labels, and optionally merges those labels back into
skills_enriched.json for downstream TCP gap analysis.

Config:
    Copy .env.example to .env and set:
      SKILLSCOPE_LLM_API_KEY
      SKILLSCOPE_LLM_BASE_URL  (default: https://api.openai.com/v1)
      SKILLSCOPE_LLM_MODEL

Examples:
    python scripts/extract_scr_llm.py --source skvm.benchmark --limit 20
    python scripts/extract_scr_llm.py --selection auto --limit 20 --merge
    python scripts/extract_scr_llm.py --source skvm.benchmark --limit 108 --merge
    python scripts/extract_scr_llm.py --skill-id some_id --merge
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from skillscope_common import DATA_DIR, PROCESSED_DIR, REPO_ROOT, read_json, write_json

ANNOTATIONS_PATH = PROCESSED_DIR / "scr_llm_annotations.json"
FAILURES_PATH = PROCESSED_DIR / "scr_llm_failures.json"


def load_dotenv(path: Path = REPO_ROOT / ".env") -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        os.environ.setdefault(key, value)


def truncate_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    head = text[: max_chars // 2]
    tail = text[-max_chars // 2 :]
    return f"{head}\n\n[...truncated...]\n\n{tail}"


def primitive_catalog_text() -> str:
    catalog = read_json(DATA_DIR / "primitive_catalog.json")
    lines = []
    for item in catalog:
        lines.append(f"- {item['primitive']} ({item['group']}): {item['description']}")
    return "\n".join(lines)


def build_prompt(record: dict[str, Any], max_chars: int) -> list[dict[str, str]]:
    catalog = primitive_catalog_text()
    rule_scr = record.get("scr", {})
    skill_text = truncate_text(record.get("raw_text") or record.get("body_text") or "", max_chars)
    system = (
        "You label Skill Capability Requirements (SCR) for LLM agent skills. "
        "Return strict JSON only. Do not include markdown fences. "
        "Use only primitives from the provided catalog. "
        "Levels are integers: 0 none, 1 basic, 2 standard multi-step, 3 complex with branching, verification, or tool coordination."
    )
    user = f"""
Primitive catalog:
{catalog}

Skill metadata:
name: {record.get("name")}
source: {record.get("source")}
description: {record.get("metadata", {}).get("description", "")}

Rule-based initial SCR, for reference only:
{json.dumps(rule_scr, ensure_ascii=False)}

Skill text:
{skill_text}

Return JSON with this exact shape:
{{
  "method": "llm",
  "confidence": 0.0,
  "requirements": [
    {{
      "primitive": "tool.exec",
      "level": 2,
      "confidence": 0.0,
      "evidence": ["short quote or paraphrase"],
      "reason": "why this skill requires the primitive"
    }}
  ]
}}
"""
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def call_chat_completion(messages: list[dict[str, str]], temperature: float = 0.0) -> str:
    base_url = os.environ.get("SKILLSCOPE_LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    api_key = os.environ.get("SKILLSCOPE_LLM_API_KEY")
    model = os.environ.get("SKILLSCOPE_LLM_MODEL")
    if not api_key:
        raise SystemExit("Missing SKILLSCOPE_LLM_API_KEY. Copy .env.example to .env and fill it in.")
    if not model:
        raise SystemExit("Missing SKILLSCOPE_LLM_MODEL. Set it in .env or your shell.")

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LLM API error {error.code}: {body}") from error

    return data["choices"][0]["message"]["content"]


def parse_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            candidate = cleaned[start : end + 1]
            candidate = re.sub(r",\s*([}\]])", r"\1", candidate)
            return json.loads(candidate)
        raise


def repair_json_with_llm(
    raw: str,
    error: Exception,
) -> dict[str, Any]:
    messages = [
        {
            "role": "system",
            "content": (
                "Repair invalid JSON. Return strict JSON only. Do not add markdown fences, comments, "
                "or explanatory text. Preserve the original fields and values where possible."
            ),
        },
        {
            "role": "user",
            "content": (
                f"The following JSON-like text failed to parse with this error: {error}\n\n"
                f"Text:\n{raw[:12000]}"
            ),
        },
    ]
    repaired = call_chat_completion(messages)
    return parse_json_object(repaired)


def save_failure(
    record: dict[str, Any],
    error: Exception,
    raw: str,
) -> None:
    failures = read_json(FAILURES_PATH) if FAILURES_PATH.exists() else []
    failures.append(
        {
            "skill_id": record["skill_id"],
            "name": record["name"],
            "source": record["source"],
            "error": str(error),
            "raw_excerpt": raw[:3000],
        }
    )
    write_json(FAILURES_PATH, failures)


def validate_annotation(annotation: dict[str, Any]) -> dict[str, Any]:
    valid_primitives = {item["primitive"] for item in read_json(DATA_DIR / "primitive_catalog.json")}
    requirements = []
    for req in annotation.get("requirements", []):
        primitive = str(req.get("primitive", ""))
        if primitive not in valid_primitives:
            continue
        try:
            level = int(req.get("level", 0))
        except (TypeError, ValueError):
            level = 0
        level = max(0, min(3, level))
        if level == 0:
            continue
        confidence = float(req.get("confidence", 0.5))
        requirements.append(
            {
                "primitive": primitive,
                "level": level,
                "method": "llm",
                "confidence": round(max(0.0, min(1.0, confidence)), 3),
                "evidence": [str(item)[:240] for item in req.get("evidence", [])[:4]],
                "reason": str(req.get("reason", ""))[:500],
            }
        )

    avg_confidence = (
        sum(req["confidence"] for req in requirements) / len(requirements)
        if requirements
        else float(annotation.get("confidence", 0.0) or 0.0)
    )
    return {
        "method": "llm",
        "confidence": round(max(0.0, min(1.0, avg_confidence)), 3),
        "requirements": sorted(requirements, key=lambda item: item["primitive"]),
    }


def llm_candidate_reason(
    record: dict[str, Any],
    min_confidence: float = 0.55,
    min_risk: float = 0.25,
) -> tuple[float, list[str]]:
    """Return a priority score and explanation for conditional LLM annotation.

    The rule extractor is cheap and deterministic. LLM annotation is reserved for
    cases where rules are likely under-specified or the skill is important enough
    that a better SCR label materially improves downstream risk analysis.
    """
    scr = record.get("scr", {})
    features = record.get("features", {})
    risks = record.get("risks", {})
    requirements = scr.get("requirements") or []
    confidence = float(scr.get("confidence", 0.0) or 0.0)
    overall_risk = float(risks.get("overall", 0.0) or 0.0)
    primitive_count = len(requirements)
    step_count = int(features.get("step_count", 0) or 0)
    code_blocks = int(features.get("code_block_count", 0) or 0)
    tool_count = int(features.get("tool_count", 0) or 0)
    dependency_count = int(features.get("dependency_count", 0) or 0)
    char_count = int(features.get("char_count", 0) or 0)
    structural_count = sum(1 for req in requirements if "structural" in str(req.get("method", "")))

    score = 0.0
    reasons: list[str] = []

    if confidence < min_confidence:
        score += (min_confidence - confidence) * 2.0
        reasons.append(f"low rule confidence {confidence:.2f}")

    if primitive_count == 0 and (step_count >= 8 or code_blocks >= 2 or char_count >= 6000):
        score += 1.5
        reasons.append("complex skill has no SCR primitives")

    if primitive_count <= 2 and (step_count >= 12 or char_count >= 8000):
        score += 0.9
        reasons.append("long workflow has few primitives")

    if structural_count and structural_count == primitive_count and primitive_count <= 2:
        score += 0.7
        reasons.append("SCR is structural-only")

    if overall_risk >= min_risk and confidence < 0.75:
        score += 0.75 + overall_risk
        reasons.append(f"high risk with uncertain SCR {overall_risk:.2f}")

    if step_count >= 15 and (tool_count >= 3 or dependency_count >= 2 or code_blocks >= 2):
        score += 0.8
        reasons.append("complex workflow mixes steps with tools/code/environment")

    if record.get("source") == "skvm.benchmark" and confidence < 0.8:
        score += 0.4
        reasons.append("SkVM benchmark sample benefits from calibrated SCR")

    return round(score, 3), reasons


def select_records(records: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    selected = records
    if args.source:
        selected = [record for record in selected if record.get("source") == args.source]
    if args.skill_id:
        selected = [record for record in selected if record.get("skill_id") == args.skill_id]
    elif args.selection == "auto":
        scored = []
        for record in selected:
            score, reasons = llm_candidate_reason(
                record,
                min_confidence=args.min_confidence,
                min_risk=args.min_risk,
            )
            if reasons and score >= args.min_score:
                scored.append((score, reasons, record))
        scored.sort(key=lambda item: (-item[0], item[2].get("source", ""), item[2].get("name", "")))
        for score, reasons, record in scored[: args.limit or len(scored)]:
            record["llm_selection_reason"] = "; ".join(reasons)
            record["llm_selection_score"] = score
        selected = [record for _score, _reasons, record in scored]
    if args.limit:
        selected = selected[: args.limit]
    return selected


def merge_annotations(records: list[dict[str, Any]], annotations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    annotation_by_id = {item["skill_id"]: item["scr"] for item in annotations}
    for record in records:
        annotation = annotation_by_id.get(record["skill_id"])
        if annotation:
            rule_scr = record.get("scr", {})
            record["scr_rule"] = rule_scr
            record["scr"] = {
                **annotation,
                "method": "rule+llm",
                "rule_confidence": rule_scr.get("confidence"),
            }
    return records


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", help="Only annotate one source, e.g. skvm.benchmark")
    parser.add_argument("--skill-id", help="Only annotate one skill id")
    parser.add_argument("--limit", type=int, default=0, help="Maximum records to annotate; 0 means no limit")
    parser.add_argument(
        "--selection",
        choices=["all", "auto"],
        default="all",
        help="Select all filtered records, or only records that need LLM SCR quality repair",
    )
    parser.add_argument("--min-confidence", type=float, default=0.55, help="Auto mode confidence trigger")
    parser.add_argument("--min-risk", type=float, default=0.25, help="Auto mode risk trigger")
    parser.add_argument("--min-score", type=float, default=1.0, help="Auto mode minimum trigger score")
    parser.add_argument("--max-chars", type=int, default=12000, help="Maximum skill text chars per request")
    parser.add_argument("--sleep", type=float, default=0.2, help="Delay between API calls")
    parser.add_argument("--retries", type=int, default=1, help="Repair/retry attempts after invalid JSON")
    parser.add_argument("--merge", action="store_true", help="Merge LLM SCR into skills_enriched.json")
    parser.add_argument("--dry-run", action="store_true", help="Print selected records without calling the LLM API")
    args = parser.parse_args(argv)

    load_dotenv()
    records = read_json(PROCESSED_DIR / "skills_enriched.json")
    existing = read_json(ANNOTATIONS_PATH) if ANNOTATIONS_PATH.exists() else []
    existing_ids = {item["skill_id"] for item in existing}

    available_records = [record for record in records if record["skill_id"] not in existing_ids]
    selected = select_records(available_records, args)
    annotations = list(existing)

    if args.dry_run:
        for index, record in enumerate(selected, start=1):
            reason = record.get("llm_selection_reason", "manual selection")
            score = record.get("llm_selection_score", 0)
            print(f"[{index}/{len(selected)}] {record['source']}::{record['name']} score={score} reason={reason}")
        print(f"Dry run selected {len(selected)} records; no LLM calls made.")
        return

    for index, record in enumerate(selected, start=1):
        reason = record.get("llm_selection_reason")
        suffix = f" ({reason})" if reason else ""
        print(f"[{index}/{len(selected)}] annotating {record['source']}::{record['name']}{suffix}")
        messages = build_prompt(record, max_chars=args.max_chars)
        raw = call_chat_completion(messages)
        parsed: dict[str, Any] | None = None
        last_error: Exception | None = None
        for attempt in range(args.retries + 1):
            try:
                parsed = parse_json_object(raw) if attempt == 0 else repair_json_with_llm(raw, last_error or "invalid JSON")
                break
            except (json.JSONDecodeError, RuntimeError) as error:
                last_error = error
                if attempt < args.retries:
                    print(f"  invalid JSON, attempting repair ({attempt + 1}/{args.retries})")
                else:
                    print(f"  skipped: invalid JSON after {args.retries + 1} attempt(s): {error}")
                    save_failure(record, error, raw)
        if parsed is None:
            time.sleep(args.sleep)
            continue

        annotation = validate_annotation(parsed)
        annotations.append(
            {
                "skill_id": record["skill_id"],
                "name": record["name"],
                "source": record["source"],
                "scr": annotation,
            }
        )
        write_json(ANNOTATIONS_PATH, annotations)
        time.sleep(args.sleep)

    if args.merge:
        merged = merge_annotations(records, annotations)
        write_json(PROCESSED_DIR / "skills_enriched.json", merged)
        print(f"Merged {len(annotations)} LLM SCR annotations into skills_enriched.json")

    print(f"LLM SCR annotations: {len(annotations)} -> {ANNOTATIONS_PATH}")


if __name__ == "__main__":
    main()
