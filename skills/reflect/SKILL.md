---
name: reflect
description: >-
  Use when explicitly asked to reflect on a completed task or correction and prevent recurrence.
  Excludes routine close-out and broad agent audits.
---

# Reflect

Turn a witnessed lesson into the smallest useful guard.
A reflection can end with no change.

1. Read the task's feedback and relevant diff, test output, or other direct evidence.
   State what happened, its impact, and the likely cause.
   Mark uncertain causes as uncertain.
   Resolve a disputed correction with the user before treating it as a lesson.
2. Check for an existing test, script, repo rule, or skill that should have caught it.
   Trace whether the failure came from this repo or a shared tool or workflow, and whether it recurred across projects.
   Repair that guard first.
   Do not add a second guard for the same failure.
3. Choose a durable change only when recurrence is plausible and the guard would catch it:
   - Deterministic regression: a focused test or check beside the failing code.
   - Repo-specific invariant: the repo's `AGENTS.md` or equivalent checked-in guidance.
   - Shared tool or portable method: the shared script or skill; create one only when the evidence warrants it.
   - Truly universal rule: global `AGENTS.md`.
   - Personal memory: only when the user explicitly asks to save it.

   If the case was a one-off, lacks evidence, or already has a sufficient guard, report the lesson without writing.
4. Explicit invocation authorizes the smallest reversible, evidence-backed guard in the active project when its target is clear.
   Apply it without another approval step.
   Ask before unclear, shared, global, destructive, or external changes, including personal memory and tracker writes.
   Preserve existing approval gates for comments and release actions.
5. Re-run the original failure case or a close check against the guard.
   For skill or script edits, run existing validation and keep a fix-proving check in the repo when applicable.
   If it still fails, revise within scope and check again.
   Report what the evidence proves and what remains unverified.
   On a later recurrence, update or remove the guard based on new evidence instead of stacking rules.

Report: **Lesson**, **guard changed or skipped**, **check result**, and **remaining risk**.
This skill does not replace task close-out, agent setup audits, or user-approved personal note capture.
