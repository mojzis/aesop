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
