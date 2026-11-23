"""aesop as a deedum App: content/*.yaml + templates/ -> site/ (`uv run deedum build`).

deedum writes the head, sitemap, robots, icons and the `index.md` sibling of every
page (each page's `source`). The curated `llms.txt` / `llms-full.txt` replace
deedum's generic ones in `after_build`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import deedum
import markdown
import yaml
from relnotes.notes import KIND_TITLES

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

_md = markdown.Markdown(extensions=["fenced_code"])


def inline_md(text: str) -> str:
    """Render one paragraph of Markdown, without the wrapping <p> element."""
    _md.reset()
    html = _md.convert(text.strip())
    if html.startswith("<p>") and html.endswith("</p>"):
        html = html[3:-4]
    return html


def block_md(text: str) -> str:
    _md.reset()
    return _md.convert(text)


@dataclass
class Tool:
    id: str
    name: str
    animal: str
    accent: str
    tagline: str
    reach_for_it: str
    guide: str
    install: str
    category: str
    order: int = 100
    honorary: bool = False
    links: dict[str, str] = field(default_factory=dict)
    quickstart: str | None = None
    mascot: str | None = None
    demo: str | None = None

    @property
    def href(self) -> str:
        return f"/{self.id}/"

    @property
    def mascot_path(self) -> str:
        return f"/static/img/{self.mascot or self.id + '.webp'}"

    @property
    def reach_html(self) -> str:
        return inline_md(self.reach_for_it)

    @property
    def quickstart_html(self) -> str | None:
        if not self.quickstart:
            return None
        return block_md(self.quickstart)


@dataclass
class NewsItem:
    """One released note from a tool repo (see build/news.py)."""

    tool: str
    file: str
    date: str
    slug: str
    kind: str
    body: str
    version: str
    released: str

    @property
    def kind_title(self) -> str:
        return KIND_TITLES.get(self.kind, self.kind)

    @property
    def anchor(self) -> str:
        return f"{self.tool}-{self.date}-{self.slug}"

    @property
    def body_html(self) -> str:
        return inline_md(self.body)


NEWS_FILE = CONTENT / "news.json"
LATEST = 3


def load_news(path: Path = NEWS_FILE) -> list[NewsItem]:
    """Released notes, newest first; empty when `uv run news` has not run."""
    if not path.exists():
        return []
    return [NewsItem(**n) for n in json.loads(path.read_text(encoding="utf-8"))]


def news_line(n: NewsItem, tools: dict[str, Tool]) -> str:
    name = tools[n.tool].name if n.tool in tools else n.tool
    return f"- **{name} {n.version}** ({n.released}, {n.kind}): {n.body}"


def news_md(site: dict, news: list[NewsItem], tools: dict[str, Tool]) -> str:
    lines = [
        "# What changed",
        "",
        "Release notes from every aesop tool, newest first.",
        f"Feed: {site['base_url']}/news/feed.xml",
        "",
    ]
    lines += [news_line(n, tools) for n in news] or ["Nothing yet."]
    return "\n".join(lines) + "\n"


VERSIONS_FILE = CONTENT / "versions.json"


def load_versions(path: Path = VERSIONS_FILE) -> dict[str, dict[str, str]]:
    """Tool id -> newest release tag and its date; empty when `build.news` has not run."""
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def versions_md(site: dict, tools: list[Tool], versions: dict[str, dict[str, str]]) -> str:
    lines = [
        "# Current versions",
        "",
        "The newest release tag of every aesop tool.",
        "",
        "| tool | version | released |",
        "| --- | --- | --- |",
    ]
    for t in tools:
        v = versions.get(t.id)
        name = f"[{t.name}]({site['base_url']}{t.href})"
        lines.append(
            f"| {name} | {v['version']} | {v['released']} |" if v else f"| {name} | – | – |"
        )
    return "\n".join(lines) + "\n"


def load_yaml(name: str) -> Any:
    return yaml.safe_load((CONTENT / name).read_text(encoding="utf-8"))


def load_tools(raw: list[dict] | None = None) -> list[Tool]:
    tools = [Tool(**t) for t in (load_yaml("tools.yaml") if raw is None else raw)]
    tools.sort(key=lambda t: t.order)
    return tools


def page_md(page_id: str) -> str:
    """Raw Markdown of a prompt page (content/<id>.md); served verbatim as index.md."""
    return (CONTENT / f"{page_id}.md").read_text(encoding="utf-8").strip()


def tool_md(site: dict, t: Tool, news: list[NewsItem] | None = None) -> str:
    lines = [
        f"# {t.name}",
        "",
        f"*{t.animal}*{' (honorary)' if t.honorary else ''} · {t.category}"
        f" · {site['base_url']}{t.href}",
        "",
        f"**{t.tagline}**",
        "",
        "## Teach your agent",
        "",
        "```",
        t.guide,
        "```",
        "",
        "## Run",
        "",
        "```",
        t.install,
        "```",
        "",
        "## Reach for it when",
        "",
        t.reach_for_it.strip(),
        "",
    ]
    if t.quickstart:
        lines += ["## Quickstart", "", t.quickstart.strip(), ""]
    mine = [n for n in news or [] if n.tool == t.id][:LATEST]
    if mine:
        lines += ["## Recent changes", ""]
        lines += [f"- {n.version} ({n.released}, {n.kind}): {n.body}" for n in mine]
        lines.append("")
    if t.links:
        lines += ["## Links", ""]
        lines += [f"- {name}: {url}" for name, url in t.links.items()]
        lines.append("")
    return "\n".join(lines)


def index_md(site: dict, tools: list[Tool], full: bool = False) -> str:
    lines = [
        f"# {site['title']}",
        "",
        f"> {site['tagline']}",
        "",
        site["tagline_alt"],
        "",
        "Each tool ships a `guide` subcommand that prints agent-oriented usage instructions.",
        "Run `uvx <tool>@latest guide` before using a tool.",
        "",
        "## Tools",
        "",
    ]
    for t in tools:
        lines.append(
            f"- [{t.name}]({site['base_url']}{t.href}) ({t.category}): {t.tagline} "
            f"Guide: `{t.guide}`. Markdown: {site['base_url']}{t.href}index.md"
        )
    lines += [
        "",
        "## Optional",
        "",
        f"- [Setup prompt: add all tools to a repo]({site['base_url']}/setup/index.md)",
        f"- [The guide principle, and a prompt to add `guide` to any CLI]"
        f"({site['base_url']}/guide/index.md)",
        f"- [What changed: release notes of every tool]({site['base_url']}/news/index.md)",
        f"- [Current versions of every tool]({site['base_url']}/versions/index.md)",
        f"- [Everything in one file]({site['base_url']}/llms-full.txt)",
        f"- [Author](https://github.com/mojzis): {site['author']}",
        "",
    ]
    if full:
        for t in tools:
            lines += ["---", "", tool_md(site, t)]
    return "\n".join(lines)


class Aesop(deedum.App):
    """Pages from content/site.yaml, tools.yaml, <page>.md and news.json."""

    def __init__(self, site: deedum.Site) -> None:
        super().__init__(site)
        self.copy: dict[str, Any] = {
            **self.data["site"],
            "title": site.title,
            "author": site.author,
            "base_url": site.absolute("").rstrip("/"),
        }
        self.tools = load_tools(self.data["tools"])
        self.news = load_news()
        self.versions = load_versions()

    def tool_news(self, tool: Tool) -> list[NewsItem]:
        return [n for n in self.news if n.tool == tool.id][:LATEST]

    def load_pages(self) -> list[deedum.Page]:
        copy, site = self.copy, self.site
        by_id = {t.id: t for t in self.tools}
        pages = [
            self.page(
                "",
                title=site.title,
                description=site.description,
                template="index.html",
                source=index_md(copy, self.tools),
            )
        ]
        for entry in copy["pages"]:
            raw = page_md(entry["id"])
            meta = {k: v for k, v in entry.items() if k not in ("title", "description")}
            pages.append(
                self.page(
                    f"{entry['id']}/",
                    title=entry["page_title"],
                    description=entry["description"],
                    heading=entry["title"],
                    body=block_md(raw),
                    source=raw + "\n",
                    **meta,
                )
            )
        for t in self.tools:
            pages.append(
                self.page(
                    t.href.lstrip("/"),
                    title=t.name,
                    description=t.tagline,
                    image=t.mascot_path.lstrip("/"),
                    template="tool.html",
                    source=tool_md(copy, t, self.news),
                    tool=t,
                    tool_news=self.tool_news(t),
                )
            )
        pages.append(
            self.page(
                "news/",
                title="what changed",
                description="Release notes from every aesop tool, newest first.",
                image="static/img/og-news.webp",
                template="news.html",
                source=news_md(copy, self.news, by_id),
            )
        )
        pages.append(
            self.page(
                "news/feed.xml",
                title="what changed",
                template="feed.xml",
                updated_on=self.news[0].released if self.news else None,
            )
        )
        return pages

    def globals(self) -> dict[str, Any]:
        return {
            "aesop": self.copy,
            "tools": self.tools,
            "tools_by_id": {t.id: t for t in self.tools},
            "by_category": {
                key: [t for t in self.tools if t.category == key] for key in self.copy["categories"]
            },
            "news": self.news,
            "latest": self.news[:LATEST],
        }

    def after_build(self, out: Path) -> None:
        """Replace deedum's generic llms files with the curated ones; add versions/index.md."""
        (out / "llms.txt").write_text(index_md(self.copy, self.tools), encoding="utf-8")
        full = index_md(self.copy, self.tools, full=True)
        (out / "llms-full.txt").write_text(full, encoding="utf-8")
        (out / "versions").mkdir(exist_ok=True)
        md = versions_md(self.copy, self.tools, self.versions)
        (out / "versions" / "index.md").write_text(md, encoding="utf-8")
