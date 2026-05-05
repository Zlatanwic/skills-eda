from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean
from typing import Any

from skillscope_common import DASHBOARD_DIR, PROCESSED_DIR, PUBLIC_DATA_DIR, read_json, write_json

try:
    from compute_risks import PRIMITIVE_MAP
except ImportError:
    PRIMITIVE_MAP = {}


def top_items(counter: Counter, limit: int = 30) -> list[dict[str, Any]]:
    return [{"name": name, "count": count} for name, count in counter.most_common(limit)]


def bucket_length(char_count: int) -> str:
    if char_count < 1000:
        return "<1k"
    if char_count < 3000:
        return "1k-3k"
    if char_count < 7000:
        return "3k-7k"
    if char_count < 15000:
        return "7k-15k"
    return "15k+"


ENVIRONMENT_CATEGORY_KEYWORDS = {
    "credentials": ["api key", "token", "secret", "credential", "env var", "environment variable"],
    "package managers": ["pip install", "npm install", "pnpm install", "yarn add", "package", "requirements.txt", "package.json"],
    "system cli": ["bash", "shell", "powershell", "cli", "curl", "wget", "docker"],
    "web/browser": ["browser", "playwright", "web", "api"],
    "version control": ["git", "github", "gh "],
    "runtime": ["python", "node", "npm", "uv", "pip"],
}


def dependency_categories(record: dict[str, Any]) -> set[str]:
    text = " ".join(
        [
            *record["features"].get("dependency_evidence", []),
            *record["features"].get("tool_evidence", []),
            " ".join(record["features"].get("code_languages", {}).keys()),
        ]
    ).lower()
    categories = {
        category
        for category, keywords in ENVIRONMENT_CATEGORY_KEYWORDS.items()
        if any(keyword in text for keyword in keywords)
    }
    return categories or ({"implicit"} if record["features"].get("dependency_count", 0) else set())


def summarize_environment(records: list[dict[str, Any]]) -> dict[str, Any]:
    category_counts: Counter[str] = Counter()
    for record in records:
        category_counts.update(dependency_categories(record))

    top_environment_risk = sorted(
        records,
        key=lambda record: (
            record["risks"].get("environment_mismatch", 0),
            record["features"].get("dependency_count", 0),
            record["features"].get("tool_count", 0),
        ),
        reverse=True,
    )[:30]

    return {
        "avg_dependency_count": round(mean(record["features"]["dependency_count"] for record in records), 2) if records else 0,
        "avg_tool_count": round(mean(record["features"]["tool_count"] for record in records), 2) if records else 0,
        "dependency_skill_count": sum(1 for record in records if record["features"]["dependency_count"] > 0),
        "env_risk_skill_count": sum(1 for record in records if record["risks"].get("environment_mismatch", 0) >= 0.4),
        "dependency_categories": top_items(category_counts, 20),
        "top_environment_risk_skills": [
            {
                "skill_id": record["skill_id"],
                "name": record["name"],
                "source": record["source"],
                "dependency_count": record["features"]["dependency_count"],
                "tool_count": record["features"]["tool_count"],
                "env_risk": record["risks"].get("environment_mismatch", 0),
            }
            for record in top_environment_risk
        ],
    }


