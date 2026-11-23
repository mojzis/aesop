"""Pull released notes from every tool repo into content/news.json.

    uv run python -m build.news           # clone or update the repos in .cache/repos/
    uv run python -m build.news --local   # read the sibling checkouts in ../ (no network)

Only notes that shipped in a release tag are kept. The newest `v*` tag of each repo
goes to content/versions.json. The build reads both JSON files when they exist;
without them the site builds with no news and no versions page.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict
from pathlib import Path

import yaml
from relnotes.notes import collect

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache" / "repos"
NEWS = ROOT / "content" / "news.json"
VERSIONS = ROOT / "content" / "versions.json"


def repos() -> dict[str, str]:
    """Tool id -> GitHub repo URL, for tools that link one."""
    tools = yaml.safe_load((ROOT / "content" / "tools.yaml").read_text(encoding="utf-8"))
    return {t["id"]: t["links"]["repo"] for t in tools if "repo" in t.get("links", {})}


def fetch(url: str, dest: Path) -> Path:
    """Blobless clone (full history, file contents on demand), or fetch if present."""
    if (dest / ".git").exists():
        subprocess.run(
            ["git", "-C", str(dest), "fetch", "-q", "--tags", "--force", "origin"], check=True
        )
        subprocess.run(["git", "-C", str(dest), "reset", "-q", "--hard", "origin/HEAD"], check=True)
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "-q", "--filter=blob:none", url, str(dest)], check=True)
    return dest


def released(tool: str, repo: Path) -> list[dict]:
    return [{"tool": tool, **asdict(n)} for n in collect(repo) if n.version]


def _version_key(tag: str) -> tuple:
    return tuple(int(x) if x.isdigit() else -1 for x in re.split(r"[.\-+]", tag.lstrip("v")))


def latest_tag(repo: Path) -> dict[str, str] | None:
    """Newest `v*` tag of the repo and its date, or None when it has no release."""
    out = subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "for-each-ref",
            "refs/tags/v*",
            "--format=%(refname:short) %(creatordate:short)",
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    tags = dict(line.split(" ", 1) for line in out.splitlines() if " " in line)
    if not tags:
        return None
    tag = max(tags, key=_version_key)
    return {"version": tag, "released": tags[tag]}


def sort_key(item: dict) -> tuple:
    return (item["released"] or "", item["date"], item["tool"], item["file"])


def main() -> None:
    ap = argparse.ArgumentParser(description="Pull released notes from the tool repos.")
    ap.add_argument("--local", action="store_true", help="read ../<repo> checkouts")
    args = ap.parse_args()
    items: list[dict] = []
    versions: dict[str, dict[str, str]] = {}
    for tool, url in repos().items():
        name = url.rstrip("/").rsplit("/", 1)[-1]
        repo = ROOT.parent / name if args.local else fetch(url, CACHE / name)
        if repo.is_dir():
            items += released(tool, repo)
            if tag := latest_tag(repo):
                versions[tool] = tag
    items.sort(key=sort_key, reverse=True)
    NEWS.write_text(json.dumps(items, indent=2) + "\n", encoding="utf-8")
    VERSIONS.write_text(json.dumps(versions, indent=2) + "\n", encoding="utf-8")
    print(f"{len(items)} released notes -> {NEWS.relative_to(ROOT)}")
    print(f"{len(versions)} tool versions -> {VERSIONS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
