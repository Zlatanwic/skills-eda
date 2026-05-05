"""Phase 6 — Real portability risk via SCR ↔ TCP gap.

Reads:
    data/processed/skills_enriched.json   project SCR labels (per skill)
    data/processed/tcp_profiles.json      SkVM TCP profiles (per harness×model)

Writes:
    data/processed/skills_enriched.json   risks + portability fields refreshed in-place
    data/dashboard/portability.json       global bottleneck + per-skill best/worst target
    public/data/portability.json          dashboard-shipped copy

Gap formula (SkVM §8.6):
    gap(skill, target, primitive) = max(0, required_level − provided_level)

Aggregation per skill across the TCP fleet:
    model_mismatch    = avg total_gap across (same harness, varying model)        / max_gap_norm
    harness_mismatch  = avg total_gap across (same model,   varying harness)      / max_gap_norm
    environment_mismatch  preserved from extract_scr (env-feature heuristic)
    overall = 0.4·model + 0.35·harness + 0.25·env
"""

from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean
from typing import Any

from skillscope_common import (
    DASHBOARD_DIR,
    PROCESSED_DIR,
    PUBLIC_DATA_DIR,
    ensure_data_dirs,
    read_json,
    write_json,
)

# ── Project primitive → SkVM primitive id ────────────────────────────────
# Project catalog has a few extras (typescript, web.search/fetch split, github,
# package_manager, data.*, doc/spreadsheet/presentation, follow.verify,
# agent.parallel, runtime.env_bind). Map each to the closest SkVM primitive.
PRIMITIVE_MAP: dict[str, str] = {
    # code generation
    "gen.code.shell": "gen.code.shell",
    "gen.code.python": "gen.code.python",
    "gen.code.javascript": "gen.code.javascript",
    "gen.code.typescript": "gen.code.javascript",
    "gen.code.sql": "gen.code.sql",
    "gen.code.test": "gen.code.python",
    # tool use
    "tool.exec": "tool.exec",
    "tool.file.read": "tool.file.read",
    "tool.file.write": "tool.file.write",
    "tool.web.search": "tool.web",
    "tool.web.fetch": "tool.web",
    "tool.browser": "tool.browser",
    "tool.git": "tool.exec",
    "tool.github": "tool.web",
    "tool.package_manager": "tool.exec",
    # data / documents — SkVM has gen.text.* but not data.*
    "data.parse": "reason.analysis",
    "data.transform": "reason.analysis",
    "data.visualize": "gen.code.python",
    "doc.generate": "gen.text.long",
    "spreadsheet.process": "gen.code.python",
    "presentation.generate": "gen.text.structured",
    # reasoning / following
    "reason.plan": "reason.planning",
    "reason.diagnose": "reason.analysis",
    "follow.procedure": "follow.procedure",
    "follow.constraints": "follow.constraint",
    "follow.verify": "follow.constraint",
    # parallel / runtime
    "agent.parallel": "follow.delegation",
    "runtime.env_bind": "tool.exec",
}

MAX_LEVEL = 3  # L0..L3


def gap(required: int, provided: int) -> int:
    return max(0, required - provided)


def evaluate_skill_against_profile(
    requirements: list[dict[str, Any]],
    profile: dict[str, Any],
) -> dict[str, Any]:
    """Compute gap stats for one skill against one (harness, model) profile."""
    capabilities: dict[str, int] = profile["capabilities"]
    per_primitive: list[dict[str, Any]] = []
    total_gap = 0
    max_gap = 0
    missing = 0
    hard_gap = 0

    for req in requirements:
        project_prim = req["primitive"]
        skvm_prim = PRIMITIVE_MAP.get(project_prim)
        required = int(req["level"])
        provided = capabilities.get(skvm_prim, 0) if skvm_prim else 0
        g = gap(required, provided)
        if g > 0:
            total_gap += g
            max_gap = max(max_gap, g)
            if provided == 0:
                missing += 1
            if required >= 2 and provided == 0:
                hard_gap += 1
            per_primitive.append(
                {
                    "primitive": project_prim,
                    "skvm_primitive": skvm_prim,
                    "required": required,
                    "provided": provided,
                    "gap": g,
                }
            )

    return {
        "profile_id": profile["profile_id"],
        "harness": profile["harness"],
        "model": profile["model"],
        "total_gap": total_gap,
        "max_gap": max_gap,
        "missing_count": missing,
        "hard_gap_count": hard_gap,
        "bottlenecks": sorted(per_primitive, key=lambda x: -x["gap"])[:5],
    }


