# aesop

Static site built with [deedum](https://github.com/mojzis/deedum) (`uv run deedum guide`): `content/site.yaml` + `content/tools.yaml` → `build/aesop.py` (`Aesop(deedum.App)`, named in `[tool.deedum] app`) → `site/`. Plan in `docs/plans/`.

- Build: `uv run deedum build --check`. Local preview: `uv run deedum serve`.
- Site config (title, description, author, `base_url` host + `base_path = "/aesop/"`, favicon) lives in `[tool.deedum]` in `pyproject.toml`; `content/site.yaml` keeps only aesop copy (exposed to templates as `aesop`, while `site` is deedum's `Site`). Data folder is `content/`.
- deedum owns the `<head>` (`templates/base.html` includes `deedum/head.html`; `templates/deedum/head.html` overrides the home title), sitemap, robots, favicons from `public/static/img/favicon.svg`, 404 and the `index.md` siblings (each page's `source`).
- `public/` is the static folder; `public/static/` keeps assets at `/static/...`.
- Lint: `uv run ruff check . && uv run ruff format .`. Tests: `uv run pytest`.
- Prompt pages: `site.yaml` `pages:` list → `content/<id>.md` → `/<id>/` (HTML via `templates/page.html`) + raw `/<id>/index.md`. `setup` = install-everything prompt; `guide` = the guide-subcommand principle + a prompt to add it to any CLI.
- Every HTML page has a Markdown sibling (`index.md`): the `source=` given in `Aesop.load_pages` (`tool_md`, `index_md`, `news_md`, raw page md). `llms.txt` / `llms-full.txt` are the curated `index_md`, written over deedum's generic ones in `Aesop.after_build`. Keep them in sync when adding fields.
- `site/` is generated, gitignored. Never edit it.
- Links in templates go through `{{ url('path/') }}` (adds `/aesop/`), absolute ones through `{{ absolute('path') }}`. Never hardcode the prefix. `url('#x')` is passed through as-is: write `{{ url('') }}#x`.
- News (release notes): `uv run python -m build.news` clones each tool repo (`links.repo`) into `.cache/repos/` and writes `content/news.json` (gitignored) with the notes that shipped in a tag, via [relnotes](https://github.com/mojzis/relnotes) (`relnotes.notes.collect`). Build → 3 latest on the home page, 3 per tool page, `/news/` (tool/kind filter, `?tool=`), `/news/feed.xml`, `/news/index.md`. No JSON → no news blocks. The feed is a page with `template="feed.xml"`. Deploy runs the pull; a tool release triggers deploy via `workflow_dispatch`.
- Art: every image follows [`art/STYLE.md`](art/STYLE.md) (19th-century natural history plates; the prompt templates `art/generate.py` uses). Read it before generating or changing any image. Subjects in `art/subjects.yaml`; `art/pick.sh` publishes a roll to `public/static/img/`. Tool pages use the square mascot as og:image, the common pages a 1200×630 group plate `og-<page>.webp` (`og-home` is the site default, `image` in `[tool.deedum]`).
- `content/tools.yaml` is the single source of truth for tool copy. Keys: id, name, animal, honorary, accent, tagline, reach_for_it, guide, install, category, links, order, quickstart (md), mascot, demo.

## Toolbox

All tools are dev deps; call them as `uv run <tool>`. To learn one, run `uv run <tool> guide` (all except introspy, which has `--help`).

**On every commit** (madoqua hook, `hooks/pre-commit`, config in `[tool.madoqua]`):
fix: ruff check --fix, ruff format → check: ruff check, ty check, `biston scan --focus-args <staged>`, `zorilla check <staged>`, `gerenuk run -- -q` (only the tests the diff can reach; full suite when non-Python files changed). Typical run well under 1 s. Timings in `.git/hook-timings.jsonl`, `uv run madoqua stats`.
Fresh clone: run `uv run madoqua install` once (core.hooksPath is local config), then restore `hooks/pre-commit` from git: the stock shim needs `madoqua` on PATH, ours execs `.venv/bin/madoqua`. No `.py` staged → madoqua is a silent no-op.

**On demand**
- `uv run tyf find <symbol>` / `tyf refs` / `tyf show` — symbol lookup via the ty LSP daemon. Use this instead of grep for definitions and references.
- `uv run gerenuk impacted-tests` — see what the hook would run and why. `uv run gerenuk audit build/__main__.py` — symbols nothing references.
- `uv run pycoati . --format pretty` — periodic test-suite audit, ranked suspicion scores. Never in the hook.
- `uv run introspy stats` / `introspy query` — query past Claude Code sessions for this repo.

**Refresh to latest**
```
uv lock --refresh --upgrade-package madoqua --upgrade-package gerenuk --upgrade-package biston --upgrade-package zorilla --upgrade-package pycoati --upgrade-package introspy --upgrade-package ty-find && uv sync
```
`--refresh` is needed: a plain `uv sync --upgrade-package` served a stale index and missed releases minutes old.
