---
name: pick-driver
description: Use before non-trivial or multi-step work, before any step runs, to decide who drives it (interactive, goal, or loop). Also use when the user asks "goal or loop?", "how should we run this", or wants a goal line or loop prompt written.
---

# pick-driver

One workflow, three drivers. The workflow is always the normal chain: brainstorm, spec, plan, review plan, execute, self review, finish, with ceremony scaled to the change. The driver decides **who advances between steps** and **who calls done**. The driver never removes a step; only the size of the change does.

| Driver | Advances | Done judged by | Workflow inside |
|---|---|---|---|
| **interactive** (default) | the user, each turn | the user | full chain; the user sees step N before N+1 |
| **goal** (`/goal <condition>`) | Claude, until the condition holds | a judge model reading the transcript | same chain; every gate pre-decided |
| **loop** (`/loop` + a prompt file) | the prompt file, re-read every wake | stop conditions in the file | same chain per unit |

Decision order:
1. Interactive unless the user asks for unattended execution ("run this unattended", "as a goal", "I'm going to bed"). Multi-step or vague work is not a reason to leave interactive.
2. Unattended but any gating decision or taste call is still open → interactive until it is decided. Name the open decision and propose a default, so one reply unlocks the driver.
3. Unattended and pre-decided: waits between steps (CI, deploy, subagents, a human) or more than one unit → loop. Otherwise → goal. A unit is one independently provable end state: one PR, one merge, one deploy. A campaign is a loop whose units are goal-shaped.

Both goal and loop die on `/clear`; context is the ceiling. A campaign ends each session at a boundary with a handoff (`park`) and relaunches with `pickup`.

## Output at task start

One line: `Driver: <interactive|goal|loop> — <reason>.` Then, for goal, the paste-ready line; for loop, confirm the prompt file exists or draft it; for interactive, proceed into the workflow.

## Goal line

One paragraph, under 4,000 chars, four parts:
1. Outcome + threshold (binary or numeric, never an activity).
2. Evidence: ``shown by `<command>` output in the conversation``. The judge reads ONLY the transcript, so the proof command must run inline, never only into a report file.
3. Scope: allowed paths / systems, which workflow steps run (spec, plan, review), and where their artifacts land.
4. Ends with: `OR Claude has posted a blocked summary naming the obstacle and options.`

Reject "make progress on X". Enumerate bounded "every X" sets inline. Anchor counts to a baseline captured before the first edit; "suite passes" is true of a suite that collects zero tests.

## Loop prompt file

The file is the program; the transcript is scratch. Sections, in order:
1. **Mission** as an outcome.
2. **Canonical inputs** read every wake, fixed order.
3. **State detection, derived only** from disk / git / tracker. Never store position in the file; a hand-written "current position" line drifts. The loop writes handoffs; it never edits its own program.
4. **Pre-decided rulings**, numbered and dated, never re-asked. Every park is a missing ruling: harvest it into this section before relaunch.
5. **Per-unit procedure**, one idempotent unit per wake: every step checks before it creates (claim, worktree, PR).
6. **Per-wake output contract**: advanced one unit or proved it is waiting; evidence written to a file; one-line position stated; then `ScheduleWakeup`.
7. **Caps**: context, wall clock, max wakes, repair rounds (one, then park).
8. **Stop and report**: done / blocked-on-owner / out-of-lane, each with what to write where.

Pacing: workers notify on completion, so the wakeup delay is a fallback (1200s+). Poll external state at its real cadence (one ~480s CI check, not eight 60s ones).

Workers write reports to files; the loop reads verdicts from files, never from agent replies. Judge (review) and worker (implement) are different agents.

## When asked to choose between options

Give a recommendation first, then pros/cons per option, then the one fact that decides it. The user analyses alongside; a bare question without the trade-offs wastes the turn.

Keep it concise and plain: one line per pro or con, no jargon without a short definition, at most three per option. Each line names the concrete consequence for this task (what breaks, what it costs, what it needs from the user), not an abstract trait. Enough context to check the reasoning, not a survey.
