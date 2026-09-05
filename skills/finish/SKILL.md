---
name: finish
description: >-
  Use when the user confirms the work is good and wants it closed out (/finish, "ship it", "commit and push") — runs the project's declared Close-out ritual: commit, push, and whatever the "Close-out:" line in CLAUDE.md/AGENTS.md specifies. Not for unverified work.
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
   check nothing unrelated or secret is staged; unrelated work gets unstaged,
   not shipped along.
   A fix in a repo with a test suite carries at least one regression check for
   the fixed path. Scripts written to prove the fix get committed or folded
   into the suite, never discarded. A new check must fail when the fix is
   reverted — a check that can only pass proves nothing.

4. **Prove frontend changes visually.** If the shipped diff changes a
   user-facing frontend, the PR must carry visual evidence before merge.
   First check what images are already attached (e.g. by /ship): if they
   match the final diff and render, verify and move on — don't recapture.
   Text-only evidence (measurement tables, smoke counts, audit output) never
   satisfies this step; capture before merge. If images are missing or stale
   (the diff changed since capture), capture the final
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

5. **Execute in order.** An approval for an exact action, target, and scope
   persists through matching close-out steps; do not ask again. Otherwise ask
   once for that action before it leaves the machine. Apply this check to each
   outward-facing action except `git push` to the usual remote. `/finish` alone
   does not authorize every external action. Comments on another person's PR
   and artifacts or transitions created under the user's name in an external
   tracker always need content-and-scope approval (count, targets, and owner).
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

6. **Post-merge tail.** Rituals with steps *after* the merge — deploy
   verification, live smoke, tracker → Done, worktree cleanup — are the part a
   cleared session loses: the merge feels like the end, and only bookkeeping
   is left. Treat the tail as its own phase.
   - Before merging, list the outstanding tail steps in your report so they
     survive into the next context.
   - /finish is re-entrant: invoked on an already-merged branch, skip to the
     tail and run only what is outstanding.
   - Never report the close-out complete while a tail step is outstanding —
     name what remains.
   - A workflow checkpoint is not the requested task's completion boundary.
     Continue an already-authorized tail in the same task. Stop and report the
     incomplete state only when new authority or a real blocker is required.

   Required check failures trigger diagnosis and an in-scope repair. Do not
   integrate until every required check passes. Implementation authority does
   not grant deployment authority.

7. **Report** what was done in one short block: commit hash, branch/PR, tracker
   actions taken or skipped and why.

## Declaring a ritual (for CLAUDE.md authors)

One line, imperative, ordered:

```
Close-out: commit to main + push; if an issue key is in scope, post a tracker comment (RCA/solution shape) + matching status transition.
```
