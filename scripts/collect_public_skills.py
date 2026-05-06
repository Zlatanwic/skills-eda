from __future__ import annotations

import base64
import os
import time
import urllib.parse
import urllib.request
from typing import Any

from skillscope_common import (
    PROCESSED_DIR,
    RAW_DIR,
    REPO_ROOT,
    content_hash,
    ensure_data_dirs,
    extract_code_blocks,
    extract_headings,
    parse_frontmatter,
    read_json,
    stable_id,
    write_json,
)


GITHUB_SEARCH_URL = "https://api.github.com/search/code"
GITHUB_CONTENTS_ACCEPT = "application/vnd.github.raw+json"
DEFAULT_QUERIES = [
    'filename:SKILL.md "description"',
    'filename:SKILL.md "skills"',
    'filename:SKILL.md "When"',
    'filename:SKILL.md "Use this skill"',
]


def load_dotenv() -> None:
    env_path = REPO_ROOT / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        os.environ.setdefault(key, value)


def request_json(url: str, token: str | None = None, accept: str = "application/vnd.github+json") -> Any:
    headers = {
        "Accept": accept,
        "User-Agent": "skillscope-public-sampler",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
    import json

    return json.loads(body)


def request_text(url: str, token: str | None = None) -> str:
    headers = {
        "Accept": GITHUB_CONTENTS_ACCEPT,
        "User-Agent": "skillscope-public-sampler",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read()

    # GitHub may still return a JSON object for contents endpoints depending on
    # proxy behavior. Handle both raw text and base64 JSON payloads.
    try:
        import json

        payload = json.loads(body.decode("utf-8"))
        if isinstance(payload, dict) and payload.get("encoding") == "base64":
            return base64.b64decode(str(payload["content"])).decode("utf-8", errors="replace")
    except Exception:
        pass

    return body.decode("utf-8", errors="replace")


def parse_public_skill(item: dict[str, Any], raw_text: str) -> dict[str, Any]:
    frontmatter, body = parse_frontmatter(raw_text)
    headings = extract_headings(body)
    code_blocks = extract_code_blocks(body)
    repo = item.get("repository", {})
    repo_full_name = repo.get("full_name", "unknown/repo")
    path = item.get("path", "SKILL.md")
    fallback_name = path.split("/")[-2] if "/" in path else path.removesuffix(".md")
    name = str(frontmatter.get("name") or fallback_name)

    html_url = item.get("html_url") or ""
    source_url = html_url.replace("/blob/", "/raw/") if html_url else item.get("url", "")

    return {
        "skill_id": stable_id("public.github", repo_full_name, path),
        "name": name,
        "source": "public.github",
        "path_or_url": source_url,
        "relative_path": f"{repo_full_name}/{path}",
        "content_hash": content_hash(raw_text),
        "raw_text": raw_text,
        "body_text": body,
        "metadata": {
            "description": str(frontmatter.get("description") or ""),
            "frontmatter": frontmatter,
            "repo": repo_full_name,
            "html_url": html_url,
            "license": (repo.get("license") or {}).get("spdx_id") if isinstance(repo.get("license"), dict) else None,
            "collected_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
        "parsed": {
            "headings": headings,
            "code_blocks": code_blocks,
        },
    }


def search_github_skills(token: str | None, limit: int, queries: list[str]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    records: list[dict[str, Any]] = []
    per_query = max(5, min(50, limit))

    for query in queries:
        if len(records) >= limit:
            break
        params = urllib.parse.urlencode({"q": query, "per_page": per_query})
        url = f"{GITHUB_SEARCH_URL}?{params}"
        payload = request_json(url, token=token)
        for item in payload.get("items", []):
            key = f"{item.get('repository', {}).get('full_name')}::{item.get('path')}"
            if key in seen:
                continue
            seen.add(key)
            try:
                raw_text = request_text(item["url"], token=token)
            except Exception as exc:
                print(f"Skip {key}: {exc}")
                continue
            if len(raw_text.strip()) < 100:
                continue
            records.append(parse_public_skill(item, raw_text))
            if len(records) >= limit:
                break
        time.sleep(1.2)

    return records


def load_cached_public_skills() -> list[dict[str, Any]]:
    cache_path = RAW_DIR / "public-skills" / "github_skill_sample.json"
    if cache_path.exists():
        return read_json(cache_path)
    return []


def main() -> None:
    ensure_data_dirs()
    load_dotenv()
    token = os.environ.get("SKILLSCOPE_PUBLIC_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
    limit = int(os.environ.get("SKILLSCOPE_PUBLIC_MAX_RESULTS", "100"))
    queries = [
        item.strip()
        for item in os.environ.get("SKILLSCOPE_PUBLIC_QUERIES", "").split(";")
        if item.strip()
    ] or DEFAULT_QUERIES

    records: list[dict[str, Any]] = []
    if token or os.environ.get("SKILLSCOPE_PUBLIC_ALLOW_UNAUTHENTICATED") == "1":
        try:
            records = search_github_skills(token=token, limit=limit, queries=queries)
            write_json(RAW_DIR / "public-skills" / "github_skill_sample.json", records)
        except Exception as exc:
            print(f"Public skill collection failed, using cache if available: {exc}")
            records = load_cached_public_skills()
    else:
        print("Public skill collection skipped: set SKILLSCOPE_PUBLIC_GITHUB_TOKEN to enable GitHub sampling.")
        records = load_cached_public_skills()

    write_json(PROCESSED_DIR / "public_skills.json", records)
    print(f"Collected {len(records)} public skills")
    print(PROCESSED_DIR / "public_skills.json")


if __name__ == "__main__":
    main()
