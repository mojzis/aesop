# aesop

Tools showcase site for the agentic-Python menagerie. Python + Jinja2, deployed to GitHub Pages.

```
uv sync
BASE_URL= uv run build  # -> site/ (empty BASE_URL = root-relative links for local preview)
python -m http.server -d site 8000
```

- `content/site.yaml` — umbrella copy, categories, `base_url`
- `content/tools.yaml` — one entry per tool (copy, links, accent, mascot)
- `templates/` — Jinja2 templates
- `static/` — CSS/JS, copied verbatim
- `build/` — generator

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
