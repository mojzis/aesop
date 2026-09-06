# aesop

Static site: `content/site.yaml` + `content/tools.yaml` → `build/__main__.py` (Jinja2) → `site/`. Plan in `docs/plans/`.

- Build: `uv run build`. Local preview: `BASE_URL= uv run build && python -m http.server -d site 8000`.
- Lint: `uv run ruff check . && uv run ruff format .`
- Every HTML page has a Markdown sibling (`index.md`) plus `llms.txt` / `llms-full.txt`, all emitted by `write_markdown`. Keep them in sync when adding fields.
- `site/` is generated, gitignored. Never edit it.
- Links use `{{ site.base_url }}` prefix (GitHub Pages project subpath). Keep it.
- `content/tools.yaml` is the single source of truth for tool copy. Keys: id, name, animal, honorary, accent, tagline, reach_for_it, guide, install, category, links, order, quickstart (md), mascot, demo.
