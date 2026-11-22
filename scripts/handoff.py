#!/usr/bin/env python3
"""Pick the base a new order cooks from, so orders handed off but not merged never collide.

    python3 handoff.py base <repo> <home branch> <ORDERS> <ticket.md>...
    python3 handoff.py landed <repo> <home branch> <branch>
    python3 handoff.py open <KITCHEN_HOME>
    python3 handoff.py clean <KITCHEN_HOME> [<NNNN>]
    python3 handoff.py --selftest

The kitchen hands each order off as one product-named branch with one commit, and the project
decides when to push or merge it. Each handoff is recorded in `$ORDERS/<NNNN>-handoff/<repo
name>/branch` (one line: the branch name). `base` reads those records for this repo, skips the
branches already in the home branch, and compares what each open one changed with the Owns of the
new order's tickets:

- no overlap: prints the home branch (cook in parallel, merge in any order);
- overlap with branches that build on one another: prints the newest (stack on it);
- overlap with two branches where neither builds on the other: exit 3, the order waits until one
  of them lands.

`open` lists every handoff of the kitchen not yet in its repo's home branch (the Repos table of
kitchen.md gives each repo's path and home branch), one line each:
`- <repo>: <branch> on <base> · <summary path> · tasted: <verdict>`. The session-start brief
prints it, so a new session knows what waits to be shipped. A record whose repo or branch is gone
is skipped.

The kitchen hands off before the pass, so the owner's verdict comes later, in
`$ORDERS/<NNNN>-handoff/tasted` (one word): `approved`, `changes` (the handoff stays open and the
next order stacks on it), `rejected`, or `none` (nothing to taste). No file yet: `waiting`. A
rejected handoff is no longer open: `open` and `base` skip it, so nothing stacks on it.

`clean` removes what a delivered order leaves behind, once every handoff of the order is in its
home branch: each `evidence/` and `scenarios/` folder and every log, image, video or archive
under `$ORDERS/<NNNN>-*/`, and the order's worktrees under `worktrees/<NNNN>*` (a worktree with
uncommitted changes is kept and named). The paperwork stays (tickets, plates, verdicts, gates,
summaries: small, and retros read them). `$ORDERS/<NNNN>-handoff/cleaned` marks it done. With
`<NNNN>` it cleans that order now, landed or not (a rejected order). The session-start hook runs
it, so an order is cleaned in the first session after its merge.

A handoff records its commit in `.../<repo name>/commit` too: a project that deletes the branch
on merge (`gh pr merge -d`) leaves the commit, so landing is still seen.

`landed` exits 0 when the branch's change is in the home branch, 1 when not. A squash merge keeps
a one-commit branch's patch, so `git cherry` sees it even though the commit ids differ.
Exit 2: bad usage or git failed.
"""
import glob
import importlib.util
import os
import subprocess
import sys

_spec = importlib.util.spec_from_file_location(
    "ownership_check", os.path.join(os.path.dirname(os.path.abspath(__file__)), "ownership-check.py"))
oc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(oc)


def git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], check=True, capture_output=True, text=True).stdout


def repo_name(repo):
    common = os.path.realpath(os.path.join(repo, git(repo, "rev-parse", "--git-common-dir").strip()))
    return os.path.basename(os.path.dirname(common))


def landed(repo, home, branch):
    return not any(l.startswith("+") for l in git(repo, "cherry", home, branch).splitlines())


def owns_of(repo, tickets):
    roots = {os.path.realpath(l[len("worktree "):])
             for l in git(repo, "worktree", "list", "--porcelain").splitlines() if l.startswith("worktree ")}
    owns, excl = [], []
    for t in tickets:
        o, e = oc.owns_from_ticket(open(t).read())
        owns += [p for r in roots for p in oc.relative_to_repo(o, r)]
        excl += [p for r in roots for p in oc.relative_to_repo(e, r)]
    return owns, excl


def tasted(order_folder):
    """The owner's verdict on a handoff: approved, changes, rejected, none, or waiting."""
    f = os.path.join(order_folder, "tasted")
    return (open(f).read().strip() or "waiting") if os.path.exists(f) else "waiting"


