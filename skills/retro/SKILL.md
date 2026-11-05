---
name: retro
description: Step 9 of the kitchen. After an order goes out, turn every gate, taster question, extra round and owner correction into a grill checklist line or an automatic check, so the next order needs fewer rounds. Use after the expedite skill's "out" step, or when the owner says "retro".
---

Adapted from mattpocock/skills `retro` and pstack `correct` (MIT).

**First:** if you haven't in this session, read `$KITCHEN/CLAUDE.md` in full (the absolute path is in
the session-start brief). It holds the rules every step below relies on.

## 1. Count the misses

From the order's folders, list every:

- gate in `gates.md`,
- question the taster found in `mise-en-place`,
- fix round and its "Act on" findings,
- row in a `plate.md` Decisions table that the owner overruled at the pass, or that a later row
  superseded,
- owner correction during the pass.

Print one line: `gates N · taster questions N · fix rounds N · owner corrections N`.

## 2. Find each one's earliest catch

For each miss, the earliest step that could have stopped it. Use the strongest fix that works,
in this order:

1. **A check** (a script, test, lint or hook that fails on the mistake). Prove it fails on this
   real case before adding it. Add a row to "Rule → what enforces it" in the kitchen CLAUDE.md.
2. **A grill checklist line** in `skills/grill/SKILL.md`, worded as the question that would have
   caught it.
3. **A template field** in `templates/` that forces the answer to be written down, or a
   **gotcha line** in the station's profile `$KITCHEN_HOME/stations/<name>/station.md` when only that station needs it.
4. **A sentence** in an agent or skill. Last resort: text is the weakest guard.

## 3. Promote scenarios

Each scenario in `orders/<id>/scenarios/` that proves lasting behavior: propose moving it to
`$KITCHEN_HOME/stations/<station>/tools/<tool>/scenarios/`, renamed by what it proves. One-off probes stay in the order.

## 4. Propose, don't apply

Show the owner the list, one line per miss: `miss → fix (kind) → file`. Apply on their go.
A miss that happened once and has no pattern is noted, not fixed.
