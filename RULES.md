# The kitchen: how agents work here

A project is a restaurant. Each repo, or each module of one repo, is a **station** with its own
cook (an agent). A station owns its paths, its tools and its check, and delivers a finished,
checked plate. Nobody supervises a station while it cooks. The owner approves the order, and
stands at **the pass** to taste the plate once it is handed off.

This kit is the Claude Code plugin `kitchen`: its skills are `kitchen:setup`, `kitchen:grill`,
`kitchen:menu`, `kitchen:mise-en-place`, `kitchen:expedite`, `kitchen:line`, `kitchen:retro`; its
agents are `kitchen:station`, `kitchen:taster`, `kitchen:reviewer`, `kitchen:adversary`. A SessionStart hook of the plugin
loads a short brief into every session of a project that has a kitchen home.

## Zero footprint: kitchens live outside the codebase

**The codebase never knows about the kitchen.** No file in any repo, no line in any `CLAUDE.md`,
nothing in `.claude/`. The only files a station adds to a repo besides the product's code are its
tests: unit tests, and scenarios in the product's own **e2e suite** (`e2e/`, see "Station tools"),
written so a coworker who never saw the kitchen can run them.

**One kitchen per workspace, many kitchens per machine.** A kitchen serves one **root**: a single
repo (a **project**) or a folder of repos side by side (a **workspace**, often not a git repo).
All kitchens live in `~/.claude/kitchens/<name>/` (base override: `KITCHENS`), each named at setup
(default: the root's folder name). Each `kitchen.md` states its root on a `- **Root:**` line. The
session-start hook gives a session the kitchen whose root is the **longest match** for the
session's folder, so a session opened in a subfolder of a workspace still gets the workspace's
kitchen, and a project inside a workspace may have a kitchen of its own.
`kitchen:setup` creates a kitchen; `sh $KITCHEN/scripts/test-session-start.sh` checks the lookup.

| In a kitchen (`$KITCHEN_HOME`) | Holds | Git |
| --- | --- | --- |
| `kitchen.md` | from `templates/kitchen.md`: root, repos, stations, shared tools, House rules | kitchen repo |
| `specs/` | every spec `NNNN-<slug>.md` and `specs/research/` | kitchen repo |
| `stations/<name>/station.md` | the station's profile (from `templates/station.md`) | kitchen repo |
| `stations/<name>/tools/` | the station's harness: `check` and `prove` (see "Station tools") | **its own repo**, one per station, so stations commit tool changes in parallel without sharing an index |
| `orders/` | all paperwork | ignored |
| `worktrees/` | station checkouts of the codebase repos, so no repo tool ever scans them | ignored |

The kitchen repo and the tools repos are local. Never add a remote unless the owner asks. Only the
expediter commits in the kitchen repo; only the owning station commits in its tools repo.

**A kitchen never changes the plugin.** Its lessons about how the kitchen works go in its own
home: **House rules** in `kitchen.md` (grill questions, spec fields, checks, leak-check allows),
kitchen-only gotchas in station profiles, checks in station tools. Its lessons about the product
(how to set it up, build, run or test it, a device or toolchain gotcha) go in the project's own
docs or suite, in product words, handed off as one branch per retro: the project learns too. A
lesson is kept only when it cost something, will recur, is new and changes an action (`retro` §2). A lesson every project would need is written to
`$KITCHEN_HOME/retro/kit-proposals.md` for the plugin's maintainer, never applied by the session.

**The product never knows about the kitchen, not even as an idea.** Stations, orders, tickets,
kitchens and their ports exist only in the kitchen home and the station tools. No product file,
setting, name, label or argument exists because stations need it, and no comment, doc, test name
or commit message cites a spec, decision, row, ticket or order (`spec C7`, `D9`, `order 0002`). When stations need isolation
(their own copy of the app, their own ports, their own data), the station tools get it **from
outside**: they run the product's own commands with ordinary overrides (an environment variable
for a port, a different project or data folder name). The product just accepts ordinary settings,
each with a default. Which overrides exist is decided once, in the spec's **Owner commands**
(their defaults column); a station never adds one on its own. When a value has no override, the
station tools isolate around it (their own copy or data folder) or the row becomes 👤.