def pick_base(repo, home, orders, tickets):
    """('home' or branch, []) or (None, [the branches that block it])."""
    owns, excl = owns_of(repo, tickets)
    name = repo_name(repo)
    open_branches = []
    for rec in sorted(glob.glob(os.path.join(orders, "*-handoff", name, "branch"))):
        b = open(rec).read().strip()
        if b and tasted(os.path.dirname(os.path.dirname(rec))) != "rejected" and not landed(repo, home, b):
            open_branches.append(b)
    hit = [b for b in open_branches
           if any(oc.owned(p, owns) and not oc.owned(p, excl)
                  for p in git(repo, "diff", "--name-only", "--no-renames", f"{home}...{b}").split())]
    if not hit:
        return home, []
    tip = next((t for t in hit if all(
        subprocess.run(["git", "-C", repo, "merge-base", "--is-ancestor", b, t]).returncode == 0 for b in hit)), None)
    return (tip, []) if tip else (None, hit)


def repos_of(home):
    """{repo name or folder name: (name, path, home branch)} from kitchen.md's Repos table."""
    import re
    repos = {}
    for m in re.finditer(r"^\|\s*([^|`]+?)\s*\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|", open(os.path.join(home, "kitchen.md")).read(), re.M):
        repos[m.group(1)] = repos[os.path.basename(m.group(2).rstrip("/"))] = (m.group(1), m.group(2), m.group(3))
    return repos


def record_landed(folder, path, branch_home):
    """True / False for one handoff record, None when neither its branch nor its commit is there."""
    for name in ("branch", "commit"):
        f = os.path.join(folder, name)
        ref = open(f).read().strip() if os.path.exists(f) else ""
        if ref:
            try:
                return landed(path, branch_home, ref)
            except subprocess.CalledProcessError:
                continue
    return None


LEFTOVER_DIRS = {"evidence", "scenarios"}
LEFTOVER_EXT = (".log", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".mp4", ".mov", ".webm", ".gz", ".zip")


def clean_order(home, number):
    """Remove one order's leftovers; returns a summary line, or None when there was nothing."""
    import shutil
    files = size = 0
    for folder in glob.glob(os.path.join(home, "orders", f"{number}-*")):
        for d, dirs, names in os.walk(folder, topdown=True):
            for x in [x for x in dirs if x in LEFTOVER_DIRS]:
                for dd, _, nn in os.walk(os.path.join(d, x)):
                    files += len(nn); size += sum(os.path.getsize(os.path.join(dd, n)) for n in nn)
                shutil.rmtree(os.path.join(d, x)); dirs.remove(x)
            for n in names:
                if n.lower().endswith(LEFTOVER_EXT):
                    size += os.path.getsize(os.path.join(d, n)); files += 1; os.remove(os.path.join(d, n))
    kept, removed = [], 0
    for wt_root in glob.glob(os.path.join(home, "worktrees", f"{number}*")):
        for gitfile in glob.glob(os.path.join(wt_root, "*", ".git")):
            wt = os.path.dirname(gitfile)
            try:
                common = git(wt, "rev-parse", "--git-common-dir").strip()
                main_repo = os.path.dirname(os.path.realpath(os.path.join(wt, common)))
                git(main_repo, "worktree", "remove", wt); removed += 1
            except subprocess.CalledProcessError:
                kept.append(wt)
        for d, _, _ in sorted(os.walk(wt_root), key=lambda w: -len(w[0])):
            if not os.listdir(d):
                os.rmdir(d)
    if not (files or removed or kept):
        return None
    line = f"- order {number}: removed {files} file(s) ({size / 1e6:.1f} MB), {removed} worktree(s)"
    return line + (f"; kept {len(kept)} with uncommitted changes: " + ", ".join(kept) if kept else "")


def clean(home, number=None):
    """Clean every delivered order not yet cleaned (or just `number`). Returns the summary lines."""
    import time
    out = []
    if number:
        numbers = [number]
    else:
        repos, numbers = repos_of(home), []
        for folder in sorted(glob.glob(os.path.join(home, "orders", "*-handoff"))):
            records = [r for r in glob.glob(os.path.join(folder, "*")) if os.path.isdir(r)]
            if os.path.exists(os.path.join(folder, "cleaned")) or not records:
                continue
            states = [record_landed(r, repos[os.path.basename(r)][1], repos[os.path.basename(r)][2])
                      if os.path.basename(r) in repos else None for r in records]
            if all(states):
                numbers.append(os.path.basename(folder)[:-len("-handoff")])
    for n in numbers:
        line = clean_order(home, n)
        if line:
            out.append(line)
        os.makedirs(os.path.join(home, "orders", f"{n}-handoff"), exist_ok=True)
        open(os.path.join(home, "orders", f"{n}-handoff", "cleaned"), "w").write(time.strftime("%Y-%m-%d") + "\n")
    return out


