# Station <name>

<!-- The permanent half of a station. Agents come and go (one fresh agent per ticket); this file
     is what each of them knows on day one. Lives at $KITCHEN_HOME/stations/<name>/station.md, outside the codebase. Written by
     the expediter when the station is created; updated only by retro, on the owner's go.

     Rules:
     - One file, about 60 lines or less: every agent reads it in full.
     - Kitchen-facing facts only. How to write code in this repo (patterns, conventions,
       architecture) stays in the repo's own docs or CLAUDE.md, if it has any; link them, never copy them. Rules shared by
       all stations stay in the kitchen RULES.md.
     - A long craft checklist (for example "compare every window against the mock, line by line")
       goes in $KITCHEN_HOME/stations/<name>/<topic>.md, linked under Gotchas; the ticket says when to read it. -->

- **Repo:** `<absolute repo path>` (conventions: its `CLAUDE.md`)
- **Owns by default:** `<paths>` (a ticket may narrow this, never widen it)
- **Reads:** `<paths other stations own that this one depends on>`
- **Port range:** `<from>-<to>` (the ticket picks one)
- **Shared services it owns:** <local DB, a backend…, or "none">

## Contracts it owns

<Shapes other stations consume. This station never breaks one without a spec that says so;
mise-en-place makes its ticket block every consumer.>

| Contract | Where it is defined | Consumers |
| --- | --- | --- |
| <REST /api/users JSON> | `<file>` | <station> |

## Run

```bash
<start command, using $PORT>
```

- **Ready when:** <a check that proves it is usable, not just that a process answers>
- **Test data:** <seed command or fixture path, from an empty state>
- **Stop:** kill only the process you started (its PID), never by name.

## Its user and the door

- **User:** <who uses what this station builds: a player, a visitor, the client app, a terminal user>
- **Door:** <DOM · canvas · HTTP/packets · terminal · code> → **driver:** <Playwright · custom driver · requests · shell>
- **Did it stick:** <how a proof shows the state was kept: reload, relog, restart then read back>

## Tools (`$KITCHEN_HOME/stations/<name>/tools/`, its own git repo; contract in the kitchen RULES.md "Station tools")

```bash
REPO=<worktree> ORDERS=<path> ORDER=<id> PORT=<n> $KITCHEN_HOME/stations/<name>/tools/check
REPO=<worktree> ORDERS=<path> ORDER=<id> PORT=<n> $KITCHEN_HOME/stations/<name>/tools/prove [--expect "<text>"]… [<scenario>…]
```

| Tool | Folder | Proves | Level |
| --- | --- | --- | --- |
| <e2e> | `tools/e2e/` | <pages and flows in a real browser> | e2e-verified |

- **Shared tools it runs (owned elsewhere):** <tool: owner station, or "none">
- **Cannot reach:** <each thing, and why. These become 👤 rows>
- **Unit tests in the repo:** <the repo's own test command, which `check` runs>

## Gotchas

<Traps that cost past runs time. One line each, with the order that found it.>

- <gotcha> (`<order id>`)