**Every path the kitchen writes is absolute** (`$ORDERS/…`, `$KITCHEN/…`, `$KITCHEN_HOME/…`). The
expediter's and the agents' working folder is usually the owner's repo, so a relative path would
put kitchen files in the codebase. Agents don't get the session-start brief: the expediter passes
them every absolute path they need.

**The owner's commands are the product's commands.** Every command the owner types day to day
(start developing, run the tests, reset the data) needs no argument on the common path: every
value has a default. The daily loop is fast (it reloads on change, no full rebuild per edit). A
production-like run is a separate command, proven by a station, not the owner's daily loop.

The names used below, all absolute and given by the session-start brief: `KITCHEN` = this kit's
folder, `KITCHEN_HOME`, `ORDERS` = `$KITCHEN_HOME/orders`, `WORKTREES` = `$KITCHEN_HOME/worktrees`.
Tickets and agent prompts carry these as absolute paths.

- `kitchen.md` lists every station: `| Station | Repo | Profile | Shared services it owns |`.
- A station is one repo, or one module of one repo; never two repos. A feature across repos is one
  ticket per repo, and **a commit never spans repos**.
- **One spec per feature**, in `$KITCHEN_HOME/specs/`, even when the feature spans repos. Numbers are
  never reused; every ticket and branch of the feature carries its number.
- **One order branch per repo touched**: `order/<NNNN>` in each repo, local only. On the owner's
  approval it becomes one **handoff branch** per repo (see "Handoff").

## Roles

| Role | Who | Does | Never |
| --- | --- | --- | --- |
| Owner | the human | brings the plan, answers the grill, approves the spec, tastes at the pass; **cooks a `Station: owner` ticket when they ask** (`kitchen:line`, the AI as sous-chef) | is asked a question a run can answer |
| Expediter | the main session | grills, writes the spec and tickets, dispatches, reviews, decides rounds, hands off | edits code a station owns while it cooks |
| Station | a permanent profile `$KITCHEN_HOME/stations/<name>/station.md` (from `templates/station.md`) + one **fresh** `kitchen:station` run per ticket | builds, tests, documents, commits on its branch, reports | asks a question, writes outside its `Owns`, merges, pushes |
| Taster | `kitchen:taster` | dry-runs a ticket before cooking: lists every question it would need to ask | writes anything |
| Reviewer | `kitchen:reviewer` | reviews one branch against ticket and spec, writes the verdict | edits code |
| Adversary | `kitchen:adversary` | attacks one branch through the door before merge, on its own worktree, port and data; reports only what a run proved | edits code, touches anything outside this machine |

## Flow of one order

| Step | Who | Skill | Output |
| --- | --- | --- | --- |
| 1. Plan | owner | | a plan, any shape |
| 2. Grill | expediter + owner | `grill` | decisions, policies, out of scope, all settled. A plan that is already a complete spec is recorded, not asked: no grill stop, its summary goes into the approval |
| 3. Spec | expediter | `menu` | `$KITCHEN_HOME/specs/NNNN-<slug>.md` |
| 4. Tickets + dry run | expediter + taster | `mise-en-place` | `$ORDERS/<id>/ticket.md` per station, zero taster questions |
| 5. Approve | owner | | approves spec + ownership map together, asks for changes, or rejects |
| 6. Cook | stations, in parallel | `expedite` | branches, `plate.md`, evidence |
| 7. Review and attack | reviewer, adversary | `expedite` | `verdict-<sha>.md`, and `attack-<sha>.md` when the ticket has an attack surface |
| 8. Round or out | expediter | `expedite` | a fix round (at most 2), or out: one handoff branch per repo at once, never pushed or merged by the kitchen |
| 9. Pass | owner | `expedite` | the expediter switches the owner's folder to the handoff branch, the owner runs the dev command and tastes; the verdict goes to `$ORDERS/<NNNN>-handoff/tasted` |
| 10. Retro | expediter | `retro` | each gate and owner correction becomes a grill question or a check |

