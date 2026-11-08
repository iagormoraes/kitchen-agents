# The kitchen: how agents work here

A project is a restaurant. Each repo, or each module of one repo, is a **station** with its own
cook (an agent). A station owns its paths, its tools and its check, and delivers a finished,
checked plate. Nobody supervises a station while it cooks. The owner stands at **the pass**:
approves the order, tastes the plate, says when it goes out.

This kit is the Claude Code plugin `kitchen`: its skills are `kitchen:setup`, `kitchen:grill`,
`kitchen:menu`, `kitchen:mise-en-place`, `kitchen:expedite`, `kitchen:line`, `kitchen:retro`; its
agents are `kitchen:station`, `kitchen:taster`, `kitchen:reviewer`. A SessionStart hook of the plugin
loads a short brief into every session of a project that has a kitchen home.

## Zero footprint: kitchens live outside the codebase

**The codebase never knows about the kitchen.** No file in any repo, no line in any `CLAUDE.md`,
nothing in `.claude/`. The only kitchen files a repo gets are the normal tests a station writes for
its code.

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
| `kitchen.md` | from `templates/kitchen.md`: root, repos, stations, shared tools | kitchen repo |
| `specs/` | every spec `NNNN-<slug>.md` and `specs/research/` | kitchen repo |
| `stations/<name>/station.md` | the station's profile (from `templates/station.md`) | kitchen repo |
| `stations/<name>/tools/` | the station's tools (see "Station tools") | **its own repo**, one per station, so stations commit tool changes in parallel without sharing an index |
| `orders/` | all paperwork | ignored |
| `worktrees/` | station checkouts of the codebase repos, so no repo tool ever scans them | ignored |

The kitchen repo and the tools repos are local. Never add a remote unless the owner asks. Only the
expediter commits in the kitchen repo; only the owning station commits in its tools repo.

**The product never knows about the kitchen, not even as an idea.** Stations, orders, tickets,
kitchens and their ports exist only in the kitchen home and the station tools. No product file,
setting, name, label or argument exists because stations need it. When stations need isolation
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
- **One order branch per repo touched**: `order/<NNNN>` in each repo. Each merges and pushes in its
  own repo, on the owner's go.

## Roles

| Role | Who | Does | Never |
| --- | --- | --- | --- |
| Owner | the human | brings the plan, answers the grill, approves the spec, tastes at the pass; **cooks a `Station: owner` ticket when they ask** (`kitchen:line`, the AI as sous-chef) | is asked a question a run can answer |
| Expediter | the main session | grills, writes the spec and tickets, dispatches, reviews, decides rounds, hands off | edits code a station owns while it cooks |
| Station | a permanent profile `$KITCHEN_HOME/stations/<name>/station.md` (from `templates/station.md`) + one **fresh** `kitchen:station` run per ticket | builds, tests, documents, commits on its branch, reports | asks a question, writes outside its `Owns`, merges, pushes |
| Taster | `kitchen:taster` | dry-runs a ticket before cooking: lists every question it would need to ask | writes anything |
| Reviewer | `kitchen:reviewer` | reviews one branch against ticket and spec, writes the verdict | edits code |

## Flow of one order

| Step | Who | Skill | Output |
| --- | --- | --- | --- |
| 1. Plan | owner | | a plan, any shape |
| 2. Grill | expediter + owner | `grill` | decisions, policies, out of scope, all settled |
| 3. Spec | expediter | `menu` | `$KITCHEN_HOME/specs/NNNN-<slug>.md` |
| 4. Tickets + dry run | expediter + taster | `mise-en-place` | `$ORDERS/<id>/ticket.md` per station, zero taster questions |
| 5. Approve | owner | | approves spec + ownership map together, asks for changes, or rejects |
| 6. Cook | stations, in parallel | `expedite` | branches, `plate.md`, evidence |
| 7. Review | reviewer | `expedite` | `verdict-<sha>.md` per station |
| 8. Round or pass | expediter | `expedite` | a fix round (at most 2), or the hand-off: the expediter switches the owner's folder to the order branch, the owner runs the dev command and tastes |
| 9. Retro | expediter | `retro` | each gate and owner correction becomes a grill question or a check |

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

## Orders: the paperwork (`$ORDERS/<id>/`)

