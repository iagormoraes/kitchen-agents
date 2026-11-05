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