**Small work** (one station, a few lines: a bug fix, a constant, a copy edit): the expediter does it
itself on `fix/<slug>`, in a worktree (never in the owner's folder), runs the check, gets a
verdict written to `$ORDERS/<date>-<name>/verdict-<sha>.md`. No ticket, no grill.

**After approval the order is frozen.** New owner input during cooking becomes the next order.
It never reaches a station that is already cooking.

## Principles

Every station, every review. When two conflict, the earlier one wins.

1. **YAGNI**: build only what the spec asks for. No speculative options, settings or extension points.
2. **KISS**: the simplest code that works. Plain control flow a newcomer reads straight through.
3. **DRY**: one source of truth for each rule, value and piece of knowledge. Real duplication is
   merged. Look-alike code that changes for different reasons is not duplication.
4. **SOLID**: only in a **brand-new project** (the spec creates the repo), because it shapes how
   every module is written. The grill marks the order `greenfield: yes`, and the spec sketches
   module boundaries and interfaces before any ticket. In an existing project, follow the patterns
   already there; never refactor toward SOLID unless the spec asks.

DRY is also the collision rule: each rule, contract and file has **one owner station**.

## Zero collisions

- Each ticket names `Owns` (paths it may write) and `Reads` (paths it may only read). The `Owns`
  lists of tickets in one order never overlap. `mise-en-place` checks this before dispatch.
- **One agent per path at a time, across all orders.** More hands on a big area = split it into
  smaller stations by module in `mise-en-place`, never two agents on the same paths. Several tickets
  on the same paths run one after another. A station never spawns helpers (no `Agent` tool).
- **Many stations, one repo.** No queue and no copy of the project. Before dispatch the expediter
  gives each station its own git worktree (a second checkout of the same repo, sharing one `.git`):
  `git -C <repo> worktree add $WORKTREES/<id>/<repo name> -b feat/<id>-<station> <base sha>`
  (empty repo: `--orphan`, see `expedite`).
  The ticket names that folder as the station's only working directory. Stations whose blockers
  are done cook at the same time, each in its own folder; a blocked station waits for its blockers.
- **Paperwork stays in one place.** `$ORDERS` (in the kitchen home), outside
  every repo and worktree. Tickets give its absolute path; stations write only there.
- **Runtime is shared, so it is assigned.** Each ticket gives its station its own port (and its own
  test database or data folder when the stack allows). A service everyone uses (a local DB, a
  backend) has one owner station: only it restarts or migrates it, and it logs each restart in its
  plate. A run that overlaps a restart is `blocked`, not `fail`, and is re-run.
- **A shared service runs the order's code before its consumers cook.** When the owner station's
  verdict is clean, it rebuilds the service from `order/<NNNN>` of its repo; consumer tickets are
  blocked until then. Each consumer's `result.json` records the service commit it tested against.
- **Specs are read from the kitchen home**, never from a worktree: the ticket gives the absolute
  path, read-only. Only the expediter writes specs.
- `python3 $KITCHEN/scripts/ownership-check.py $ORDERS/<id>/ticket.md <repo> <base>` fails when the
  branch touched anything outside `Owns`. It runs before review; a failure is an automatic round.
- A shared contract (types, REST JSON, packet, DB shape) is frozen in the spec, or owned by one
  station whose ticket blocks the consumers. Consumers read it and never change it.

## Handoff: the kitchen hands over branches, the project ships them

**The kitchen's job ends at a proven branch.** Spec alignment, engineering, testing and handoff
are the kitchen's. Push, pull requests, merge and deploy belong to the project: its own
`CLAUDE.md` and skills, or the owner. The kitchen never pushes, never merges into the home
branch, never opens a pull request.

- **One handoff branch per repo touched**, named for the product (`invoice-export`), with **one
  commit** whose message says what changed in the product. Name and message pass
  `leak-check.py --message`. It is recorded in `$ORDERS/<NNNN>-handoff/<repo name>/`:
  `branch` (one line: its name), `commit` (its commit id, so landing is seen even when the project
  deletes the branch on merge), `summary.md` (from `templates/handoff.md`, product words only) and
  `evidence/` (the files the summary shows, named by scenario).
- **Open orders never collide.** An order is open while it cooks, and after its handoff until its
  change is in the home branch (`python3 $KITCHEN/scripts/handoff.py landed <repo> <home> <branch>`).
  Before cutting worktrees, `python3 $KITCHEN/scripts/handoff.py base <repo> <home> $ORDERS
  <tickets>` compares the new order's Owns with every open handoff:

  | The new order's Owns vs open handoffs | Base |
  | --- | --- |
  | no overlap | the home branch: both merge in any order |
  | overlap with branches that build on one another | the newest of them (stacked) |
  | overlap with two branches where neither builds on the other (exit 3) | the order waits until one lands |

  An overlap with an order **still cooking** waits until that order hands off, then stacks
  (`expedite` §1). Grill, spec and tickets go ahead meanwhile; only cooking waits.
- **Every handoff names its base.** `summary.md` says **Builds on:** (the home branch, or the
  branch it stacks on) and **Proven on:** (the exact commits the full suite passed on).
- **Every session knows what waits to ship.** The session-start brief lists each handoff not yet
  in its home branch (`handoff.py open`), so the project's own flow can ship it from a new
  session too, and a new order sees what it may stack on. When the project ships is its own rule:
  the kitchen never adds a question. A merged one drops off by itself.
- **The handoff comes before the pass.** A clean order is handed off at once, and the owner
  tastes the handoff branch itself, so the project's flow can start while the owner tastes. The
  verdict is one word in `$ORDERS/<NNNN>-handoff/tasted`, shown next to each open handoff in the
  brief: `approved`, `changes`, `rejected`, or `none` (no 👤 row, no gate: nothing to taste);
  `waiting` until then. **A handed-off branch is never rewritten:** changes become the next order,
  stacked on it. A rejected handoff is no longer open, so nothing stacks on it; dropping its branch
  is the project's.
- **A delivered order leaves nothing behind.** In the first session after all of an order's
  handoffs are merged, the session-start hook runs `handoff.py clean`: it removes the order's
  `evidence/` and `scenarios/` folders, its logs, images, videos and archives, and its worktrees,
  and says so in the brief. The paperwork stays (tickets, plates, verdicts, gates, summaries).
  Evidence is never kept once its order is merged: re-running the suite recreates it. A rejected
  order is cleaned at once: `handoff.py clean <KITCHEN_HOME> <NNNN>`.
- **The kitchen vouches only for the base it proved on.** When a base branch changes after the
  handoff (the project's review changed it), restacking is the project's. Proving it again is the
  kitchen's: a **re-prove** order rebases the branch on the new base and runs the full suite, with
  no cooking unless something fails.

## Orders: the paperwork (`$ORDERS/<id>/`)

One folder per ticket. Id: spec number + station (`0012-api`), or date + name for small work.
One writer per file. Copy each file from `$KITCHEN/templates/`; never invent a shape.

| File | Written by | Holds |
| --- | --- | --- |
| `ticket.md` | expediter | goal, Owns/Reads, done check, verify commands, policies, autonomy |
| `plate.md` | station | commits, each 🤖 row with evidence, the append-only decision log, could not check |
| `gates.md` | station asks, owner answers at the pass | owner-only decisions, with the default the station took |
| `verdict-<sha>.md` | reviewer | Act on / Consider / Noted / Dismissed |
| `evidence/` | tools, with `ORDER=<id>` | screenshots, videos, logs, outputs |
| `$ORDERS/<NNNN>-handoff/<repo name>/` | expediter, at the out step | `branch`, `commit`, `summary.md`, `evidence/`: what the project's flow ships (see "Handoff"). `$ORDERS/<NNNN>-handoff/tasted` (the owner's verdict at the pass) and `cleaned` once its leftovers are removed |

## What proves a plate

A behavior needs one of the first three levels. `build-only` is never a pass.

| Level | Means |
| --- | --- |
| `e2e-verified` | driven in the running app (browser, CLI, game driver); screenshot or output saved |
| `runtime-verified` | read back from the running service: log line, DB row, HTTP response |
| `test-verified` | an automated test that fails without the change and passes with it |
| `build-only` | builds and lints. Not proof of behavior |
| `blocked` | could not run, with the reason. Not a pass |

Every claim in a plate points at evidence. A test counts only with its exact command, its exit
code and its output path. Each order leaves its tests behind in the repo for the next change: a
🤖 `e2e-verified` row is a scenario in the product's e2e suite, written in the same order.

**An order is proven completely before the handoff.** While cooking, a station runs the scenarios its
ticket names. Before the handoff, the **full suite** runs once on the merged `order/<NNNN>` (its
`results.json` says `"selected": "all"`), so the order proves its own work and that nothing older
broke.
Look, feel, phone, real payment: 👤 rows for the owner, with exact steps and a reference image
or mock agreed in the grill.

## Station tools

**Prove through the user's door, never a back door.** Every station proves its work by using the
product the way its user does: a player plays the game, a visitor clicks the site, the client and
the website call the server. Never call internal functions to cause an effect, never use
test-only endpoints, never write to the DB to fake a state.

**The driver follows what the door is made of** (the default; the grill may choose another, for
example plain requests plus a headless browser when the owner allows no new dependency):

| The user's door | Driver |
| --- | --- |
| DOM (web pages, webviews) | a browser automation driver |
| Canvas or native graphics (a game, a drawing tool) | a custom driver: real input events, named positions and probes, logs |
| HTTP, packets (a server) | real requests, or the driver of the client that is its user |
| Terminal (a CLI) | real commands in a shell |
| Code (a library) | a small example program calling the public API |

**The suite is the product's; the harness is the kitchen's.** What proves the product (the door
driver and the scenarios) lives in the repo, where coworkers and CI can run it with no kitchen. What
only the kitchen needs (its paths, ids, evidence and result format) stays outside.

```
<repo>/e2e/                      the product's e2e suite (one per repo that has a door to drive)
  package.json                   its own package: its dependencies never enter the product's
  README.md                      how to run it, what it needs running, in product words
  run.*                          the one command (`npm run e2e` or the stack's equivalent)
  driver/                        the door driver: one owner station
  scenarios/<behavior>.*         one file per behavior (`bid-survives-reload`), never an id
$KITCHEN_HOME/stations/<station>/
  station.md                     the profile (kitchen repo)
  tools/                         the station's own git repo: the harness
    check                        build, lint and the repo's unit tests, run inside $REPO
    prove                        runs the repo's suite, writes the kitchen's evidence and result.json
    README.md                    flags, what it cannot reach (those become 👤 rows)
```

**A scenario lives in the repo whose door it uses.** A server proven through its client is a
scenario in the client's suite, under a client ticket blocked by the server ticket; the server's
own repo may have no suite. A suite may need other repos running (a backend): its README says so.

**The suite's contract** (any runner that keeps it will do; a repo that already has a suite keeps
its runner):