One folder per ticket. Id: spec number + station (`0012-api`), or date + name for small work.
One writer per file. Copy each file from `$KITCHEN/templates/`; never invent a shape.

| File | Written by | Holds |
| --- | --- | --- |
| `ticket.md` | expediter | goal, Owns/Reads, done check, verify commands, policies, autonomy |
| `plate.md` | station | commits, each 🤖 row with evidence, the append-only decision log, could not check |
| `gates.md` | station asks, owner answers at the pass | owner-only decisions, with the default the station took |
| `verdict-<sha>.md` | reviewer | Act on / Consider / Noted / Dismissed |
| `evidence/` | tools, with `ORDER=<id>` | screenshots, logs, outputs |

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
code and its output path. Each order leaves at least one test behind for the next change.
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

**Layout: one interface per station, one app per tool**, in the kitchen, never in the codebase:

```
$KITCHEN_HOME/stations/<station>/
  station.md     the profile (kitchen repo)
  tools/         the station's own git repo
    check        build, lint and the repo's own unit tests, run inside $REPO
    prove        starts what it needs from $REPO on $PORT, runs the tools the change needs,
                 merges one result.json
    README.md    each tool, its flags, what it cannot reach (those become 👤 rows)
    <tool>/      each tool its own app with its own dependencies (for example `e2e/` for the browser driver, `api/` for request checks)
      scenarios/ durable proofs, named by what they prove
```

Tools live outside the repo, so they can only reach the product through its door: a URL, a port,
a command. The station owns its `tools/` repo: it commits tool changes there on the ticket's
branch `feat/<id>-<station>`, the expediter merges that branch with the order, and the ticket's
`Owns` names it (`$KITCHEN_HOME/stations/<station>/tools/`). Tests of the code itself (unit tests)
are normal repo tests and stay in the repo, inside the ticket's `Owns`.

**The contract every tool keeps.** It is fixed here so no ticket has to spell it out: a station
building its first tools follows it, and any internal it doesn't fix falls under the Unwritten
details policy (the station picks, logs it in its plate, keeps the contract).

