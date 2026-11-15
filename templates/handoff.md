<!-- $ORDERS/<NNNN>-handoff/<repo name>/summary.md, written by the expediter at the out step, one per
     repo. It is for the project's own flow (a pull request skill, a teammate, the owner): every
     line in product words. No kitchen word, order, spec, ticket or id; leak-check.py --message
     checks this file. Image and video paths are relative to this file (./evidence/<scenario>/…),
     so a tool that uploads them (`gh pr create --body-file … --attach …`) finds them.
     Delete this comment when filling it in. -->

# <What changed, as a title>

**Branch:** `<handoff branch>` · **Builds on:** `<home branch, or the branch it stacks on>` ·
**Proven on:** `<base sha>` + `<this branch's sha>`

## What changed

<One short paragraph: the outcome for the user of the product.>

## How to try it

```bash
<the daily "start developing" command, no argument>
```

1. <step> → <what you should see>

## Evidence

| Behavior | Result | Proof |
| --- | --- | --- |
| <what the user can do now> | pass | ![<behavior>](./evidence/<scenario>/<last step>.png) [video](./evidence/<scenario>/<scenario>.mp4) |

<Full suite: N scenarios, all passed (`e2e/`, `<the repo's e2e command>`).>
<Pre-existing failures, unrelated to this change: <scenario: one line>, or delete this line.>

## Not in this change

- <out of scope, one line each, or "nothing">
