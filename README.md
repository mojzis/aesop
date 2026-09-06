# agentic-python

Static portfolio site. Python + Jinja2 + Markdown, deployed to GitHub Pages.

```
uv sync
uv run build            # -> site/
python -m http.server -d site 8000
```

- `content/site.yaml` — site title, tagline, links, `base_url`
- `content/projects/*.md` — one project per file, YAML front matter + Markdown
- `templates/` — Jinja2 templates
- `static/` — CSS/JS, copied verbatim
- `build/` — generator

Deploy: push to `main`; `.github/workflows/deploy.yml` builds and publishes.
In repo settings → Pages, set source to **GitHub Actions**.
