# aesop

Static site: `content/site.yaml` + `content/tools.yaml` → `build/__main__.py` (Jinja2) → `site/`. Plan in `docs/plans/`.

- Build: `uv run build`. Local preview: `BASE_URL= uv run build && python -m http.server -d site 8000`.
- Lint: `uv run ruff check . && uv run ruff format .`. Tests: `uv run pytest`.
- Prompt pages: `site.yaml` `pages:` list → `content/<id>.md` → `/<id>/` (HTML via `templates/page.html`) + raw `/<id>/index.md`. `setup` = install-everything prompt; `guide` = the guide-subcommand principle + a prompt to add it to any CLI.
- Every HTML page has a Markdown sibling (`index.md`) plus `llms.txt` / `llms-full.txt`, all emitted by `write_markdown`. Keep them in sync when adding fields.
- `site/` is generated, gitignored. Never edit it.
- Links use `{{ site.base_url }}` prefix (GitHub Pages project subpath). Keep it.
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
