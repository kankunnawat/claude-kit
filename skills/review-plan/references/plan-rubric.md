# Plan Review Rubric

Use this rubric when reviewing an **implementation plan** (file under `docs/superpowers/plans/`).

Walk every item top-to-bottom. For each, grade the artifact as **pass** or **gap**. Be specific — cite task numbers or section names. A gap without a pointer is not useful.

Group gaps into 🚫 / ⚠️ / 💭 / ❓ when reporting (see `gap-classification.md`).

---

## 1. Coverage — every spec requirement maps to ≥1 plan step

For each requirement in the underlying spec, find the plan step that delivers it. If you cannot find one, that's a 🚫 Blocker. Over-delivery (steps that don't trace to a spec requirement) is a ⚠️ Risk of scope creep.

## 2. Sequencing — steps are ordered by dependency

Read the plan as if executing top-to-bottom. Does step N ever reference something step N+k creates? If yes, the order is wrong. Forward references are 🚫 Blockers.

## 3. Verifiability — each step has an independent verification check

Every step should answer: *how do I know this step is done?* Acceptable checks: a test passes, a command succeeds, a specific file contains specific content, a screen renders correctly. "Implement X" without a verify check is under-specified.

## 4. Test placement — tests are planned before or alongside the code they cover

Implementation-first plans accumulate un-testable code. If tests are all clustered at the end, flag it as a ⚠️ Risk and recommend interleaving.

## 5. Edge cases — boundaries and failure modes are identified

For each step that touches logic, ask:
- What happens at the boundary (empty list, zero, nil, max value, concurrent access)?
- What inputs, states, or sequences does this not handle?
- What user action or system event could break the happy path?

Unhandled edge cases are either 🚫 Blockers (will cause failure) or 💭 Assumptions (worth validating before execution).

## 6. Regression surface — existing behavior that could break is called out

For each change, ask:
- What existing feature depends on the code being modified?
- Could this introduce O(n²) patterns, redundant fetches, render storms, N+1 queries, or lock contention?
- Does this touch shared state, cached data, or frequently-called paths?
- Could this affect unrelated screens or features?

Regression risks without mitigations are ⚠️ Risks at minimum.

## 7. Rollback and recovery — exists where the change is not trivially reversible

Migrations, file deletions, schema changes, and destructive operations need a rollback path or explicit "non-reversible" acknowledgement. Missing rollback on a destructive step is a 🚫 Blocker.

## 8. Granularity — steps are realistically sized

Red flags:
- A step like *"Add caching"* that obviously takes a day of work
- A 50-step mega-task the user is expected to track in their head
- Steps that mix multiple concerns (refactor + feature + test in one step)

Mis-sized steps are ⚠️ Risks — execution will either stall or skip over substeps.

## 9. Affected files / modules — identified per step

Each step should name the files or modules it touches. This surfaces unexpected scope ("wait, this step touches 14 files?") and helps the executor avoid surprises. Missing file lists on large steps are ❓ Open questions.

## 10. Scope discipline — no drift beyond the spec

If the plan proposes work that the spec did not ask for, flag it. Either update the spec first or remove the step. Silent scope drift is a ⚠️ Risk.

## 11. Assumptions — taken-for-granted facts are explicit

What does the plan assume about:
- API contracts and response shapes
- Data already present in the database / cache / state
- Behavior of libraries or frameworks
- Existing code working correctly

Unstated assumptions that, if wrong, would change the whole approach are 💭 Assumptions to validate.

## 12. Missing pieces — things obviously needed mid-execution

What will come up during execution that isn't in the plan? Config changes, feature flags, migration scripts, ops coordination, documentation updates. Ask: *if I hand this plan to a competent engineer and walk away, what will they trip on?*

## 13. Companion — the `.html` pair exists and is current

Per rendering-specs-as-html, every spec/plan ships as an `.md` + `.html` pair. A missing or stale companion is a **trivial gap** — render or update it as part of the review (auto-fix), don't surface it as a decision.

## 14. Closing sections — "Not yet specified" and "Out of scope" both present

Every plan ends with both:

- **Not yet specified** — in-scope questions you can name but can't yet phrase sharply enough to plan. Don't pre-slice them into steps.
- **Out of scope** — consciously ruled out; returns only if the goal is redrawn.

A missing section where the content is obvious from the document is a **trivial gap** (auto-fix). A question sharp enough to state precisely belongs in a plan step or an ❓ Open question, never parked in "Not yet specified" as fog — flag that misfiling as a gap.

---

## Specificity examples

✅ *"Task 3 says 'wire the WebSocket' but doesn't list which screens call `subscribe()`. The executor will guess. Add the file list or call out the affected screens."*

✅ *"Task 7 adds a `NOT NULL` column to `orders` with no backfill step and no down migration. On the production table the ALTER locks writes, and the deploy has no rollback path. Add the backfill + down migration, or split the change into add-nullable → backfill → constrain."*

❌ *"Task 3 is vague."*

❌ *"The plan could be more thorough."*
