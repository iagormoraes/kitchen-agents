#!/usr/bin/env python3
"""Fail when a station branch touched a path outside its ticket's Owns.

    python3 ownership-check.py orders/<id>/ticket.md <repo> <base sha> [<ref, default HEAD>]
    python3 ownership-check.py --selftest

Owns comes from the ticket line "**Owns (may write):**": every `backticked` token on it.
A token may be absolute: one under the repo's main checkout or any of its worktrees is made
relative to it; one elsewhere (the station's tools repo, another repo) is not part of this repo
and is ignored here. <repo> may be the main checkout or a worktree: the result is the same.
A token starting with ! is an exclusion (`!src/lib/types.src`): never owned, even inside an owned
folder. An exclusion written in prose ("except `x`") is refused. In an empty repo (HEAD with no
commit) the default <ref> is the ticket's **Branch:**.
A token with * ? or [ is a glob (fnmatch, so * also crosses /). Any other token matches itself
and everything under it. Paths are relative to the repo root. Exit 1 lists each stray path.
"""
import fnmatch
import os
import re
import subprocess
import sys


def blocked(msg):
    print(msg, file=sys.stderr)
    raise SystemExit(2)


def owns_from_ticket(text):
    """(owned, excluded): backticked tokens of the Owns line; `!path` tokens are exclusions."""
    for line in text.splitlines():
        if "**Owns" in line:
            # "except `x`" reads as an owned `x` to a parser: refuse it instead of guessing.
            if re.search(r"\b(except|but not|excluding|without)\b[^`]*`", line, re.I):
                blocked("Owns line: write an exclusion as `!path`, not in prose")
            tokens = [t.strip().rstrip("/") for t in re.findall(r"`([^`]+)`", line)]
            return ([t for t in tokens if not t.startswith("!")],
                    [t[1:] for t in tokens if t.startswith("!")])
    blocked("ticket has no **Owns (may write):** line")


def branch_from_ticket(text):
    m = re.search(r"\*\*Branch:\*\*\s*`([^`]+)`", text)
    return m.group(1) if m else None


def relative_to_repo(patterns, repo_root):
    root = repo_root.rstrip("/") + "/"
    out = []
    for p in patterns:
        if not p.startswith("/"):
            out.append(p)
        elif (p + "/").startswith(root):
            out.append(p[len(root):] or "*")   # the repo root itself: everything
    return out


def owned(path, patterns):
    for p in patterns:
        if any(c in p for c in "*?["):
            if fnmatch.fnmatch(path, p):
                return True
        elif path == p or path.startswith(p + "/"):
            return True
    return False


def selftest():
    owns, excl = owns_from_ticket("- **Owns (may write):** `src/api/`, `tests/api_*.src`, `README.md`")
    assert owns == ["src/api", "tests/api_*.src", "README.md"] and excl == [], owns
    o2, e2 = owns_from_ticket("- **Owns (may write):** `src/lib/`, `!src/lib/types.src`")
    assert o2 == ["src/lib"] and e2 == ["src/lib/types.src"], (o2, e2)
    try:   # the real pilot line: prose exclusion must be refused, not read as owned
        owns_from_ticket("- **Owns (may write):** `src/lib/tasks/**` (except `types.src`)")
        raise AssertionError("prose exclusion accepted")
    except SystemExit:
        pass
    assert branch_from_ticket("- **Branch:** `feat/0001-app` from base `abc`") == "feat/0001-app"
    assert owned("src/api/routes.src", owns)
    assert owned("tests/api_users.src", owns)
    assert owned("README.md", owns)
    assert not owned("src/apix/x.src", owns)  # prefix must stop at a folder boundary
    assert not owned("src/web/app.src", owns)
    assert not owned("tests/web_test.src", owns)
    abs_owns = relative_to_repo(["/r/app/", "/r/", "/k/stations/web/tools", "src/x"], "/r")
    assert abs_owns == ["app/", "*", "src/x"], abs_owns   # tools repo path dropped, root = all
    assert owned("app/page.src", relative_to_repo(["/r/app"], "/r"))
    assert owned("README.md", relative_to_repo(["/r"], "/r"))
    assert not owned("lib/x.src", relative_to_repo(["/r/app", "/k/tools"], "/r"))
    print("selftest ok")


def main(argv):
    if argv[1:] == ["--selftest"]:
        return selftest()
    if len(argv) not in (4, 5):
        raise SystemExit(__doc__)
    ticket, repo, base = argv[1:4]
    ref = argv[4] if len(argv) == 5 else "HEAD"
    git = lambda *a: subprocess.run(["git", "-C", repo, *a], check=True,
                                    capture_output=True, text=True).stdout.strip()
    # Absolute Owns may name the main checkout or any worktree of this repo (the station's):
    # accept every root git knows for it, so the check gives the same answer wherever it runs.
    roots = {os.path.realpath(git("rev-parse", "--show-toplevel"))}
    roots |= {os.path.realpath(l[len("worktree "):])
              for l in git("worktree", "list", "--porcelain").splitlines() if l.startswith("worktree ")}
    text = open(ticket).read()
    raw, raw_excl = owns_from_ticket(text)
    owns = sorted({p for r in roots for p in relative_to_repo(raw, r)})
    excl = sorted({p for r in roots for p in relative_to_repo(raw_excl, r)})
    # An empty repo's main checkout has no commit (HEAD is unborn): use the ticket's branch.
    if ref == "HEAD" and subprocess.run(["git", "-C", repo, "rev-parse", "-q", "--verify", "HEAD"],
                                        capture_output=True).returncode != 0:
        ref = branch_from_ticket(text) or blocked("HEAD has no commit and the ticket names no branch")
    # --no-renames: a file moved out of another station's path shows as a delete there too.
    changed = subprocess.run(
        ["git", "-C", repo, "diff", "--name-only", "--no-renames", f"{base}..{ref}"],
        check=True, capture_output=True, text=True).stdout.split()
    stray = [p for p in changed if not owned(p, owns) or owned(p, excl)]
    for p in stray:
        print(f"outside Owns: {p}")
    print(f"{len(changed)} changed, {len(stray)} outside Owns ({', '.join(owns)})")
    return 1 if stray else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
