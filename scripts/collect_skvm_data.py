"""Collect SkVM benchmark skills and TCP profiles from SJTU-IPADS/SkVM-data.

Outputs:
    data/processed/skvm_skills.json   list[SkillRecord]   benchmark skills
    data/processed/tcp_profiles.json  list[ProfileRecord] flat (harness, model) TCP

Run:
    python scripts/collect_skvm_data.py            # uses cached clone if present
    python scripts/collect_skvm_data.py --refresh  # git pull or fresh clone
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Any

from skillscope_common import (
    PROCESSED_DIR,
    RAW_DIR,
    SkillPath,
    content_hash,
    ensure_data_dirs,
    extract_code_blocks,
    extract_headings,
    parse_frontmatter,
    read_json,
    read_text,
    resolve_skill_name,
    stable_id,
    write_json,
)

SKVM_REPO_URL = "https://github.com/SJTU-IPADS/SkVM-data.git"
SKVM_CLONE_DIR = RAW_DIR / "skvm-data"
SKVM_SOURCE = "skvm.benchmark"

LEVEL_TO_INT: dict[str, int] = {"L0": 0, "L1": 1, "L2": 2, "L3": 3}


def ensure_clone(refresh: bool = False) -> Path:
    """Clone SkVM-data shallowly, or pull if --refresh."""
    if SKVM_CLONE_DIR.exists() and (SKVM_CLONE_DIR / ".git").exists():
        if refresh:
            subprocess.run(
                ["git", "-C", str(SKVM_CLONE_DIR), "pull", "--ff-only"],
                check=True,
            )
        return SKVM_CLONE_DIR

    SKVM_CLONE_DIR.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--depth", "1", SKVM_REPO_URL, str(SKVM_CLONE_DIR)],
        check=True,
    )
    return SKVM_CLONE_DIR


def iter_benchmark_skills(skvm_root: Path) -> list[SkillPath]:
    skills_dir = skvm_root / "skills"
    if not skills_dir.exists():
        return []
    paths: list[SkillPath] = []
    for path in sorted(skills_dir.rglob("SKILL.md")):
        paths.append(SkillPath(source=SKVM_SOURCE, root=skills_dir, path=path))
    return paths


def parse_skill(skill_path: SkillPath) -> dict[str, Any]:
    raw_text = read_text(skill_path.path)
    frontmatter, body = parse_frontmatter(raw_text)
    headings = extract_headings(body)
    parent = skill_path.path.parent
    dir_name = parent.name
    grandparent_name = parent.parent.name if parent.parent != parent else ""
    name = resolve_skill_name(frontmatter, headings, dir_name, grandparent_name)
    description = str(frontmatter.get("description") or "")
    return {
        "skill_id": stable_id(skill_path.source, skill_path.relative_path),
        "name": name,
        "source": skill_path.source,
        "path_or_url": str(skill_path.path),
        "relative_path": skill_path.relative_path,
        "content_hash": content_hash(raw_text),
        "raw_text": raw_text,
        "body_text": body,
        "metadata": {
            "description": description,
            "frontmatter": frontmatter,
            "skill_dir": dir_name,
            "benchmark": True,
        },
        "parsed": {
            "headings": headings,
            "code_blocks": extract_code_blocks(body),
        },
    }


def normalize_capabilities(raw: dict[str, Any]) -> dict[str, int]:
    """Map {primitiveId: 'L2'} -> {primitiveId: 2}. Unknown labels become 0."""
    return {
        primitive: LEVEL_TO_INT.get(str(level).upper(), 0)
        for primitive, level in raw.items()
        if isinstance(primitive, str)
    }


def parse_profile(profile_path: Path, harness: str, model_dir: str) -> dict[str, Any] | None:
    try:
        payload = read_json(profile_path)
    except (OSError, ValueError):
        return None

    capabilities = normalize_capabilities(payload.get("capabilities") or {})
    if not capabilities:
        return None

    model = str(payload.get("model") or model_dir.replace("--", "/"))
    return {
        "profile_id": stable_id(harness, model),
        "harness": harness,
        "model": model,
        "model_slug": model_dir,
        "version": str(payload.get("version") or ""),
        "profiled_at": str(payload.get("profiledAt") or ""),
        "capabilities": capabilities,
        "primitive_count": len(capabilities),
    }


def iter_profiles(skvm_root: Path) -> list[dict[str, Any]]:
    profiles_dir = skvm_root / "profiles"
    if not profiles_dir.exists():
        return []

    records: list[dict[str, Any]] = []
    for harness_dir in sorted(p for p in profiles_dir.iterdir() if p.is_dir()):
        harness = harness_dir.name
        for model_dir in sorted(p for p in harness_dir.iterdir() if p.is_dir()):
            latest = model_dir / "latest.json"
            if not latest.exists():
                continue
            record = parse_profile(latest, harness=harness, model_dir=model_dir.name)
            if record is not None:
                records.append(record)
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Pull latest from origin if clone exists",
    )
    args = parser.parse_args()

    ensure_data_dirs()
    skvm_root = ensure_clone(refresh=args.refresh)

    skills = [parse_skill(path) for path in iter_benchmark_skills(skvm_root)]
    write_json(PROCESSED_DIR / "skvm_skills.json", skills)

    profiles = iter_profiles(skvm_root)
    write_json(PROCESSED_DIR / "tcp_profiles.json", profiles)

    harnesses = sorted({p["harness"] for p in profiles})
    models = sorted({p["model"] for p in profiles})
    primitives = sorted({prim for p in profiles for prim in p["capabilities"]})

    print(f"SkVM clone:        {skvm_root}")
    print(f"Benchmark skills:  {len(skills):>4}  -> {PROCESSED_DIR / 'skvm_skills.json'}")
    print(f"TCP profiles:      {len(profiles):>4}  -> {PROCESSED_DIR / 'tcp_profiles.json'}")
    print(f"  harnesses ({len(harnesses)}): {', '.join(harnesses)}")
    print(f"  models ({len(models)}): {len(models)} unique")
    print(f"  primitive ids ({len(primitives)}): {len(primitives)} unique")


if __name__ == "__main__":
    main()
