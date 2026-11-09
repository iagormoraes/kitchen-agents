#!/usr/bin/env python3
"""Fail when a branch adds kitchen words to the product: the product never knows about the kitchen.

    python3 leak-check.py <repo or worktree> <base sha> [<ref>] [--spec <spec.md>]... [--allow w,w] [--exclude glob]...
    python3 leak-check.py <repo or worktree> --all [<ref>] [--spec <spec.md>]... [--allow w,w] [--exclude glob]...
    python3 leak-check.py --selftest

Reads only the lines the branch adds (`git diff <base>..<ref>`), skipping lock files; `--all` reads
the whole product at <ref> instead, so a leak an earlier order left behind is found too. A hit is a
kitchen word or id in product code, comments or docs: kitchen, station, ticket, plate.md,
expediter, taster, the orders or kitchen paths, "order 0002" / "spec 0001" style ids, spec
decision ids ("spec C4", "decision D12"). `--spec` adds every id a spec defines in its tables
(`D9`, `C7`, `S5`, `R-S6`): found bare, in parentheses or inside a name (`TestEachD9Event`), not
inside a placeholder (`TS_D1`). `--exclude` skips paths (the owner's own design docs). `--allow` drops words that are the product's own domain
(a help desk's "ticket", a train app's "station"); the kitchen's House rules list them.
Exit 0 clean, 1 hits (each printed as file:line: word: text), 2 git failed.
Prose that names no kitchen word ("as a later order will do") is the reviewer's to catch.
"""
import fnmatch
import re
import subprocess
import sys

TERMS = {
    "kitchen": r"\bkitchens?\b",
    "station": r"\bstations?\b",
    "ticket": r"\btickets?\b",
    "plate": r"\bplate\.md\b",
    "expediter": r"\bexpediters?\b",
    "taster": r"\btasters?\b",
    "orders path": r"\$ORDERS\b|\$KITCHEN(_HOME)?\b|\.claude/kitchens\b",
    "order id": r"\b(order|spec)\s+#?\d{4}\b",
    "spec decision id": r"\b(spec|decision|contract)\s+[A-Z]\d{1,3}\b",
}
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
SPEC_ID_CELL = re.compile(r"^\|(?:\s*[^|]*\|)?\s*((?:R-)?[A-Z]{1,2}\d{1,3})\s*\|", re.M)
LOCKFILE = re.compile(r"(^|/)([^/]*[.-]lock(\.json|\.yaml|b)?|[^/]*\.lock|go\.sum)$")


def spec_ids(texts):
    """The ids a spec defines: the first or second cell of its table rows (| D9 |, |   | S5 |)."""
    ids = set()
    for t in texts:
        ids |= set(SPEC_ID_CELL.findall(t))
    return ids


def scan(diff, allow=(), ids=(), exclude=()):
    """Yield (file, line number, term, text) for each added line that names a kitchen word or id."""
    pats = {name: re.compile(p, re.I) for name, p in TERMS.items() if name not in allow}
    ids = [i for i in ids if i not in allow]
    if ids:   # bare, in parentheses or inside a name (lowercase before), never inside a placeholder
        pats["spec id"] = re.compile(r"(?<![A-Z0-9_{\-])(" + "|".join(map(re.escape, sorted(ids, key=len, reverse=True))) + r")(?![0-9])")
    path, line = None, 0
    for raw in diff.splitlines():
        if raw.startswith("+++ "):
            path = raw[6:] if raw.startswith("+++ b/") else None
        elif raw.startswith("@@"):
            m = re.search(r"\+(\d+)", raw)
            line = int(m.group(1)) if m else 0
        elif raw.startswith("+") and path and not LOCKFILE.search(path) and not any(fnmatch.fnmatch(path, g) for g in exclude):
            for name, pat in pats.items():
                if pat.search(raw[1:]):
                    yield path, line, name, raw[1:].strip()
                    break
            line += 1
        elif not raw.startswith("-") and not raw.startswith("\\"):
            line += 1


