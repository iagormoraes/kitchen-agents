---
name: grill
description: Step 2 of the kitchen. Grill the owner about a plan until every decision a station would need is settled, so no station ever asks a question while cooking. Use when the owner brings a plan, a feature, or says "grill me". Ends by handing to the menu skill.
---

Adapted from mattpocock/skills `grilling` (MIT) and pstack `in-your-own-words` / `figure-it-out` (MIT).

**First:** if you haven't in this session, read `$KITCHEN/RULES.md` in full (the absolute path is in
the session-start brief). It holds the rules every step below relies on.

**Done bar:** a station that reads only its ticket could build, test and hand off without asking a
single question. Grill until then. There is no question cap.

## 0. Say it back

Before the first round, tell the owner in your own words: the goal, the problem behind it, and the
smallest change you expect to meet it. Fix any mismatch first.

## 1. Sort every question

| Kind | Who answers | How |
| --- | --- | --- |
| **Fact** (what the code, data or tools do today) | you | a fresh read-only subagent (`Explore`). Never ask the owner a fact |
| **Experiment** (which of two ways works, how fast, does it fit) | you | run it, or a throwaway prototype. Bring the result, not the question |
| **Decision** (product, design, taste, priority, risk) | the owner | ask, with your recommended answer |

Don't block on a running fact or experiment: only the questions that depend on it wait.

## 2. Ask in rounds over a design tree

Every decision branches into the decisions that hang off it. The **frontier** is every decision
whose prerequisites are settled. Ask the whole frontier in one round, numbered, each with your
recommendation, worded so "yes" accepts it:

```
❓ **Q1** - **<title>**: <question, with the options>

➡️ <your recommended answer>
```

A question that depends on another question still open in this round belongs to a later round.
Settled answers move the frontier outward. Recompute it and ask again.

**One at a time, when the owner asks.** If the owner asks for one question at a time, keep it so
for the rest of the grill: one decision per message. Plain confirmations of your own
recommendations can still go together ("Q5 to Q8 take my defaults: yes?"), so the grill doesn't
turn into dozens of one-word turns.

**Mark what doesn't exist yet.** A URL, a command or a screen that exists only after cooking is
always written as such ("after the build: `http://localhost:<port>`"), never as if it were live.

## 3. The checklist (every grill covers these)

Each line comes from questions stations had to park in past orders. Also ask every **Grill
question** in this kitchen's House rules (`$KITCHEN_HOME/kitchen.md`): `retro` adds those, per
kitchen, never here.

1. **Greenfield?** Does this order create a brand-new project? Yes = SOLID applies and the spec
   sketches modules and interfaces first. No = follow the existing patterns.
2. **Stations.** Which stations exist, and which paths each one owns. Two stations never own the
   same path. Who owns each shared contract (types, API shape, DB shape, wire format)?
   **Does the owner cook any of it?** Only if they ask. If so, the owner takes the main logic as a
   `Station: owner` ticket (`kitchen:line`); agent stations cook the boilerplate (scaffold, config,
   copy, wiring) first, and the owner ticket is blocked by them.
3. **Done.** Each outcome as a check that passes or fails. "Works well" is not a check.
4. **Out of scope.** Name every nearby thing that will **not** be done. Nothing is "decide later":
   it is either in this order or out of it.
5. **Tie-breaks.** For each place where two requirements can collide at runtime (two UI elements
   in one space, two rules on one value, limits on small screens), the rule that decides who wins.
   Stations apply the rule; they don't ask.
6. **Defaults.** Constant or setting? (Default: constant.) New dependency allowed? (Default: no.)
   Behavior on bad input or error? Copy and text: who writes it, which languages?
7. **Reference for the look.** Any visual or feel outcome needs a reference agreed now: a mock, a
   screenshot, an existing screen, or a design system's defaults (for example "the UI kit's
   default theme"). "Looks right" without a reference is a future round.
8. **Unwritten details.** Agree the standing rule for every detail the spec doesn't spell out
   (a spacing, a button variant, a tool's log name): **the station picks the reference's default
   or the simplest option, logs it in its plate's Decisions table, and the owner judges at the
   pass.** It goes into the spec's Policies. Without it, every such detail becomes a taster question.
9. **Data and content.** Every number, list or table the feature needs (prices, drop rates, limits),
   and **every string the product renders or sends**, including the ones nobody sees on the
   screen: page title, meta and social-preview text, alt text, error and empty-state messages,
   email subjects. For each: the exact value, or the policy that lets the station write it.
10. **Permissions.** Every local action the stations will need (migrate the dev DB, reset a cache,
   restart a service). Granted here = in the ticket; never a gate later.
11. **Budget.** Time or build cycles per station, and what to do when it runs out.
12. **Proof the owner keeps.** Which rows only the owner can taste (👤), with the steps.
13. **Proof tools.** For each 🤖 row: which station tool proves it (station profile, "Tools"),
    and **can the station observe the expected result through the door?** A fault the row
    expects (a dependency down, a dropped write) needs a named way to cause it and to see it from
    outside; an ordering claim says ordered by what. If it can't be observed, rewrite the row.
    No tool reaches it: building or extending the tool is the first ticket of that station.
    A new station: who is its user, what is the door, which driver (kitchen RULES.md "Station
    tools"), and may the tool add its dependency (for example a browser driver in the station's `tools/e2e/`)?
    Its tools follow the standard contract in the kitchen RULES.md: don't grill their internals.
14. **Generators and CLIs.** For each scaffolding command or CLI the work runs (a project
    generator, a UI kit's init, a migration tool, a code generator): run its `--help` now and put the exact command, with
    flags, in the spec. Its flags change between versions; a guessed flag is a taster round.
    Then **build what the spec will name**: run the scaffold in a throwaway folder (your scratch
    space, never the repo), install every add-on the spec allows (a test runner, a UI kit), add
    one stub of each file the Design names (a route with its exports, a config entry), and build
    and test it. Paste the generated config into the spec. Never specify an export, flag or
    version the built scaffold hasn't accepted.

15. **The owner's daily loop.** How will the owner run this every day, after the order? Agree
    each owner command now: what it does, and that it needs **no argument** on the common path
    (every value has a default). The daily loop reloads on change; a production-like run is a
    separate command. These commands are the product's own: nothing in them exists for stations
    (RULES.md "Zero footprint"). They go in the spec's **Owner commands**.
    **Check every default on this machine** (a fact, not a question): each default port is free,
    each default folder is writable. A default that something else already uses is chosen again
    now. And a command whose port is taken stops with a clear message; it never starts half.

16. **Untrusted input and the attack surface.** For every value taken from outside (a request
    field, a header, an upload, a query): its maximum size, what happens above it, and exactly
    which derived value is stored or logged (never the raw value by default). Then the rest of
    the surface: who may call each entry point and how it's checked; every delete or overwrite
    and what its target is built from (only values the server generated); every outbound call
    and where its address comes from; secrets and personal data and where they may appear; each
    new dependency. They go in the spec's **Attack surface**: `kitchen:adversary` attacks exactly
    these.

## 4. Close

The grill is done when the frontier is empty and every checklist line has an answer. Show the
owner one summary: **decisions**, **policies** (tie-breaks + defaults), **out of scope**,
**stations and ownership**, **owner commands** (marked "after the build"). Do not act until the
owner confirms. Then run the `menu` skill.
