# Toolbox integration prompt

Integrate the aesop toolbox (https://mojzis.github.io/aesop/llms.txt) into this repo so it's used automatically where it should be, and documented where it shouldn't. Each tool teaches you how to use itself — run `uv run <tool> guide` first and follow its conventions rather than guessing at flags. If a tool has no `guide` yet, fall back to `--help` and its README.

## 0. Install everything first

```
uv add --dev madoqua gerenuk biston zorilla pycoati ty-find ruff ty pytest pytest-cov
```

ruff and ty are madoqua's default fix/check steps; pytest is what gerenuk becomes; pytest-cov is how pycoati gets coverage. Call every tool as `uv run <tool>`. ty-find's binary is `tyf`. If the project is not an installable package, pytest needs `[tool.pytest.ini_options] pythonpath = ["."]`.

## 1. Every commit — the hook

**madoqua** is THE commit hook. Replace or consolidate whatever hook setup exists; migrate existing checks (lint, format, typecheck) into its config so there's one hook, not two systems. Run `uv run madoqua guide`, baseline with `madoqua run`, then `madoqua install`. Start from this config and tune, don't rediscover it:

```toml
[tool.madoqua]
# fix phase keeps the defaults: ruff check --fix, ruff format (re-staged).
# check phase keeps the defaults (ruff check, ty check) and adds:
extend_check = [
    # madoqua appends the staged .py files. biston reads them as --focus-args focus files
    # (only clone pairs touching a staged file); zorilla lints exactly those files.
    { name = "biston",  cmd = "biston scan --focus-args", timeout_s = 60,  max_output_lines = 80 },
    { name = "zorilla", cmd = "zorilla check",            timeout_s = 30,  max_output_lines = 80 },
    # gerenuk scopes itself from the git diff, so no file list.
    { name = "gerenuk", cmd = "gerenuk run -- -q",        pass_files = false, timeout_s = 120, max_output_lines = 120 },
]

[tool.biston.scan]
exclude = ["tests/**", "migrations/**"]   # plus generated code for this repo
```

- **biston** — in the hook, no debate. Your only job is tuning thresholds and excludes so it's fast and quiet on a clean commit. If the codebase already trips it, tune around the findings and list them for me instead of blocking commits.
- **zorilla** — fast syntactic test linter, belongs in the gate. It flags path and URL literals in tests (ZR005); when those are test data for a URL-generating program, suppress per line with `# zorilla: ignore[ZR005]`, don't disable the rule. List anything it finds in existing tests.
- **gerenuk** — runs only the tests the diff can reach; whole suite when unsure. It diffs the *working tree* against `origin/main` (then `main`, `master`), not the index, so unstaged edits count. It needs `tyf` on PATH; `uv run gerenuk doctor` confirms the wiring, and the first real run starts ty-find's daemon.

Known traps:

- The shim `madoqua install` writes is `exec madoqua run`, so a commit from a shell without the venv active fails with `madoqua: not found`. Replace the shim's last line with:

  ```sh
  root=$(git rev-parse --show-toplevel)
  [ -x "$root/.venv/bin/madoqua" ] && exec "$root/.venv/bin/madoqua" run
  exec madoqua run
  ```

  madoqua itself (0.2.1+) then puts `.venv/bin` on PATH for the tools it runs.
- madoqua acts only on staged `.py`/`.pyi` files. A commit without one is a silent no-op: no steps, no log row, exit 0. That is not a verified hook.

## 2. Every now and then — audits, never in the hook

- **pycoati** — dev dep only; do NOT add it to any hook or CI. Document it in CLAUDE.md as the periodic test-suite audit: `uv run pycoati . --format pretty` scores every test for suspicion and hands you a ranked list plus a remediation ladder. Run it before a test cleanup session. It runs the suite with `--cov`, so pytest-cov must be installed or coverage is silently null.

## 3. On demand — instead of grep

- **ty-find** — confirm `uv run tyf find <some symbol>` answers in this repo (this starts the daemon). Add a note to CLAUDE.md (create it if missing): agents must use `uv run tyf` instead of grep for symbol definitions and references. `uv run gerenuk audit <file>` lists symbols nothing references.

## CLAUDE.md

Add a short "toolbox" section: what runs on commit and typical timing (`uv run madoqua stats`), what's on-demand with the exact commands, the `uv run <tool> guide` convention, fresh-clone step (`uv run madoqua install` once; `core.hooksPath` is local config), and how to refresh:

```
uv lock --refresh --upgrade-package madoqua --upgrade-package gerenuk --upgrade-package biston --upgrade-package zorilla --upgrade-package pycoati --upgrade-package ty-find && uv sync
```

(`--refresh` matters: without it uv may serve a cached index and miss a release published minutes ago.)

## Finish — two commits, both through the hook

1. Commit the setup itself, with at least one `.py` change staged (a docstring line is enough), otherwise madoqua does not run at all. Non-Python files changed, so gerenuk runs the full suite. Report what the hook ran and how long, from `.git/hook-timings.jsonl` (`uv run madoqua stats`).
2. Push, then change one Python symbol that a test reaches and commit again. Run `uv run gerenuk impacted-tests` first and paste its verdict: it must say `selected` with the test(s) and the symbol they reach, not `run_all`. That is the proof the chain works.