def build_model_harness_contribution(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        return {
            "avg_model_mismatch": 0,
            "avg_harness_mismatch": 0,
            "dominant_axis": "none",
            "margin": 0,
            "interpretation": "No records available.",
        }

    avg_model = mean(record["risks"].get("model_mismatch", 0) for record in records)
    avg_harness = mean(record["risks"].get("harness_mismatch", 0) for record in records)
    if avg_model > avg_harness:
        dominant = "model"
    elif avg_harness > avg_model:
        dominant = "harness"
    else:
        dominant = "balanced"

    return {
        "avg_model_mismatch": round(avg_model, 3),
        "avg_harness_mismatch": round(avg_harness, 3),
        "dominant_axis": dominant,
        "margin": round(abs(avg_model - avg_harness), 3),
        "interpretation": (
            "Model mismatch contributes more to average risk."
            if dominant == "model"
            else "Harness mismatch contributes more to average risk."
            if dominant == "harness"
            else "Model and harness mismatch are approximately balanced."
        ),
    }


def prioritization_score(record: dict[str, Any]) -> float:
    features = record["features"]
    scr = record["scr"]
    primitive_count = len(scr["requirements"])
    complexity = min(1.0, features["step_count"] / 20 + features["code_block_count"] / 20)
    primitive_pressure = min(1.0, primitive_count / 24)
    confidence_gap = 1 - float(scr.get("confidence", 0))
    score = (
        record["risks"]["overall"] * 0.38
        + record["risks"].get("environment_mismatch", 0) * 0.22
        + primitive_pressure * 0.16
        + complexity * 0.14
        + confidence_gap * 0.10
    )
    return round(min(1.0, score), 3)


def build_prioritization(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = sorted(records, key=prioritization_score, reverse=True)[:50]
    return [
        {
            "skill_id": record["skill_id"],
            "name": record["name"],
            "source": record["source"],
            "taxonomy": record["taxonomy"]["primary_type"],
            "priority_score": prioritization_score(record),
            "overall_risk": record["risks"]["overall"],
            "environment_mismatch": record["risks"].get("environment_mismatch", 0),
            "primitive_count": len(record["scr"]["requirements"]),
            "scr_confidence": record["scr"].get("confidence", 0),
            "step_count": record["features"]["step_count"],
            "code_block_count": record["features"]["code_block_count"],
            "reason": "high gap/risk, environment pressure, primitive diversity, complexity, or low SCR confidence",
        }
        for record in ranked
    ]


def build_validation_sample(records: list[dict[str, Any]], limit: int = 60) -> list[dict[str, Any]]:
    if not records:
        return []

    low_confidence = sorted(records, key=lambda record: record["scr"].get("confidence", 1))[: limit // 3]
    high_risk = sorted(records, key=lambda record: record["risks"]["overall"], reverse=True)[: limit // 3]
    diverse_sources = []
    seen_sources: set[str] = set()
    for record in sorted(records, key=lambda item: (item["source"], item["name"])):
        if record["source"] in seen_sources:
            continue
        diverse_sources.append(record)
        seen_sources.add(record["source"])

    selected: dict[str, dict[str, Any]] = {}
    for record in [*low_confidence, *high_risk, *diverse_sources, *records]:
        selected[record["skill_id"]] = record
        if len(selected) >= limit:
            break

    return [
        {
            "skill_id": record["skill_id"],
            "name": record["name"],
            "source": record["source"],
            "taxonomy": record["taxonomy"]["primary_type"],
            "scr_confidence": record["scr"].get("confidence", 0),
            "primitive_count": len(record["scr"]["requirements"]),
            "top_primitives": [
                {
                    "primitive": requirement["primitive"],
                    "level": requirement["level"],
                    "evidence": requirement["evidence"][:3],
                }
                for requirement in record["scr"]["requirements"][:8]
            ],
            "manual_status": "unreviewed",
            "manual_notes": "",
        }
        for record in selected.values()
    ]


def build_skvm_alignment() -> dict[str, Any]:
    return {
        "implemented": [
            "Treat skills as analyzable natural-language programs.",
            "Extract derived skill capability requirements (SCR).",
            "Import official SkVM target capability profiles (TCP).",
            "Compute SCR/TCP portability gaps by model and harness.",
            "Detect environment dependency risk from skill text.",
        ],
        "partial": [
            "Primitive catalog is project-defined and mapped approximately to SkVM primitive ids.",
            "Environment binding is represented as risk detection, not generated setup scripts.",
            "Concurrency is represented as primitive demand and complexity signals, not executable DAG extraction.",
            "Validation sample is generated for manual review, but labels are not fully adjudicated yet.",
        ],
        "out_of_scope": [
            "AOT compilation into target-specific skill variants.",
            "JIT code solidification and adaptive recompilation.",
            "Runtime task execution, token reduction, and speedup evaluation.",
            "Full public skill ecosystem crawling at 118k-scale.",
        ],
        "primitive_mapping": [
            {"project_primitive": project, "skvm_primitive": skvm}
            for project, skvm in sorted(PRIMITIVE_MAP.items())
        ],
    }


def build_findings(
    records: list[dict[str, Any]],
    summary: dict[str, Any],
    portability: dict[str, Any] | None,
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    total = len(records) or 1
    top_primitive = (summary["capabilities"]["primitive_counts"] or [{"name": "n/a", "count": 0}])[0]
    top_bottleneck = ((portability or {}).get("primitive_bottleneck") or [{"primitive": "n/a", "gap_sum": 0}])[0]
    risk_by_source = sorted(summary["risks"]["by_source"], key=lambda item: item["avg_risk"], reverse=True)
    risk_by_taxonomy = sorted(summary["risks"]["by_taxonomy"], key=lambda item: item["avg_risk"], reverse=True)
    best_target = ((portability or {}).get("target_ranking") or [{}])[0]
    dependency_count = summary["environment"]["dependency_skill_count"]
    verification_count = sum(1 for record in records if record["features"].get("has_verification"))
    model_harness = summary["model_harness_contribution"]

    findings.append(
        {
            "title": "Most common capability",
            "value": top_primitive["name"],
            "detail": f'{top_primitive["count"]} skills ({top_primitive["count"] / total:.1%}) require this primitive.',
            "question": "What capability requirements are most common?",
        }
    )
    findings.append(
        {
            "title": "Largest portability bottleneck",
            "value": top_bottleneck["primitive"],
            "detail": f'Aggregated SCR/TCP gap score: {top_bottleneck["gap_sum"]}.',
            "question": "Which primitive capabilities become bottlenecks most often?",
        }
    )
    if risk_by_source:
        findings.append(
            {
                "title": "Riskiest source",
                "value": risk_by_source[0]["name"],
                "detail": f'Average overall risk is {risk_by_source[0]["avg_risk"]:.3f} across {risk_by_source[0]["count"]} skills.',
                "question": "Do skills from different sources have different structures and risks?",
            }
        )
    if risk_by_taxonomy:
        findings.append(
            {
                "title": "Riskiest taxonomy",
                "value": risk_by_taxonomy[0]["name"],
                "detail": f'Average overall risk is {risk_by_taxonomy[0]["avg_risk"]:.3f}.',
                "question": "How do skill taxonomy and primitive requirements relate?",
            }
        )
    if best_target:
        findings.append(
            {
                "title": "Best target profile",
                "value": f'{best_target.get("model", "n/a").split("/")[-1]} / {best_target.get("harness", "n/a")}',
                "detail": f'Lowest average gap is {best_target.get("avg_gap", 0):.3f}.',
                "question": "Which model/harness pairs are most compatible with the corpus?",
            }
        )
    findings.append(
        {
            "title": "Environment dependency footprint",
            "value": f"{dependency_count}/{len(records)}",
            "detail": f"{dependency_count / total:.1%} of skills mention dependencies, credentials, packages, or environment setup.",
            "question": "Are environment dependencies a major portability risk?",
        }
    )
    findings.append(
        {
            "title": "Verification-heavy workflows",
            "value": f"{verification_count}/{len(records)}",
            "detail": f"{verification_count / total:.1%} of skills include test/check/verify signals.",
            "question": "How procedural are skills?",
        }
    )
    findings.append(
        {
            "title": "Dominant mismatch axis",
            "value": model_harness["dominant_axis"],
            "detail": f'Model avg {model_harness["avg_model_mismatch"]:.3f}, harness avg {model_harness["avg_harness_mismatch"]:.3f}; margin {model_harness["margin"]:.3f}.',
            "question": "Is model mismatch or harness mismatch stronger?",
        }
    )
    return findings


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    source_counts = Counter(record["source"] for record in records)
    taxonomy_counts = Counter(record["taxonomy"]["primary_type"] for record in records)
    domain_counts = Counter(domain for record in records for domain in record["taxonomy"]["domains"])
    length_buckets = Counter(bucket_length(record["features"]["char_count"]) for record in records)
    primitive_counts = Counter(
        requirement["primitive"]
        for record in records
        for requirement in record["scr"]["requirements"]
    )
    primitive_level_counts = Counter(
        f'{requirement["primitive"]}:L{requirement["level"]}'
        for record in records
        for requirement in record["scr"]["requirements"]
    )
    code_language_counts = Counter(
        language
        for record in records
        for language, count in record["features"]["code_languages"].items()
        for _ in range(count)
    )
    tool_counts = Counter(
        tool
        for record in records
        for tool in record["features"]["tool_evidence"]
    )
    dependency_counts = Counter(
        dependency
        for record in records
        for dependency in record["features"]["dependency_evidence"]
    )

    risk_by_source = defaultdict(list)
    risk_by_taxonomy = defaultdict(list)
    for record in records:
        risk_by_source[record["source"]].append(record["risks"]["overall"])
        risk_by_taxonomy[record["taxonomy"]["primary_type"]].append(record["risks"]["overall"])

    top_risky = sorted(records, key=lambda record: record["risks"]["overall"], reverse=True)[:50]

    summary = {
        "overview": {
            "skill_count": len(records),
            "source_counts": top_items(source_counts),
            "taxonomy_counts": top_items(taxonomy_counts),
            "domain_counts": top_items(domain_counts),
            "length_buckets": [{"name": name, "count": length_buckets[name]} for name in ["<1k", "1k-3k", "3k-7k", "7k-15k", "15k+"]],
            "avg_char_count": round(mean(record["features"]["char_count"] for record in records), 2) if records else 0,
            "avg_code_blocks": round(mean(record["features"]["code_block_count"] for record in records), 2) if records else 0,
            "avg_steps": round(mean(record["features"]["step_count"] for record in records), 2) if records else 0,
        },
        "capabilities": {
            "primitive_counts": top_items(primitive_counts, 50),
            "primitive_level_counts": top_items(primitive_level_counts, 100),
        },
        "code_tools": {
            "code_language_counts": top_items(code_language_counts, 40),
            "tool_counts": top_items(tool_counts, 40),
            "dependency_counts": top_items(dependency_counts, 40),
        },
        "risks": {
            "by_source": [
                {"name": source, "avg_risk": round(mean(values), 3), "count": len(values)}
                for source, values in sorted(risk_by_source.items())
            ],
            "by_taxonomy": [
                {"name": taxonomy, "avg_risk": round(mean(values), 3), "count": len(values)}
                for taxonomy, values in sorted(risk_by_taxonomy.items())
            ],
            "top_risky_skills": [
                {
                    "skill_id": record["skill_id"],
                    "name": record["name"],
                    "source": record["source"],
                    "taxonomy": record["taxonomy"]["primary_type"],
                    "domains": record["taxonomy"]["domains"],
                    "risk": record["risks"],
                    "primitive_count": len(record["scr"]["requirements"]),
                    "path_or_url": record["path_or_url"],
                }
                for record in top_risky
            ],
        },
        "environment": summarize_environment(records),
        "model_harness_contribution": build_model_harness_contribution(records),
        "prioritization": build_prioritization(records),
        "validation_sample": build_validation_sample(records),
        "skvm_alignment": build_skvm_alignment(),
        "findings": [],
    }
    portability = read_json(DASHBOARD_DIR / "portability.json") if (DASHBOARD_DIR / "portability.json").exists() else None
    summary["findings"] = build_findings(records, summary, portability)
    return summary


def build_skill_index(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "skill_id": record["skill_id"],
            "name": record["name"],
            "source": record["source"],
            "path_or_url": record["path_or_url"],
            "description": record["metadata"]["description"],
            "features": record["features"],
            "taxonomy": record["taxonomy"],
            "scr": record["scr"],
            "risks": record["risks"],
            "portability": record.get("portability"),
        }
        for record in records
    ]


def main() -> None:
    records = read_json(PROCESSED_DIR / "skills_enriched.json")
    summary = summarize(records)
    skill_index = build_skill_index(records)
    write_json(DASHBOARD_DIR / "summary.json", summary)
    write_json(DASHBOARD_DIR / "findings.json", summary["findings"])
    write_json(DASHBOARD_DIR / "environment.json", summary["environment"])
    write_json(DASHBOARD_DIR / "prioritization.json", summary["prioritization"])
    write_json(DASHBOARD_DIR / "validation_sample.json", summary["validation_sample"])
    write_json(DASHBOARD_DIR / "skvm_alignment.json", summary["skvm_alignment"])
    write_json(DASHBOARD_DIR / "skills_index.json", skill_index)
    write_json(PUBLIC_DATA_DIR / "summary.json", summary)
    write_json(PUBLIC_DATA_DIR / "findings.json", summary["findings"])
    write_json(PUBLIC_DATA_DIR / "environment.json", summary["environment"])
    write_json(PUBLIC_DATA_DIR / "prioritization.json", summary["prioritization"])
    write_json(PUBLIC_DATA_DIR / "validation_sample.json", summary["validation_sample"])
    write_json(PUBLIC_DATA_DIR / "skvm_alignment.json", summary["skvm_alignment"])
    write_json(PUBLIC_DATA_DIR / "skills_index.json", skill_index)
    print(f"Built dashboard data for {len(records)} skills")
    print(DASHBOARD_DIR / "summary.json")
    print(DASHBOARD_DIR / "skills_index.json")
    print(PUBLIC_DATA_DIR / "summary.json")
    print(PUBLIC_DATA_DIR / "skills_index.json")


if __name__ == "__main__":
    main()
