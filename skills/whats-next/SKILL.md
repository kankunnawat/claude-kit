---
name: whats-next
description: >-
  Use when the user asks "what's next", "whats next", "what's our current
  status",
  "is it done?", or "where are we" — a position check against this repo's live
  tracker, not a request to start work. Trigger: /whats-next or any of those
  phrases as a standalone prompt.
---

# whats-next

Answer position + next action from the repo's declared tracker, verified live.
Read-only: no doc edits, no artifacts, no starting the work.

## Venue

The repo's CLAUDE.md/AGENTS.md declares the source — a `Next-work:` line, or
an existing tracker declaration (JQL, Plane project, tracker file). No
declaration → fall back to: newest handoff/resume file, `git log` since last
session — and say the repo has no declared tracker.

Resolve the forge, remote, and base branch from repository declarations and Git configuration.
Fetch the relevant remote before comparing refs when network access is authorized.
If fetch or a live source is unavailable, label the stale evidence; do not claim live verification.
Use the forge's available read-only connector or CLI to inspect both merged and open pull requests.
Compare unpushed commits against the resolved upstream/base ref, and inspect `git worktree list`.
A pull request awaiting review or verification outranks the next tracker ticket.

## Rules

- Query the declared tracker in this turn; memory and document queues may be stale.
- Check available peer tools from the current runtime before proposing work. If unavailable, report that limit.
- Treat busy peers, locked worktrees, and recent branch activity as possible ownership. Do not propose work that maps to an active owner. Do not message or wait on peers for this status check.
- If ownership remains ambiguous, name the possible conflict for the user to resolve.
- Include this task's running workers, unpushed commits, and open worktrees.
- Report tracker/git disagreement. Merged work with an open tracker item may need authorized close-out.
- Do not call work unshipped from local refs alone. Check the branch's merged pull requests and compare against the resolved base branch.

## Answer shape

ADHD shape, ≤6 lines, no headers:

1. First line: the one next concrete action (command, ticket, or step).
2. Position: "X done, Y in progress/awaiting QA" with the 1-3 items named.
3. Blockers, only if real (who/what it waits on).

"Is it done?" gets a yes/no first, then evidence (test run, commit, PR state).
