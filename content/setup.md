# Toolbox integration prompt

Integrate the aesop toolbox (https://mojzis.github.io/aesop/llms.txt) into this repo so it's used automatically where it should be, and documented where it shouldn't. Each tool teaches you how to use itself — run `uv run <tool> guide` first and follow its conventions rather than guessing at flags. If a tool has no `guide` yet, fall back to `--help` and its README.

## 0. Install everything first

Start clean: `git fetch && git rebase origin/main` (or `git pull --ff-only`) before any edit, so the finish commits don't land on a stale base.

```
uv add --dev madoqua gerenuk biston zorilla pycoati ty-find ruff ty pytest pytest-cov
```

Then refresh once, because `uv add` leaves a tool the repo already declared at its old version, and old biston/zorilla have no `guide` or `--focus-args`:

```
uv lock --refresh --upgrade-package madoqua --upgrade-package gerenuk --upgrade-package biston --upgrade-package zorilla --upgrade-package pycoati --upgrade-package ty-find && uv sync
```

If `uv sync` uninstalls packages, the repo has optional groups; add `--all-groups` (or the right `--group`) to that line and to the fresh-clone line later. Order is install → refresh → guides → baselines. Add `.coverage` to `.gitignore` if it isn't; pycoati leaves one at the repo root.

ruff and ty are madoqua's default fix/check steps; pytest is what gerenuk becomes; pytest-cov is how pycoati gets coverage. Call every tool as `uv run <tool>`. ty-find's binary is `tyf`. If the project is not an installable package, pytest needs `[tool.pytest.ini_options] pythonpath = ["."]`.

Three things to check right after:

- If `[tool.uv] exclude-newer` is set, the install fails with "no versions of biston". Add `exclude-newer-package = { madoqua = "<today>", gerenuk = ..., biston = ..., zorilla = ..., pycoati = ..., ty-find = ... }` for the six tools and leave the global cutoff alone; the refresh command below then needs the same bump.

- If the repo already declares *dev tools* under `[project.optional-dependencies]` (an extra named `dev` or similar; leave feature extras alone), `uv add --dev` creates a second list under `[dependency-groups]` and pytest/ruff end up declared twice with different floors. Move the old extra into the dependency group so there is one dev list. Don't keep both.
- If `uv.lock` is gitignored, un-ignore it. The refresh step below is lock-based, and the setup commit should pin the toolbox versions.

## 1. Every commit — the hook

**madoqua** is THE commit hook. Replace or consolidate whatever hook setup exists; migrate existing checks (lint, format, typecheck) into its config so there's one hook, not two systems. Delete the old hook script, its installer and any helper scripts with their tests, and grep for every mention (`install-hooks`, `pre-commit.sh`, `core.hooksPath` in scripts, poe/just/make tasks, `.claude/hooks/`, `docs/`) and repoint or remove them. If the old hook did something madoqua doesn't (a skip env var, a personal overlay file, a repo-wide `ty check` that is now staged-only), note it in CLAUDE.md rather than dropping it silently. Run `uv run madoqua guide`. Stage a one-line docstring change in a *source* module now (madoqua is silent without a staged `.py`; ruff format may add to the diff, that's fine), baseline with `madoqua run`, then `madoqua install`; it writes a tracked `hooks/pre-commit` and sets `core.hooksPath=hooks`, commit the hook file. Start from this config and tune, don't rediscover it:

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
    # mirror the repo's own quick-test flags after `--` (-n auto if xdist is there, -o addopts= to drop --cov);
    # set timeout_s from the measured full run, the hook runs it on every commit without a .py-only diff.
]

[tool.biston.scan]
exclude = ["**/tests/**", "migrations/**"]   # anchored at repo root; ** covers src-layout and workspaces; drop what doesn't exist
```

Merge into an existing `[tool.biston.scan]` or `[tool.madoqua]` table if the repo already has one; a duplicate TOML table is a parse error. If pytest `addopts` carries `--cov`, append `-o addopts=` to the gerenuk cmd (after `--`): the hook never reads the coverage table. If the repo has a check aggregator (`poe check`, `make check`) and the zorilla/biston baselines are clean, add `zorilla check .` and `biston scan .` there too; on a dirty baseline that turns a green aggregator red, so skip it and say so. Leave CI alone.

- **biston** — in the hook, no debate. Tune *excludes* (tests, migrations, generated code) so it's fast; do not raise thresholds to hide findings, its guide forbids that. If the codebase already has clone pairs, list them for me and name the files in CLAUDE.md (same warning as for zorilla findings below). With `--focus-args` they block only commits that stage one of the files involved, which is the intended pressure.
- **zorilla** — fast syntactic test linter, belongs in the gate. Baseline with `uv run zorilla stats .` (by-rule table; `zorilla check .` for the lines). It flags path and URL literals in tests (ZR005). When a whole family is genuinely test data (TestClient routes, URLs a program generates) use `[tool.zorilla.rules.ZR005] allowed_prefixes = [...]` in pyproject.toml; use per-line `# zorilla: ignore[ZR005] -- <reason>` only when the knob would over-allow (the reason is part of the syntax, it must be on the same line, and it counts toward ruff's line length, so it will trip E501 on long lines). A per-line ignore stages the file, and if that file has any other zorilla finding the hook blocks the commit, so there the knob is the only option; use the full literal as the prefix to keep over-allowing at zero. Never disable the rule. Prefer the config knob: it doesn't touch test files. Every other rule (ZR004 assertion roulette, ZR001, ...) is usually real; leave it, don't edit those files at all in this session, and note that the hook will block the next commit touching them until they're fixed.
- **ty** — run `uv run ty check` once too. madoqua checks staged files only, so repo-wide diagnostics don't block clean commits, but a file with existing diagnostics blocks the first commit that touches it. List the files with counts.
- **gerenuk** — runs only the tests the diff can reach; whole suite when unsure. It diffs the *working tree* against `origin/main` (then `main`, `master`), not the index, so unstaged edits count. That means every commit on an unpushed branch that touched `pyproject.toml` or `uv.lock` runs the full suite; on a repo where that costs a minute, `gerenuk run --base HEAD` in the hook scopes to the commit itself. It needs `tyf` on PATH; `uv run gerenuk doctor` confirms the wiring, and the first real run starts ty-find's daemon.

Known traps:

- Check the shim `madoqua install` wrote ends with a `.venv/bin/madoqua` lookup (0.2.2+ does; older versions write a bare `exec madoqua run`, which fails with `madoqua: not found` from a shell without the venv active, and need this as the last lines):

  ```sh
  root=$(git rev-parse --show-toplevel)
  [ -x "$root/.venv/bin/madoqua" ] && exec "$root/.venv/bin/madoqua" run
  exec madoqua run
  ```

  madoqua itself (0.2.1+) then puts `.venv/bin` on PATH for the tools it runs. Verify from a bare shell: `env -i HOME=$HOME PATH=/usr/bin:/bin sh hooks/pre-commit` with a `.py` staged (keep `HOME`, some suites need it; git runs hooks with the login environment). The point is the binary lookup, not the suite. It is a full madoqua run and lands in `madoqua stats` like any other.
- ty-find's index can go stale after a formatter rewrites a file (the hook's `ruff format` does exactly that). Symptoms: the gerenuk step jumps from ~1 s to ~6 s, or `tyf refs` lists only lines inside the definition. `uv run tyf daemon restart` fixes it.
- madoqua acts only on staged `.py`/`.pyi` files. A commit without one is a silent no-op: no steps, no log row, exit 0. That is not a verified hook.

