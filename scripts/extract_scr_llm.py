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
    return json.loads(cleaned)


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


def select_records(records: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    selected = records
    if args.source:
        selected = [record for record in selected if record.get("source") == args.source]
    if args.skill_id:
        selected = [record for record in selected if record.get("skill_id") == args.skill_id]
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", help="Only annotate one source, e.g. skvm.benchmark")
    parser.add_argument("--skill-id", help="Only annotate one skill id")
    parser.add_argument("--limit", type=int, default=20, help="Maximum records to annotate")
    parser.add_argument("--max-chars", type=int, default=12000, help="Maximum skill text chars per request")
    parser.add_argument("--sleep", type=float, default=0.2, help="Delay between API calls")
    parser.add_argument("--merge", action="store_true", help="Merge LLM SCR into skills_enriched.json")
    args = parser.parse_args()

    load_dotenv()
    records = read_json(PROCESSED_DIR / "skills_enriched.json")
    existing = read_json(ANNOTATIONS_PATH) if ANNOTATIONS_PATH.exists() else []
    existing_ids = {item["skill_id"] for item in existing}

    selected = [record for record in select_records(records, args) if record["skill_id"] not in existing_ids]
    annotations = list(existing)

    for index, record in enumerate(selected, start=1):
        print(f"[{index}/{len(selected)}] annotating {record['source']}::{record['name']}")
        messages = build_prompt(record, max_chars=args.max_chars)
        raw = call_chat_completion(messages)
        annotation = validate_annotation(parse_json_object(raw))
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
