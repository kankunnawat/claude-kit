---
name: pickup
description: Use when the user says /pickup, "continue where we left off", "pick up the handoff", or pastes nothing but expects continuation — resumes from this project's persistent state (newest handoff or resume file), including work parked in a git worktree.
---

# pickup

Venue-agnostic verb for resuming work from persistent state. Counterpart of the `park` skill.

## Steps

1. **Gather candidates from ALL of these sources** — work often lives in a worktree the cwd scan can't see:
   - `RESUME FROM: <path>` lines in the auto-memory MEMORY.md (written by `park`; the most explicit signal)
   - every worktree from `git worktree list --porcelain`, applying the rules below inside each one — not just the checkout you launched in
   - per checkout, in preference order: the `Resume-from:` line in CLAUDE.md/AGENTS.md (explicit path or glob), newest file in `.handoffs/` (any `*.md`), `resume-state.md` / `docs/progress.md`
   A file reachable from several sources is one candidate. A handoff also present on `main` counts only for the branch/worktree it was written on — compare content or `git log --follow`, not just filename.

2. **Pick or ask.**
   - One in-flight task → take its most-recently-modified state file (a fresh handoff carries decisions and dead ends an older declared file predates).
   - Multiple distinct in-flight tasks (pointers or fresh handoffs for different branches/worktrees) → ask the user which to resume (AskUserQuestion), one option per task labeled by branch + handoff title + date. Never silently pick one.
   - A `RESUME FROM` pointer whose path or worktree no longer exists is stale: say so and fall back to the scan.
   - Nothing anywhere → say so and ask what to work on; don't invent state.

3. **Read it fully**, plus anything it links as required context. Cross-check
   against reality before acting (git log/status since the handoff was written —
   the state file may be stale; code wins). Resume in the checkout the handoff
   belongs to — cd into its worktree, don't redo the work on main.

4. **State the plan in 2–3 lines** (where things stood, what's next, the first
   verify check) and start. If the handoff's next step was completed by a later
   session, say so instead of redoing it.
