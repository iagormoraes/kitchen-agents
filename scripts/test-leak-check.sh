#!/bin/sh
# Check of leak-check.py on a real repo. Run after changing it.   sh scripts/test-leak-check.sh -> "ok"
set -e
kit=$(cd "$(dirname "$0")/.." && pwd); chk="python3 -I $kit/scripts/leak-check.py"
t=$(mktemp -d); trap 'rm -rf "$t"' EXIT
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
cd "$t"; git init -q -b main; echo "# app" > README.md; git add .; git commit -qm init; base=$(git rev-parse HEAD)
expect() { set +e; $chk "$t" "$base" HEAD $2 >/dev/null 2>&1; got=$?; set -e; [ "$got" = "$1" ] || { echo "FAIL: $3 gave $got, want $1"; exit 1; }; }
echo "Counts are summed per hour." >> README.md; git commit -qam clean
expect 0 "" "clean product text"
echo "Run the station's check tool first." >> README.md; git commit -qam leak     # the adserver case
expect 1 "" "a station word in the docs"
expect 0 "--allow station" "the same word allowed as the product's domain"
git commit -q --allow-empty -m none; expect 1 "" "the hit stays visible on later commits"
# spec ids (the real pilot cases) and a whole-product scan that finds what an earlier change left
printf '| C7 | env | data |\n| D9 | every event is recorded | owner |\n' > "$t.spec"
base2=$(git rev-parse HEAD); echo "# Env (C7): DB_HOST" > env.src; git add .; git commit -qm env
set +e; $chk "$t" "$base2" HEAD --spec "$t.spec" >/dev/null 2>&1; got=$?; set -e; [ "$got" = 1 ] || { echo "FAIL: (C7) not found with --spec"; exit 1; }
base3=$(git rev-parse HEAD); echo "fine" > other.src; git add .; git commit -qm other
set +e; $chk "$t" "$base3" HEAD --spec "$t.spec" >/dev/null 2>&1; got=$?; set -e; [ "$got" = 0 ] || { echo "FAIL: a clean diff failed"; exit 1; }
set +e; $chk "$t" --all HEAD --spec "$t.spec" --allow station >/dev/null 2>&1; got=$?; set -e; [ "$got" = 1 ] || { echo "FAIL: --all missed the earlier (C7)"; exit 1; }
set +e; $chk "$t" --all HEAD --spec "$t.spec" --allow station --exclude 'env.src' >/dev/null 2>&1; got=$?; set -e; [ "$got" = 0 ] || { echo "FAIL: --exclude did not skip"; exit 1; }
rm -f "$t.spec"
set +e; $chk "$t" deadbeef HEAD >/dev/null 2>&1; got=$?; set -e; [ "$got" = 2 ] || { echo "FAIL: bad base gave $got, want 2"; exit 1; }
echo ok
