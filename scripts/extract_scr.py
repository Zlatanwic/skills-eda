from __future__ import annotations

from typing import Any

from skillscope_common import PROCESSED_DIR, keyword_hits, read_json, write_json


RULES = [
    {
        "primitive": "gen.code.shell",
        "keywords": ["```bash", "```sh", "```shell", "shell command", "bash", "powershell", "command line"],
        "evidence": "shell-related language",
    },
    {
        "primitive": "gen.code.python",
        "keywords": ["python", "pytest", "pandas", "numpy", "matplotlib", "python-pptx"],
        "evidence": "Python-related language",
    },
    {
        "primitive": "gen.code.javascript",
        "keywords": ["javascript", "node", "npm", "vite", "react", "js "],
        "evidence": "JavaScript-related language",
    },
    {
        "primitive": "gen.code.typescript",
        "keywords": ["typescript", "tsx", "tsconfig", "type-safe"],
        "evidence": "TypeScript-related language",
    },
    {
        "primitive": "gen.code.sql",
        "keywords": ["sql", "sqlite", "postgres", "mysql", "query", "migration"],
        "evidence": "SQL/database language",
    },
    {
        "primitive": "gen.code.test",
        "keywords": ["test", "tests", "pytest", "vitest", "playwright", "unit test", "e2e"],
        "evidence": "testing language",
    },
    {
        "primitive": "tool.exec",
        "keywords": ["execute command", "run command", "shell command", "terminal", "cli", "subprocess"],
        "evidence": "command execution language",
    },
    {
        "primitive": "tool.file.read",
        "keywords": ["read file", "inspect file", "open file", "load file", "parse file"],
        "evidence": "file reading language",
    },
    {
        "primitive": "tool.file.write",
        "keywords": ["write file", "edit file", "create file", "modify", "patch", "save"],
        "evidence": "file writing language",
    },
    {
        "primitive": "tool.web.search",
        "keywords": ["web search", "search the web", "google", "search query", "latest"],
        "evidence": "web search language",
    },
    {
        "primitive": "tool.web.fetch",
        "keywords": ["fetch url", "fetch", "download", "http request", "curl", "wget"],
        "evidence": "web fetch language",
    },
    {
        "primitive": "tool.browser",
        "keywords": ["browser", "screenshot", "click", "navigate", "playwright", "localhost"],
        "evidence": "browser interaction language",
    },
    {
        "primitive": "tool.git",
        "keywords": ["git", "commit", "branch", "diff", "merge", "rebase"],
        "evidence": "git language",
    },
    {
        "primitive": "tool.github",
        "keywords": ["github", "pull request", "gh issue", "gh pr", "github issue"],
        "evidence": "GitHub language",
    },
    {
        "primitive": "tool.package_manager",
        "keywords": ["npm install", "pip install", "package manager", "dependencies", "requirements.txt", "package.json"],
        "evidence": "package management language",
    },
    {
        "primitive": "data.parse",
        "keywords": ["parse", "json", "yaml", "csv", "xml", "extract", "scrape"],
        "evidence": "data parsing language",
    },
    {
        "primitive": "data.transform",
        "keywords": ["transform", "clean", "aggregate", "normalize", "deduplicate", "filter", "join"],
        "evidence": "data transformation language",
    },
    {
        "primitive": "data.visualize",
        "keywords": ["visualize", "visualization", "chart", "plot", "dashboard", "graph", "map"],
        "evidence": "visualization language",
    },
    {
        "primitive": "doc.generate",
        "keywords": ["document", "markdown", "report", "docs", "pdf", "docx", "write document", "write report"],
        "evidence": "document generation language",
    },
    {
        "primitive": "spreadsheet.process",
        "keywords": ["spreadsheet", "excel", "xlsx", "csv", "sheet"],
        "evidence": "spreadsheet language",
    },
    {
        "primitive": "presentation.generate",
        "keywords": ["presentation", "slide", "ppt", "pptx", "deck"],
        "evidence": "presentation language",
    },
    {
        "primitive": "reason.plan",
        "keywords": ["plan", "roadmap", "approach", "strategy", "milestone"],
        "evidence": "planning language",
    },
    {
        "primitive": "reason.diagnose",
        "keywords": ["diagnose", "debug", "root cause", "investigate", "failure", "bug"],
        "evidence": "diagnosis language",
    },
    {
        "primitive": "follow.procedure",
        "keywords": ["step", "phase", "workflow", "checklist", "process", "procedure"],
        "evidence": "procedure language",
    },
    {
        "primitive": "follow.constraints",
        "keywords": ["must", "never", "always", "do not", "constraint", "rule", "requirement"],
        "evidence": "constraint language",
    },
    {
        "primitive": "follow.verify",
        "keywords": ["verify", "validate", "check", "confirm", "test", "review"],
        "evidence": "verification language",
    },
    {
        "primitive": "agent.parallel",
        "keywords": ["parallel", "concurrent", "sub-agent", "delegate", "worker", "spawn"],
        "evidence": "parallel agent language",
    },
    {
        "primitive": "runtime.env_bind",
        "keywords": ["setup", "install", "configure", "api key", "credential", "dependency", "environment variable"],
        "evidence": "environment setup language",
    },
]