def selftest():
    diff = "\n".join([
        "diff --git a/data/README.md b/data/README.md", "+++ b/data/README.md", "@@ -0,0 +1,3 @@",
        "+Run the station's check tool before you push.",       # real case: a station word in docs
        "+Counts are summed per hour.",
        "+See spec C4 for the rollup.",                         # a spec decision id
        "diff --git a/web/auth.src b/web/auth.src", "+++ b/web/auth.src", "@@ -10,0 +30,2 @@",
        "+  // session refresh lands in order 0002",              # an order id
        "+  return session",
        "+++ b/package-lock.json", "@@ -0,0 +1 @@", "+  \"station\": \"x\"",   # lock file: skipped
        "+++ b/help/tickets.src", "@@ -0,0 +1 @@", "+open a support ticket",  # domain word
    ])
    hits = list(scan(diff))
    assert [(f, n, t) for f, n, t, _ in hits] == [
        ("data/README.md", 1, "station"), ("data/README.md", 3, "spec decision id"),
        ("web/auth.src", 30, "order id"), ("help/tickets.src", 1, "ticket")], hits
    assert [h[2] for h in scan(diff, allow={"ticket"})] == ["station", "spec decision id", "order id"]
    assert list(scan("+++ b/a.src\n@@ -0,0 +1 @@\n+orders ship in 2 days\n")) == []   # plain "orders"
    # spec ids: the real cases of a pilot order, read from the spec's own tables
    spec = "| D9 | every event is recorded | owner |\n|   | S5 | 🤖 | steps | result |\n| C7 | env | data |\n"
    ids = spec_ids([spec])
    assert ids == {"D9", "S5", "C7"}, ids
    real = "\n".join(["+++ b/edge/events_test.src", "@@ -0,0 +1,4 @@",
                      "+func TestEachD9EventIsRecorded(t *testing.T) {",   # inside a name
                      "+# Env (C7): DB_HOST",                               # in parentheses
                      "+  ts: {{TS_D9}} and TS_D9",                         # placeholders: not ids
                      "+S50 is a size, C70 too"])                          # longer numbers: not ids
    assert [(n, t) for _, n, t, _ in scan(real, ids=ids)] == [(1, "spec id"), (2, "spec id")]
    assert list(scan(real, ids=ids, exclude=("edge/*",))) == []
    print("selftest ok")


def main(argv):
    if argv[1:] == ["--selftest"]:
        return selftest()
    args, allow, specs, exclude, whole = [], set(), [], [], False
    i = 1
    while i < len(argv):
        a = argv[i]
        if a in ("--allow", "--spec", "--exclude") and i + 1 < len(argv):
            v = argv[i + 1]
            if a == "--allow":
                allow |= {w.strip() for w in v.split(",") if w.strip()}
            elif a == "--spec":
                specs.append(v)
            else:
                exclude.append(v)
            i += 2
        elif a == "--all":
            whole = True; i += 1
        else:
            args.append(a); i += 1
    if whole and len(args) in (1, 2):
        repo, base, ref = args[0], EMPTY_TREE, (args[1] if len(args) == 2 else "HEAD")
    elif not whole and len(args) in (2, 3):
        repo, base = args[0], args[1]
        ref = args[2] if len(args) == 3 else "HEAD"
    else:
        print(__doc__); return 2
    try:
        ids = spec_ids(open(p).read() for p in specs)
    except OSError as e:
        print(e, file=sys.stderr); return 2
    r = subprocess.run(["git", "-C", repo, "diff", "-U0", "--no-renames", "--no-color", f"{base}..{ref}"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr.strip(), file=sys.stderr); return 2
    hits = list(scan(r.stdout, allow, ids, exclude))
    for f, n, term, text in hits:
        print(f"{f}:{n}: {term}: {text[:120]}")
    print(f"leak check: {len(hits)} kitchen word(s) in the product" + (f" (allowed: {', '.join(sorted(allow))})" if allow else ""))
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
