---
name: retro
description: Step 10 of the kitchen. After an order goes out, turn the misses that earn it (they cost something, will recur, are new, change an action) into lessons at the right level - the kitchen's House rules for how the kitchen works, the project's own docs or suite for facts about the product (handed off as one branch), the plugin's proposals for what every kitchen needs. A miss that came back strengthens its old fix instead of adding a line. Use after the expedite skill's "out" step, or when the owner says "retro".
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

## 2. Keep only what earns its place

A lesson is read by every station on every ticket, so a needless one is noise that costs every
order. Keep a miss as a lesson only if **all four** hold; otherwise note it in the retro file and
nothing else:

1. **It cost something:** a fix round, a question to the owner, an owner correction, a failed gate.
2. **It will recur:** it happened twice, or it is certain to come back (the same device, the same
   toolchain, the same kind of order). Read the earlier `$KITCHEN_HOME/retro/*.md` to tell.
3. **It is new:** no rule, House rule, profile, repo doc or check covers it. When one covers it and
   the miss happened anyway, that one failed: strengthen it (step 3), never add a second line.
4. **It changes an action:** a concrete step or fact ("wake the phone and accept USB before a
   benchmark"), never advice anyone follows anyway ("measure carefully").

**A miss that came back.** When an earlier retro already fixed this miss, its fix was too weak:
move that same fix one step up the strength table below (a sentence becomes a spec field or a
grill question, those become a check; a project doc fact becomes a test in the project's suite),
and delete the weaker form. Never stack a second lesson on the first.

## 3. Put each lesson at its level, at the earliest catch

| Level | What | Where |
| --- | --- | --- |
| **Kitchen** | how the kitchen works: what to grill, what a spec must say, what to check before review or handoff, a station's kitchen-only facts (its ports, its tools) | this kitchen's home (the table below) |
| **Project** | facts about the product that anyone working on it needs, kitchen or not: how to set up, build, run, test or deploy it, a device or toolchain gotcha, a test it should have | the project's own docs (its `CLAUDE.md`, `README` or `docs/`) or its test suite, in product words: step 5 hands them off |
| **Plugin** | a lesson every kitchen would need | `$KITCHEN_HOME/retro/kit-proposals.md` (miss, evidence, proposed change, proof it fails on the real case), for the plugin's maintainer; never applied to the plugin |

A project fact never goes in a station profile: a coworker, another machine or a session without
the kitchen would never see it. Most retros have no project lesson at all.

For each kitchen lesson, the earliest step that could have stopped it. Use the strongest fix that
works. **Never in the kitchen plugin** (`$KITCHEN`): it is shared by every kitchen and changed only
by its maintainer. The guard hook refuses a project session's edits inside it.

| Strength | Fix | Where it goes |
| --- | --- | --- |
| 1 | **A check** (a script, test or lint that fails on the mistake). Prove it fails on this real case before adding it | the owning station's tools, `$KITCHEN_HOME/stations/<name>/tools/`; listed under **House rules → Checks** in `$KITCHEN_HOME/kitchen.md` |
| 2 | **A grill question**, worded as the question that would have caught it | **House rules → Grill questions** in `$KITCHEN_HOME/kitchen.md` |
| 3 | **A spec field** that forces the answer to be written down | **House rules → Spec fields** in `$KITCHEN_HOME/kitchen.md` |
| 3 | **A gotcha** about the kitchen's own work, when only one station needs it (a fact about the product goes to the project) | that station's profile, `$KITCHEN_HOME/stations/<name>/station.md` |
| 4 | **A sentence**: last resort, text is the weakest guard | **House rules** in `$KITCHEN_HOME/kitchen.md` |

The session-start brief loads `kitchen.md`, so every later order of this kitchen runs with its
House rules.

## 4. Scenarios left behind

Each order writes its scenarios straight into the repo's e2e suite, so nothing is promoted here.
List any 🤖 `e2e-verified` row that has no scenario in the suite, and any pre-existing failure the
pass listed: each becomes a next order (a scenario to write, a failure to fix), on the owner's go,
because it changes the product.

## 5. Write it down, apply, hand off the project's lessons

1. **Always write the retro to disk:** `$KITCHEN_HOME/retro/<order id>.md`, with the counts line
   and one row per miss: `miss → evidence → kept? (which of the four failed) → level → fix (kind)
   → where → applied | handed off | needs the owner`.
2. **Apply, without waiting, every fix that only adds safety to this kitchen's own process:** a
   new check (proven on the real case), a grill question, a spec field, a station gotcha. These
   change the kitchen home only, never the product, and the kitchen repo's history can undo each.
3. **Project lessons go out as one handoff**, the kitchen's small work: in a worktree from the home
   branch (never the owner's folder), write every project lesson of this retro into the repo's
   docs or suite, in product words, as one commit on a product-named branch (`docs-phone-benchmarks`).
   Run `leak-check.py` on the branch (`--spec`, every spec) and `--message` on its name and
   message, and the station's `check` when a test was added. Record it like any handoff in
   `$ORDERS/<order id>-lessons-handoff/<repo name>/` (`branch`, `commit`, a short `summary.md`),
   so the brief lists it and the project's own flow ships it. Merging it is the owner's go: no
   question now. No project lesson: no branch.
4. **Wait for the owner's go** on anything that:
   - loosens a bar: a leak-check allow, a removed or weakened check, a relaxed rule;
   - changes the product, its dependencies, the owner's data or a deploy;
   - is a decision only the owner can make (product, taste, money, risk).
5. Commit the kitchen repo, then tell the owner in **one line**: `Retro <id>: kept K of N misses;
   applied A in <sha>; project lessons handed off as <branch> (or "none"); M wait for your go:
   <one phrase each> (see retro/<id>.md). Say "revert <row>" to drop one.`

The House rules stay short (about 15 lines): when a new line repeats or covers an old one, merge
them instead of adding.
