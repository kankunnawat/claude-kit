---
name: finish
description: Use when the user confirms a fix/feature works, or says /finish, "ship it", "wrap it up", or "commit push [and post jira]" — executes this project's declared definition-of-done ritual (commit, push, and whatever the "Close-out:" line in CLAUDE.md/AGENTS.md specifies).
---

# finish

Venue-agnostic close-out verb: the workflow is invariant, the project supplies
the specifics. **Only run once the user has confirmed the work is good** — never
to force closure on unverified work.

## Steps

1. **Resolve the ritual.** Look for a `Close-out:` line in the project's
   CLAUDE.md / AGENTS.md (repo root, then parents). No line → default ritual:
   commit + push, nothing else. Then resolve context the ritual needs: ticket
   key (branch name → conversation → recent commits), current branch, base
   branch.

2. **Prove tracker consistency.** When GitHub issues are in scope, fetch every
   issue targeted by `Closes`/`Fixes` and inspect its body live. If any checklist
   item remains unchecked, fail closed: use `Refs` and leave it open unless the
   user explicitly confirms closure or every remaining item is moved to linked
   trackers.
   Classify parent/umbrella versus leaf issues, and search semantic
   cross-references for the ticket/PR, including dependency prose without
   checkbox syntax. In issue bodies, explicitly mark each completed dependency:
   check its existing box or convert its dependency line to a checked item.

3. **Preflight.** Run the project's tests/linters for the touched area if the
   ritual or repo rules require green-before-commit. Review the full diff —
   check nothing unrelated or secret is staged.

4. **Prove frontend changes visually.** If the shipped diff changes a
   user-facing frontend, the PR must carry visual evidence before merge.
   First check what's already attached (e.g. by /ship): if it matches the
   final diff and renders, verify and move on — don't recapture. If evidence
   is missing or stale (the diff changed since capture), capture the final
   implemented app itself with representative synthetic/test data. Generated
   images, mockups, and design references do not satisfy this proof. Cover
   desktop, mobile, and each materially changed state needed for review (for
   example list and detail).
   Resolve the capture harness and attachment mechanism from the project's
   CLAUDE.md/AGENTS.md and memory store — projects differ (seeded local dev +
   gist embeds, Playwright recording as a PR comment, signed sim build,
   proof-agent report gate). No declared convention → default: capture with
   the repo's usual harness and attach as GitHub user-attachments. Either
   way, verify every image/video actually renders in the PR.

5. **Execute in order**, confirming before each outward-facing step (anything
   leaving the machine besides `git push` to the usual remote — Jira/issue
   comments, status transitions, PR creation, notifications).
   Complete all close-out bookkeeping — tracker edits, ledger/status-doc
   updates — *before* the first PR push, so it rides the same commit set.
   Never trigger another full CI run solely for tracker or ledger edits; rerun
   only after substantive changes or a failed-gate repair. Typical steps a
   ritual declares:
   - commit (project's commit convention, ticket key in subject)
   - push (branch policy per the ritual — direct vs feature branch + PR)
   - tracker update (e.g. Jira comment + matching status transition — use the
     project's declared comment shape)
   - status-doc/memory updates
   Skip any step whose precondition is absent (no ticket key → no tracker
   step; say so). After merge, re-read the tracker state and checklist; reopen
   an umbrella that was auto-closed with unchecked work and report the repair.

6. **Report** what was done in one short block: commit hash, branch/PR, tracker
   actions taken or skipped and why.

## Declaring a ritual (for CLAUDE.md authors)

One line, imperative, ordered:

```
Close-out: commit to main + push; if a BMIV key is in scope, post Jira comment (RCA/solution shape) + matching status transition.
```
