# Plate <order id>

<!-- Written by the station. Update it at every stop, not only at the end: it is the resume note
     too. One fact per line. Every claim points at evidence; a claim with none is "unverified". -->

- **Status:** done | paused | blocked
- **Branch:** `feat/<order id>-<station>` @ `<last sha>`
- **Ownership:** `git diff --name-only <base>..HEAD` inside Owns: yes | no

## Attention

<Read first. Risky choices, anything skipped, anything that passed suspiciously easily. "None" is valid.>

## 🤖 smoke rows

| Id | Result | Level | Evidence |
| --- | --- | --- | --- |
| <id> | pass / fail | e2e-verified / runtime-verified / test-verified / build-only / blocked | `orders/<id>/evidence/<file>` |

## What I ran

<Every check command exactly as typed, with its exit code. A reviewer must be able to re-run it.>

```bash
$ <command>        # exit 0
```

## Tests added

- `<test file>::<test name>`: <what it catches>

## Docs updated

- `<file>`: <what>

## Commits

- `<sha>` <subject>

## Decisions

<Append-only. One row per real decision: a choice not spelled out in the ticket, a fork taken, a
revert, a pivot. Not one row per action. Never edit or delete a row; a wrong call gets a new row
that supersedes it ("supersedes #3"). Evidence is a pointer (sha, file:line, evidence path), never
prose. retro and the reviewer read this table.>

| # | When | Decision | Decided by | Why | Evidence | Result |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | <hh:mm> | <what was chosen> | policy · spec · existing code · run · default (gate G<n>) | <plain reason> | <sha, file:line or path> | kept · reverted · superseded by #<n> |

## Deviations from the ticket

<Anything done differently, and why. "None" is valid.>

## Could not check

<What no tool here can reach, and why. Each becomes a 👤 row with exact steps.>

## Orders for other stations

<Changes another station must make: what, and the exact shape. "None" if none.>

## Profile updates

<What your station profile must say after this order, as exact text per section: new tools and
their commands, the run command, a new gotcha, what still cannot be reached. You don't edit the
profile; the expediter applies this at the out step. "None" if none.>

## Gates

<Open entries in gates.md and the default taken for each. "None" if none.>

## Resume point (only when paused or blocked)

- **Done and verified:** <list, with the level for each>
- **Next step:** <first action on resume>
- **Gotchas:** <what the next run must know>