def fleet_max_gap_norm(requirements: list[dict[str, Any]]) -> int:
    """Worst-case total gap = sum of required levels (provider gives L0 everywhere)."""
    return sum(int(req["level"]) for req in requirements) or 1


def aggregate_risk(
    evaluations: list[dict[str, Any]],
    norm: int,
) -> tuple[float, float]:
    """Return (model_mismatch, harness_mismatch) in [0,1]."""
    by_harness: dict[str, list[float]] = defaultdict(list)
    by_model: dict[str, list[float]] = defaultdict(list)
    for ev in evaluations:
        score = ev["total_gap"] / norm
        by_harness[ev["harness"]].append(score)
        by_model[ev["model"]].append(score)

    # model_mismatch: variation across models within each harness, then averaged
    model_mismatch = (
        mean(mean(scores) for scores in by_harness.values()) if by_harness else 0.0
    )
    # harness_mismatch: variation across harnesses within each model, then averaged
    harness_mismatch = (
        mean(mean(scores) for scores in by_model.values()) if by_model else 0.0
    )
    return min(1.0, model_mismatch), min(1.0, harness_mismatch)


def compute_for_skill(
    record: dict[str, Any],
    profiles: list[dict[str, Any]],
) -> dict[str, Any]:
    requirements = record["scr"]["requirements"]
    if not requirements or not profiles:
        return {
            "evaluations": [],
            "risks": record.get("risks", {}),
            "best_target": None,
            "worst_target": None,
            "bottleneck_primitives": [],
        }

    evaluations = [evaluate_skill_against_profile(requirements, p) for p in profiles]
    norm = fleet_max_gap_norm(requirements)

    model_mm, harness_mm = aggregate_risk(evaluations, norm)
    env_mm = float(record.get("risks", {}).get("environment_mismatch", 0.0))
    overall = round(model_mm * 0.4 + harness_mm * 0.35 + env_mm * 0.25, 3)

    sorted_evals = sorted(evaluations, key=lambda e: (e["total_gap"], e["max_gap"]))
    best = sorted_evals[0]
    worst = sorted_evals[-1]

    bottleneck_counter: Counter[str] = Counter()
    for ev in evaluations:
        for b in ev["bottlenecks"]:
            bottleneck_counter[b["primitive"]] += b["gap"]

    return {
        "evaluations": evaluations,
        "risks": {
            "model_mismatch": round(model_mm, 3),
            "harness_mismatch": round(harness_mm, 3),
            "environment_mismatch": round(env_mm, 3),
            "overall": overall,
        },
        "best_target": {
            "harness": best["harness"],
            "model": best["model"],
            "total_gap": best["total_gap"],
        },
        "worst_target": {
            "harness": worst["harness"],
            "model": worst["model"],
            "total_gap": worst["total_gap"],
        },
        "bottleneck_primitives": [
            {"primitive": prim, "gap_sum": gap_sum}
            for prim, gap_sum in bottleneck_counter.most_common(8)
        ],
    }


