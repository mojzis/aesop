# aesop

Tools showcase site for the agentic-Python menagerie. Built with
[deedum](https://github.com/mojzis/deedum), deployed to GitHub Pages.

```
uv sync
uv run deedum build --check   # -> site/
uv run deedum serve           # http://localhost:8000, rebuilds on change
```

- `pyproject.toml` `[tool.deedum]` — title, description, `base_url` + `base_path`, favicon
- `content/site.yaml` — umbrella copy, categories, nav pages
- `content/tools.yaml` — one entry per tool (copy, links, accent, mascot)
- `templates/` — Jinja2 templates (deedum writes the `<head>` tags)
- `public/` — copied verbatim; `public/static/` → `/static/`
- `build/aesop.py` — the `deedum.App` subclass that turns the YAML into pages

Deploy: push to `main`; `.github/workflows/deploy.yml` builds and publishes.
In repo settings → Pages, set source to **GitHub Actions**.

## Docs theme

`docs-theme/` is the mdBook theme shared by the tools' doc sites: the aesop
palette, with each tool's accent, mascot and tagline taken from
`content/tools.yaml`.

```
uv run python docs-theme/sync.py           # copy into ../<tool>/docs
uv run python docs-theme/sync.py --check   # exit 1 if a copy is stale
```

It writes `custom.css`, `aesop.js` and `theme/head.hbs` in every sibling repo
that has `docs/book.toml`. Edit the theme here, never in a tool repo; then
commit and push each tool repo.
