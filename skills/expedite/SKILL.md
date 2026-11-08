---
name: expedite
description: Steps 6 to 8 of the kitchen. Dispatch approved tickets to stations, watch them, check ownership, run the review, decide fix rounds, and hand the owner one finished plate. Use after the owner approves the spec and ownership map from mise-en-place.
---

Adapted from pstack `orchestrate`, `autopilot-stack`, `ketchup` (MIT) and mattpocock/skills
`implement-spec` (MIT).

**First:** if you haven't in this session, read `$KITCHEN/RULES.md` in full (the absolute path is in
the session-start brief). It holds the rules every step below relies on.

**You run the order, never the code.** You don't edit a path a station owns. You read diffs and
evidence, not only summaries.

## 1. Dispatch

- **First ticket alone.** On a new kitchen or a new kind of order, send one ticket and take it
  through cook, review and verdict before sending the rest. A flawed ticket then costs one run.
- **Each station's worktree and branches** are made once, in `mise-en-place` (before the taster),
  with the commands below; reuse them here, and make them only if they're missing. Never the Agent
  `isolation` option: it needs the session inside a git repo and picks its own folder and branch.
  Also create the ticket's branch `feat/<id>-<station>` in the station's tools repo
  (`git -C $KITCHEN_HOME/stations/<station>/tools switch -c feat/<id>-<station>`). An owner ticket
  (`Station: owner`) gets **no worktree**: the owner cooks in their own folder (`kitchen:line`).
  ```bash
  git -C <repo> worktree add $WORKTREES/<id>/<repo name> -b feat/<id>-<station> <base sha>
  ```
  The last folder carries the **repo's own name**, never the order id: tools that read the folder
  name (a project generator run in `.` names the project after it) then get the real name.
  **Empty repo** (no commit yet): there is no base to branch from.
  ```bash
  git -C <repo> worktree add --orphan -b feat/<id>-<station> $WORKTREES/<id>/<repo name>
  ```
  The base sha is git's empty tree, `4b825dc642cb6eb9a060e54bf8d69288fbee4904` (the ownership
  check and the reviewer diff against it). The out step has the matching merge.
  Write that folder, the base sha, the absolute `$ORDERS` path and the station's port into the
  ticket. A station alone in its repo still gets a worktree, so the owner's checkout is never touched
  while cooking (only at the pass, by you, in §5 Set the table).
- **One agent per path, across all orders.** Before dispatching a ticket, compare its `Owns` with
  every ticket still cooking in any order (`$ORDERS/*/plate.md` not `done`). An overlap waits until
  that station hands back, exactly like a `Blocked by`.
- **An owner ticket** (`Station: owner`) is never dispatched to an agent. When its blockers are
  done, run `kitchen:line` with the owner, while agent tickets keep cooking. Its review and pass
  are the same as any station's.
- Then dispatch every ticket whose `Blocked by` is done, in parallel, in the background:
  `Agent` with `subagent_type: kitchen:station`, `run_in_background: true`. The prompt is only the ticket's
  absolute path and "read it in full and follow it". Everything else is in the ticket.
  **Headless session** (`claude -p`, CI, a script): background agents are stopped when the
  session ends its turn. Dispatch with `run_in_background: false` instead, every station call in
  one response so they still cook in parallel, and carry the order to the pass in that turn.
  Keep about 4 stations cooking at once; the rest wait for a free slot.
- A ticket that depends on another station's work gets that station's `plate.md` pasted into its
  Context section before dispatch. When it also needs that station's code, create its worktree
  from the blocker's last clean sha (or from `order/<NNNN>` after the merge), not from the base.

## 2. Watch

- Every 30 minutes per cooking station: `ORDERS=$ORDERS $KITCHEN/scripts/watchdog.sh <station
  worktree> <id>` (the worktree, where its commits are). Exit 2 = stop it, start a fresh run on the
  same ticket (its plate holds the resume point), tell the owner.
- Retry by cause: smaller scope after a context limit; same ticket after a dropped run. After two
  failed retries, drop the ticket and tell the owner why.
- Never forward new owner input to a cooking station. Write it down as the next order.
- Send each `Agent` dispatch in a response of its own, with no other tool call: a hook that
  rewrites commands (for example a token-saving proxy) can make auto mode reject a mixed response.

## 3. When a station hands back

1. Read `$ORDERS/<id>/plate.md`. If the station returned its plate as text instead (a write was
   blocked), save that text unchanged as `plate.md`, with one line on top saying so.
2. `python3 $KITCHEN/scripts/ownership-check.py $ORDERS/<id>/ticket.md <repo> <base>`. Fail = a fix
   round with "revert or move the out-of-scope changes", no review needed yet.
3. Read the product diff for kitchen terms (kitchen, station, order or ticket as concepts, the
   orders or kitchen paths, an isolation port base). Any hit is a fix round before review: the
   product never knows about the kitchen.
4. Review: `Agent` with `subagent_type: kitchen:reviewer`, giving it, all as **absolute** paths: the
   order id, the station worktree, branch and base sha, the ticket, the spec, the plate, `$KITCHEN`,
   and the verdict path to write (`$ORDERS/<id>/verdict-<sha>.md`); for a re-review, the previous
   verdict. Agents don't get the session-start brief: a path you don't pass, they can't resolve.
