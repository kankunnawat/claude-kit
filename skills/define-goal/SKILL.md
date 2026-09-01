---
name: define-goal
description: Use when the user asks to define or refine a measurable completion goal, requests /goal, $define-goal, the native goal tool, or explicit persistent goal-backed execution. Ordinary implementation does not trigger it.
---

# Define Goal

Define a judgeable outcome before activating persistence.
This shared skill supports Claude Code and Codex; use the matching runtime branch below.

Modified from the Apache-2.0 OpenAI `define-goal` skill for shared Claude Code and Codex use.

## Goal contract

Every goal names:

1. **Outcome and threshold:** a binary or numeric result, not an activity.
2. **Evidence:** the exact command, read-back, metric, or review that proves completion.
3. **Scope:** allowed paths, systems, and behavior boundaries when they matter.
4. **Stop condition:** when to report the blocker and options instead of grinding.

For "every X" goals, enumerate the bounded set inline or in the first response.
Rewrite vague goals when local context makes the validator safe to infer.
Ask one short question when the missing validator or environment changes the intended outcome.
Reject activity goals such as "make progress" until they become verifiable.

## Codex

If the user only requests a draft, return one concise objective and do not create a goal.

Create persistent state only when the user explicitly requests goal-backed execution:

1. Call `get_goal`.
2. Continue an active matching goal.
3. If no goal is active, call `create_goal` with the outcome, evidence, scope, and stop condition.
4. If an unfinished goal conflicts, ask the user to finish it or use a separate goal-backed thread.

Set `token_budget` only when the user explicitly requests one.
Do not create a goal for ordinary multi-step implementation.

## Claude Code

Return one paste-ready `/goal <condition>` line.
Drafting the line does not activate persistence unless the user explicitly asks Claude to set it.

The condition must be one paragraph under 4,000 characters.
The judge sees only the conversation transcript, so require named evidence "shown by `<command>` output in the conversation."
End with `OR Claude has posted a blocked summary naming the obstacle and options.`

`/goal` shows status, `/goal clear` stops it, and `/clear` also clears it.
For non-interactive use, `claude -p "/goal <condition>"` runs the loop in one invocation.

## Validator guide

| Domain | Completion evidence |
|---|---|
| Bug | Reproduction fails, then the same validator passes |
| Tests | Exact command exits successfully; repeat count for flakiness |
| Performance | Metric, target, measurement command, and run count |
| Review comments | Initial bounded list, requested changes, and fresh thread read-back |
| Research | Decision enabled, sources in scope, and evidence standard |
| Operations | Healthy state, observation window, failure threshold, and rollback trigger |

Example objective: checkout API p95 is below 250 ms across three consecutive benchmark runs, the checkout test command exits successfully, and changes stay within `src/checkout`.
