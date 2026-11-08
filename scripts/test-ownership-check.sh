#!/bin/sh
# Check of ownership-check.py on a real repo with a worktree. Run after changing the script.
#   sh scripts/test-ownership-check.sh     # prints "ok", exit 1 on the first wrong case
# The worktree cases come from pilot 2: Owns named the worktree and the check ran on the main repo.
set -e
kit=$(cd "$(dirname "$0")/.." && pwd); chk="python3 $kit/scripts/ownership-check.py"
t=$(mktemp -d); trap 'rm -rf "$t"' EXIT
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
mkdir -p "$t/repo/app" "$t/repo/lib"; cd "$t/repo"; git init -q
echo a > app/a.txt; echo l > lib/l.txt; git add .; git commit -qm init; base=$(git rev-parse HEAD)
git worktree add -q "$t/wt/0001/repo" -b feat/x "$base"
cd "$t/wt/0001/repo"; echo b >> app/a.txt; echo m >> lib/l.txt; git commit -qam change
R=$(cd "$t/repo" && pwd -P); W=$(cd "$t/wt/0001/repo" && pwd -P)

expect() {  # <exit code> <owns line tokens> <repo dir> <ref>
  printf -- '- **Owns (may write):** %s\n' "$2" > "$t/ticket.md"
  set +e; $chk "$t/ticket.md" "$3" "$base" "$4" >/dev/null; got=$?; set -e
  [ "$got" = "$1" ] || { echo "FAIL: owns $2 on $3 gave $got, want $1"; exit 1; }
}
expect 0 "\`$W/\`"     "$R" feat/x   # Owns = whole worktree, run on the main repo (pilot 2)
expect 1 "\`$W/app/\`" "$R" feat/x   # worktree app/ only, run on the main repo: lib/ is stray
expect 1 "\`$W/app/\`" "$W" HEAD     # same, run on the worktree
expect 0 "\`$R/\`"     "$W" HEAD     # Owns = main checkout, run on the worktree
expect 1 "\`app/\`"    "$W" HEAD     # relative Owns: lib/ is stray
expect 0 "\`app/\`, \`lib/\`, \`/elsewhere/tools/\`" "$W" HEAD   # a path outside the repo is ignored
expect 1 "\`app/\`, \`lib/\`, \`!lib/l.txt\`" "$W" HEAD   # !path excludes a file inside an owned folder
expect 2 "\`app/**\` (except \`lib/l.txt\`)" "$W" HEAD   # prose exclusion (pilot line): refused, exit 2

# Empty repo (pilot B2): main has no commit; the station's orphan worktree has one.
mkdir -p "$t/empty"; cd "$t/empty"; git init -q -b main
git worktree add -q --orphan -b feat/0001-app "$t/wt2/0001/empty"
cd "$t/wt2/0001/empty"; echo x > a.txt; git add .; git commit -qm first
E=$(cd "$t/empty" && pwd -P)
printf -- '- **Branch:** `feat/0001-app`\n- **Owns (may write):** `%s/`\n' "$E" > "$t/ticket.md"
set +e; $chk "$t/ticket.md" "$E" 4b825dc642cb6eb9a060e54bf8d69288fbee4904 >/dev/null; got=$?; set -e
[ "$got" = 0 ] || { echo "FAIL: empty repo gave $got, want 0"; exit 1; }
echo ok
