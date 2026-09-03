---
name: review-plan
description: Use when the user asks for a plan or spec to be reviewed, gap-checked, or challenged before execution, or passes a plan/spec path for a second look — rubric-driven adversarial review that closes gaps, edge cases, and regression risks.
---

# review-plan

Stress-test a spec or plan artifact before it flows to the next stage. Apply a fixed rubric, auto-fix trivial gaps, surface decision-required gaps to the user, commit the updated file. The review is adversarial: it is trying to find real problems before implementation begins, not approving the document. A fixed rubric guarantees every review walks the same checks; when a gap bites in production, add a line to the relevant `references/*-rubric.md`.

## When this skill runs

- **When the user asks, or when a review is clearly wanted** (e.g. the user ordered "review then execute" ahead of time). Simple tasks shouldn't pay the review cost — don't chain it automatically from `brainstorming` or `writing-plans` without such a signal.
- Primary target: **plan files** (`docs/superpowers/plans/*.md`). Plans are concrete enough to critique, and plan→execution is the unguarded gate where regressions are born.
- Secondary target: spec files (`docs/superpowers/specs/*-design.md`) — a lighter pass with its own rubric.

## Checklist

1. **Find the artifact** — explicit path arg; else the most recent file in `docs/superpowers/plans/` (or `docs/plans/`); else the most recent in `docs/superpowers/specs/` (or `docs/specs/`). A project-declared plans/specs location overrides these defaults. If nothing is found, or the candidate is older than a day and the user didn't specify, confirm first. Tell the user which file you're reviewing and its date.
2. **Detect mode** — `plans/` → plan mode, `references/plan-rubric.md`; `specs/` → spec mode, `references/spec-rubric.md`; ambiguous → ask once.
3. **Load the rubric** plus `references/gap-classification.md`. If a reference file is missing, stop and name it — never fabricate rubric content.
4. **Walk the rubric** — grade every item Pass or Gap. A gap is a concrete claim pointing at a section or task ("Task 3 assumes the WebSocket is connected before calling subscribe(), but there's no connection guard"), never "the plan seems incomplete". Classify each gap per `gap-classification.md`.
5. **Auto-fix trivial gaps** inline in the artifact: a missing verification step whose check is obvious from the task, an under-specified step with a single obvious completion, a missing "non-goals" section clear from context, typos and broken internal references, file paths derivable from the spec or adjacent steps. Anything with a hidden design choice is decision-required, not trivial.
6. **Surface decision-required gaps** grouped as 🚫 Blockers / ⚠️ Risks / 💭 Assumptions / ❓ Open questions — one concrete claim per bullet with section, task, or line references; omit empty categories; ask one group at a time, Blockers first. Only escalate what the user genuinely needs to decide.
7. **Apply decisions** to the artifact.
8. **Re-run the rubric once** if step 7 made a material change (new task, clarified requirement, deleted non-goal). Further iteration is the user's call via manual re-invocation; the skill keeps no state.
9. **Commit** — `review: <artifact-filename>` with a short body listing trivial fixes and resolved decisions. Commit nothing outside the artifact and its immediate references. The `.html` companion (rendering-specs-as-html pair) **is** an immediate reference: carry the same fixes and decisions into it and commit both together.
10. **Report** in one line: "Review complete. N trivial fixes applied, M decisions resolved, K items passed. Ready to proceed."

## Reviewing code, not a document

This skill's rubrics grade plans and specs. When the artifact is a **diff, branch, or PR**, the rubrics don't apply — but the same review discipline does:

- Sync to the latest remote first (`git fetch origin`), so you review against what is actually there.
- Evaluate in order: **architecture > correctness > code quality > tests > performance.** The order is the priority: an architectural defect outranks a naming nit, always.
- For each issue: describe it concretely with `file:line` references, present the options with their tradeoffs, recommend one, and ask before proceeding. A finding that names a problem without a concrete failure scenario isn't finished.

For a final verdict with fresh context, dispatch the Fable-pinned `reviewer` agent rather than reviewing in the main loop.
