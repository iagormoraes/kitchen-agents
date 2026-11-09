# Kitchen

<!-- Lives at $KITCHEN_HOME/kitchen.md, outside the codebase. kitchen:setup writes it; the plugin's
     session-start hook loads it into every session started in the root. The paths (KITCHEN,
     KITCHEN_HOME, ORDERS, WORKTREES) come from the hook, so they are not repeated here. -->

- **Root:** `<absolute root path>` · **Kind:** project | workspace

## Repos

| Repo | Absolute path | Default branch |
| --- | --- | --- |
| <name> | `<path>` | `main` |

## Stations

| Station | Repo | Profile | Shared services it owns |
| --- | --- | --- | --- |
| <name> | <repo> | `stations/<name>/station.md` | <or "none"> |

## Shared tools

| Tool | Owner station | Path |
| --- | --- | --- |
| <name> | <station> | `<absolute path>` |

## Owner resources

<Everything the owner's own runs use, from the spec's Owner commands defaults: project or stack
names, data folders, databases, ports. Globs allowed. The guard hook refuses any destructive command
that names one of these, and every station tool's destructive step must refuse them too. The kitchen
never removes, wipes or resets them.>

- **Names:** `<the owner's project or stack name>`, `<its data volumes, for example name_*>`
- **Folders:** `<the owner's data folders>`
- **Ports:** `<the owner's default ports>`

## House rules

<This kitchen's own lessons, added by kitchen:retro (lessons that only add safety apply themselves; the rest on the owner's go). The session-start brief
loads this file, so every order of this kitchen follows them. Never copied into the plugin.>

- **Grill questions:** <one line each: the question that would have caught a past miss> or "none"
- **Spec fields:** <one line each: what every spec of this kitchen must also write down> or "none"
- **Checks:** <one line each: command (in a station's tools), what it fails on> or "none"
- **Leak check allows:** <words that are this product's own domain, for example `ticket`> or "none"
