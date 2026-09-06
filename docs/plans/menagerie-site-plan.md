# Tools showcase site — plan

## Goal

One place that answers "what is this and when do I reach for it" for the agentic-coding tool family. It is a router, not a manual: mascot, tagline, install line, guide command, short demo, links out. Two audiences: humans scrolling in from LinkedIn, and agents that need to discover the toolbox.

## Scope (v1)

ty-find, tyreach, biston, zorilla, gerenuk, madoqua, introspect. pycoati pending. Personal/playground repos stay out.

## The universal CTA: the guide command

Every tool ships a `guide` subcommand that prints agent-oriented usage instructions. This becomes the site's signature move — the global pitch line is roughly:

> Every tool here teaches your agent itself. Just say: run `uvx biston guide`.

Per-tool pages show the guide command as the primary copy button (`uvx <tool> guide`), install line second. This is a genuinely distinctive hook — no one else's tool pages lead with "tell your agent to run this" — so it belongs above the fold on the index too.

Consider a matching `llms.txt` at the site root: one line per tool (name, purpose, guide command) so an agent pointed at the site can absorb the whole toolbox in one fetch.

## Architecture

- Python + Jinja static build (same pattern as existing sites), output to GitHub Pages.
- All showcase content lives in the site repo in a single `tools.yaml`. Repos are not the source of truth for marketing copy.
- Build-time enrichment (optional, phase 2): latest version + release date pulled from PyPI/crates.io or the GitHub API, so version badges never rot.

### tools.yaml schema (draft)

```yaml
- id: biston                # slug, also the URL path /biston/
  name: biston
  animal: peppered moth
  tagline: Finds the code your agent wrote twice.
  reach_for_it: >
    The repo grew fast and you suspect three slightly different
    copies of the same helper.
  guide: uvx biston guide
  install: uvx biston        # or cargo/pipx variant if relevant
  category: guardrails       # guardrails | workflow | meta
  links:
    repo: https://github.com/mojzis/biston
    docs: https://mojzis.github.io/biston/
    pypi: https://pypi.org/project/biston/
  mascot: biston.png         # also used as og:image
  demo: biston.gif           # VHS-rendered, optional in v1
  order: 30
```

## Pages

- **Index** — umbrella tagline, the guide-command pitch, then cards grouped by category. Each card: mascot, name, tagline, guide command, "more →".
- **Per-tool page** (`/biston/`) — mascot hero, tagline, reach-for-it paragraph, guide + install copy buttons, demo gif, quickstart (3–5 lines), links to repo/docs. Own `og:title`, `og:description` (the tagline), `og:image` (the mascot) — this is what makes LinkedIn previews work per-post.

Per-tool pages double as each tool's real landing page, which sidesteps the "docs sites are meh" problem: fix the quickstart here, leave deep docs in the repos.

## Imagery

- One mascot per tool, single consistent style (see image-prompts artifact). Reused as og:image, in repo READMEs, and in LinkedIn posts.
- og:image needs 1200×630; generate mascots on a background canvas at that ratio (or compose: mascot left, name + tagline right).
- Terminal demos via VHS (charmbracelet): one `.tape` per tool, rendered in CI so gifs regenerate when output changes. Phase 2 — don't block v1 on it.

## LinkedIn cadence

1–2 posts/week, one tool each. Post links to the per-tool page; the mascot renders as the preview. Rough post shape: the pain (one paragraph, agent-era specific) → the tool in one line → the guide command → link. Kickoff post introduces the menagerie as a whole and links the index.

## Phases

1. **v1 (timeboxed):** tools.yaml + two Jinja templates + mascots + index and per-tool pages deployed. No gifs, no version badges.
2. **v2:** VHS demos, version badges from registries, llms.txt.
3. **Later:** benchmarks/comparisons per tool if posts generate questions ("vs testmon", "vs grep").

## Open questions

- pycoati: what it does, whether it's in scope.
- Non-animal names (ty-find, tyreach, introspect): assign honorary animals for visual consistency, or give them a different visual treatment? (Candidates suggested in the image-prompts artifact.)
- Site name/path: lives at a new repo (e.g. `mojzis.github.io/menagerie/`) or takes over a nicer path? Naming the *collection* also helps the LinkedIn kickoff post.
- Whether `guide` output should follow a shared convention (sections, length, token budget) — worth a tiny spec so all eight feel like siblings when an agent reads them.
