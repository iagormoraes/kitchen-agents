---
name: menu
description: Step 3 of the kitchen. Turn a finished grill into the spec, the contract every ticket is cut from. Use right after the grill skill closes, or when the owner says "write the spec". Does not interview; it writes what the grill settled.
---

Adapted from mattpocock/skills `to-spec` (MIT) and pstack `architect` (MIT).

**First:** if you haven't in this session, read `$KITCHEN/RULES.md` in full (the absolute path is in
the session-start brief). It holds the rules every step below relies on.

Do **not** ask new questions. Write what the grill settled. If you find a gap while writing, go
back to `grill` for that one branch.

## Steps

1. Copy `$KITCHEN/templates/spec.md` to `$KITCHEN_HOME/specs/NNNN-<kebab-slug>.md`: one spec per
   feature, even across repos. `NNNN` is the next number that is free **both** in `specs/` and in
   every repo of the kitchen (and the station tools repos): no `feat/NNNN-*` or `order/NNNN` branch
   (`git -C <repo> branch --list 'feat/NNNN-*' 'order/NNNN'`). A kitchen set up again over old repos
   must not reuse a number its old branches hold.
2. Fill every section, and every **Spec field** in this kitchen's House rules
   (`$KITCHEN_HOME/kitchen.md`). A section you cannot fill means the grill is not finished.
3. **Greenfield only (`greenfield: yes`):** before the tickets, design the modules twice.
   - Run two fresh `Plan` subagents with the same brief, each told to design a structurally
     different shape. Each writes caller usage first (two or three real call sites), then the types.
   - Pick one, or merge the two, against SOLID and these red flags: shallow module, pass-through
     method, split ownership of state, two ways to do one task, a hand-synced list, internals other
     modules import.
   - Write the result in the spec's **Design** section: modules, their interfaces, who owns what,
     and the alternative you rejected with the reason.
   In an existing project, skip this step: the Design section says "follow the patterns in
   `<paths>`" and names them.
4. **The owner tastes through the daily loop.** Every 👤 row runs the spec's **Owner commands**
   (the daily "start developing" one), never a production-like build. A production-like run is a
   🤖 row a station proves. Every owner command has a default for every value.
5. **Run every expected text through the spec's own rules.** For each smoke row and Behavior
   line, pass its expected value through the transforms the spec applies (normalize, encode,
   escape, trim, round) and check it still reads as written. A URL encoder stores `<` as `%3C`,
   so a row expecting the raw text can never pass.
6. Keep the spec a contract, not a research log: about 300 lines or less. Long findings go to
   `$KITCHEN_HOME/specs/research/` and the spec links them.
7. Run the `mise-en-place` skill.
