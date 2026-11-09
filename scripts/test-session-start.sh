#!/bin/sh
# Check of session-start.sh: which kitchen a session gets. Run after changing the hook.
#   sh scripts/test-session-start.sh      # prints "ok", exit 1 on the first wrong case
set -e
kit=$(cd "$(dirname "$0")/.." && pwd)
t=$(mktemp -d); trap 'rm -rf "$t"' EXIT
mkdir -p "$t/kitchens/shop" "$t/kitchens/game" "$t/ws/web" "$t/ws/server/src" "$t/ws-x" "$t/other"
printf -- '- **Root:** `%s`\n\nmarker SHOP\n' "$t/ws/web" > "$t/kitchens/shop/kitchen.md"
printf -- '- **Root:** `%s/`\n\nmarker GAME\n' "$t/ws" > "$t/kitchens/game/kitchen.md"   # trailing / on purpose

expect() {  # <folder> <text the output must contain>
  out=$(CLAUDE_PROJECT_DIR=$1 CLAUDE_PLUGIN_ROOT=$kit KITCHENS=$t/kitchens sh "$kit/scripts/session-start.sh")
  case "$out" in *"$2"*) ;; *) echo "FAIL: $1 should give '$2'"; echo "$out" | head -3; exit 1 ;; esac
}
expect "$t/ws"            "marker GAME"        # workspace root
expect "$t/ws/server/src" "marker GAME"        # subfolder of the workspace
expect "$t/ws/web"        "marker SHOP"        # inner project with its own kitchen: longest root wins
expect "$t/ws-x"          "no kitchen covers"  # a sibling sharing a prefix is not inside
expect "$t/other"         "no kitchen covers"  # unrelated folder
expect "$t/ws"            "## Principles"      # the brief carries the principles
# a station still cooking is listed at session start (restart or compaction)
mkdir -p "$t/kitchens/game/orders/0004-web" "$t/wtc"; git -C "$t/wtc" init -q
printf -- '- **Worktree:** `%s`: your only working directory\n' "$t/wtc" > "$t/kitchens/game/orders/0004-web/ticket.md"
expect "$t/ws"            "0004-web: idle"
printf -- '- **Status:** done\n' > "$t/kitchens/game/orders/0004-web/plate.md"
out=$(CLAUDE_PROJECT_DIR=$t/ws CLAUDE_PLUGIN_ROOT=$kit KITCHENS=$t/kitchens sh "$kit/scripts/session-start.sh")
case "$out" in *"0004-web"*) echo "FAIL: a finished station was listed"; exit 1 ;; esac
echo ok
