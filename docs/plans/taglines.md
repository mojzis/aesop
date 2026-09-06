# Taglines & copy

## Site umbrella

**Primary:** A small menagerie of fast tools that keep agentic Python development honest.

**Alt:** Agents write code fast. These keep it from going feral.

**Guide-command pitch (site-wide, above the fold):**
Every tool here teaches your agent itself — just say: run `uvx <tool> guide`.

---

## ty-find

**Tagline:** Find the symbol, not 400 grep hits.

**Reach for it when:** your agent needs definitions and references in a large repo — LSP-accurate answers at CLI speed, without the token bonfire of `grep -rn`.

**Guide:** `uvx ty-find guide`

## tyreach

**Tagline:** Know what your code can actually reach.

**Reach for it when:** you want a reachability snapshot before or after a refactor — and to catch the orphaned functions agents leave behind like shed skin.

**Guide:** `uvx tyreach guide`

## biston

**Tagline:** Finds the code your agent wrote twice.

**Reach for it when:** the repo grew fast and you suspect three slightly different copies of the same helper. Structural detection via tree-sitter, so renamed variables don't fool it.

**Guide:** `uvx biston guide`

## zorilla

**Tagline:** Sniffs out tests that test nothing.

**Reach for it when:** an agent just proudly delivered 40 green tests and you want to know how many actually assert something.

**Guide:** `uvx zorilla guide`

## gerenuk

**Tagline:** Runs only the tests your diff can touch.

**Reach for it when:** you want tests in the pre-commit hook without colleagues hating you — diff → changed symbols → impacted tests, in seconds.

**Guide:** `uvx gerenuk guide`

## madoqua

**Tagline:** The commit hook that's silent when you're fine and precise when you're not.

**Reach for it when:** you're done with noisy hook runners — auto-fixes, restages, one-line verdict on success, dense token-aware output on failure.

**Guide:** `uvx madoqua guide`

## introspect

**Tagline:** What did your agent actually do all day?

**Reach for it when:** you want to query your Claude Code sessions with SQL — costs, tool calls, patterns, the works.

**Guide:** `uvx introspect guide`

## pycoati

**Tagline:** _(pending — what does it do?)_

**Reach for it when:** _(pending)_

**Guide:** `uvx pycoati guide`

## pycoati (resolved)

**Tagline:** Ranks the tests that are probably lying to you.

**Reach for it when:** the suite is green but you don't trust it — too many mocks, tests that patch the thing they claim to test. Scores every test for suspicion, hands your agent a remediation ladder.
