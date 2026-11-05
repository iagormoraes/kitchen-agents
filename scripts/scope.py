#!/usr/bin/env python3
"""Count a big order's scope list: the line every progress update to the owner starts with.

    python3 scope.py orders/<spec>-scope.json [-v]
    python3 scope.py                                # selftest

The list is JSON: [{"group": ..., "name": ..., "status": ...}, ...].
Status, in order: todo < first-pass < checked < owner (the owner tasted it).
Stations move a row up when they finish it. -v lists the rows not yet checked.
"""
import json
import sys
from collections import Counter

ORDER = ["todo", "first-pass", "checked", "owner"]


def summary(rows):
    n = len(rows)
    c = Counter(r["status"] for r in rows)
    bad = set(c) - set(ORDER)
    if bad:
        raise SystemExit(f"unknown status: {', '.join(sorted(bad))}")
    reached = lambda s: sum(c[x] for x in ORDER[ORDER.index(s):])
    return (f"{reached('first-pass')} / {n} first pass, {reached('checked')} / {n} checked, "
            f"{c['owner']} / {n} owner tasted, {c['todo']} not started")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        rows = [{"status": s} for s in ["todo", "first-pass", "first-pass", "checked", "owner"]]
        assert summary(rows) == "4 / 5 first pass, 2 / 5 checked, 1 / 5 owner tasted, 1 not started"
        print("selftest ok")
        raise SystemExit(0)
    rows = json.load(open(sys.argv[1]))
    print(summary(rows))
    if "-v" in sys.argv:
        for r in rows:
            if r["status"] in ("todo", "first-pass"):
                print(f"  {r['status']:10} {r.get('group', ''):14} {r['name']}")
