from __future__ import annotations

import build_dashboard_data
import collect_local_skills
import collect_skvm_data
import combine_corpora
import compute_risks
import extract_features
import extract_scr


def main() -> None:
    collect_local_skills.main()
    collect_skvm_data.main()
    combine_corpora.main()
    extract_features.main()
    extract_scr.main()
    compute_risks.main()
    build_dashboard_data.main()


if __name__ == "__main__":
    main()
