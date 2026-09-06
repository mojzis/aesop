from dataclasses import replace

from build.__main__ import Tool, inline_md, load_tools, tool_md

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
    assert BASE.mascot_path == "/static/img/biston.svg"  # zorilla: ignore[ZR005]
    assert BASE.og_image == "/static/img/biston-og.png"  # zorilla: ignore[ZR005]


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
