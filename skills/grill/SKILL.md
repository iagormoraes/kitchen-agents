---
name: grill
description: Step 2 of the kitchen. Grill the owner about a plan, one researched question at a time, until every decision a station would need is settled, so no station ever asks a question while cooking. Use when the owner brings a plan, a feature, or says "grill me". Ends by handing to the menu skill.
---

Adapted from mattpocock/skills `grilling` (MIT) and pstack `in-your-own-words` / `figure-it-out` (MIT).

**First:** if you haven't in this session, read `$KITCHEN/RULES.md` in full (the absolute path is in
the session-start brief). It holds the rules every step below relies on.

**Done bar:** a station that reads only its ticket could build, test and hand off without asking a
single question. Grill until then. There is no question cap.

## 0. Say it back

Before the first question, tell the owner in your own words: the goal, the problem behind it, and
the smallest change you expect to meet it. Fix any mismatch first.

## 1. Sort every question

| Kind | Who answers | How |
| --- | --- | --- |
| **Fact** (what the code, data, docs or tools say today) | you | read it: a fresh read-only subagent (`Explore`) for the codebase, the primary documentation for a tool or standard. Never ask the owner a fact |
| **Experiment** (which of two ways works, how fast, does it fit) | you | run it, or a throwaway prototype in your scratch space. Bring the result, not the question |
| **Decision** (product, design, taste, priority, risk) | the owner | ask it, one at a time (§3), with options from research (§2) |

## 2. Research before you ask

The options of a decision come from evidence, never from memory or a guess. Before you ask a
decision, gather what its options rest on:

- **The codebase:** what exists, the patterns in use, what a choice would touch (`file:line`).
- **Primary sources:** the official documentation, standard or specification of every tool,
  format or protocol involved (its URL and section). Not a blog, not memory.
- **The owner's own material:** their design docs, earlier specs, the kitchen's House rules.
- **A run:** when two options can be compared by trying them, try them, and bring the numbers.

Then:

- **Only evidenced options.** Each option says what it is, what it costs or risks, and the source
  that backs it. An option you can't source is dropped, or researched first.
- **Evidence that leaves one sane option is not a question.** State it as settled, with its
  source ("Settled by evidence: X, because <source>"), and move on. The owner can still overrule.
- **Say what you couldn't verify,** in one line, instead of filling the gap.
- **Research ahead.** While the owner answers one question, research the next ones in the
  background, so they never wait on you.

When the owner challenges an option ("you're guessing", "you're copying the old system"), go back
to the sources and come back with the question rebuilt, not defended.

## 3. Ask one question at a time

Every decision branches into the decisions that hang off it. Ask **one decision per message**:
the most upstream one still open (the one whose answer reshapes the most others), never one that
depends on a question still unanswered.

```
**Q<n> of ~<estimated total>: <title>**

<why it matters here, one or two lines>

| Option | What it means | Trade-off | Evidence |
| --- | --- | --- | --- |
| **A** (recommended) | … | … | `<file:line>` · <doc URL §> · <run result> |
| **B** | … | … | … |

➡️ **A**, because <the evidence that favors it>. Reply A, B, or your own answer.
```

- After each answer: one line `Recorded: <the decision>`, then the next question, in the same
  message. Update the estimated total as the tree grows or shrinks.
- **Faster, only when the owner asks** ("take your defaults for the rest of the UI"): list those
  remaining decisions with their recommendations in one message, for one yes or for corrections.
- **Mark what doesn't exist yet.** A URL, a command or a screen that exists only after cooking is
  always written as such ("after the build: `http://localhost:<port>`"), never as if it were live.

## 4. The checklist (every grill covers these)

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

## 5. Close

The grill is done when no decision is left open and every checklist line has an answer. Show the
owner one summary: **decisions** (each with the source it rests on), **policies** (tie-breaks + defaults), **out of scope**,
**stations and ownership**, **owner commands** (marked "after the build"). Do not act until the
owner confirms. Then run the `menu` skill.
