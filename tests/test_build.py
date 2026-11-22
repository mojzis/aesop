from dataclasses import replace
from pathlib import Path

import deedum
from deedum.app import build
from deedum.check import check_folder

from build.aesop import (
    ROOT,
    Tool,
    index_md,
    inline_md,
    load_news,
    load_tools,
    load_yaml,
    news_md,
    page_md,
    tool_md,
)

BASE = Tool(
    id="biston",
    name="biston",
    animal="peppered moth",
    accent="#000",
    tagline="Finds clones.",
    reach_for_it="When *it* grew.",
    guide="uvx biston guide",
    install="uvx biston",
    category="guardrails",
)
SITE = {"base_url": "https://x"}  # zorilla: ignore[ZR005]


def test_inline_md_strips_wrapping_paragraph():
    assert inline_md("a *b*") == "a <em>b</em>"


def test_tool_paths_derive_from_id():
    assert BASE.href == "/biston/"  # zorilla: ignore[ZR005]
    assert BASE.mascot_path == "/static/img/biston.webp"  # zorilla: ignore[ZR005]


def test_tool_md_has_guide_before_install():
    md = tool_md(SITE, BASE)
    assert md.index("uvx biston guide") < md.index("uvx biston\n")
    assert "## Links" not in md


def test_tool_md_lists_links_when_present():
    md = tool_md(SITE, replace(BASE, links={"repo": "https://r"}))  # zorilla: ignore[ZR005]
    assert "- repo: https://r" in md  # zorilla: ignore[ZR005]


def test_load_tools_sorted_by_order_and_every_tool_has_a_guide():
    tools = load_tools()
    assert [t.order for t in tools] == sorted(t.order for t in tools)
    assert all(t.guide.endswith(" guide") for t in tools)


def test_every_page_has_content_and_a_url_prompt():
    site = load_yaml("site.yaml")
    ids = [p["id"] for p in site["pages"]]
    assert "setup" in ids and "guide" in ids
    for page in site["pages"]:
        assert "{url}" in page["prompt"]
        assert page_md(page["id"]).startswith("# ")


def test_index_md_links_both_prompt_pages():
    md = index_md(
        {**SITE, "title": "t", "tagline": "a", "tagline_alt": "b", "author": "me"}, [BASE]
    )
    assert "https://x/setup/index.md" in md
    assert "https://x/guide/index.md" in md


SAMPLE_NEWS = Path(__file__).parent / "news_sample.json"


def test_load_news_missing_file_means_no_news(tmp_path):
    assert load_news(tmp_path / "news.json") == []


def test_news_md_lists_every_item_with_tool_version_and_kind():
    news = load_news(SAMPLE_NEWS)
    md = news_md(SITE, news, {"biston": BASE})
    assert md.count("\n- ") == len(news)
    assert "- **biston v0.7.8** (2026-11-20, fixed): A `pyproject.toml`" in md


def test_tool_md_shows_only_that_tools_latest_changes():
    md = tool_md(SITE, BASE, load_news(SAMPLE_NEWS))
    assert "## Recent changes\n\n- v0.7.8 (2026-11-20, fixed)" in md
    assert "madoqua" not in md


def test_news_item_anchor_is_unique_per_tool_and_note():
    anchors = [n.anchor for n in load_news(SAMPLE_NEWS)]
    assert len(set(anchors)) == len(anchors)


def test_full_build_writes_pages_markdown_siblings_and_curated_llms(tmp_path):
    out = tmp_path / "site"
    report = build(deedum.load_site(ROOT), out)
    assert report.pages > len(load_tools())
    assert (out / "biston" / "index.md").read_text().startswith("# biston\n")
    llms = (out / "llms.txt").read_text()
    assert "Run `uvx <tool>@latest guide`" in llms
    assert (out / "static" / "css" / "main.css").exists()
    assert check_folder(out, "/aesop/").errors == 0
