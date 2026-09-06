# The guide principle

A CLI built to be driven by agents should teach the agent itself. `<tool> guide` prints one page of instructions written for the agent that is about to use the tool: what to run, in what order, what the output means, and what to do about it. No README to hunt for, no docs site to fetch, no flags to guess. The page ships inside the binary, so it always matches the version that runs.

This document is both the description of the convention and a prompt. To add a `guide` subcommand to a CLI, tell your agent: *Add a `guide` subcommand to this CLI: follow https://mojzis.github.io/aesop/guide/index.md*.

## The contract

1. **`<tool> guide` prints Markdown to stdout and exits 0.** It touches nothing: no config written, no network, no repository required. It must be safe as the very first command in a fresh checkout, including `uvx <tool>@latest guide`. Exit non-zero only if stdout itself could not be written.
2. **Topics.** `guide [TOPIC]`; `--help` lists them with one line each. The canonical set:
   - `setup`: the tool is not wired into this repository yet. Install, configure, first run, where to record the convention (`CLAUDE.md`, README).
   - `triage`: the tool reported something. What the output means and what to do about each kind of finding. Tools with nothing to triage ship `use` instead: which command answers which question.
   - `tune`: the reference. Config keys, thresholds, knobs, exit codes. Never auto-selected.
3. **Auto-detection.** With no topic, pick one from the state of the current directory: `setup` when the tool is not configured here, `triage` (or `use`) when it is. Detection reads files only, never the network, and says what it looked at. The first printed line names the pick and the reason:

   ```
   # <tool> guide: configured via pyproject.toml [tool.<tool>] -> triage
   ```

4. **Written for an agent about to act, not a human browsing.**
   - Exact commands, in order, as they are run in this repository: `uv run <tool> scan .`, not "run a scan".
   - A remedy ladder: numbered, "take the first rule that applies". Ordered from cheapest to most invasive; changing policy or asking a human comes last.
   - Say what done looks like: "one `ok` line on stdout and nothing on stderr".
   - A **Do not** list naming the shortcuts an agent will reach for: `--no-verify`, deleting the check, raising the threshold, suppressing a rule to pass one commit.
   - End with `next: <command>`, the single thing to run after reading.
   - One screen per topic. Short lines, no marketing, no history.
5. **Cross-reference, do not duplicate.** `setup` says `see <tool> guide tune` rather than inlining the reference. `--help` and the README point at `guide`.
6. **Pages live with the code.** Each topic is a Markdown file embedded at build time. Tests assert that every topic in `--help` prints, exits 0, and that every command the pages mention exists in the CLI.

## Add it to a CLI

Work in this order. Do not skip to writing prose.

**1. Learn the tool.** Run `--help` for every subcommand, read the README and the config loader. List: the commands, what each prints on success and failure, the exit codes, the config file and its keys, and the one way it is meant to run in a repository (hook, on demand, scheduled).

**2. Decide the topics.** `setup` and `tune` are always there. `triage` when the tool reports findings or blocks something; `use` when it answers questions. A tool that is a pipeline (scan, then analyze, then remediate) gets one topic per stage and auto-selects by the artifact each stage leaves behind.

**3. Decide detection.** Name the one file or table that means "configured here" (`[tool.<tool>]` in `pyproject.toml`, a `<tool>.toml`, a hook line). Detection looks at the current directory only unless the tool itself walks up; say which in `--help`.

**4. Write the pages.** One Markdown file per topic, next to the source, embedded at build time (`include_str!`, `importlib.resources`, `embed`). Follow the contract above. Write `triage` first: it is the page the agent reads under pressure. Every command in it must be copy-pasteable and must work on the current version.

**5. Wire the subcommand.** `guide [TOPIC]`, topics as an enum so `--help` lists them. No other options unless the tool already has a `--root` or `--workspace` that detection should honour. Print the pick line, then the page, to stdout. Never log to stderr on the happy path.

**6. Test.** Every topic prints and exits 0. Auto-detection picks `setup` in an empty temp directory and `triage`/`use` in a configured one. Grep each page for `<tool> <subcommand>` and assert each subcommand exists.

**7. Point at it.** The top-level `--help` description ends with "run `<tool> guide` first". The README's first code block is `uvx <tool>@latest guide`. If the project has a `CLAUDE.md`, add one line: run `<tool> guide` before using it.

**8. Read it as the agent would.** In a fresh temp directory, run `uvx --from . <tool> guide` (or the equivalent) and follow the instructions literally, without your knowledge of the tool. Every place you had to guess is a gap in the page.

**Do not:**

- Do not paste the README into a page. The README is for a person choosing a tool; `guide` is for an agent that already has it.
- Do not describe options. Give the command with the options already chosen for this situation.
- Do not fetch the page from the network at runtime. It must match the binary that runs.
- Do not make `guide` do anything besides print. No "guide --apply".

next: `uvx <tool>@latest guide` in an empty directory, and read what it prints.
