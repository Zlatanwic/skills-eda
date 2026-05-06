from __future__ import annotations

import os

import build_dashboard_data
import collect_public_skills
import collect_local_skills
import collect_skvm_data
import combine_corpora
import compute_risks
import extract_features
import extract_scr
import extract_scr_llm
from skillscope_common import PROCESSED_DIR, REPO_ROOT, read_json, write_json


def load_dotenv() -> None:
    env_path = REPO_ROOT / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        os.environ.setdefault(key.strip(), value)


def run_optional_llm_scr() -> bool:
    enabled = os.environ.get("SKILLSCOPE_LLM_SCR_ENABLE", "0").lower() in {"1", "true", "yes"}
    if not enabled:
        print("LLM SCR skipped: set SKILLSCOPE_LLM_SCR_ENABLE=1 to enable optional LLM-assisted extraction.")
        return False

    args = ["--merge"]
    limit = os.environ.get("SKILLSCOPE_LLM_SCR_LIMIT")
    if limit:
        args.extend(["--limit", limit])
    selection = os.environ.get("SKILLSCOPE_LLM_SCR_SELECTION")
    if selection:
        args.extend(["--selection", selection])
    source = os.environ.get("SKILLSCOPE_LLM_SCR_SOURCE")
    if source:
        args.extend(["--source", source])
    min_confidence = os.environ.get("SKILLSCOPE_LLM_SCR_MIN_CONFIDENCE")
    if min_confidence:
        args.extend(["--min-confidence", min_confidence])
    min_risk = os.environ.get("SKILLSCOPE_LLM_SCR_MIN_RISK")
    if min_risk:
        args.extend(["--min-risk", min_risk])
    min_score = os.environ.get("SKILLSCOPE_LLM_SCR_MIN_SCORE")
    if min_score:
        args.extend(["--min-score", min_score])
    max_chars = os.environ.get("SKILLSCOPE_LLM_SCR_MAX_CHARS")
    if max_chars:
        args.extend(["--max-chars", max_chars])

    extract_scr_llm.main(args)
    return True


def reapply_existing_llm_scr() -> bool:
    if not extract_scr_llm.ANNOTATIONS_PATH.exists():
        return False
    annotations = read_json(extract_scr_llm.ANNOTATIONS_PATH)
    if not annotations:
        return False
    records = read_json(PROCESSED_DIR / "skills_enriched.json")
    merged = extract_scr_llm.merge_annotations(records, annotations)
    write_json(PROCESSED_DIR / "skills_enriched.json", merged)
    print(f"Reapplied {len(annotations)} existing LLM SCR annotations")
    return True


def main() -> None:
    load_dotenv()
    collect_local_skills.main()
    collect_skvm_data.main()
    collect_public_skills.main()
    combine_corpora.main()
    extract_features.main()
    extract_scr.main()
    ran_llm = run_optional_llm_scr()
    if not ran_llm:
        ran_llm = reapply_existing_llm_scr()
    if ran_llm:
        print("Recomputing TCP gap risks after LLM SCR merge")
    compute_risks.main()
    build_dashboard_data.main()


if __name__ == "__main__":
    main()
