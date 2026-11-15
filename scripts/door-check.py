#!/usr/bin/env python3
"""Fail when the product's e2e suite can reach past the user's door, or the product reaches into it.

    python3 door-check.py <repo or worktree> [<suite folder, default e2e>]
    python3 door-check.py --selftest

The suite lives in the repo, so where it sits no longer keeps it out of the product's internals.
This check puts the wall back: a file in the suite may import only other files in the suite,
`node:` built-ins, or packages the suite's own package.json lists. A product file outside the
suite may never import from it. Exit 0 clean, 1 each crossing printed as file: import, 2 no suite.
"""
import json
import os
import re
import sys

# ponytail: JS/TS imports only (import/export from, import(), require); add a language when a suite uses one.
SOURCE = (".js", ".mjs", ".cjs", ".ts", ".mts", ".cts", ".jsx", ".tsx")
IMPORT = re.compile(r"""(?:\bfrom\s*|\bimport\s*\(?\s*|\brequire\s*\(\s*)['"]([^'"]+)['"]""")
SKIP = {"node_modules", ".git", "out", "dist", "build", ".next"}


def sources(root):
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP]
        for f in files:
            if f.endswith(SOURCE):
                yield os.path.join(d, f)


def package_name(spec):
    parts = spec.split("/")
    return "/".join(parts[:2]) if spec.startswith("@") else parts[0]


def crossings(repo, suite_dir="e2e"):
    repo = os.path.realpath(repo)
    suite = os.path.join(repo, suite_dir)
    if not os.path.isdir(suite):
        raise FileNotFoundError(suite)
    inside = lambda p: p == suite or p.startswith(suite + os.sep)
    deps = set()
    pkg = os.path.join(suite, "package.json")
    if os.path.exists(pkg):
        j = json.load(open(pkg))
        deps = set(j.get("dependencies", {})) | set(j.get("devDependencies", {}))
    for path in sources(repo):
        mine = inside(path)
        for spec in IMPORT.findall(open(path, errors="replace").read()):
            if spec.startswith((".", "/")):
                target = os.path.realpath(os.path.join(os.path.dirname(path), spec) if spec.startswith(".") else spec)
                if mine and not inside(target):
                    yield os.path.relpath(path, repo), spec, "reaches outside the suite"
                elif not mine and inside(target):
                    yield os.path.relpath(path, repo), spec, "the product imports the suite"
            elif mine and not spec.startswith("node:") and package_name(spec) not in deps:
                yield os.path.relpath(path, repo), spec, "a package the suite's package.json does not list"


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        def w(p, s):
            os.makedirs(os.path.dirname(os.path.join(t, p)), exist_ok=True)
            open(os.path.join(t, p), "w").write(s)
        w("e2e/package.json", '{"devDependencies": {"@playwright/test": "1"}}')
        w("e2e/driver/browser.mjs", 'import { spawn } from "node:child_process";\n')
        w("e2e/scenarios/ok.mjs", 'import { open } from "../driver/browser.mjs";\nimport { test } from "@playwright/test";\n')
        assert list(crossings(t)) == [], list(crossings(t))
        # the back doors the door rule forbids: product code, an unlisted package (the app itself)
        w("e2e/scenarios/bad.mjs", 'import { db } from "../../src/db.js";\nconst app = require("my-app/lib");\n')
        w("src/app.ts", 'import { seed } from "../e2e/driver/browser.mjs";\nimport x from "./x";\n')
        got = sorted((f, why) for f, _, why in crossings(t))
        assert got == [("e2e/scenarios/bad.mjs", "a package the suite's package.json does not list"),
                       ("e2e/scenarios/bad.mjs", "reaches outside the suite"),
                       ("src/app.ts", "the product imports the suite")], got
        try:
            list(crossings(t, "tests/e2e"))
            raise AssertionError("missing suite accepted")
        except FileNotFoundError:
            pass
    print("selftest ok")


def main(argv):
    if argv[1:] == ["--selftest"]:
        return selftest()
    if len(argv) not in (2, 3):
        print(__doc__); return 2
    try:
        hits = list(crossings(argv[1], argv[2] if len(argv) == 3 else "e2e"))
    except FileNotFoundError as e:
        print(f"no suite at {e}", file=sys.stderr); return 2
    for f, spec, why in hits:
        print(f"{f}: {spec}: {why}")
    print(f"door check: {len(hits)} crossing(s)")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
