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

Always, tracker or not, also check git-side state in the same turn: `gh pr
list`, unpushed branches, `git worktree list`. A PR parked awaiting the user's
review/verification (the /ship → review → /finish gap) outranks the tracker's
next ticket as the next action — the tracker won't show it.

## Rules

- **Verify live, never answer from memory** — memory and doc queues drift;
  query the declared tracker (JQL, Plane, tracker file) in this turn.
- Anything in flight from this session counts as position too (running
  subagents, unpushed commits, open worktrees).
- Tracker/git disagreement is a finding, not noise: tracker says In Progress
  but the PR is merged → a skipped /finish close-out is the next action.

## Answer shape

ADHD shape, ≤6 lines, no headers:

1. First line: the one next concrete action (command, ticket, or step).
2. Position: "X done, Y in progress/awaiting QA" with the 1-3 items named.
3. Blockers, only if real (who/what it waits on).

"Is it done?" gets a yes/no first, then evidence (test run, commit, PR state).
