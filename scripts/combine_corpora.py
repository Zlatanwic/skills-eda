from __future__ import annotations

from skillscope_common import PROCESSED_DIR, ensure_data_dirs, read_json, write_json


def main() -> None:
    ensure_data_dirs()
    local_skills = read_json(PROCESSED_DIR / "skills.json")
    skvm_path = PROCESSED_DIR / "skvm_skills.json"
    skvm_skills = read_json(skvm_path) if skvm_path.exists() else []
    public_path = PROCESSED_DIR / "public_skills.json"
    public_skills = read_json(public_path) if public_path.exists() else []

    seen_hashes: set[str] = set()
    combined = []
    for record in [*local_skills, *skvm_skills, *public_skills]:
        dedupe_key = f"{record['source']}::{record['content_hash']}"
        if dedupe_key in seen_hashes:
            continue
        seen_hashes.add(dedupe_key)
        combined.append(record)

    combined.sort(key=lambda item: (item["source"], item["name"], item["skill_id"]))
    write_json(PROCESSED_DIR / "skills_corpus.json", combined)

    print(
        "Combined corpus: "
        f"{len(local_skills)} local + {len(skvm_skills)} SkVM + {len(public_skills)} public "
        f"-> {len(combined)} skills"
    )
    print(PROCESSED_DIR / "skills_corpus.json")


if __name__ == "__main__":
    main()
