#!/bin/sh
# Check of watch-orders.sh: one line for a stalled station, none for a fresh or finished one.
#   sh scripts/test-watch-orders.sh     # prints "ok"
set -e
kit=$(cd "$(dirname "$0")/.." && pwd)
t=$(mktemp -d); trap 'rm -rf "$t"' EXIT
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
root="$t/app"; home="$t/kitchens/app"; mkdir -p "$root" "$home/orders/0001-api" "$t/wt"
printf -- '- **Root:** `%s`\n' "$root" > "$home/kitchen.md"
cd "$t/wt"; git init -q; echo a > a.txt; git add .
GIT_AUTHOR_DATE="2026-01-01T00:00:00" GIT_COMMITTER_DATE="2026-01-01T00:00:00" git commit -qm old
printf -- '- **Worktree:** `%s`: your only working directory\n' "$t/wt" > "$home/orders/0001-api/ticket.md"
touch -t 202601010000 "$home/orders/0001-api/ticket.md"
run() { cd "$root" && KITCHENS="$t/kitchens" sh "$kit/scripts/watch-orders.sh" "$kit" --once; }
out=$(run); [ "$(echo "$out" | grep -c 'stalled')" = 1 ] || { echo "FAIL: stalled station not reported: $out"; exit 1; }
printf -- '- **Status:** done\n' > "$home/orders/0001-api/plate.md"
[ -z "$(run)" ] || { echo "FAIL: a finished station was reported"; exit 1; }
rm "$home/orders/0001-api/plate.md"; cd "$t/wt"; echo b >> a.txt; git commit -qam fresh
[ -z "$(run)" ] || { echo "FAIL: a fresh station was reported"; exit 1; }
cd "$t"; [ -z "$(KITCHENS="$t/kitchens" sh "$kit/scripts/watch-orders.sh" "$kit" --once)" ] || { echo "FAIL: reported outside any kitchen"; exit 1; }
echo ok
