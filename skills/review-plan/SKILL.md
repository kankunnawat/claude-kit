---
name: review-plan
description: Rubric-driven adversarial review of implementation plans and specs — closes gaps, edge cases, and regression risks before execution. Invoke when the user says "review the plan/spec", "gap-check this", "poke holes in this", "challenge my design", or passes a spec/plan path for a second look.
---

# review-plan

Stress-test a spec or plan artifact before it flows to the next stage. Apply a fixed rubric, auto-fix trivial gaps, surface decision-required gaps to the user, commit the updated file.

The review is adversarial by design — the reviewer is not approving the document, it is trying to find real problems before implementation begins.

## When this skill runs

- **When the user asks, or when a review is clearly wanted** (e.g. the user ordered "review then execute" ahead of time). Simple tasks shouldn't pay the review cost — don't chain it automatically from `brainstorming` or `writing-plans` without such a signal.
- Primary target: **plan files** (`docs/superpowers/plans/*.md`). Plans are concrete enough to critique, and plan→execution is the unguarded gate where regressions are born.
- Secondary target: spec files (`docs/superpowers/specs/*-design.md`). Spec review is a lighter pass using a different rubric.

## Why a rubric, not ad-hoc review

Without a fixed checklist, reviews drift into "whatever the reviewer happened to notice." A rubric guarantees coverage — every review walks the same checks, every time. Rubrics evolve: when a gap bites in production, add a line. Same pattern as CLAUDE.md global instructions, applied to review quality.

## Checklist

0. **Verify prerequisites** — confirm the rubric reference files exist before starting (see Step 0)
1. **Find the artifact** — explicit path, else most recent plan, else most recent spec
2. **Detect mode** — `plans/` → plan mode; `specs/` → spec mode; ambiguous → ask once
3. **Load the rubric** — read `references/plan-rubric.md` or `references/spec-rubric.md`
4. **Walk the rubric** — grade every item against the artifact, classify each gap using `references/gap-classification.md`
5. **Auto-fix trivial gaps** — edit the artifact file inline
6. **Surface decision-required gaps** — present as 🚫 Blockers / ⚠️ Risks / 💭 Assumptions / ❓ Open questions, ask the user one group at a time
7. **Apply decisions** — edit the artifact with the user's answers
8. **Re-run the rubric once** if any material change was made in step 7
9. **Commit** — `review: <artifact-name>` with a short body listing trivial fixes and resolved decisions
10. **Report** — "N trivial fixes applied, M decisions resolved, K items passed on first check. Ready to proceed."

## Step 0: Verify prerequisites

This skill depends on three rubric reference files living next to it in `references/`:

- `references/plan-rubric.md`
- `references/spec-rubric.md`
- `references/gap-classification.md`

Before doing anything else, confirm all three exist (`ls references/` or equivalent). If any is missing, stop and tell the user exactly which file is absent rather than failing partway through the review — the rubric is the whole point of the skill, and a partial review is worse than none. Do not fabricate rubric content to work around a missing file.

## Step 1: Find the artifact

Resolution order:

1. Explicit path arg from the user
2. Most recent file in `docs/superpowers/plans/`, else `docs/plans/` (sorted by date in filename)
3. Most recent file in `docs/superpowers/specs/`, else `docs/specs/`
4. If none found, or if the candidate is older than a day and the user didn't specify, confirm before proceeding

A project-declared plans/specs location overrides these defaults (same escape as rendering-specs-as-html). Tell the user which file you're reviewing and its date.

## Step 2: Detect mode

| Path contains | Mode | Rubric |
|---|---|---|
| `plans/` | plan | `references/plan-rubric.md` |
| `specs/` | spec | `references/spec-rubric.md` |
| ambiguous | ask once | — |

## Step 3–4: Walk the rubric

Read the rubric file. For each item, grade the artifact against it:

- **Pass** — the artifact satisfies this item cleanly
- **Gap** — the artifact does not satisfy this item

Be specific. A gap is a concrete claim pointing at a section or task: *"Task 3 assumes the WebSocket is connected before calling subscribe(), but there's no connection guard in the plan."* That is good. *"The plan seems incomplete"* is not.

Classify each gap using `references/gap-classification.md`. Trivial gaps are auto-fixed. Decision-required gaps are queued for the user.

## Step 5: Auto-fix trivial gaps

Edit the artifact directly. Typical auto-fixes:

- Missing verification step on a plan task (the verification is obvious from the task)
- Under-specified step that has a single obvious completion
- Missing "non-goals" section, where non-goals are clear from context
- Typos / broken internal references
- Missing file paths that are derivable from the spec or adjacent steps

If you are not certain a gap is trivial — if it has a hidden design choice — treat it as decision-required and surface it.

## Step 6: Surface decision-required gaps

Group by category and present concisely. Only escalate things the user genuinely needs to decide.

```
🚫 Blockers (N) — issues that will cause failure or wrong behavior if not addressed
⚠️ Risks (N) — things that could go wrong but may be acceptable
💭 Assumptions (N) — taken for granted; should be explicitly validated
❓ Open questions (N) — gaps where the document is silent
```

One concrete claim per bullet. Reference section names, task numbers, or line numbers. Ask one group at a time (start with 🚫 Blockers), not all four at once.

Omit any category with zero items.

## Step 7–8: Apply decisions and re-run once

Apply each user decision back into the artifact file. If any material change was made (a new task added, a requirement clarified, a non-goal deleted), walk the rubric one more time. Stop after one extra pass — further iteration is the user's call via manual re-invocation.

## Step 9: Commit

Stage and commit the updated artifact:

```
review: <artifact-filename>

- <trivial fix 1>
- <trivial fix 2>
- <resolved decision 1>
```

Do not commit anything outside the artifact file and its immediate references. The artifact's `.html` companion (rendering-specs-as-html pair) **is** an immediate reference — when one exists, carry the same fixes and decisions into it and commit both together; a `review:` commit touching only the `.md` of a pair violates the pair-sync rule.

## Step 10: Report

Summarize in one line:

> Review complete. `<N>` trivial fixes applied, `<M>` decisions resolved, `<K>` items passed. Ready to proceed with `writing-plans` / `executing-plans`.

## Second pass

If the user wants another review after changes, they re-invoke the skill manually. The skill does not track iteration state — re-invoking is one word, and avoiding state keeps the skill simple and portable.

## Portability

This skill runs in the current session using only `Read`, `Edit`, `Grep`, and `Bash` (for `git`). No subagent dispatch, no Claude-specific tooling. Behaves identically in Claude Code and Codex CLI.

## Reviewing code, not a document

This skill's rubrics grade plans and specs. When the artifact is a **diff, branch, or PR**, the rubrics don't apply — but the same review discipline does:

- Sync to the latest remote first (`git fetch origin`), so you review against what is actually there.
- Evaluate in order: **architecture > correctness > code quality > tests > performance.** The order is the priority: an architectural defect outranks a naming nit, always.
- For each issue: describe it concretely with `file:line` references, present the options with their tradeoffs, recommend one, and ask before proceeding. A finding that names a problem without a concrete failure scenario isn't finished.

For a final verdict with fresh context, dispatch the Fable-pinned `reviewer` agent rather than reviewing in the main loop.

## Self-improving the rubric

When a gap bites in production that the rubric should have caught, add a line to the relevant `references/*-rubric.md`. The rubric is a living document — it accumulates the project's scar tissue and gets better over time.
