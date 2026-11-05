---
name: setup
description: Create a kitchen for the project or workspace this session runs in, outside the codebase, so the owner can open Claude and start producing with stations. Use when the session-start brief says no kitchen covers this folder and the owner brings a plan, or when the owner says "set up the kitchen".
---

The codebase is never touched: no file in any repo, no line in any `CLAUDE.md`, nothing in `.claude/`.
Read `$KITCHEN/CLAUDE.md` "Zero footprint" first (the path is in the session-start brief).

## 1. Find the root

The root is the folder the kitchen serves, decided **from the filesystem only**, never from what
the conversation was about (an earlier task in this session says nothing about which repos belong
together).

- **The session's folder is a repo, or a workspace** (a folder whose subfolders are the repos of
  one product, often with a shared `CLAUDE.md` or a shared run setup): that folder is the root.
- **It sits inside a workspace** (a repo whose parent is such a workspace): recommend the
  workspace folder. A kitchen per workspace, not per repo, unless the owner wants a project kitchen.
- **It is a folder of unrelated projects** (like `~/projects` or `~/code`: separate
  repos and workspaces for different products): it is never a root. List the candidates you see
  there and ask which one, in the decision round.

## 2. Look at the root (facts, no questions)

- **Kind:** the root is a git repo = project; it holds git repos as subfolders = workspace.
- **Repos:** only the git repos **under the root**, each with its path and default branch
  (`git -C <repo> symbolic-ref refs/remotes/origin/HEAD`, else the current branch). A repo outside
  the root is never a station, even when the plan touches it: the hook finds a kitchen by the
  session's folder, so a session opened in that repo would never load this kitchen. It gets its
  own kitchen, or the owner moves the root up to a folder that holds both.
- For each repo, with a fresh read-only `Explore` subagent: stack, build, lint and test commands, how
  it runs locally, its user and door (kitchen CLAUDE.md "Station tools"), local services it needs.

## 3. One decision round with the owner

Always ask it, also in a headless session: send the round and end your turn. Never pick these
defaults yourself; they are the owner's. With your recommendation for each:

- the root (step 1) and the **kitchen name** (default: the root's folder name; must not exist yet
  in `${KITCHENS:-~/.claude/kitchens}/`),
- the station list (name, repo or module, default `Owns`), which station owns each shared service,
  and the port range per station. One station per repo is the usual start; split a repo into
  modules only where two areas really cook apart.

## 4. Write the kitchen

```bash
H=${KITCHENS:-$HOME/.claude/kitchens}/<name>
mkdir -p "$H"/specs/research "$H"/orders "$H"/worktrees
git -C "$H" init -q && printf 'orders/\nworktrees/\nstations/*/tools/\n' > "$H/.gitignore"
# per station:
mkdir -p "$H/stations/<station>/tools" && git -C "$H/stations/<station>/tools" init -q
```

- `$H/kitchen.md` from `$KITCHEN/templates/kitchen.md`, every field filled. It keeps the line
  `- **Root:** \`<absolute root path>\``: the hook finds the kitchen by it.
- `$H/stations/<station>/station.md` per station from `$KITCHEN/templates/station.md`, filled from
  step 2. A tool the station doesn't have yet goes under "Cannot reach"; its first ticket builds it.
- Commit in the kitchen repo: `chore(kitchen): set up the <name> kitchen`.

## 5. Check and hand over

- `python3 -I $KITCHEN/scripts/kitchen.py check $H` passes: every repo in `kitchen.md` is under the
  root. Run it **before** the setup commit; a failure means step 1 or 2 is wrong, not the check.
- `CLAUDE_PROJECT_DIR=<root> sh $KITCHEN/scripts/session-start.sh | head -3` names this kitchen.
- Tell the owner the kitchen path, the stations, and what each can prove today. The hook loads the
  kitchen in every new session in the root or below it. In this session, continue with `grill`.
