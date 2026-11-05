#!/usr/bin/env python3
"""Kitchen lookup and the owner guard, shared by the plugin's hooks.

    kitchen.py find <dir>     print "<kitchen home>\\t<root>" of the kitchen covering <dir>; exit 1 if none
    kitchen.py check <home>   exit 1 when a repo in <home>/kitchen.md lies outside its Root (every
                              station's repo must be under the root, or the hook never finds the kitchen)
    kitchen.py guard          PreToolUse hook: stdin is the hook JSON. Denies Edit/Write/MultiEdit/
                              NotebookEdit on a path an active owner ticket owns (the owner cooks it)
    kitchen.py --selftest

Kitchens live in ${KITCHENS:-~/.claude/kitchens}/<name>/kitchen.md, each with a line
`- **Root:** \\`<absolute path>\\``. A folder belongs to the kitchen whose root is the longest match.
An owner ticket is `$KITCHEN_HOME/orders/<id>/ticket.md` with `**Station:** owner`; it is active until
its plate says `**Status:** done`, and it stops guarding when `$ORDERS/<id>/takeover` exists (the
owner said "take over"). Its Owns are read by ownership-check.py's parser: relative paths are
under the ticket's `**Repo:**`, `!path` tokens are exclusions (the test files the sous-chef writes).
"""
import glob
import importlib.util
import json
import os
import re
import sys

sys.dont_write_bytecode = True   # importing ownership-check.py must not leave a __pycache__ behind
HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("ownership_check", os.path.join(HERE, "ownership-check.py"))
oc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(oc)


def find_kitchen(folder, base=None):
    base = base or os.environ.get("KITCHENS") or os.path.expanduser("~/.claude/kitchens")
    folder = os.path.realpath(folder).rstrip("/") + "/"
    best = (None, "")
    for md in glob.glob(os.path.join(base, "*", "kitchen.md")):
        m = re.search(r"^- \*\*Root:\*\* `([^`]*)`", open(md).read(), re.M)
        if not m:
            continue
        root = os.path.realpath(m.group(1)).rstrip("/")
        if folder.startswith(root + "/") and len(root) > len(best[1]):
            best = (os.path.dirname(md), root)
    return best if best[0] else None


def repos_outside_root(home):
    """Absolute repo paths in kitchen.md's Repos table that are not under its Root."""
    text = open(os.path.join(home, "kitchen.md")).read()
    m = re.search(r"^- \*\*Root:\*\* `([^`]*)`", text, re.M)
    if not m:
        return ["(no Root line)"]
    root = os.path.realpath(m.group(1)).rstrip("/")
    section = text.split("## Repos", 1)[1].split("\n## ", 1)[0] if "## Repos" in text else ""
    paths = [p for p in re.findall(r"`(/[^`]+)`", section)]
    return [p for p in paths if not (os.path.realpath(p).rstrip("/") + "/").startswith(root + "/")]


def active_owner_tickets(home):
    """Yield (order id, repo root, owned patterns, excluded patterns) for each owner ticket cooking."""
    for t in sorted(glob.glob(os.path.join(home, "orders", "*", "ticket.md"))):
        order = os.path.dirname(t)
        text = open(t).read()
        if not re.search(r"\*\*Station:\*\*\s*`?owner\b", text):
            continue
        plate = os.path.join(order, "plate.md")
        if os.path.exists(plate) and re.search(r"\*\*Status:\*\*\s*done", open(plate).read()):
            continue
        if os.path.exists(os.path.join(order, "takeover")):
            continue
        repo = re.search(r"\*\*Repo:\*\*\s*`([^`]+)`", text)
        if not repo:
            continue
        try:
            owns, excl = oc.owns_from_ticket(text)
        except SystemExit:
            continue
        yield os.path.basename(order), os.path.realpath(repo.group(1)), owns, excl


def owner_path(home, path):
    """The order id whose owner ticket owns <path>, or None."""
    path = os.path.realpath(path)
    for order, repo, owns, excl in active_owner_tickets(home):
        if not (path + "/").startswith(repo + "/"):
            continue
        rel = os.path.relpath(path, repo)
        if oc.owned(rel, oc.relative_to_repo(owns, repo)) and not oc.owned(rel, oc.relative_to_repo(excl, repo)):
            return order
    return None


