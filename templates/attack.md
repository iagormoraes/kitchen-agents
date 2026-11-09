# Attack <order id> @ <sha>

<!-- Written by kitchen:adversary. Save as $ORDERS/<order id>/attack-<sha>.md, <sha> = the branch's
     last commit. A later commit gets a new report that re-attacks every earlier finding and what
     the fix changed.

     Method:
     1. List the surface: the spec's Attack surface rows the branch touches, then every entry point
        in the diff (where outside data comes in), every write, overwrite or delete, every outbound
        call, every check of who the caller is, every new dependency.
     2. Run the app from your own detached worktree, on your port, with data only in your scratch
        folder. Attack through the door: requests, the page, the command line. Never call internals.
     3. Try each class below that applies. Each attempt is a command or a short script you keep.
     4. Escapes are proven against a canary, never against a real file: run the app with its data
        folder inside your scratch folder, create a canary file elsewhere in the scratch folder
        (`<scratch>/outside/canary`), and aim every path, delete or overwrite attack at it.
     5. A finding exists only with its run: the exact command, the output it printed, and the result
        the spec requires instead. Re-run it once before writing it down.

     Attack classes (try every one that applies to the surface):
     - Input limits: empty, oversized (10× the stated limit and more), deeply nested, wrong type,
       wrong encoding, control characters, duplicated fields, unicode look-alikes.
     - Injection: into queries, shell commands, templates, generated markup or documents (scripts in
       stored text that a page or a document later shows), headers and logs (line breaks).
     - Paths and names: `..`, encoded `..`, absolute paths, odd separators, very long names, in any
       value that becomes a file, folder, key or URL; deletes or overwrites built from a value the
       caller can edit.
     - Outbound: any value that makes the server fetch, redirect or connect (internal addresses,
       loopback, metadata addresses, other schemes); open redirects.
     - Who the caller is: missing, expired, forged or another user's credentials or session;
       acting on another owner's records by changing an id.
     - Resources: many requests at once, huge bodies, slow bodies, archives that expand without
       bound, operations repeated until a limit should stop them.
     - Races and order: the same action twice at once, a crash or a kill halfway, a retry after
       success.
     - Secrets and leaks: secrets or personal data in responses, error messages, logs, shipped
       client files or the repo.
     - Dependencies: for each new one, what it does, what it runs at install, and whether a smaller
       built-in way exists.
     Skip a class that cannot apply and say why in one line. -->

- **Attacked:** `<base sha>..<sha>` on `feat/<order id>-<station>`, from `<detached worktree>`
- **Surface:** <the Attack surface rows and entry points attacked>
- **App run:** `<start command>` on port `<n>`, data in `<scratch folder>`
- **Result:** held | broken

## Proven findings

<Each one breaks the spec, loses or leaks data, or lets a caller do what it must not. Ordered by
severity. All proven findings are "Act on" for the expediter.>

### F1 · <short title>

- **Severity:** critical | high | medium
- **Class:** <attack class>
- **Where:** `<file>:<line>` or `<entry point>`
- **Run:** `<the exact command or script>`
- **Output:** <what it printed or did>
- **Required instead:** <the spec line or rule it breaks, quoted>

## Tried, held

<One line per attempt that did not break it: class, what you sent, what it answered. This is the
proof the surface was attacked, not skimmed.>

## Untested

<Each attack you could not run here (needs the internet, a real third-party account, production),
with the reason. These become questions for the owner, not findings.>
