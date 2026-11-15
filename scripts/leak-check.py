#!/usr/bin/env python3
"""Fail when a branch adds kitchen words to the product: the product never knows about the kitchen.

    python3 leak-check.py <repo or worktree> <base sha> [<ref>] [--spec <spec.md>]... [--allow w,w] [--exclude glob]...
    python3 leak-check.py <repo or worktree> --all [<ref>] [--spec <spec.md>]... [--allow w,w] [--exclude glob]...
    python3 leak-check.py --message <file> [--spec <spec.md>]... [--allow w,w]
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
`--message` checks a commit message, a branch name or a handoff summary before it is used (the
history is the product's: no "(order 0002)", no spec id, no bare order number like "0063").
A new file's path is checked too: a kitchen word, a spec id, or (with `--spec`) an order number
taken from the spec file names (`scenarios/0063-board.mjs`) fails like a line does.
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


def spec_numbers(paths):
    """The order numbers the kitchen uses: the NNNN of each spec file name (0063-mining.md)."""
    return {m.group(1) for p in paths if (m := re.match(r"(\d{4})-", p.rsplit("/", 1)[-1]))}


def scan(diff, allow=(), ids=(), exclude=(), numbers=(), number_lines=False):
    """Yield (file, line number, term, text) for each added line that names a kitchen word or id,
    and (file, 0, term, path) for each added file whose path does (scenarios/0063-board.mjs)."""
    pats = {name: re.compile(p, re.I) for name, p in TERMS.items() if name not in allow}
    ids = [i for i in ids if i not in allow]
    if ids:   # bare, in parentheses or inside a name (lowercase before), never inside a placeholder
        pats["spec id"] = re.compile(r"(?<![A-Z0-9_{\-])(" + "|".join(map(re.escape, sorted(ids, key=len, reverse=True))) + r")(?![0-9])")
    path_pats = dict(pats)
    if numbers:   # an order number in a file or folder name, never inside a longer number
        path_pats["order number"] = re.compile(r"(?<![0-9])(" + "|".join(sorted(numbers)) + r")(?![0-9])")
    path, line, prev = None, 0, ""
    for raw in diff.splitlines():
        if raw.startswith("+++ "):
            path = raw[6:] if raw.startswith("+++ b/") else None
            if path and prev == "--- /dev/null" and not any(fnmatch.fnmatch(path, g) for g in exclude):
                for name, pat in path_pats.items():
                    if pat.search(path):
                        yield path, 0, name, path
                        break
        elif raw.startswith("@@"):
            m = re.search(r"\+(\d+)", raw)
            line = int(m.group(1)) if m else 0
        elif raw.startswith("+") and path and not LOCKFILE.search(path) and not any(fnmatch.fnmatch(path, g) for g in exclude):
            for name, pat in (path_pats if number_lines else pats).items():
                if pat.search(raw[1:]):
                    yield path, line, name, raw[1:].strip()
                    break
            line += 1
        elif not raw.startswith("-") and not raw.startswith("\\"):
            line += 1
        prev = raw


def message_as_diff(text):
    lines = text.splitlines() or [""]
    return "+++ b/COMMIT_MESSAGE\n@@ -0,0 +1,%d @@\n" % len(lines) + "\n".join("+" + l for l in lines)


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
    # commit messages: the real squash message of a pilot order, and a clean one
    bad = "feat: all tag types, full events, management, reports and the display SDK (order 0002)"
    assert [t for _, _, t, _ in scan(message_as_diff(bad))] == ["order id"]
    assert list(scan(message_as_diff("feat: all tag types, full events and the display SDK"))) == []
    # paths: the real v1 case (scenarios named by order), and a behavior name next to it
    nums = spec_numbers(["/k/specs/0063-mining.md", "/k/specs/research/notes.md"])
    assert nums == {"0063"}, nums
    new = "\n".join(["--- /dev/null", "+++ b/e2e/scenarios/0063-p4b-board.mjs", "@@ -0,0 +1 @@", "+ok",
                     "--- /dev/null", "+++ b/e2e/scenarios/cash-shop-storage.mjs", "@@ -0,0 +1 @@", "+ok",
                     "--- /dev/null", "+++ b/tools/station-check.sh", "@@ -0,0 +1 @@", "+ok",
                     "--- /dev/null", "+++ b/data/100635.csv", "@@ -0,0 +1 @@", "+ok",   # longer number
                     "--- a/old-0063.txt", "+++ b/old-0063.txt", "@@ -1 +1 @@", "+ok"])     # existing file: not new
    assert [(f, n, t) for f, n, t, _ in scan(new, numbers=nums)] == [
        ("e2e/scenarios/0063-p4b-board.mjs", 0, "order number"), ("tools/station-check.sh", 0, "station")]
    assert [t for _, _, t, _ in scan(message_as_diff("invoice-export-0063"), numbers=nums, number_lines=True)] == ["order number"]
    assert list(scan(message_as_diff("invoice-export"), numbers=nums, number_lines=True)) == []
    print("selftest ok")


def main(argv):
    if argv[1:] == ["--selftest"]:
        return selftest()
    args, allow, specs, exclude, whole, message = [], set(), [], [], False, None
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
        elif a == "--message" and i + 1 < len(argv):
            message = argv[i + 1]; i += 2
        else:
            args.append(a); i += 1
    if message is not None:
        try:
            ids = spec_ids(open(p).read() for p in specs)
            diff = message_as_diff(open(message).read())
        except OSError as e:
            print(e, file=sys.stderr); return 2
        hits = list(scan(diff, allow, ids, numbers=spec_numbers(specs), number_lines=True))
        for _, n, term, text in hits:
            print(f"commit message line {n}: {term}: {text[:120]}")
        print(f"leak check: {len(hits)} kitchen word(s) in the commit message")
        return 1 if hits else 0
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
    hits = list(scan(r.stdout, allow, ids, exclude, spec_numbers(specs)))
    for f, n, term, text in hits:
        print(f"{f}:{n}: {term}: {text[:120]}")
    print(f"leak check: {len(hits)} kitchen word(s) in the product" + (f" (allowed: {', '.join(sorted(allow))})" if allow else ""))
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