def open_handoffs(home):
    """Lines for the handoffs of this kitchen not yet in their repo's home branch."""
    import re
    repos = repos_of(home)
    out = []
    for rec in sorted(glob.glob(os.path.join(home, "orders", "*-handoff", "*", "branch"))):
        folder = os.path.dirname(rec)
        if os.path.basename(folder) not in repos:
            continue
        name, path, branch_home = repos[os.path.basename(folder)]
        b = open(rec).read().strip()
        verdict = tasted(os.path.dirname(folder))
        if not b or verdict == "rejected" or record_landed(folder, path, branch_home) is not False:   # landed, gone or dropped
            continue
        summary = os.path.join(folder, "summary.md")
        m = os.path.exists(summary) and re.search(r"\*\*Builds on:\*\*\s*`([^`]+)`", open(summary).read())
        out.append(f"- {name}: {b} on {m.group(1) if m else branch_home} · {summary} · tasted: {verdict}")
    return out


def selftest():
    import tempfile
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    with tempfile.TemporaryDirectory() as t:
        repo, orders = os.path.join(t, "shop"), os.path.join(t, "orders")
        sh = lambda *a: subprocess.run(["git", "-C", repo, *a], check=True, capture_output=True, env=env)

        def commit(branch, path, base=None):
            if base:
                sh("switch", "-q", "-c", branch, base)
            os.makedirs(os.path.dirname(os.path.join(repo, path)), exist_ok=True)
            open(os.path.join(repo, path), "w").write(branch)
            sh("add", "."); sh("commit", "-qm", branch)

        def handoff(n, branch):
            os.makedirs(os.path.join(orders, f"{n}-handoff", "shop"), exist_ok=True)
            open(os.path.join(orders, f"{n}-handoff", "shop", "branch"), "w").write(branch + "\n")

        def ticket(*owns):
            p = os.path.join(t, "ticket-" + "-".join(o.replace("/", "_") for o in owns) + ".md")
            open(p, "w").write("- **Owns (may write):** " + ", ".join(f"`{o}`" for o in owns) + "\n")
            return p

        os.makedirs(repo); subprocess.run(["git", "init", "-q", "-b", "main", repo], check=True)
        commit("main", "README.md")
        commit("invoice-export", "src/invoice/export.js", "main"); handoff("0001", "invoice-export")
        commit("invoice-email", "src/invoice/email.js", "invoice-export"); handoff("0002", "invoice-email")
        commit("cart-badge", "src/cart/badge.js", "main"); handoff("0003", "cart-badge")
        sh("switch", "-q", "main")
        base = lambda *owns: pick_base(repo, "main", orders, [ticket(*owns)])
        open(os.path.join(t, "kitchen.md"), "w").write(
            f"| Repo | Absolute path | Default branch |\n| --- | --- | --- |\n| shop | `{repo}` | `main` |\n")
        open(os.path.join(orders, "0002-handoff", "shop", "summary.md"), "w").write("**Builds on:** `invoice-export`\n")
        assert [l.split(" · ")[0] for l in open_handoffs(t)] == [
            "- shop: invoice-export on main", "- shop: invoice-email on invoice-export", "- shop: cart-badge on main"], open_handoffs(t)
        assert all(l.endswith(" · tasted: waiting") for l in open_handoffs(t)), open_handoffs(t)
        open(os.path.join(orders, "0003-handoff", "tasted"), "w").write("approved\n")
        assert open_handoffs(t)[2].endswith(" · tasted: approved"), open_handoffs(t)
        assert base("src/profile") == ("main", []), base("src/profile")                  # disjoint
        assert base("src/cart") == ("cart-badge", []), base("src/cart")                  # one overlap
        assert base("src/invoice") == ("invoice-email", []), base("src/invoice")         # a chain: the tip
        assert base("src") == (None, ["invoice-export", "invoice-email", "cart-badge"]), base("src")  # wait
        assert base("src", "!src/cart") == ("invoice-email", [])                         # an exclusion
        # the project squash-merges the first handoff: it lands, its stack stays open
        sh("merge", "--squash", "invoice-export"); sh("commit", "-qm", "Export invoices")
        assert landed(repo, "main", "invoice-export") and not landed(repo, "main", "invoice-email")
        assert base("src/invoice") == ("invoice-email", [])
        for p in ("0003-web/evidence/web-1/badge/01-open.png", "0003-web/evidence/web-1/result.json",
                  "0003-web/server.log", "0003-web/plate.md", "0003-web/verdict-abc.md", "0002-web/evidence/x.png"):
            os.makedirs(os.path.dirname(os.path.join(orders, p)), exist_ok=True)
            open(os.path.join(orders, p), "w").write("x" * 100)
        sh("worktree", "add", "-q", os.path.join(t, "worktrees", "0003-web", "shop"), "cart-badge")
        assert clean(t) == [], clean(t)                                                  # nothing landed yet
        assert os.path.exists(os.path.join(orders, "0003-web", "server.log"))
        sh("merge", "--squash", "cart-badge"); sh("commit", "-qm", "Cart badge")
        lines = clean(t)
        assert [l.split(":")[0] for l in lines] == ["- order 0003"] and "1 worktree" in lines[0], lines
        assert sorted(os.listdir(os.path.join(orders, "0003-web"))) == ["plate.md", "verdict-abc.md"]
        assert not os.path.exists(os.path.join(t, "worktrees", "0003-web"))
        assert os.path.exists(os.path.join(orders, "0002-web", "evidence", "x.png"))    # its stack is still open
        assert clean(t) == []                                                            # done once
        assert os.path.exists(os.path.join(orders, "0001-handoff", "cleaned"))           # landed, nothing to remove
        assert base("src/cart") == ("main", []), base("src/cart")                        # landed: home again
        # a rejected handoff is dropped: nothing stacks on it and the brief stops listing it
        commit("cart-total", "src/cart/total.js", "main"); handoff("0004", "cart-total"); sh("switch", "-q", "main")
        assert base("src/cart") == ("cart-total", []), base("src/cart")
        open(os.path.join(orders, "0004-handoff", "tasted"), "w").write("rejected\n")
        assert base("src/cart") == ("main", []), base("src/cart")
        assert all("cart-total" not in l for l in open_handoffs(t)), open_handoffs(t)
        assert [l.split(" · ")[0] for l in open_handoffs(t)] == ["- shop: invoice-email on invoice-export"]
        # the project deletes the branch on merge: the recorded commit still shows it landed
        open(os.path.join(orders, "0002-handoff", "shop", "commit"), "w").write(
            subprocess.run(["git", "-C", repo, "rev-parse", "invoice-email"], capture_output=True, text=True).stdout)
        sh("merge", "--squash", "invoice-email"); sh("commit", "-qm", "Email invoices")
        sh("branch", "-D", "invoice-email")
        assert open_handoffs(t) == []
        assert [l.split(":")[0] for l in clean(t)] == ["- order 0002"]
        assert not os.path.exists(os.path.join(orders, "0002-web", "evidence"))
        # a rejected order is cleaned by its number, landed or not
        os.makedirs(os.path.join(orders, "0009-web", "evidence")); open(os.path.join(orders, "0009-web", "evidence", "a.mp4"), "w").write("v")
        assert [l.split(":")[0] for l in clean(t, "0009")] == ["- order 0009"]
    print("selftest ok")


def main(argv):
    if argv[1:] == ["--selftest"]:
        return selftest()
    try:
        if len(argv) >= 6 and argv[1] == "base":
            b, blockers = pick_base(argv[2], argv[3], argv[4], argv[5:])
            if b:
                print(b); return 0
            print("wait: these open handoffs overlap and none builds on the others: " + ", ".join(blockers))
            return 3
        if len(argv) == 3 and argv[1] == "open":
            for line in open_handoffs(argv[2]):
                print(line)
            return 0
        if len(argv) in (3, 4) and argv[1] == "clean":
            for line in clean(argv[2], argv[3] if len(argv) == 4 else None):
                print(line)
            return 0
        if len(argv) == 5 and argv[1] == "landed":
            ok = landed(*argv[2:5])
            print("landed" if ok else "not landed"); return 0 if ok else 1
    except subprocess.CalledProcessError as e:
        print(e.stderr.strip() if e.stderr else e, file=sys.stderr); return 2
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
