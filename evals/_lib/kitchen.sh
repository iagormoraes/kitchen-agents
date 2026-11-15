# Shared fixture for the kitchen evals: sourced by each case's setup.sh, run in the empty workspace.
# Builds a workspace with one repo (shop) and its kitchen. The kitchen's real folder is
# ./.kitchens/shop inside the workspace (the run may only write there); the session-start hook finds it
# through $HOME/.claude/kitchens/shop, a symlink.
set -euo pipefail
export GIT_AUTHOR_NAME=owner GIT_AUTHOR_EMAIL=owner@example.invalid
export GIT_COMMITTER_NAME=owner GIT_COMMITTER_EMAIL=owner@example.invalid
ROOT=$(pwd -P)
K=$ROOT/.kitchens/shop
REPO=$ROOT/shop
KITCHEN_KIT=$(cd "$(dirname "$0")/../.." && pwd -P)   # this plugin: the case dir is evals/<case>/

g() { git -C "$REPO" "$@"; }
put() { mkdir -p "$(dirname "$1")"; cat > "$1"; }

kitchen() {
  mkdir -p "$K"/specs "$K"/orders "$K"/worktrees "$HOME/.claude/kitchens"
  ln -s "$K" "$HOME/.claude/kitchens/shop"
  git init -q -b main "$REPO"
  put "$REPO/package.json" <<'EOF'
{ "name": "shop", "private": true, "scripts": { "dev": "node src/server.js", "test": "node --test", "e2e": "node e2e/run.mjs" } }
EOF
  put "$REPO/src/server.js" <<'EOF'
import { createServer } from "node:http";
createServer((req, res) => res.end("shop")).listen(process.env.PORT || 3000);
EOF
  put "$REPO/src/cart.js" <<'EOF'
export const total = (items) => items.reduce((sum, i) => sum + i.price * i.qty, 0);
EOF
  put "$REPO/e2e/package.json" <<'EOF'
{ "name": "shop-e2e", "private": true, "type": "module" }
EOF
  put "$REPO/e2e/run.mjs" <<'EOF'
// Runs every scenario in ./scenarios against the shop on --port; writes --out/results.json.
console.log("e2e: 0 scenarios");
EOF
  put "$REPO/e2e/driver/browser.mjs" <<'EOF'
export async function open(port, path = "/") { return (await fetch(`http://localhost:${port}${path}`)).text(); }
EOF
  put "$REPO/e2e/scenarios/home-page.mjs" <<'EOF'
import { open } from "../driver/browser.mjs";
export default async (port) => (await open(port)).includes("shop");
EOF
  g add -A && g commit -qm "Shop server and its e2e suite"

  put "$K/kitchen.md" <<EOF
# Kitchen

- **Root:** \`$ROOT\` · **Kind:** workspace

## Repos

| Repo | Absolute path | Default branch |
| --- | --- | --- |
| shop | \`$REPO\` | \`main\` |

## Stations

| Station | Repo | Profile | Shared services it owns |
| --- | --- | --- | --- |
| web | shop | \`stations/web/station.md\` | none |

## Shared tools

| Driver | Owner station | Path |
| --- | --- | --- |
| browser | web | \`$REPO/e2e/driver/\` |

## Owner resources

- **Names:** \`shop\`
- **Folders:** \`$REPO/data\`
- **Ports:** \`3000\`

## House rules

- **Grill questions:** none
- **Spec fields:** none
- **Checks:** none
- **Leak check allows:** none
EOF
  mkdir -p "$K/stations/web/tools"
  put "$K/stations/web/station.md" <<EOF
# Station web

- **Repo:** \`$REPO\`
- **Owns by default:** \`src/\`, \`e2e/\`
- **Port range:** \`4100-4199\`
- **Shared services it owns:** none

## The e2e suite

- **Suite:** \`$REPO/e2e/\` · run: \`npm run e2e\`
- **Driver:** \`e2e/driver/\` · owner: web · video: no

## Harness (\`$K/stations/web/tools/\`, its own git repo)

\`\`\`bash
REPO=<worktree> ORDERS=$K/orders ORDER=<id> PORT=<n> $K/stations/web/tools/check
REPO=<worktree> ORDERS=$K/orders ORDER=<id> PORT=<n> $K/stations/web/tools/prove [--row <row>=<scenario>]… [--all]
\`\`\`
EOF
  for t in check prove; do
    printf '#!/bin/sh\necho "%s: ok"\n' "$t" > "$K/stations/web/tools/$t"; chmod +x "$K/stations/web/tools/$t"
  done
  git -C "$K/stations/web/tools" init -q -b main && git -C "$K/stations/web/tools" add -A && git -C "$K/stations/web/tools" commit -qm tools
  git -C "$K" init -q -b main
  printf 'orders/\nworktrees/\nstations/*/tools/\n' > "$K/.gitignore"
}

# spec NNNN slug "goal"
spec() {
  put "$K/specs/$1-$2.md" <<EOF
# $1 $2

- **Status:** approved
- **Goal:** $3

## Smoke

| Id | Kind | Steps | Result |
| --- | --- | --- | --- |
| S1 | 🤖 | $3 | works |
EOF
  git -C "$K" add -A && git -C "$K" commit -qm "spec $1" >/dev/null
}

# ticket id owns-line base   (writes $K/orders/<id>/ticket.md)
ticket() {
  put "$K/orders/$1/ticket.md" <<EOF
# Ticket $1

- **Station:** web. Profile: \`$K/stations/web/station.md\`
- **Repo:** \`$REPO\`
- **Worktree:** \`$K/worktrees/$1/shop\`
- **Branch:** \`feat/$1\` from base \`$3\`
- **Orders:** \`$K/orders\`
- **Kitchen:** \`$KITCHEN_KIT\`
- **Port:** \`4101\`
- **Spec:** \`$(ls "$K"/specs/"${1%%-*}"-*.md)\`
- **Specs folder:** \`$K/specs/\` · **Leak check:** none
- **Blocked by:** none

## Scope

- **Owns (may write):** $2
EOF
}

# a station branch feat/<id>-web from main with the given files already cooked, plate done
cooked() {
  local id=$1; shift
  g switch -q -c "feat/$id" main
  while [ $# -gt 0 ]; do put "$REPO/$1" <<<"$2"; shift 2; done
  g add -A && g commit -qm "Cooked $id" && g switch -q main
  put "$K/orders/$id/plate.md" <<EOF
# Plate $id

- **Status:** done
- **Branch:** \`feat/$id\` @ \`$(g rev-parse "feat/$id")\`
EOF
}