def infer_level(record: dict[str, Any], hits: list[str], primitive: str) -> int:
    features = record["features"]
    level = 1

    if features["code_block_count"] >= 2 or features["step_count"] >= 5:
        level = 2
    if features["has_branching"] or features["has_verification"]:
        level = max(level, 2)
    if features["step_count"] >= 8 or features["code_block_count"] >= 5:
        level = 3
    if primitive.startswith("tool.") and features["tool_count"] >= 8:
        level = max(level, 3)
    if primitive == "runtime.env_bind" and features["dependency_count"] >= 4:
        level = max(level, 3)
    if primitive == "follow.procedure" and features["step_count"] >= 8:
        level = 3
    if len(hits) >= 5:
        level = max(level, 2)

    return min(level, 3)


def extract_scr(record: dict[str, Any]) -> dict[str, Any]:
    text = record["raw_text"]
    requirements = []
    for rule in RULES:
        hits = keyword_hits(text, rule["keywords"])
        if not hits:
            continue

        level = infer_level(record, hits, rule["primitive"])
        confidence = min(0.92, 0.48 + 0.08 * len(hits) + 0.06 * level)
        requirements.append(
            {
                "primitive": rule["primitive"],
                "level": level,
                "method": "rule",
                "confidence": round(confidence, 3),
                "evidence": [rule["evidence"], *hits[:8]],
            }
        )

    requirements = sorted(requirements, key=lambda item: (item["primitive"], item["level"]))
    if not requirements:
        confidence = 0.2
    else:
        confidence = round(sum(item["confidence"] for item in requirements) / len(requirements), 3)

    return {
        "method": "rule",
        "confidence": confidence,
        "requirements": requirements,
    }


def compute_risks(record: dict[str, Any]) -> dict[str, float]:
    features = record["features"]
    requirements = record["scr"]["requirements"]

    model_mismatch = min(
        1.0,
        0.04 * features["step_count"]
        + 0.03 * features["code_block_count"]
        + (0.14 if features["has_branching"] else 0)
        + (0.12 if features["has_verification"] else 0)
        + 0.02 * sum(req["level"] for req in requirements),
    )
    harness_mismatch = min(
        1.0,
        0.06 * features["tool_count"]
        + 0.10 * len([req for req in requirements if req["primitive"].startswith("tool.")])
        + (0.12 if any(req["primitive"] == "agent.parallel" for req in requirements) else 0),
    )
    environment_mismatch = min(
        1.0,
        0.10 * features["dependency_count"]
        + (0.18 if any(req["primitive"] == "tool.package_manager" for req in requirements) else 0)
        + (0.16 if any(req["primitive"] == "runtime.env_bind" for req in requirements) else 0),
    )
    overall = round((model_mismatch * 0.4 + harness_mismatch * 0.35 + environment_mismatch * 0.25), 3)

    return {
        "model_mismatch": round(model_mismatch, 3),
        "harness_mismatch": round(harness_mismatch, 3),
        "environment_mismatch": round(environment_mismatch, 3),
        "overall": overall,
    }


def main() -> None:
    records = read_json(PROCESSED_DIR / "skills_features.json")
    for record in records:
        record["scr"] = extract_scr(record)
        record["risks"] = compute_risks(record)

    write_json(PROCESSED_DIR / "skills_enriched.json", records)
    print(f"Extracted SCR and risks for {len(records)} skills")
    print(PROCESSED_DIR / "skills_enriched.json")


if __name__ == "__main__":
    main()
