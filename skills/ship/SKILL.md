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
4. **Self review** — use the configured supported runtime mechanism on the full
   branch diff (`git diff <base>...HEAD`); apply confirmed in-scope fixes. This
   self-review cannot substitute for any independently required review.
5. **Verification evidence** — capture proof the change works (screenshots /
   command output, via the repo's verification harness) and attach it to the PR
   body before handing over for review — evidence gates the merge decision, it
   never lands post-merge. Image uploads that need an external route (e.g. the
   secret-gist technique) require the user's explicit go-ahead first. The PR
   body also carries a risk line — `Risk: low|medium|high` plus a one-line
   reason (blast radius, surfaces touched) — so the reviewer's depth can match
   it:
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
