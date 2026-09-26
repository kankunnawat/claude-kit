---
name: ship
description: >-
  Use when a design/spec has been approved and the user wants it implemented end to
  end — /ship, "ship it end to end", "execute subagent driven", "write plan,
  review plan and execute", or any spelled-out variant of that chain. Optionally
  takes a spec path (/ship docs/specs/foo.md). Not for trivial single-file
  edits, and not a merge/close-out verb — it stops at the PR boundary.
---

# ship

One word runs the approved-design execution chain. This skill only sequences
existing skills — it adds no procedure of its own.

## Precondition

An approved spec/design exists. Given a path argument, that file is the spec.
No spec and no approval in the conversation? Say so and stop — do not
brainstorm inside /ship.

## The chain

Prefix note: where superpowers is installed bare (no plugin), these skills
resolve without the `superpowers:` prefix — same skills, same order.

1. **superpowers:writing-plans** — write the implementation plan from the spec
   (with `rendering-specs-as-html` for the md+html pair, if your global rules
   call for one).
2. **review-plan** — adversarial gap-check of that plan.
3. **superpowers:subagent-driven-development** — execute. Never
   superpowers:executing-plans (main-loop implementation is banned). Implementer
   dispatch follows the repo's model routing; every spawn carries an explicit
   model pin and the reporting contract: every claim points at a tool result
   from the session, unverified items named as such.
   Do the skill's setup in the main loop first: worktree, ledger, pre-flight
   scan, one brief per task, and one routing question per plan. Write any
   plan-mandated destructive SQL, such as a `DELETE` or `DROP` migration
   body, during that setup, where the user sees it: a permission check can
   deny a workflow agent's write of it and stop the run.
   Invoking /ship does not pick the runner. In the routing question, ask
   the user to choose the saved `sdd-run` workflow or the skill's loop run
   by hand, with a short comparison for this plan and one recommendation:
   - `sdd-run`: one combined review per task, automatic fix rounds (round 3
     escalates), main loop idle. Fits many tasks with self-contained briefs,
     a clean pre-flight scan, and no expected rulings.
   - By hand: separate spec and quality reviews, controller judgment
     between tasks (skip or merge reviews on trivial tasks, stop drift
     early), the user sees each step, main-loop context grows. Fits few
     tasks, tasks that need rulings or taste calls, or a user who wants to
     watch.
   Record the pick in the ledger and in any handoff. For `sdd-run`, call
   `Workflow({name: 'sdd-run', args:
   {worktree, plan, spec, sdd, constraints, base, mergeBase, tasks: [{n,
   model}], notes}})`, with the repo's gate and forbidden commands in `notes`.
   It runs every task through implement, task review, and up to 3 fix
   rounds, then the final whole-branch review with one fix wave. When it
   returns, append its `ledgerLines` to the ledger. Rule on each
   `needsController` item as a ledgered `Ruling:`. Re-invoke it with the
   remaining tasks. Without the Workflow tool or the saved workflow, run the
   skill's loop by hand.
4. **Self review** — use the configured supported runtime mechanism on the full
   branch diff (`git diff <base>...HEAD`); apply confirmed in-scope fixes. This
   self-review cannot substitute for any independently required review.
5. **Verification evidence** — capture proof the change works (screenshots /
   command output, via the repo's verification harness) and attach it to the PR
   body before handing over for review — evidence gates the merge decision, it
   never lands post-merge. Uploading images through the repo's declared
   evidence route (CLAUDE.md/AGENTS.md), or through `finish`'s default GitHub
   user-attachments when none is declared, is part of this step when they show
   only synthetic or test data — do it before asking for review, not as a
   separate approval. Ask first only when an image may show real user data.
   The PR body also carries a risk line —
   `Risk: low|medium|high` plus a one-line reason (blast radius, surfaces
   touched) — so the reviewer's depth can match it:
   low = evidence check only, high = full diff read.
6. **Stop at the PR/merge boundary by default** — open the PR per repo
   convention with the evidence attached. Merge/tracker close-out stays with
   the `finish` skill unless the user already authorized it for this task. A
   skill endpoint is a checkpoint, not proof that the requested task is done;
   continue any already-authorized close-out in the same task.

Steps run end to end without per-step approval; stop only for destructive
actions, decision-required gaps, or genuine scope changes (deviation protocol
applies throughout).

Diagnose and repair in-scope failures from required checks. Do not integrate
until every required check passes. Implementation authority does not grant
deployment authority. If repair needs new authority or a real blocker remains,
report the task as incomplete and name what is needed.

## Checkpoint override

"pause after plan" / "pause after review-plan" / `--pause-after plan`: run
through that step, report position ("plan written and reviewed, execution
pending"), and stop so the user can clear context and resume in a fresh session
(resume = /ship with the plan path).
