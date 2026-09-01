---
name: park
description: Use when the user wants to freeze the session before clearing context mid-execution — /park, "create a checkpoint", "checkpoint before we clear", "context is getting long", "let's clear and continue in a fresh session" — while a multi-step chain (ship, SDD, plan execution, long debug) is still in flight. Not the built-in /rewind checkpoint; this writes resume state to disk. Counterpart of the pickup skill.
---

# park

Freeze a mid-execution session so a fresh one resumes without re-deriving anything. State on disk beats memory: after /clear the next session knows only what files and trackers say.

## Pick the boundary first

Finish the smallest in-flight unit whose result exists only in this session — an awaited subagent verdict, an unresolved review, an uncommitted edit. Subagents die with the session; a verdict not yet written to the tracker is lost. A worker minutes from reporting: wait for it, then freeze. A long-running worker: record in the handoff that its task must be **re-dispatched** (its brief/prompt path), never "wait for" a dead agent.

## Required elements — all six, every park

1. **Tracker closed to a boundary.** The ledger/progress file records every completed unit, every ruling, every deferred finding. Nothing load-bearing lives only in conversation.
2. **Handoff file** at the project's declared resume location (the repo CLAUDE.md's "Resume-from" convention; no convention → a `.handoffs/` scratch directory in the repo). Contents, each item one line where possible: position in the chain (done / **RESUME HERE** with the exact next dispatch or command), where everything lives (worktree, branch, plan, ledger, artifact URLs), standing decisions and rulings, deferred minors, gotchas discovered. Absolute dates only. Redact secrets — reference the local ignored file that holds them.
3. **Durable without committing the handoff.** The handoff file stays uncommitted — `.handoffs/` is globally gitignored, and committing personal scratch onto a feature branch leaks into the PR diff. Durability = the tracker (element 1, committed on the feature branch/worktree — never push main) plus the memory pointer (element 4). Only a repo that declares a tracked resume location gets the handoff committed there.
4. **Memory pointer — only if an auto-memory store exists** (a container without one skips this element). Update the auto-memory pointer file and its MEMORY.md line with `RESUME FROM: <handoff path>` (absolute path, or repo-relative with the worktree named). Memory loads regardless of cwd — this is what routes a fresh session into a worktree that a cwd-only scan of the main checkout would miss. The `pickup` skill reads exactly this string.
5. **Resume verb.** Tell the user exactly what to type after /clear: `/pickup`, `/ship <plan>`, or the chain's own skill.
6. **Downloads paste file — only if the user says they'll drive the next session by hand.** `~/Downloads/<slug>.md` per house paste rules: one unwrapped line per paragraph, no em dashes.

Then say: "safe to /clear" plus the resume verb. Nothing else.

## Common mistakes

| Mistake | Fix |
|---|---|
| Load-bearing ruling lives only in the handoff | The tracker is the committed record — write it there first (element 1) |
| Handoff on a branch the fresh session's /pickup can't see | The memory pointer (element 4) carries the path |
| "Wait for agent X" in the handoff | X is dead after /clear — write "re-dispatch with brief at <path>" |
| Freezing while a worker is seconds from reporting | Collect the verdict first; that's the boundary |
| Relative dates ("this morning's review") | Absolute dates only |
| Handoff duplicates plan/spec content | Reference artifacts by path/URL; never inline them |
