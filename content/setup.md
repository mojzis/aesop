# Toolbox integration prompt

Integrate the aesop toolbox (https://mojzis.github.io/aesop/llms.txt) into this repo so it's used automatically where it should be, and documented where it shouldn't. Add ALL of the tools below as dev dependencies with `uv add --dev <tool>`, then call them via `uv run <tool>`. Each tool teaches you how to use itself — run `uv run <tool> guide` first and follow its conventions rather than guessing at flags.

## Every commit — the hook

1. **madoqua** — set it up as THE commit hook for this repo, replacing or consolidating whatever hook setup currently exists. Migrate any existing checks (lint, format, etc.) into its config so there's one hook, not two systems.

2. **gerenuk** — wire it INTO the madoqua hook so that on commit, only the tests impacted by the diff are run, not the whole suite. Verify the chain works end to end: make a small change, commit, confirm the right subset of tests ran.

3. **biston** — add it to the madoqua hook, no debate. Your only job is tuning its config for this repo (thresholds, ignored paths like generated code or migrations) so it's fast and quiet on a clean commit. If the current codebase already trips it, tune around the existing findings and list them for me instead of blocking commits.

4. **zorilla** — add it to the madoqua hook, scoped to the tests directory. It is a fast syntactic linter (no assertion, sleep, patch stacks); it belongs in the per-commit gate. If existing tests trip it, tune or suppress per rule and list the findings for me.

## Every now and then — audits, never in the hook

5. **pycoati** — dev dep only; do NOT add it to any hook or CI. Document it in CLAUDE.md as the periodic test-suite audit: it scores every test for suspicion and hands you a ranked list plus a remediation ladder. Run it before a test cleanup session. Record the exact command.

6. **introspy** — dev dep only. Document it as the way to query past agent sessions (costs, tool calls, patterns) when reviewing how the repo gets worked on.

## On demand — instead of grep

7. **ty-find** — it runs a daemon, so after adding it as a dev dep, confirm `uv run ty-find` starts the daemon and answers queries in this repo. Then add a note to CLAUDE.md (create it if missing): agents must use `uv run ty-find` instead of grep for symbol definitions and references in this repo.

## CLAUDE.md

While updating CLAUDE.md, add a short "toolbox" section covering all of the above: what runs automatically on commit, what's on-demand, the `uv run <tool> guide` convention for learning any of them, and how to refresh the toolbox to latest versions:

```
uv sync --upgrade-package madoqua --upgrade-package gerenuk --upgrade-package biston --upgrade-package zorilla --upgrade-package pycoati --upgrade-package introspy --upgrade-package ty-find
```

## Finish

Commit the setup itself — which doubles as the live test of the new hook. Report what the hook ran and how long it took.
