# agentic-python

Static site: `content/` (YAML + Markdown) → `build/__main__.py` (Jinja2) → `site/`.

- Build: `uv run build`. Preview: `python -m http.server -d site 8000`.
- Lint: `uv run ruff check . && uv run ruff format .`
- `site/` is generated, gitignored. Never edit it.
- Links use `{{ site.base_url }}` prefix (GitHub Pages project subpath). Keep it.
- Project front matter keys: title, summary, date, tags, repo, url, featured, slug.
