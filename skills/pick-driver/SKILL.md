---
name: pick-driver
description: Use before non-trivial or multi-step work, before any step runs, to decide who drives it (interactive, goal, or loop). Also use when the user asks "goal or loop?", "how should we run this", or wants a goal line or loop prompt written.
---

# pick-driver

One workflow, three drivers. The workflow is always the normal chain: brainstorm, spec, plan, review plan, execute, self review, finish, with ceremony scaled to the change. The driver decides **who advances between steps** and **who calls done**. The driver never removes a step; only the size of the change does.

| Driver | Advances | Done judged by | Workflow inside |
|---|---|---|---|
| **interactive** (default) | the agent within the user's authorized scope | evidence against the requested outcome | full chain; pause only at explicit approval gates or unresolved blocking decisions |
| **goal** | the supported goal runtime, until the condition holds | evidence against the goal | same chain; every gate pre-decided |
| **loop** | the supported scheduler, re-reading its prompt each wake | stop conditions in the prompt | same chain per unit |

Decision order:
1. Interactive unless the user asks for unattended execution ("run this unattended", "as a goal", "I'm going to bed"). Multi-step or vague work is not a reason to leave interactive.
2. Unattended but any gating decision or taste call is still open → interactive until it is decided. Name the open decision and propose a default, so one reply unlocks the driver.
3. Unattended and pre-decided: waits between steps (CI, deploy, delegated work, a human) or more than one unit → loop. Otherwise → goal. A unit is one independently provable end state: one PR, one merge, one deploy. A campaign is a loop whose units are goal-shaped.

Before any goal, loop, or scheduled operation, read `references/runtime-routing.md`.
Detect the runtime from sanctioned runtime metadata and observable tools, then use only mechanisms verified there.
A missing reference or persistence capability blocks that unattended operation; continue authorized interactive work.
An unavailable required reviewer blocks integration; self-review is not a substitute.

Every driver preserves the requested outcome and evidence, the allowed scope and authority, approval gates, and blocker semantics.
Never broaden authority to make an unattended driver fit.

## Output at task start

One line: `Driver: <interactive|goal|loop> — <reason>.`
Then follow the selected runtime route, or proceed into the interactive workflow.

## Goal line

**A goal exists to buy autonomy over MANY turns. If interactive mode would finish the same work in one or two turns, do not set a goal; just do it.** Scope the goal to the outcome the user would call done, never to the next internal unit. Spec reviewed, plan written, one task green: those are checkpoints inside a goal, not goals. A feature's goal ends at the PR open with gate evidence (or the repo's close-out boundary); pre-implementation chores (allowlists, merge-forwards, decision-file edits) ride inside the same goal as ordered steps.

One paragraph with four parts:
1. Outcome + threshold (binary or numeric, never an activity).
2. Evidence: name the exact command, read-back, metric, or review available to the selected runtime's completion judge.
3. Scope: allowed paths / systems, which workflow steps run (spec, plan, review), and where their artifacts land.
4. Stop condition: report a blocker and options when the outcome cannot be reached without new authority or a blocking decision. A blocked or awaiting-approval report is not success.

Reject "make progress on X". Enumerate bounded "every X" sets inline. Anchor counts to a baseline captured before the first edit; "suite passes" is true of a suite that collects zero tests.

## When asked to choose between options

Give a recommendation first, then pros/cons per option, then the one fact that decides it. The user analyses alongside; a bare question without the trade-offs wastes the turn.

Keep it concise and plain: one line per pro or con, no jargon without a short definition, at most three per option. Each line names the concrete consequence for this task (what breaks, what it costs, what it needs from the user), not an abstract trait. Enough context to check the reasoning, not a survey.
