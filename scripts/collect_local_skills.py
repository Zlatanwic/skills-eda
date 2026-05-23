from __future__ import annotations

from pathlib import Path

from skillscope_common import (
    PROCESSED_DIR,
    SKILL_ROOTS,
    SkillPath,
    content_hash,
    ensure_data_dirs,
    extract_code_blocks,
    extract_headings,
    parse_frontmatter,
    read_text,
    resolve_skill_name,
    stable_id,
    write_json,
)


def iter_skill_paths() -> list[SkillPath]:
    skill_paths: list[SkillPath] = []
    for root_config in SKILL_ROOTS:
        root = Path(root_config["root"])
        if not root.exists():
            continue
        for path in root.rglob("SKILL.md"):
            skill_paths.append(
                SkillPath(
                    source=str(root_config["source"]),
                    root=root,
                    path=path,
                )
            )
    return sorted(skill_paths, key=lambda item: (item.source, item.relative_path))


def parse_skill(skill_path: SkillPath) -> dict:
    raw_text = read_text(skill_path.path)
    frontmatter, body = parse_frontmatter(raw_text)
    headings = extract_headings(body)
    code_blocks = extract_code_blocks(body)

    parent = skill_path.path.parent
    # Walk up to find a meaningful directory name (skip "skills", root, etc.)
    dir_name = parent.name
    grandparent_name = parent.parent.name if parent.parent != parent else ""
    name = resolve_skill_name(frontmatter, headings, dir_name, grandparent_name, parent.stem)
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
        },
        "parsed": {
            "headings": headings,
            "code_blocks": code_blocks,
        },
    }


def main() -> None:
    ensure_data_dirs()
    records = [parse_skill(skill_path) for skill_path in iter_skill_paths()]
    write_json(PROCESSED_DIR / "skills.json", records)
    print(f"Collected {len(records)} local skills")
    print(PROCESSED_DIR / "skills.json")


if __name__ == "__main__":
    main()
