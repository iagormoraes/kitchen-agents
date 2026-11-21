#!/bin/sh
# SessionStart hook of the kitchen plugin. Its stdout becomes context for the session.
# One machine holds many kitchens, one per workspace or project, all outside the codebases
# (the lookup lives in kitchen.py, shared with the owner guard):
#   ${KITCHENS:-~/.claude/kitchens}/<name>/kitchen.md   with a line   - **Root:** `<absolute path>`
# The session belongs to the kitchen whose root is the longest match for its folder, so a session
# started in a subfolder of a workspace still gets the workspace's kitchen.
# Match: print a short brief (paths, the principles, kitchen.md). No match: one line offering
# kitchen:setup. It writes nothing but one thing: the leftovers of orders already merged (evidence,
# logs, media, worktrees) are removed from the kitchen home (handoff.py clean). Output stays small:
# session-start context is cut when long.
dir=${CLAUDE_PROJECT_DIR:-$PWD}
kit=${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}
base=${KITCHENS:-$HOME/.claude/kitchens}

found=$(KITCHENS=$base python3 -I "$kit/scripts/kitchen.py" find "$dir")
best=${found%%	*}; best_root=${found#*	}

if [ -z "$best" ]; then
  echo "Kitchen plugin: no kitchen covers $dir. When the owner brings a plan to build with stations, offer the kitchen:setup skill (kitchens live in $base)."
  exit 0
fi
# The real path: a kitchens folder behind a symlink still gives every tool the folder it writes to.
best=$(cd "$best" && pwd -P)

cat <<INFO
# Kitchen "$(basename "$best")" loaded for this session

| Name | Absolute path |
| --- | --- |
| ROOT | \`$best_root\` |
| KITCHEN | \`$kit\` |
| KITCHEN_HOME | \`$best\` |
| ORDERS | \`$best/orders\` |
| WORKTREES | \`$best/worktrees\` |

Before any kitchen step (grill, spec, tickets, dispatch, review, retro), read the full rules in
\`$kit/RULES.md\`. They are not loaded here: they are too long for the session start.

INFO
# The principles apply to every change, even small work done without a kitchen skill. Taken from
# the rules file itself, so there is one source: from "## Principles" up to the next "## ".
awk '/^## Principles/{on=1; print; next} on && /^## /{exit} on' "$kit/RULES.md"
echo
cat "$best/kitchen.md"

# Stations still cooking: after a restart or a compaction the expediter may not know them anymore.
cooking=$(python3 -I "$kit/scripts/kitchen.py" cooking "$best" | head -5)
if [ -n "$cooking" ]; then
  echo
  echo "## Stations still cooking (a restart or compaction may have stopped them)"
  echo "$cooking" | while IFS='	' read -r id wt; do
    idle=$(ORDERS="$best/orders" sh "$kit/scripts/watchdog.sh" "$wt" "$id" 2>/dev/null)
    echo "- $idle. Over the limit: start a fresh run from its ticket and plate (expedite §2)."
  done
fi

# Orders handed off but not yet in their home branch: the project's own flow ships them (push,
# PR, merge); a new order overlapping one of them stacks on it (RULES.md "Handoff").
cleaned=$(python3 -I "$kit/scripts/handoff.py" clean "$best" 2>/dev/null | head -5)
if [ -n "$cleaned" ]; then
  echo
  echo "## Merged orders cleaned (evidence, logs, media, worktrees removed; paperwork kept)"
  echo "$cleaned"
fi
open=$(python3 -I "$kit/scripts/handoff.py" open "$best" 2>/dev/null | head -5)
if [ -n "$open" ]; then
  echo
  echo "## Handed off, not yet in the home branch (the project's own flow ships these)"
  echo "$open"
fi