| Rule | Detail |
| --- | --- |
| Call shape | `REPO=<worktree> ORDERS=<abs path> ORDER=<id> PORT=<n> $KITCHEN_HOME/stations/<station>/tools/prove [--expect "<text>"]… [<scenario>…]`. `check` takes the same variables and needs only `REPO`. A missing required variable: a usage line, exit 2 |
| Exit code | `0` pass · `1` fail · `2` blocked. Blocked is never a pass |
| Blocked (exit 2) | the tool could not run: a required variable missing, port busy, an install step failing, a browser or runtime missing (say the install command, never install it), the app not ready within 60 s, an unknown scenario, a runner producing no readable result |
| Fail (exit 1) | the tool ran and something is wrong: a build, lint or test failure, any check failing |
| Combining steps | `check` runs every step even after one fails and prints each exit code. The result: any step blocked gives 2; else any step failing gives 1; else 0 |
| `check` | inside `$REPO`: install if missing, then lint, build and the repo's unit tests. Writes no evidence |
| `prove` | creates the evidence folder first, then: port free, installs present, a clean build, start the app on `$PORT`, wait until ready, drive the scenarios, write `result.json`, stop the app |
| Evidence | `$ORDERS/$ORDER/evidence/<station>-<YYYYMMDD-HHMMSS>/` (suffix `-2` on a clash), always with `result.json`, plus logs (`build.log`, `server.log`, the runner's own) and screenshots |
| `result.json` | `{"commit", "buildTime", "status": "pass" \| "fail" \| "blocked", "checks": [{"id", "pass", "detail"}], "reason"?, "serviceCommit"?}` (`serviceCommit`: the shared service's commit it tested against, when it uses one). Written on every exit. `blocked` or a failed build: `checks: []`, a `reason`, `buildTime: null` |
| Check ids | unique, prefixed by the smoke row they prove (`S4.renewal`); `--expect` texts become `expect.1`, `expect.2`… |
| Waits for a signal | a selector, a log line, a response, a probe. A fixed sleep only where no signal exists, with the reason |
| Safety | its own port, data and browser profile; kills only the processes it started (by PID) and their children, on any exit; never touches the owner's browser, dev server or accounts; read-only on shared services it doesn't own |
| Selftest | `--selftest` runs the tool's own logic on fake inputs, with no app, server or network: `check` its combining rule (`0 0 0`→0, `0 1 0`→1, `0 2 0`→2); `prove` its merge (a failing check→1, all pass→0, unreadable result→2) |

**Shared tools** (one driver several stations use, like a game driver the server station plays
rules with): one owner station, usually the one whose app it drives. Others run it and never edit
it; a missing feature goes under "Orders for other stations". It lives in its owner's `tools/`,
and `kitchen.md` lists it under Shared tools.

**Scenarios:** an order's one-off scenarios stay in `$ORDERS/<id>/scenarios/`. A scenario that proves
lasting behavior is promoted to `stations/<station>/tools/<tool>/scenarios/`, renamed by what it proves
(`bid-survives-reload`, not `0012-p3`). `retro` does the promotion.

**A new station** starts with no tools: its first ticket builds `check`, `prove` with a boot check
(it starts and answers with no error), the evidence layout and the safety rules. Other tools grow
order by order.

## Autonomy

| A station or the expediter just does it | Needs the owner's go |
| --- | --- |
| read, build, test, run its own check, start its own server on its own port | merge to `main`, any commit on `main`, push, release tag |
| at the pass, the expediter switches the owner's folder to `order/<NNNN>` and back, only when its working tree is clean (never stash or reset) | |
| commit on its feature branch (only files it owns) | production, deploy, anything outside this machine |
| change local dev data the ticket names | wipe or restore a database |
| the review, and fixing its findings | product or design choices no run can settle |
| choosing between two ways to build when running both settles it | |

A question whose answer can be observed by running something is not the owner's: run it.

## Rounds

- A verdict with "Act on" findings, or a failed ownership check, sends a **fresh** station run
  with the ticket, the plate and the verdict. Never resume an old run: resumed runs drop directives.
- **At most 2 fix rounds per ticket.** Still failing after round 2 means the ticket or the spec is
  wrong: the expediter stops and brings the owner a re-spec, not a round 3.
- Stuck station: no commit, plate change or new evidence for 30 minutes (60 during a long build):
  `ORDERS=$ORDERS $KITCHEN/scripts/watchdog.sh <station worktree> <id>` exits 2. Stop it, start a
  fresh run from ticket + plate, tell the owner.
- Pausing: one `chore(wip): <what>` commit, `plate.md` with `Status: paused` and a resume point.
  The next run treats ticket + plate as true and never redoes verified work.

## Big orders

- **Count the whole job first.** An order over many items gets `$ORDERS/<spec>-scope.json`, one row
  per item. Only the expediter writes it, moving rows up from the plates (one writer per file).
  Every progress update starts with the line `python3 $KITCHEN/scripts/scope.py` prints.
- **Wide first, then deep.** Pass 1 brings every item to the new baseline; pass 2 polishes group by
  group. Running out of time leaves less polish, never half the items untouched.
- **Merge per group** on the owner's go. No group waits days on a branch.

## Rule → what enforces it

Prefer a check over a sentence. When the owner corrects the same mistake twice, `retro` turns it
into a check and adds a row here.

| Rule | Enforced by |
| --- | --- |
| Stations write only their `Owns` | `scripts/ownership-check.py` before review; `scripts/test-ownership-check.sh` proves it on a real repo with a worktree, run from either side |
| The right kitchen loads in each folder | `scripts/test-session-start.sh` |
| Every station's repo is under its kitchen's root | `scripts/kitchen.py check <kitchen>`, run by `kitchen:setup` before its commit; selftest case from the 2026-11-05 setup bug (a sibling repo offered as a station) |
| Owner command defaults work on the owner's machine | grill line 15 checks each default is free; `expedite` runs each owner command once with no argument before the pass |
| The product never knows about the kitchen; owner commands need no argument | `agents/taster.md` and the verdict's "Kitchen leak" and "Owner commands" lenses; the expediter reads every product diff for kitchen terms before the review |
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
| A stalled station is replaced | `scripts/watchdog.sh` |
| A station tool can't pass while broken | each tool's `--selftest` |
| Tools prove through the user's door | tools live outside the repo (they can only reach the URL, port or command); reviewer checks scenarios |

## Writing style

The owner reads every report. Lead with the outcome. Plain words; a codebase term gets its meaning
the first time. Numbers, paths and commands exact, in tables or code blocks. One idea per sentence.
