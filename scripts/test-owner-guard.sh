#!/bin/sh
# Check of the owner guard as Claude Code calls it: hook JSON on stdin, decision JSON on stdout.
#   sh scripts/test-owner-guard.sh      # prints "ok", exit 1 on the first wrong case
set -e
kit=$(cd "$(dirname "$0")/.." && pwd)
t=$(mktemp -d); trap 'rm -rf "$t"' EXIT
repo="$t/app"; home="$t/kitchens/app"; o="$home/orders/0002-owner"
mkdir -p "$repo/src/lib" "$o" "$t/other"
printf -- '- **Root:** `%s`\n' "$repo" > "$home/kitchen.md"
printf -- '- **Station:** owner\n- **Repo:** `%s`\n- **Owns (may write):** `src/lib/`, `!src/**/*.test.ts`\n' "$repo" > "$o/ticket.md"

expect() {  # <deny|allow> <tool> <path> [cwd]
  out=$(printf '{"tool_name":"%s","tool_input":{"file_path":"%s"},"cwd":"%s"}' "$2" "$3" "${4:-$repo}" |
        KITCHENS="$t/kitchens" python3 -I "$kit/scripts/kitchen.py" guard)
  case "$1:$out" in deny:*'"deny"'*|allow:) ;; *) echo "FAIL: $2 $3 want $1, got: $out"; exit 1 ;; esac
}
expect deny  Edit  "$repo/src/lib/store.ts"
expect deny  Write "src/lib/new.ts"                    # relative path, resolved from cwd
expect deny  MultiEdit "$repo/src/lib/store.ts"
expect allow Edit  "$repo/src/lib/store.test.ts"       # the sous-chef's tests
expect allow Write "$repo/src/app/page.tsx"            # an agent station's or nobody's path
expect allow Read  "$repo/src/lib/store.ts"            # reading is always fine
expect allow Edit  "$t/other/x.ts" "$t/other"          # no kitchen covers it
touch "$o/takeover";  expect allow Edit "$repo/src/lib/store.ts"; rm "$o/takeover"
printf -- '- **Status:** done\n' > "$o/plate.md"; expect allow Edit "$repo/src/lib/store.ts"; rm "$o/plate.md"
# a broken hook input never blocks
out=$(echo 'not json' | KITCHENS="$t/kitchens" python3 -I "$kit/scripts/kitchen.py" guard); [ -z "$out" ] || { echo "FAIL: bad input blocked"; exit 1; }
echo ok
