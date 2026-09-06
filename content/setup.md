Set up the aesop toolbox in this repository. Reference: https://mojzis.github.io/aesop/llms.txt

Every tool has a `guide` subcommand written for you. Run `uvx <tool> guide` only when you need that tool's details — this prompt is the plan, the guides are the manuals.

Wire the tools in three tiers:

## 1. Every commit — fast gate

madoqua is the hook runner; zorilla and gerenuk run inside it.

- `uv add --dev madoqua zorilla gerenuk`
- Run `uvx madoqua guide` and follow setup: baseline with `madoqua run`, fix what it reports, then `madoqua install`.
- Extend the registry in pyproject.toml so the hook also lints tests and runs only impacted tests:

```toml
[tool.madoqua]
extend_check = ["zorilla check tests", "gerenuk run -- -q"]
```

Verify both commands with `uvx zorilla guide` and `uvx gerenuk guide` before committing the config. If gerenuk reports the repo is not indexable (`gerenuk doctor`), leave it out of the hook and note why.

## 2. Every now and then — audits that tell you what to fix first

Not in the hook. Run before a cleanup session, or when the suite feels wrong.

- `uvx pycoati guide` — scores every test for suspicion, hands you a ranked list and a remediation ladder.
- `uvx biston guide` — structural duplicates, the helper written three times. `biston scan`, then work the report.

## 3. On demand — instead of grep

- ty-find for definitions and references. Never `grep -rn` for a symbol in this repo; run `uvx ty-find guide` once to learn the commands.
- introspy to review your own sessions: `uvx introspy guide`.

## Finish

Add a short "Tooling" section to CLAUDE.md that lists the three tiers and the one-line commands, so future sessions skip this setup. Commit the hook shim, the pyproject changes and CLAUDE.md in one commit.
