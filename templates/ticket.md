# Ticket <order id>

<!-- Written by the expediter (mise-en-place). Fill every field. A station cannot ask you anything
     and cannot see the chat, so anything vague here becomes a guess. The taster dry-runs this file
     until it finds zero questions. -->

- **Station:** <name>. Profile: `<absolute path of $KITCHEN_HOME/stations/<name>/station.md>` (read it first)
- **Repo:** `<absolute repo path>` (read its `CLAUDE.md`; never work in this folder)
- **Worktree:** `<absolute worktree folder>`: your only working directory, already on your branch
- **Branch:** `feat/<order id>-<station>` from base `<base sha>` (already created)
- **Orders:** `<absolute $ORDERS path>`: write the plate, gates and evidence only under `<this>/<order id>/`
- **Kitchen:** `<absolute path of the kitchen kit>` (its `RULES.md` is your contract)
- **Port:** `<n>` for any server you start. **Shared services:** <name: owner station, and whether you may restart it (only its owner may)>
- **Spec:** `<absolute path in $KITCHEN_HOME/specs/>` (read-only)
- **Specs folder:** `<absolute path of $KITCHEN_HOME/specs/>` (every spec, for the leak check) · **Leak check:** `<--allow and --exclude from House rules, or "none">`
- **Greenfield:** yes | no
- **Blocked by:** <order ids, or "none">

## Goal

<One sentence: the outcome, which a stranger with no access to the chat could execute.>

## Scope

<!-- The Owns line is parsed: only backticked paths or globs on it, nothing else in backticks.
     Exclusions are `!path` tokens, never prose. The station also owns its tools repo, where it
     works on branch feat/<order id>-<station>. -->
- **Owns (may write):** `<path or glob in the repo>`, `!<path it must not write inside them>`, `<absolute path of $KITCHEN_HOME/stations/<station>/tools/>`
- **Reads (may only read):** `<paths>`
- **Contracts consumed (frozen, never change):** <name: shape pasted here, or the spec section>
- **Leaving scope:** a change outside Owns is never made. Write it under "Orders for other stations"
  and continue with the rest.

## Done when

- [ ] <checkable criterion, true or false>
- [ ] Every 🤖 row below passes at `e2e-verified`, `runtime-verified` or `test-verified`.
- [ ] Docs updated for every behavior, command or config added.

## Owner steps (only when Station is `owner`)

<The owner cooks this ticket with the sous-chef (`kitchen:line`). Cut it into steps a person
finishes in one sitting, in the order that builds understanding. The AI never writes these
files; it writes the test cases (excluded from Owns with `!`, for example `!<the repo's test file pattern>`).>

| # | Files (where the change goes) | Concept (what to learn here) | Test cases (pending, from the spec) |
| --- | --- | --- | --- |
| 1 | `<path>` | <name: one sentence> | <behavior 1> · <behavior 2> |

## Verify

```bash
REPO=<worktree> ORDERS=<orders path> ORDER=<order id> PORT=<port> <tools path>/check
REPO=<worktree> ORDERS=<orders path> ORDER=<order id> PORT=<port> <tools path>/prove --expect "<text>" <scenario>
<any other exact command proving a criterion, every argument filled>
```

- **🤖 rows to run:** <ids from the spec smoke table, with their steps pasted>
- **Known gotchas:** <stale build, cache, port, ordering>

## Attack surface

<The spec's Attack surface rows this ticket touches, copied word for word. Build each defense, and
prove the "Never" column with a test that tries it. `kitchen:adversary` attacks the branch before
merge. "None" when the spec's surface has no row here.>

## Policies

<Copied word for word from the spec's Policies section.>

## Principles

YAGNI > KISS > DRY. <If greenfield: "> SOLID, following the spec's Design section." Otherwise:
"Follow the existing patterns in `<paths>`; no SOLID refactors.">

## Granted actions

<Every local action this station may take without asking: migrate the dev DB, restart its
service, add the test dependency X. Plus everything in the kitchen Autonomy table.>

## Context

<Pointers, not pasted files: spec sections, files to read first. When this ticket depends on
another station's work, paste that station's plate.md here in full.>

## Timebox

<About N hours or N build cycles. When it runs out: pause by the pause rule and hand back what is
verified. Never keep going past it silently.>

## Forbidden

- Writing outside Owns. Push, merge into `main`, any commit on `main`, release tags, deploy.
- Wiping or restoring a database. Anything outside this machine.
- Calling internals or test-only endpoints to fake a result a check should observe.
- <order-specific bans>

## Hand back

1. `$ORDERS/<order id>/plate.md` from `templates/plate.md`.
2. Five lines: `status` · `branch @ last sha` · `🤖 rows passed / total` · `open gates` · `blocker, or none`
