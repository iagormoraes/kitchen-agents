---
name: retro
description: Step 9 of the kitchen. After an order goes out, turn every gate, taster question, extra round and owner correction into a check, a grill question or a spec field in this kitchen's House rules (never in the plugin). It writes the retro to disk and applies lessons that only add safety on its own; anything that loosens a bar or touches the product waits for the owner. Use after the expedite skill's "out" step, or when the owner says "retro".
---

Adapted from mattpocock/skills `retro` and pstack `correct` (MIT).

**First:** if you haven't in this session, read `$KITCHEN/RULES.md` in full (the absolute path is in
the session-start brief). It holds the rules every step below relies on.

## 1. Count the misses

From the order's folders, list every:

- gate in `gates.md`,
- question the taster found in `mise-en-place` (`$ORDERS/<id>/taster-*.md`),
- fix round and its "Act on" findings, and every proven finding in an `attack-*.md` (the earliest
  catch is usually the grill's Attack surface, line 16),
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

## 4. Write it down, apply what only adds safety

1. **Always write the retro to disk:** `$KITCHEN_HOME/retro/<order id>.md`, with the counts line
   and one row per miss: `miss → evidence → fix (kind) → where → applied | needs the owner`.
2. **Apply, without waiting, every fix that only adds safety to this kitchen's own process:** a
   new check (proven on the real case), a grill question, a spec field, a station gotcha. These
   change the kitchen home only, never the product, and the kitchen repo's history can undo each.
3. **Wait for the owner's go** on anything that:
   - loosens a bar: a leak-check allow, a removed or weakened check, a relaxed rule;
   - changes the product, its dependencies, the owner's data or a deploy;
   - is a decision only the owner can make (product, taste, money, risk).
4. Commit the kitchen repo, then tell the owner in **one line**: `Retro <id>: applied N lessons in
   <sha> (see retro/<id>.md); M wait for your go: <one phrase each>. Say "revert <row>" to drop one.`
5. A miss that happened once and has no pattern is noted in the file, not fixed.

The House rules stay short (about 15 lines): when a new line repeats or covers an old one, merge
them instead of adding.
