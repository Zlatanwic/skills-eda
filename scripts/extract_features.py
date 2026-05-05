from __future__ import annotations

import re
from collections import Counter
from typing import Any

from skillscope_common import (
    PROCESSED_DIR,
    count_regex,
    keyword_hits,
    read_json,
    write_json,
)


TOOL_KEYWORDS = [
    "bash",
    "shell",
    "powershell",
    "python",
    "node",
    "npm",
    "pnpm",
    "yarn",
    "pip",
    "uv",
    "git",
    "github",
    "gh ",
    "browser",
    "playwright",
    "curl",
    "wget",
    "docker",
    "sql",
    "sqlite",
    "postgres",
    "api",
    "cli",
]

DEPENDENCY_KEYWORDS = [
    "install",
    "dependency",
    "dependencies",
    "package",
    "requirements.txt",
    "package.json",
    "pip install",
    "npm install",
    "pnpm install",
    "yarn add",
    "api key",
    "token",
    "env var",
    "environment variable",
    "secret",
    "credential",
]

DOMAIN_KEYWORDS = {
    "code": ["code", "typescript", "javascript", "python", "refactor", "test", "bug", "api"],
    "data": ["data", "csv", "json", "excel", "spreadsheet", "chart", "plot", "visualization"],
    "document": ["document", "markdown", "pdf", "docx", "report", "write", "docs"],
    "web": ["web", "browser", "html", "css", "frontend", "react", "site"],
    "security": ["security", "audit", "vulnerability", "secret", "iam", "penetration"],
    "research": ["research", "paper", "search", "literature", "academic", "citation"],
    "agent": ["agent", "skill", "tool", "workflow", "orchestration", "sub-agent"],
    "cloud": ["aws", "azure", "gcp", "cloud", "serverless", "terraform"],
}


def infer_taxonomy(text: str, features: dict[str, Any]) -> dict[str, Any]:
    lower = text.lower()
    tool_score = sum(lower.count(word) for word in ["tool", "api", "cli", "command", "library", "package"])
    procedure_score = features["step_count"] + sum(
        lower.count(word) for word in ["step", "workflow", "process", "phase", "verify", "checklist"]
    )
    generative_score = sum(
        lower.count(word) for word in ["generate", "write", "create", "draft", "compose", "produce"]
    )

    scores = {
        "tool-reference": tool_score,
        "procedural": procedure_score,
        "generative": generative_score,
    }
    primary_type, max_score = max(scores.items(), key=lambda item: item[1])
    if max_score == 0:
        primary_type = "mixed"

    sorted_scores = sorted(scores.values(), reverse=True)
    confidence = 0.45
    if sorted_scores[0] > 0:
        confidence = min(0.95, 0.5 + (sorted_scores[0] - sorted_scores[1]) / (sorted_scores[0] + 1) * 0.45)

    domains = []
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if keyword_hits(lower, keywords):
            domains.append(domain)

    return {
        "primary_type": primary_type,
        "scores": scores,
        "domains": domains or ["general"],
        "confidence": round(confidence, 3),
    }


def extract_features(record: dict[str, Any]) -> dict[str, Any]:
    text = record["body_text"]
    all_text = record["raw_text"]
    headings = record["parsed"]["headings"]
    code_blocks = record["parsed"]["code_blocks"]
    code_languages = Counter(block["language"] or "plain" for block in code_blocks)

    step_count = count_regex(text, r"^\s*(?:\d+[\.)]|[-*]\s+\[[ x]\]|[-*]\s+(?:step|phase)\b)")
    explicit_step_words = count_regex(text, r"\b(?:step|phase|stage)\s+\d+\b")
    step_count = max(step_count, explicit_step_words)

    branch_hits = keyword_hits(text, ["if ", "else", "when ", "unless", "otherwise", "condition", "branch"])
    loop_hits = keyword_hits(text, ["loop", "repeat", "iterate", "for each", "until"])
    verify_hits = keyword_hits(text, ["verify", "validate", "test", "check", "confirm", "inspect"])
    tool_hits = keyword_hits(all_text, TOOL_KEYWORDS)
    dependency_hits = keyword_hits(all_text, DEPENDENCY_KEYWORDS)

    features = {
        "char_count": len(all_text),
        "word_count": len(re.findall(r"\b\w+\b", all_text)),
        "line_count": len(all_text.splitlines()),
        "section_count": len(headings),
        "code_block_count": len(code_blocks),
        "code_line_count": sum(block["line_count"] for block in code_blocks),
        "code_languages": dict(sorted(code_languages.items())),
        "step_count": step_count,
        "dependency_count": len(dependency_hits),
        "tool_count": len(tool_hits),
        "has_branching": bool(branch_hits),
        "has_loop": bool(loop_hits),
        "has_verification": bool(verify_hits),
        "branching_evidence": branch_hits[:10],
        "loop_evidence": loop_hits[:10],
        "verification_evidence": verify_hits[:10],
        "tool_evidence": tool_hits[:20],
        "dependency_evidence": dependency_hits[:20],
    }
    return features


def main() -> None:
    corpus_path = PROCESSED_DIR / "skills_corpus.json"
    records = read_json(corpus_path if corpus_path.exists() else PROCESSED_DIR / "skills.json")
    enriched = []
    for record in records:
        features = extract_features(record)
        record["features"] = features
        record["taxonomy"] = infer_taxonomy(record["raw_text"], features)
        enriched.append(record)

    write_json(PROCESSED_DIR / "skills_features.json", enriched)
    print(f"Extracted features for {len(enriched)} skills")
    print(PROCESSED_DIR / "skills_features.json")


if __name__ == "__main__":
    main()