def build_global_portability(
    records: list[dict[str, Any]],
    profiles: list[dict[str, Any]],
) -> dict[str, Any]:
    """Aggregate fleet-wide portability stats for the dashboard."""
    profile_avg_gap: dict[str, list[int]] = defaultdict(list)
    primitive_bottleneck: Counter[str] = Counter()
    skill_overall_gaps: list[tuple[str, str, int]] = []  # (skill_id, name, total)

    for record in records:
        portability = record.get("portability") or {}
        for ev in portability.get("evaluations", []):
            profile_avg_gap[ev["profile_id"]].append(ev["total_gap"])
        for entry in portability.get("bottleneck_primitives", []):
            primitive_bottleneck[entry["primitive"]] += entry["gap_sum"]
        if portability.get("evaluations"):
            total = sum(ev["total_gap"] for ev in portability["evaluations"])
            skill_overall_gaps.append((record["skill_id"], record["name"], total))

    profile_lookup = {p["profile_id"]: p for p in profiles}
    target_ranking = [
        {
            "profile_id": pid,
            "harness": profile_lookup[pid]["harness"],
            "model": profile_lookup[pid]["model"],
            "avg_gap": round(mean(values), 3),
            "skill_count": len(values),
        }
        for pid, values in profile_avg_gap.items()
        if pid in profile_lookup
    ]
    target_ranking.sort(key=lambda x: x["avg_gap"])
    target_matrix = [
        {
            "harness": profile_lookup[pid]["harness"],
            "model": profile_lookup[pid]["model"],
            "avg_gap": round(mean(values), 3),
            "skill_count": len(values),
        }
        for pid, values in profile_avg_gap.items()
        if pid in profile_lookup
    ]
    target_matrix.sort(key=lambda x: (x["harness"], x["model"]))

    top_risky = sorted(skill_overall_gaps, key=lambda x: -x[2])[:25]

    return {
        "profile_count": len(profiles),
        "harnesses": sorted({p["harness"] for p in profiles}),
        "models": sorted({p["model"] for p in profiles}),
        "primitive_bottleneck": [
            {"primitive": prim, "gap_sum": gap_sum}
            for prim, gap_sum in primitive_bottleneck.most_common(20)
        ],
        "target_ranking": target_ranking,
        "target_matrix": target_matrix,
        "top_risky_skills": [
            {"skill_id": sid, "name": name, "fleet_gap": total}
            for sid, name, total in top_risky
        ],
    }


def main() -> None:
    ensure_data_dirs()
    records = read_json(PROCESSED_DIR / "skills_enriched.json")
    profiles = read_json(PROCESSED_DIR / "tcp_profiles.json")

    if not profiles:
        raise SystemExit("No TCP profiles. Run scripts/collect_skvm_data.py first.")

    for record in records:
        portability = compute_for_skill(record, profiles)
        record["risks"] = portability["risks"]
        record["portability"] = {
            "best_target": portability["best_target"],
            "worst_target": portability["worst_target"],
            "bottleneck_primitives": portability["bottleneck_primitives"],
            "evaluations": portability["evaluations"],
        }

    write_json(PROCESSED_DIR / "skills_enriched.json", records)

    global_portability = build_global_portability(records, profiles)
    write_json(DASHBOARD_DIR / "portability.json", global_portability)
    write_json(PUBLIC_DATA_DIR / "portability.json", global_portability)

    avg_overall = mean(record["risks"]["overall"] for record in records) if records else 0
    print(f"Computed gap risks for {len(records)} skills × {len(profiles)} profiles")
    print(f"  fleet primitive bottlenecks: "
          f"{[b['primitive'] for b in global_portability['primitive_bottleneck'][:5]]}")
    print(f"  best target: {global_portability['target_ranking'][0] if global_portability['target_ranking'] else 'n/a'}")
    print(f"  worst target: {global_portability['target_ranking'][-1] if global_portability['target_ranking'] else 'n/a'}")
    print(f"  avg overall risk: {avg_overall:.3f}")
    print(PROCESSED_DIR / "skills_enriched.json")
    print(DASHBOARD_DIR / "portability.json")


if __name__ == "__main__":
    main()
