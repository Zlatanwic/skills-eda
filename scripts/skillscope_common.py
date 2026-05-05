from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DASHBOARD_DIR = DATA_DIR / "dashboard"
PUBLIC_DATA_DIR = REPO_ROOT / "public" / "data"


SKILL_ROOTS = [
    {
        "source": "local.codex",
        "root": Path.home() / ".codex" / "skills",
    },
    {
        "source": "local.agents",
        "root": Path.home() / ".agents" / "skills",
    },
    {
        "source": "local.cc-switch",
        "root": Path.home() / ".cc-switch" / "skills",
    },
]


def ensure_data_dirs() -> None:
    for directory in [RAW_DIR, PROCESSED_DIR, DASHBOARD_DIR, PUBLIC_DATA_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def read_text(path: Path) -> str:
    for encoding in ["utf-8-sig", "utf-8", "gb18030", "latin-1"]:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_id(*parts: str) -> str:
    raw = "::".join(parts)
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", parts[-1]).strip("_").lower()
    return f"{slug}__{digest}" if slug else digest


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, flags=re.DOTALL)
    if not match:
        return {}, text

    frontmatter_text = match.group(1)
    body = text[match.end() :]
    metadata: dict[str, Any] = {}

    for raw_line in frontmatter_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if value.lower() == "true":
            metadata[key] = True
        elif value.lower() == "false":
            metadata[key] = False
        elif value.lower() in {"null", "none"}:
            metadata[key] = None
        else:
            metadata[key] = value

    return metadata, body


def extract_headings(markdown: str) -> list[dict[str, Any]]:
    headings = []
    for match in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", markdown, flags=re.MULTILINE):
        headings.append(
            {
                "level": len(match.group(1)),
                "title": match.group(2).strip(),
                "position": match.start(),
            }
        )
    return headings


def extract_code_blocks(markdown: str) -> list[dict[str, Any]]:
    blocks = []
    pattern = re.compile(r"```([^\n`]*)\n(.*?)```", flags=re.DOTALL)
    for match in pattern.finditer(markdown):
        language = match.group(1).strip().lower()
        code = match.group(2).strip("\n")
        blocks.append(
            {
                "language": language or "plain",
                "code": code,
                "line_count": len(code.splitlines()) if code else 0,
            }
        )
    return blocks


def count_regex(markdown: str, pattern: str) -> int:
    return len(re.findall(pattern, markdown, flags=re.IGNORECASE | re.MULTILINE))


def keyword_hits(markdown: str, keywords: list[str]) -> list[str]:
    lower = markdown.lower()
    return sorted({keyword for keyword in keywords if keyword.lower() in lower})


@dataclass(frozen=True)
class SkillPath:
    source: str
    root: Path
    path: Path

    @property
    def relative_path(self) -> str:
        try:
            return self.path.relative_to(self.root).as_posix()
        except ValueError:
            return self.path.as_posix()
