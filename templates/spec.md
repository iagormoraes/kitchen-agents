# NNNN · <title>

<!-- Written by the expediter with the menu skill, from a finished grill. A contract, not a research
     log: about 300 lines or less. A section you cannot fill = the grill is not finished. -->

- **Status:** draft | approved | implemented
- **Greenfield:** yes | no   <!-- yes = brand-new project: SOLID applies, Design section is a sketch -->
- **Reviewed:** <sha, verdict clean>   <!-- filled at the "out" step -->

## Problem

<The owner's problem, from their side. Two to five lines.>

## Behavior

<What is true when this ships, from the user's side. Numbered, each one testable.>

1. <behavior>

## Decisions

<Every decision the grill settled. One row each. The ledger stations and reviewers judge against.>

| Id | Decision | Why |
| --- | --- | --- |
| D1 | <what> | <owner's reason> |

## Policies

<How stations decide what the spec doesn't spell out. Copied into every ticket word for word.>

- **Tie-breaks:** <when X and Y collide, X wins and Y does Z>
- **Defaults:** constant over setting · no new dependency without a decision row · <error behavior> · <copy/text rule>
- **References for the look:** <mock / screenshot paths, per screen>
- **Unwritten details:** the station picks the reference's default or the simplest option, logs it in
  its plate's Decisions table, and the owner judges at the pass. <or a stricter rule the grill agreed>

## Out of scope

- <each nearby thing that will not be done>

## Attack surface

<From grill line 16. Every way in for outside data or callers, and what it can reach. The stations
build the defenses; `kitchen:adversary` attacks each row through the door before merge. "None" only
for a change with no outside input, no caller check, no stored write and no new dependency.>

| Entry point | Input or caller | Limits and checks | Can reach | Never |
| --- | --- | --- | --- | --- |
| <a route, a form, an upload, a command> | <fields, headers, files; who may call> | <sizes, types, auth> | <tables, files, outbound calls> | <what must never happen: another owner's data, a delete outside its folder…> |

## Contracts

<Every shape shared between stations, frozen here, or owned by one station whose ticket blocks the others.
An API contract lists, per call: the request body fields with types and limits, the response shape
(a list's item shape too), and every error code with its body. A shared tool lists its frozen call
shape: arguments and environment, exit codes, output format.>

| Contract | Shape (or link) | Owner station | Consumers |
| --- | --- | --- | --- |

## Design

<Greenfield: modules, their interfaces (caller usage first), who owns which state, the rejected
alternative and why. Existing project: "follow the patterns in <paths>".>

## Owner commands

<The product's own commands the owner types day to day, from grill line 15. Each needs no argument
on the common path: every value has a default. Nothing here exists for stations: they reuse these
commands with ordinary overrides (RULES.md "Zero footprint").>

| Command (after the build) | Does | Defaults | When |
| --- | --- | --- | --- |
| <start developing> | <runs the app and what it needs, reloads on change> | <port, data folder…> | daily |
| <production-like run> | <builds and runs it as it will ship> | <…> | before a release; proven by a station |

## Stations

| Station | Repo / module | Owns | Blocked by | Budget |
| --- | --- | --- | --- | --- |

## Smoke test

<🤖 = a station runs it and attaches evidence. 👤 = only the owner can judge it (look, feel, phone,
real payment). Write a row as 🤖 whenever a check can prove it.>

| ✓ | Id | Who | Steps | Expected |
| --- | --- | --- | --- | --- |
|   | S1 | 🤖 | <exact steps> | <exact result> |
|   | S<n> | 👤 | the daily loop: the **Owner commands** "start developing" command, with no argument; change one behavior | it starts, and the change takes effect without a restart |
