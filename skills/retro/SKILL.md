---
name: retro
description: Step 9 of the kitchen. After an order goes out, turn every gate, taster question, extra round and owner correction into a check, a grill question or a spec field in this kitchen's House rules (never in the plugin), so the next order needs fewer rounds. Use after the expedite skill's "out" step, or when the owner says "retro".
---

Adapted from mattpocock/skills `retro` and pstack `correct` (MIT).

**First:** if you haven't in this session, read `$KITCHEN/RULES.md` in full (the absolute path is in
the session-start brief). It holds the rules every step below relies on.

## 1. Count the misses

From the order's folders, list every:

- gate in `gates.md`,
- question the taster found in `mise-en-place` (`$ORDERS/<id>/taster-*.md`),
- fix round and its "Act on" findings,
- row in a `plate.md` Decisions table that the owner overruled at the pass, or that a later row
  superseded,
- owner correction during the pass,
- for an owner ticket (`kitchen:line`): every `take over` row in its plate's Decisions table, and
  each concept the owner got stuck on (the steps where they asked "explain" or "I'm stuck"). The
  next owner ticket gives those concepts more depth.

Print one line: `gates N · taster questions N · fix rounds N · owner corrections N`.

## 2. Find each one's earliest catch

For each miss, the earliest step that could have stopped it. Use the strongest fix that works.
**Every fix lands in this kitchen's home, never in the kitchen plugin** (`$KITCHEN`): the plugin
is shared by every kitchen and is changed only by its maintainer. The guard hook refuses a
project session's edits inside it.

| Strength | Fix | Where it goes |
| --- | --- | --- |
| 1 | **A check** (a script, test or lint that fails on the mistake). Prove it fails on this real case before adding it | the owning station's tools, `$KITCHEN_HOME/stations/<name>/tools/`; listed under **House rules → Checks** in `$KITCHEN_HOME/kitchen.md` |
| 2 | **A grill question**, worded as the question that would have caught it | **House rules → Grill questions** in `$KITCHEN_HOME/kitchen.md` |
| 3 | **A spec field** that forces the answer to be written down | **House rules → Spec fields** in `$KITCHEN_HOME/kitchen.md` |
| 3 | **A gotcha**, when only one station needs it | that station's profile, `$KITCHEN_HOME/stations/<name>/station.md` |
| 4 | **A sentence**: last resort, text is the weakest guard | **House rules** in `$KITCHEN_HOME/kitchen.md` |

The session-start brief loads `kitchen.md`, so every later order of this kitchen runs with its
House rules.

**A lesson every project would need** (not only this one): also append it to
`$KITCHEN_HOME/retro/kit-proposals.md` (miss, evidence, proposed change to the plugin, proof it
fails on the real case). That file is for the plugin's maintainer. Never apply it to the plugin.

## 3. Promote scenarios

Each scenario in `$ORDERS/<id>/scenarios/` that proves lasting behavior: propose moving it to
`$KITCHEN_HOME/stations/<station>/tools/<tool>/scenarios/`, renamed by what it proves. One-off probes stay in the order.

## 4. Propose, don't apply

Show the owner the list, one line per miss: `miss → fix (kind) → file`, all in the kitchen home,
plus the lines added to `kit-proposals.md`. Apply on their go. Commit the kitchen repo.
A miss that happened once and has no pattern is noted, not fixed.
