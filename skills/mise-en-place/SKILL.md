---
name: mise-en-place
description: Step 4 of the kitchen. Cut an approved-to-be spec into one ticket per station with disjoint ownership, then dry-run every ticket with the taster until no station would need to ask a question. Use right after the menu skill, before showing the owner the spec for approval.
---

Adapted from mattpocock/skills `to-tickets` and `triage/AGENT-BRIEF.md` (MIT), and pstack
`feature` throughput checkpoint and `orchestrate` (MIT).

**First:** if you haven't in this session, read `$KITCHEN/RULES.md` in full (the absolute path is in
the session-start brief). It holds the rules every step below relies on.

## 1. Cut the tickets

- One ticket per station. A station is one repo or one module with its own check.
- **Contracts first.** A ticket that creates a shared contract blocks every ticket that consumes
  it. Or the spec freezes the contract and nobody blocks.
- **Blocking edges.** Each ticket lists `Blocked by`. A ticket with no blockers starts at once.
- **Wide refactors:** expand (new beside old), migrate in batches, contract (delete old). Each its
  own ticket, chained by blocking edges.
- Code-coupled work (one feature inside one module) is one ticket. Split only where the outputs
  are independent.
- Each ticket fits one fresh context window. Too big: split by item, wide first (see "Big orders"
  in the kitchen RULES.md).

## 2. Fill each ticket

Copy `$KITCHEN/templates/ticket.md` to `$ORDERS/<id>/ticket.md`. Every field filled. Start from the
station's profile `$KITCHEN_HOME/stations/<name>/station.md`: `Owns` may narrow its default, never widen it; Verify uses
its tools' `check` and `prove`, and Owns always includes its tools repo `$KITCHEN_HOME/stations/<name>/tools/`. A station with no profile gets one first (from `templates/station.md`), approved with the spec. Paste, never
point at this chat: a station cannot see it. Copy the spec's **Policies** and the applying
**Principles** word for word.

**An owner ticket** (`Station: owner`, the owner asked to cook it): its Owns are the main-logic
paths, with the test files excluded as `!path` (the AI writes those). Fill its **Owner steps**:
each step one sitting for a person, with the files, the concept, and the test cases from the spec.
It is blocked by the boilerplate tickets, so the owner starts on a project that already builds.
The taster dry-runs it as the owner: could they start each step from the files and the concept
alone?

## 3. Check ownership

List each ticket's `Owns`. No path or glob may appear in two tickets, and no glob may contain
another ticket's path. A shared file (a route table, an index or re-export file, a lock file) gets one owner;
the others put what they need under "Orders for other stations" in their plate, or the owner's
ticket does it first.

## 4. Dry run with the taster

First create each station's worktree and branches, **once** (the commands in `expedite` §1
Dispatch; no worktree for a `Station: owner` ticket), so every path the ticket names exists when the
taster checks it. `expedite` reuses them.

For each ticket, run `Agent` with `subagent_type: kitchen:taster`, giving it only the ticket path and the
spec path. It returns `facts: N · decisions: N`. Save each answer, unchanged, to
`$ORDERS/<id>/taster-<round>.md`: the retro counts them.

- **Fact:** add it to the ticket (a path, a command, a value, a permission).
- **Decision:** back to `grill` for that branch, then into the spec and the ticket.
- **Answer the cause, not the instance.** When a question is a detail the policies should have
  settled, fix the policy, not the one detail. Never answer a detail by prescribing *how* to build
  it: the ticket says what must be true, the station decides how.
- Re-run a **fresh** taster on the changed ticket.
- **Stop at `facts: 0 · decisions: 0`, or after 3 rounds.** After 3 rounds: remaining facts go into
  the ticket and the order dispatches, with the leftovers listed under Attention in the approval
  message; a remaining decision means the grill missed a branch: say so and grill it.

## 5. Owner approval

Write every URL or command that exists only after cooking as "after the build". Show the owner,
in one message, opening with: **"This approves the plan, not the result. You taste
the real thing before anything reaches `main`."**

1. The spec path and a 5-line summary.
2. The **ownership map**: station, owns, blocked by, budget.
3. The 👤 rows they will taste.
4. `taster: facts 0 · decisions 0 on N tickets, in R rounds`.
5. **Attention:** the leftovers after 3 taster rounds, or "none".

The owner approves, asks for changes (back to the step that owns the change), or rejects. A
rejection deletes the worktrees and branches made for the taster.
Approved = the order is frozen. Then run the `expedite` skill.
