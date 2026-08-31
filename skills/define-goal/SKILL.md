---
name: define-goal
description: Use when the user asks for help writing a /goal condition, wants an unattended goal-backed run in Claude Code, or explicitly asks to turn a fuzzy objective into a judgeable completion condition. Also use before suggesting /goal; ordinary implementation does not trigger this skill.
---

# Define Goal (drafting /goal conditions)

## Overview

`/goal <condition>` makes Claude Code work unattended: after every turn, a small fast model (not Claude) reads the condition plus the conversation transcript and answers met / not-met; Claude keeps going until yes. **The judge cannot run tools or see external systems — a condition is met only when the transcript itself shows the proof.** Condition cap: 4,000 chars. Session-scoped; `/goal` alone shows status, `/goal clear` stops it, `/clear` also clears it.

Deliverable of this skill: one paste-ready `/goal ...` line. Activation is the user's move — they run the line themselves (or explicitly tell Claude to set it); drafting it never starts persistence. (Codex differs by design: its runtime activates via native goal tools on explicit request.)

## The condition contract — four slots, all REQUIRED

Write the condition as one paragraph containing:

1. **OUTCOME + threshold** — a binary or numeric bar, never an activity. Name the exact validator: command + pass condition ("`npm run test:checkout` exits 0"), or metric + target + measurement + reps ("p95 under 250 ms across 3 consecutive `npm run bench:checkout` runs").
2. **EVIDENCE in transcript** — append "as shown by `<command>` output in the conversation". External state (CI, GitHub, a deployed env) counts only via pasted output of a named read-back command (`gh pr view 482`, `gh run list`).
3. **SCOPE bounds** — what may change and what may not, whenever it constrains: allowed paths/modules, "no test deleted, skipped, quarantined, retried, or given a longer timeout", "no user-visible behavior change".
4. **STOP disjunct** — an honest exit: "OR Claude has posted a message stating it is blocked, on what, and the options" — so decision points escalate instead of grinding forever or self-approving.

**Bounded sets:** for "every X" goals (review comments, flaky tests, records), the condition must fix the set — enumerate it inline, or require it enumerated in the transcript's first turn ("the tests listed in Claude's first message") — otherwise the judge cannot decide completion.

## Repair before setting

- Vague outcome with a safe local rewrite → rewrite to the most honest binary validator and state the assumption inside the condition.
- Missing detail that changes the outcome (which metric? which environment?) → ask ONE short question first.
- Pure activity goal ("keep investigating", "make progress") → don't goal it; sharpen it or decline.

## Per-domain thresholds

| Domain | Success shape |
|---|---|
| Bug | repro shown failing, then the same validator shown passing |
| Tests | exact command + pass condition + rep count for flakiness |
| Perf | metric, target number, measurement command, run count |
| PR comments | set fixed by a listing at start; per item: reply exists + requested diff pushed, `gh pr view` pasted |
| Research | the decision it must enable + sources in scope + evidence bar |
| Ops | healthy-state definition, watch window, failure threshold, rollback/escalation trigger |

## Example

Good:

> /goal Checkout p95 latency is below 250 ms, shown by 3 consecutive `npm run bench:checkout` runs pasted in the conversation, with `npm run test:checkout` output showing 0 failures and no changes outside src/checkout/ — OR Claude has posted a blocked-summary naming the obstacle and the options.

Weak: `/goal make checkout faster` (no threshold, no evidence, no scope, no exit).

## Reminders when handing the line over

- `/goal` does not change permissions — for unattended runs pair it with an auto-accepting permission mode.
- Non-interactive: `claude -p "/goal <condition>"` runs the loop to completion in one invocation.
