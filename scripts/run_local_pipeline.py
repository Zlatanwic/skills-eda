from __future__ import annotations

import collect_local_skills
import combine_corpora
import extract_features
import extract_scr
import build_dashboard_data


def main() -> None:
    collect_local_skills.main()
    combine_corpora.main()
    extract_features.main()
    extract_scr.main()
    build_dashboard_data.main()


if __name__ == "__main__":
    main()