| Rule | Detail |
| --- | --- |
| Call | `run [--port <n>] [--out <dir>] [--video] [--list] [<scenario>…]`, every value defaulted: no argument runs every scenario. `--list` prints the scenario names |
| Boot | the suite starts what it drives on `--port` (with the product's own commands and ordinary settings), waits for a signal it is ready, and stops only the processes it started |
| Exit | `0` pass · `1` a scenario failed · `2` could not run (a runtime missing, port busy, an unknown scenario, a needed service not answering) |
| `results.json` | in `--out`, on every exit: `{"status", "reason", "selected": "all" \| [names], "scenarios": [{"name", "status", "ms", "error", "video"?, "steps": [{"name", "pass", "screenshot"?}]}]}` |
| Evidence | `--out/<scenario>/`: a screenshot per step, the console or log lines, and with `--video` `<scenario>.mp4`, recorded by the driver from the app it drives (a headless browser's own frames, never the screen) |
| Accounts | test accounts come from a path in an ordinary setting (`E2E_ACCOUNTS`); the repo keeps only an example file. Never the owner's own account |
| The door | a scenario imports only the suite's own files, `node:` built-ins and packages the suite's `package.json` lists; the product never imports the suite. `scripts/door-check.py` proves both |

**The harness's contract** (every station tool keeps it, so no ticket has to spell it out; any
internal it doesn't fix falls under the Unwritten details policy: the station picks, logs it in its
plate, keeps the contract):

| Rule | Detail |
| --- | --- |
| Call shape | `REPO=<worktree> ORDERS=<abs path> ORDER=<id> PORT=<n> $KITCHEN_HOME/stations/<station>/tools/prove [--row <smoke row>=<scenario>]… [--all]`. `check` takes the same variables and needs only `REPO`. A missing required variable: a usage line, exit 2 |
| Exit code | `0` pass · `1` fail · `2` blocked. Blocked is never a pass |
| Blocked (exit 2) | the tool could not run: a required variable missing, port busy, an install step failing, a browser or runtime missing (say the install command, never install it), the app not ready within 60 s, an unknown scenario, a runner producing no readable result |
| Fail (exit 1) | the tool ran and something is wrong: a build, lint or test failure, any check failing |
| Combining steps | `check` runs every step even after one fails and prints each exit code. The result: any step blocked gives 2; else any step failing gives 1; else 0 |
| `check` | inside `$REPO`: install if missing, then lint, build, the repo's unit tests, and `python3 $KITCHEN/scripts/door-check.py $REPO` when the repo has a suite. Writes no evidence |
| `prove` | creates the evidence folder first, then runs the repo's suite with `--port $PORT --out <evidence folder>`, `--video` for a station with a visual door, and the named scenarios (`--all`: every one), then writes `result.json` from the suite's `results.json` |
| Evidence | `$ORDERS/$ORDER/evidence/<station>-<YYYYMMDD-HHMMSS>/` (suffix `-2` on a clash), always with `result.json`, plus the suite's own output and logs |
| `result.json` | `{"commit", "buildTime", "status": "pass" \| "fail" \| "blocked", "selected", "checks": [{"id", "pass", "detail"}], "reason"?, "serviceCommit"?}` (`serviceCommit`: the shared service's commit it tested against, when it uses one). Written on every exit. `blocked` or a failed build: `checks: []`, a `reason`, `buildTime: null` |
| Check ids | `<smoke row>.<scenario>` (`S4.renewal`): the row comes from `--row`, so spec ids stay in the kitchen and scenarios carry only behavior names |
| Waits for a signal | a selector, a log line, a response, a probe. A fixed sleep only where no signal exists, with the reason |
| Safety | its own port, data and browser profile; kills only the processes it started (by PID) and their children, on any exit; never touches the owner's browser, dev server or accounts; read-only on shared services it doesn't own. **Its destructive steps (remove, wipe, reset, drop) act only on names it created itself and refuse every name in `kitchen.md` Owner resources, even when a setting or a fallback points at one; its `--selftest` proves that refusal** |
| Selftest | `--selftest` runs the tool's own logic on fake inputs, with no app, server or network: `check` its combining rule (`0 0 0`→0, `0 1 0`→1, `0 2 0`→2); `prove` its mapping (a failing scenario→1, all pass→0, unreadable `results.json`→2) |

**One driver, one owner.** A driver several stations use (a game driver the server station plays
rules with) lives in the suite of the repo it drives, and one station owns `driver/`. Others write
only their own scenario files; a driver feature they need is a ticket for the owner that blocks
them. `kitchen.md` lists each driver under Shared tools.

**A new station** starts with no tools: its first ticket builds `check` and `prove`, and, when the
repo has a door to drive and no suite yet, the suite with a boot scenario (it starts and answers
with no error), the evidence layout and the safety rules. Scenarios grow order by order.

## Autonomy

| A station or the expediter just does it | Needs the owner's go |
| --- | --- |
| read, build, test, run its own check, start its own server on its own port | the approval of the spec and ownership map (step 5) |
| the handoff (step 8), once the order is clean | |
| at the pass, the expediter switches the owner's folder to the handoff branch and back, only when its working tree is clean (never stash or reset) | |
| commit on its feature branch (only files it owns) | production, deploy, anything outside this machine |
| change local dev data the ticket names | wipe or restore a database |
| | **never the kitchen's**, even on a go: push, merge into the home branch, any commit on it, a pull request, a release tag. The project's own flow does them |
| the review, and fixing its findings | product or design choices no run can settle |
| choosing between two ways to build when running both settles it | |

A question whose answer can be observed by running something is not the owner's: run it.

## Rounds

- A verdict with "Act on" findings, or a failed ownership check, sends a **fresh** station run
  with the ticket, the plate and the verdict. Never resume an old run: resumed runs drop directives.
- **At most 2 fix rounds per ticket.** Still failing after round 2 means the ticket or the spec is
  wrong: the expediter stops and brings the owner a re-spec, not a round 3.
- **A failure the order didn't cause is not its round.** A scenario the order did not touch that
  fails in the full suite is run again on the base commit, in a detached worktree. Failing there too,
  it is **pre-existing**: listed in the pass, never a fix round of this order. Passing there, the
  order broke it: a fix round. The order's own scenarios are never retried to get a pass.
- Stuck station: no commit, plate change or new evidence for 30 minutes (60 during a long build):
  `ORDERS=$ORDERS $KITCHEN/scripts/watchdog.sh <station worktree> <id>` exits 2. The plugin's
  monitor runs it every 5 minutes in interactive sessions and wakes the expediter; after a restart
  the session-start brief lists the stations still cooking. Stop it, start a fresh run from ticket +
  plate, tell the owner.
- Pausing: one `chore(wip): <what>` commit, `plate.md` with `Status: paused` and a resume point.
  The next run treats ticket + plate as true and never redoes verified work.

## Big orders

- **Count the whole job first.** An order over many items gets `$ORDERS/<spec>-scope.json`, one row
  per item. Only the expediter writes it, moving rows up from the plates (one writer per file).
  Every progress update starts with the line `python3 $KITCHEN/scripts/scope.py` prints.
- **Wide first, then deep.** Pass 1 brings every item to the new baseline; pass 2 polishes group by
  group. Running out of time leaves less polish, never half the items untouched.
- **Hand off per group** on the owner's go. No group waits days on a branch.

## Rule → what enforces it

Prefer a check over a sentence. When the owner corrects the same mistake twice, `retro` turns it
into a check in this kitchen's House rules (never here: a kitchen never changes the plugin); a
lesson every project needs goes to `$KITCHEN_HOME/retro/kit-proposals.md` for the maintainer.

| Rule | Enforced by |
| --- | --- |
| Stations write only their `Owns` | `scripts/ownership-check.py` before review; `scripts/test-ownership-check.sh` proves it on a real repo with a worktree, run from either side |
| The right kitchen loads in each folder | `scripts/test-session-start.sh` |
| Every station's repo is under its kitchen's root | `scripts/kitchen.py check <kitchen>`, run by `kitchen:setup` before its commit; selftest case from the 2026-11-05 setup bug (a sibling repo offered as a station) |
| The kitchen never destroys the owner's resources | `kitchen.md` Owner resources; the guard hook (`scripts/kitchen.py guard`) refuses destructive commands naming them; each station tool's `--selftest` proves its own refusal (a hook can't see inside a script); `scripts/test-owner-guard.sh` |
| Owner command defaults work on the owner's machine | grill line 15 checks each default is free; `expedite` runs each owner command once with no argument before the pass |
| The product never knows about the kitchen; owner commands need no argument | `agents/taster.md` and the verdict's "Kitchen leak" and "Owner commands" lenses; the expediter reads every product diff for kitchen terms before the review |
| A project session never changes the plugin | the guard hook (`scripts/kitchen.py guard`) denies edits inside the plugin from any session a kitchen covers; `scripts/test-owner-guard.sh` |
| Every change to the attack surface is attacked before merge | `kitchen:adversary` writes `attack-<sha>.md`; a proven finding is a fix round with a test that runs the attack. Replayed blind on 4 real bugs a reviewer had caught: found 3 (2026-11-08); the miss, a two-step stored-input delete, became an attack class |
| No kitchen word or spec id in the product | `scripts/leak-check.py --spec`: by the station before hand-back, by the expediter on every branch before review, `--all` on the whole product before every handoff (catches what earlier orders left), `--message` on the handoff commit message, branch name and summary; new file paths too (an order number in a scenario name); `scripts/test-leak-check.sh` |
| Open orders never collide; a handoff names its base | `scripts/handoff.py base` before worktrees are cut, `handoff.py landed` to close an order; its `--selftest` builds real stacked and squash-merged branches |
| A new session knows the open handoffs and their verdicts | `handoff.py open` in the session-start brief; `scripts/test-session-start.sh` (listed while open, gone once squash-merged); `handoff.py --selftest` (the verdict shown, a rejected handoff dropped and never stacked on) |
| A merged order leaves no evidence, logs, media or worktrees behind | `handoff.py clean`, run by the session-start hook; its `--selftest` (nothing removed while open, paperwork kept, a branch deleted on merge still seen through its commit) and `scripts/test-session-start.sh` |
| The kitchen never pushes or merges | text only: `expedite` §5 has no push or merge step; `agents/station.md` Never |
| Stations never ask the owner | `agents/station.md` has no `AskUserQuestion` tool |
| The AI never writes the code an owner ticket gives the owner | the plugin's `PreToolUse` hook `scripts/kitchen.py guard` denies `Edit`/`Write`/`MultiEdit`/`NotebookEdit` on those paths until the plate is done or the owner says "take over"; `scripts/test-owner-guard.sh`. Writes through Bash: text only (`kitchen:line`) |
| The station's hand-back file is `plate.md` | Claude Code refuses a subagent's write to a file named `report.md` ("Subagents should return findings as text"); tested 2026-11-04 |
| The taster loop ends | at `facts 0 · decisions 0`, or after 3 rounds (`mise-en-place`) |
| Exclusions inside an owned folder are `!path`, never prose | `scripts/ownership-check.py` refuses a prose exclusion (exit 2); `test-ownership-check.sh` |
| The ownership check works in an empty repo | falls back to the ticket's branch; `test-ownership-check.sh` |
| Tools and proofs never run in the owner's folder | text only: `expedite` uses detached worktrees and stops if one can't be made |
| Data loss is Act on | text only: `templates/verdict.md`, `agents/reviewer.md` |
| Tickets need no questions | taster dry run in `mise-en-place`, zero questions to dispatch |
| Taster never edits | `agents/taster.md` tools: Read, Grep, Glob only |
| Reviewer never edits code | text only (it needs Bash to re-run checks and Write for the verdict) |
| A stalled station is replaced | `scripts/watchdog.sh`, run every 5 minutes by the plugin monitor (`monitors/monitors.json` → `scripts/watch-orders.sh`); interrupted stations listed at session start; `scripts/test-watch-orders.sh`, `scripts/test-session-start.sh` |
| A station tool can't pass while broken | each tool's `--selftest` |
| Tools prove through the user's door | `scripts/door-check.py` (a scenario imports only the suite, `node:` and the suite's listed packages; the product never imports the suite), run by every `check`; the reviewer reads every `driver/` diff |
| An order is proven completely | `prove --all` on `order/<NNNN>` before the handoff; its `result.json` must say `"selected": "all"` |

## Writing style

The owner reads every report. Lead with the outcome. Plain words; a codebase term gets its meaning
the first time. Numbers, paths and commands exact, in tables or code blocks. One idea per sentence.
