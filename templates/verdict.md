# Verdict <order id> @ <sha>

<!-- Written by the reviewer agent. Save as $ORDERS/<order id>/verdict-<sha>.md, where <sha> is the
     last commit of the branch you reviewed. A later commit needs a new verdict that reviews only
     the change since this one.

     How to review:
     1. Read ticket.md, the spec and plate.md before the diff. The intent below comes from them.
     2. Review `git diff <base>..<sha>`, and read the callers and callees around it, not only the
        changed lines.
     3. Spot-check the evidence: open at least two of the evidence files the plate cites and
        confirm they show what the plate claims. Re-run one cheap check from "What I ran".
     4. Apply the lenses below. Skip a lens that does not apply; a small fix does not need an
        essay on architecture.
     5. Filter before you write (rules at the bottom). At most 5 findings in "Act on".

     Lenses:
     - Correctness: edge cases, error paths, what happens if it runs twice or crashes halfway,
       concurrent access. Trace the call path; do not just say "this could be null".
     - Root cause: does it fix the cause, or guard a symptom? A workaround that needs a long
       comment is a sign the code is wrong.
     - Spec: (a) asked for but missing or partial, (b) built but not asked for, (c) looks
       implemented but behaves wrong. Quote the spec or ticket line.
     - Ownership: every changed path inside the ticket's Owns. Outside = Act on.
     - User's door: a scenario or check that calls internals, a test-only endpoint or writes the DB
       to cause the effect it then "proves" is not proof. Act on.
     - Verification: does the evidence prove the behavior at the level the plate claims? A
       `build-only` row presented as a pass is a finding. A test that recomputes its expected
       value the way the code does, or mocks an internal, proves nothing.
     - YAGNI: options, settings, layers or abstractions for cases the spec doesn't have
       (smell: Speculative Generality, a new layer with one caller).
     - KISS: could it be smaller and still correct? Dead code, pass-through methods, a call chain
       needing more than three files to trace.
     - DRY: one rule or value written in two places (smells: Duplicated Code, Shotgun Surgery,
       a hand-synced list, two ways to do one task). Look-alike code with different reasons
       to change is not a finding.
     - SOLID, only when the ticket says `greenfield: yes`: a module with two reasons to change
       (Divergent Change), callers that must know internal rules, internals other modules import,
       a subtype that refuses its parent's contract. Judge against the spec's Design section.
     - Structure (existing projects): does it fit the code around it, or is it bolted on?
     - Security: secrets in client code or logs, unvalidated input reaching the DB or a shell.
     - The owner's rules: the ticket's Policies, the kitchen RULES.md and the repo CLAUDE.md. -->

- **Reviewed:** `<base sha>..<sha>` on `feat/<order id>-<station>`
- **Inputs read:** ticket.md, plate.md, spec `<path>`
- **Evidence spot-checked:** `<file>` (shows what it claims: yes / no), `<file>` (yes / no)
- **Check re-run:** `<command>` (exit <n>)
- **Result:** clean | changes needed

## Intent

<One paragraph: what this change is meant to do, from the ticket and the spec. The review judges
the code against this, not against what the reviewer would have built.>

## Act on

<At most 5. Each would block a merge: wrong behavior, data loss, security, a broken owner rule,
evidence that does not prove what the plate claims.>

### A1 · <short title>

- **Severity:** critical | warning
- **Where:** `<file>:<line>` or `<function>`
- **Problem:** <what is wrong, concretely>
- **Evidence:** <the call path or input that makes it fail, or the evidence file that does not match>
- **Fix:** <what to do instead, when there is a clear one>

## Consider

<Real points whose cost may not be worth paying now. One line each, with the trade-off.>

## Noted

<Valid but not actionable now. One line each.>

## Dismissed

<Each finding rejected during filtering, one line each, with the reason. This list lets the owner
override the review.>

<!-- Filtering rules, apply before writing:
     - Nitpick gravity: a reviewer who finds nothing serious tends to inflate nits. If all you
       have are nits and style, the result is "clean"; say so.
     - Hypothetical is not actual: "what if X is null" is a finding only if a real caller can pass
       null. Trace it; if upstream validates it, dismiss.
     - "I would have done it differently" is not a finding unless you show a concrete problem
       with how it was done.
     - Missing context: a pattern that matches the rest of the codebase, or code the change did
       not touch, is not a finding against this change.
     - Do not dismiss a security or data-loss finding without tracing it.
     - Kitchen leak: a product file, setting, name, label or argument that exists only because
       stations need it, or any kitchen term in product code (kitchen, station, order or ticket
       as concepts, the orders or kitchen paths), or a spec, decision, row or order id in a
       comment, doc, test name or commit message. Act on, also when an earlier order wrote it:
       isolation belongs in the station tools, and the product's text explains, never cites.
     - Owner commands: one the owner types day to day that needs an argument on the common path,
       or a daily loop that rebuilds everything on each change. Act on.
     - Data loss is always Act on, never Consider: a write path that can fail and leave the app
       showing or confirming data that a restart forgets (in-memory change kept after a failed
       save), or that can overwrite good data. -->
