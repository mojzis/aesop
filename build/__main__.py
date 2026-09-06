"""Static site generator: content/ + templates/ -> site/."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
OUT = ROOT / "site"


@dataclass
class Project:
    slug: str
    title: str
    summary: str
    body_html: str
    date: date | None = None
    tags: list[str] = field(default_factory=list)
    repo: str | None = None
    url: str | None = None
    featured: bool = False

    @property
    def href(self) -> str:
        return f"/projects/{self.slug}/"


def split_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    _, fm, body = text.split("---", 2)
    return yaml.safe_load(fm) or {}, body.strip()


def load_projects() -> list[Project]:
    md = markdown.Markdown(extensions=["fenced_code", "tables", "toc"])
    projects: list[Project] = []
    for path in sorted((CONTENT / "projects").glob("*.md")):
        meta, body = split_front_matter(path.read_text(encoding="utf-8"))
        md.reset()
        projects.append(
            Project(
                slug=meta.get("slug", path.stem),
                title=meta["title"],
                summary=meta.get("summary", ""),
                body_html=md.convert(body),
                date=meta.get("date"),
                tags=meta.get("tags", []),
                repo=meta.get("repo"),
                url=meta.get("url"),
                featured=meta.get("featured", False),
            )
        )
    projects.sort(key=lambda p: p.date or date.min, reverse=True)
    return projects


def load_site_config() -> dict:
    return yaml.safe_load((CONTENT / "site.yaml").read_text(encoding="utf-8"))


def render(env: Environment, template: str, out: Path, **ctx) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(env.get_template(template).render(**ctx), encoding="utf-8")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    env = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    site = load_site_config()
    projects = load_projects()
    base = {"site": site, "projects": projects, "year": date.today().year}

    render(env, "index.html", OUT / "index.html", page_title=None, **base)
    for p in projects:
        render(
            env,
            "project.html",
            OUT / "projects" / p.slug / "index.html",
            project=p,
            page_title=p.title,
            **base,
        )

    shutil.copytree(STATIC, OUT / "static")
    (OUT / ".nojekyll").touch()
    print(f"built {len(projects)} projects -> {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