def guard(event):
    if event.get("tool_name") not in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        return None
    ti = event.get("tool_input") or {}
    path = ti.get("file_path") or ti.get("notebook_path")
    if not path:
        return None
    path = os.path.join(event.get("cwd") or os.getcwd(), path)
    k = find_kitchen(os.path.dirname(path)) or find_kitchen(event.get("cwd") or os.getcwd())
    if not k:
        return None
    order = owner_path(k[0], path)
    if not order:
        return None
    return {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            f"{path} is the owner's to cook (owner ticket {order}). Don't write it: point the owner "
            "to the file and the concept (kitchen:line). Only on the owner's own words \"take over\" "
            f"create {k[0]}/orders/{order}/takeover and log it in the plate."),
    }}


def selftest():
    import tempfile
    t = tempfile.mkdtemp()
    base, repo = os.path.join(t, "kitchens"), os.path.join(t, "app")
    home = os.path.join(base, "app")
    os.makedirs(os.path.join(home, "orders", "0002-owner"))
    os.makedirs(os.path.join(repo, "src", "lib"))
    open(os.path.join(home, "kitchen.md"), "w").write(f"- **Root:** `{repo}`\n")
    ticket = os.path.join(home, "orders", "0002-owner", "ticket.md")
    open(ticket, "w").write(f"- **Station:** owner\n- **Repo:** `{repo}`\n"
                            "- **Owns (may write):** `src/lib/`, `!src/**/*.test.ts`\n")
    os.environ["KITCHENS"] = base
    ev = lambda p: {"tool_name": "Edit", "tool_input": {"file_path": os.path.join(repo, p)}, "cwd": repo}
    assert find_kitchen(os.path.join(repo, "src"))[0] == home
    assert guard(ev("src/lib/store.ts"))["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert guard(ev("src/lib/store.test.ts")) is None          # tests are the sous-chef's
    assert guard(ev("src/app/page.tsx")) is None               # not in the owner's Owns
    assert guard({"tool_name": "Read", "tool_input": {"file_path": os.path.join(repo, "src/lib/a.ts")}}) is None
    open(os.path.join(home, "orders", "0002-owner", "takeover"), "w").close()
    assert guard(ev("src/lib/store.ts")) is None               # owner said "take over"
    os.remove(os.path.join(home, "orders", "0002-owner", "takeover"))
    open(os.path.join(home, "orders", "0002-owner", "plate.md"), "w").write("- **Status:** done\n")
    assert guard(ev("src/lib/store.ts")) is None               # ticket finished
    # check: the real setup bug, a sibling repo offered as a station of another workspace's kitchen
    ws, other = os.path.join(t, "code", "acme"), os.path.join(t, "code", "billing-lib")
    k2 = os.path.join(t, "k2"); os.makedirs(k2)
    open(os.path.join(k2, "kitchen.md"), "w").write(
        f"- **Root:** `{ws}` · **Kind:** workspace\n\n## Repos\n\n| Repo | Absolute path | Default branch |\n"
        f"| --- | --- | --- |\n| web | `{ws}/web` | `main` |\n| billing-lib | `{other}` | `main` |\n\n## Stations\n")
    assert repos_outside_root(k2) == [other], repos_outside_root(k2)
    open(os.path.join(k2, "kitchen.md"), "w").write(
        f"- **Root:** `{ws}`\n\n## Repos\n\n| web | `{ws}/web` | `main` |\n")
    assert repos_outside_root(k2) == []
    print("selftest ok")


def main(argv):
    if argv[1:] == ["--selftest"]:
        return selftest()
    if len(argv) == 3 and argv[1] == "find":
        k = find_kitchen(argv[2])
        if not k:
            return 1
        print(f"{k[0]}\t{k[1]}")
        return 0
    if len(argv) == 3 and argv[1] == "check":
        bad = repos_outside_root(argv[2])
        for p in bad:
            print(f"repo outside the kitchen's Root: {p}")
        print("kitchen check: " + ("fail" if bad else "ok"))
        return 1 if bad else 0
    if argv[1:] == ["guard"]:
        try:
            out = guard(json.load(sys.stdin))
        except Exception:
            return 0          # a broken guard must never block every edit
        if out:
            print(json.dumps(out))
        return 0
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv))
