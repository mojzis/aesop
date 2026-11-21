"""Static site generator: content/*.yaml + templates/ -> site/."""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from relnotes.notes import KIND_TITLES

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
OUT = ROOT / "site"

_md = markdown.Markdown(extensions=["fenced_code"])


def inline_md(text: str) -> str:
    """Render one paragraph of Markdown, without the wrapping <p> element."""
    _md.reset()
    html = _md.convert(text.strip())
    if html.startswith("<p>") and html.endswith("</p>"):
        html = html[3:-4]
    return html


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
    def og_image(self) -> str:
        return f"/static/img/{self.id}-og.png"

    @property
    def reach_html(self) -> str:
        return inline_md(self.reach_for_it)

    @property
    def quickstart_html(self) -> str | None:
        if not self.quickstart:
            return None
        _md.reset()
        return _md.convert(self.quickstart)


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


def load_yaml(name: str):
    return yaml.safe_load((CONTENT / name).read_text(encoding="utf-8"))


def load_tools() -> list[Tool]:
    tools = [Tool(**t) for t in load_yaml("tools.yaml")]
    tools.sort(key=lambda t: t.order)
    return tools


def render(env: Environment, template: str, out: Path, **ctx) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(env.get_template(template).render(**ctx), encoding="utf-8")


def page_md(page_id: str) -> str:
    """Raw Markdown of a prompt page (content/<id>.md); served verbatim as index.md."""
    return (CONTENT / f"{page_id}.md").read_text(encoding="utf-8").strip()


def render_page(env: Environment, page: dict, **base) -> None:
    """One prompt page: content/<id>.md -> /<id>/index.html + /<id>/index.md."""
    raw = page_md(page["id"])
    _md.reset()
    out = OUT / page["id"]
    render(env, "page.html", out / "index.html", page=page, raw=raw, html=_md.convert(raw), **base)
    (out / "index.md").write_text(raw + "\n", encoding="utf-8")


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
        f"- [Everything in one file]({site['base_url']}/llms-full.txt)",
        f"- [Author](https://github.com/mojzis): {site['author']}",
        "",
    ]
    if full:
        for t in tools:
            lines += ["---", "", tool_md(site, t)]
    return "\n".join(lines)


def write_markdown(site: dict, tools: list[Tool], news: list[NewsItem]) -> None:
    (OUT / "llms.txt").write_text(index_md(site, tools), encoding="utf-8")
    (OUT / "index.md").write_text(index_md(site, tools), encoding="utf-8")
    (OUT / "llms-full.txt").write_text(index_md(site, tools, full=True), encoding="utf-8")
    for t in tools:
        (OUT / t.id / "index.md").write_text(tool_md(site, t, news), encoding="utf-8")
    by_id = {t.id: t for t in tools}
    (OUT / "news" / "index.md").write_text(news_md(site, news, by_id), encoding="utf-8")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    env = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    site = load_yaml("site.yaml")
    site["base_url"] = os.environ.get("BASE_URL", site["base_url"])
    tools = load_tools()
    by_category = {key: [t for t in tools if t.category == key] for key in site["categories"]}
    news = load_news()
    base = {
        "site": site,
        "tools": tools,
        "tools_by_id": {t.id: t for t in tools},
        "by_category": by_category,
        "news": news,
        "latest": news[:LATEST],
        "year": date.today().year,
    }

    render(env, "index.html", OUT / "index.html", **base)
    for page in site["pages"]:
        render_page(env, page, **base)
    for t in tools:
        mine = [n for n in news if n.tool == t.id][:LATEST]
        render(env, "tool.html", OUT / t.id / "index.html", tool=t, tool_news=mine, **base)
    render(env, "news.html", OUT / "news" / "index.html", **base)
    render(
        env,
        "feed.xml",
        OUT / "news" / "feed.xml",
        updated=news[0].released if news else None,
        **base,
    )

    shutil.copytree(STATIC, OUT / "static")
    write_markdown(site, tools, news)
    (OUT / ".nojekyll").touch()
    print(f"built {len(tools)} tools, {len(news)} news -> {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