5. Merge the station branches of the order into `order/<NNNN>` **of their own repo** when their
   verdicts are clean (one order branch per repo touched; disjoint `Owns` means no conflicts; a
   conflict is an ownership bug: stop and tell the owner). Merge in a **temporary worktree**
   (`git -C <repo> worktree add $WORKTREES/<NNNN>-merge/<repo name> order/<NNNN>`), run every
   station's verify command once more there, then **remove that worktree**: a branch checked out
   in a worktree can't be switched to in the owner's folder (step 5).
6. A station that owns a **shared service** (a local backend, a DB): once its repo's `order/<NNNN>`
   is merged, send a fresh run of that station to rebuild the service from it and log the restart.
   Only then dispatch the tickets that consume it.

## 4. Decide: another round, or the pass

| State | Action |
| --- | --- |
| Verdict clean, every 🤖 row passes at a verified level, ownership check passes | the pass |
| "Act on" findings, fix round 1 or 2 | a **fresh** station run: ticket + plate + verdict. Only "Act on" goes back |
| Still "Act on" after fix round 2 | stop. The ticket or spec is wrong. Bring the owner a re-spec proposal |
| A 🤖 row only `build-only` or `blocked` | a fix round, unless the plate proves no tool can reach it: then it becomes a 👤 row |
| "Consider" or "Noted" only | the pass. List them for the owner, don't cook them |

**Every run of a tool or proof happens in a worktree, never in the owner's folder.** For a run on
a branch that is checked out somewhere else, use a detached one:
`git -C <repo> worktree add --detach $WORKTREES/<id>-check/<repo name> <branch or sha>`, and remove
it after. If the worktree can't be created, stop: never fall back to the owner's folder.

## 5. Set the table: the kitchen switches the branch

The owner never runs git. They taste in their own folder with the project's usual dev command;
every branch move is yours. For each repo touched, in the owner's main checkout:

1. **Look first.** `git -C <repo> status --porcelain` must be empty. Uncommitted changes there
   are the owner's work: never stash, reset or switch over them. Stop and tell the owner which
   files, and taste from the screenshots until they commit or clear them.
2. Note the branch it is on now (`git -C <repo> branch --show-current`): the **home branch**.
3. `git -C <repo> switch order/<NNNN>`, then the station profile's install step when the lockfile
   differs from the home branch (the project's own install command).
4. Tell the owner, in the pass message, that the folder is now on the order branch.

Before the pass message, **start each owner command yourself, once, with no argument**, in a
detached worktree of `order/<NNNN>` (never the owner's folder): it must answer on its defaults on
this machine, then stop it. The stations always ran on their own ports, so this is the first run on
the owner's defaults; a default that is taken is a fix round, not the owner's surprise.

The worktrees stay until the out step, so a fix round can still cook while the owner tastes.

## 6. The pass: one hand-off to the owner

Every item must be decidable from this message alone. Never hand the owner a check you could run.

```markdown
## <order> ready to taste

**Outcome:** <one sentence, against the spec's goal>

| Station | Repo | Branch @ sha | 🤖 rows | Verdict | Rounds |
| --- | --- | --- | --- | --- | --- |

**Your folder is ready:** I switched `<repo>` to `order/<NNNN>` and installed its dependencies.
Run `<the daily "start developing" command from the spec's Owner commands, with no argument>`
there and open `<url>`. Nothing is in `<home branch>` yet.

**Taste these (👤):** <numbered steps, expected result each>
**Screenshots:** `<evidence folder>`
**Gates waiting on you:** <each: question, options, default taken> or "none"
**Consider (not done):** <one line each> or "none"
**Next orders born during cooking:** <one line each> or "none"

Approve to merge into `<home branch>` in: <each repo touched>? (separate go for push)
```

## 7. Out

- **Approved:** in each repo, `switch` back to the home branch, squash-merge `order/<NNNN>` into it,
  run the install step again, then push only on a second go. **Home branch with no commit yet**
  (empty repo): `git switch --orphan <home>`, `git checkout order/<NNNN> -- .`, then one commit:
  that commit starts the history. Merge each station's
  `feat/<id>-<station>` branch in its tools repo (if it changed tools). The spec gets
  `Status: implemented` and `Reviewed: <sha>, verdict clean`. Apply the plate's **Profile updates**
  to `$KITCHEN_HOME/stations/<name>/station.md` (they are facts: its tools, run command, gotchas,
  what it cannot reach), so the next ticket starts from a true profile. Commit both in the kitchen
  repo.
- **Changes asked or rejected:** `switch` each repo back to its home branch and run the install
  step, so the folder is as the owner left it. A **rejected** order also deletes its worktrees and
  its `feat/<id>-*` and `order/<NNNN>` branches, in the product repo and the tools repos. Changes become the next order (or a fix round, when
  they are a spec violation the review missed).

Then remove each station's worktree (`git -C <repo> worktree remove <folder>`). Once the squash
commit is on the home branch and its tree equals `order/<NNNN>`'s (`git diff --quiet <home> order/<NNNN>`),
delete `order/<NNNN>` and every `feat/<id>-*` branch of the order in the product repo
(`git branch -D`): the product keeps only its own history, never kitchen branches. Then run the
`retro` skill.