## 2. Every now and then — audits, never in the hook

- **pycoati** — dev dep only; do NOT add it to any hook or CI. Document it in CLAUDE.md as the periodic test-suite audit: `uv run pycoati . --format pretty` scores every test for suspicion and hands you a ranked list plus a remediation ladder. Run it before a test cleanup session. It runs the suite with `--cov`, so pytest-cov must be installed or coverage is silently null. Run it once now to confirm coverage shows up; it's the most expensive step here (three suite runs, several minutes on a suite over a minute), so background it.

## 3. On demand — instead of grep

- **ty-find** — confirm `uv run tyf find <symbol>` answers in this repo with a name taken from `uv run tyf list <module>` (this starts the daemon), and that a made-up name prints "No results found". Add a note to CLAUDE.md (create it if missing): agents must use `uv run tyf` instead of grep for symbol definitions and references.
- **gerenuk audit** — run `uv run gerenuk audit <file>` once on the largest module; it lists symbols nothing references. Report the count; don't delete anything.

## CLAUDE.md

Add a short "toolbox" section: what runs on commit and typical timing (`uv run madoqua stats`), what's on-demand with the exact commands, the `uv run <tool> guide` convention, fresh-clone step (this repo's real sync command including any extras, then `uv run madoqua install` once; `core.hooksPath` is local config), and how to refresh:

```
uv lock --refresh --upgrade-package madoqua --upgrade-package gerenuk --upgrade-package biston --upgrade-package zorilla --upgrade-package pycoati --upgrade-package ty-find && uv sync
```

(`--refresh` matters: without it uv may serve a cached index and miss a release published minutes ago.)

Expect gerenuk's selection to cost 1–2 s of `tyf` round-trips; on a suite that runs in under ~2 s the full run is cheaper and that's fine, the proof below still matters.

## Finish — two commits, both through the hook

1. Commit the setup itself (pyproject.toml, uv.lock, CLAUDE.md, `hooks/pre-commit`), with at least one `.py` change staged (a docstring line in a *source* module is enough, not a test file, which may carry ZR004), otherwise madoqua does not run at all. Non-Python files changed, so gerenuk runs the full suite. Report what the hook ran and how long: the last row of `.git/hook-timings.jsonl` is the commit (its `head` is the parent sha, the hook runs before the commit exists); `uv run madoqua stats` aggregates every run including your manual baselines.
   If the push is rejected because upstream moved, `git fetch && git rebase origin/main`; the rebased commit is not re-verified by the hook, so run `uv lock` on a lock conflict and `uv run madoqua run` again.
2. Push, then change one Python symbol that a test reaches and commit again. Pick a plain library function a test imports directly, not a command callback; that gets a function-level chain. Run `uv run ruff format --check <file>` first: if the file was never formatted, the hook's fix phase rewrites it and the commit carries five changed symbols instead of one. Format it in commit 1 or accept it and paste only the pre-commit verdict. Run `uv run gerenuk impacted-tests` *before* committing and paste its verdict (after the push the tree equals `origin/main` and it prints `No impacted tests.` / `0 symbol(s) visited`, which is not the proof; `--base HEAD~1` reproduces it): it must say `selected` with the test(s) and the symbol they reach, not `run_all`. That is the proof the chain works. Then check `uv run gerenuk run --dry-run`: if its node ids are every test file, the selection is nominal (a root `conftest.py` that imports the app does this) and the hook will run the full suite on every commit; report that. Whenever a test does `from pkg import mod` and calls `mod.fn(...)` (CliRunner tests, module-style imports) the chain ends at `tests/test_x.py (whole file) ← pkg.mod`; that is still `selected`. Per-test selection needs `from pkg.mod import fn`.
