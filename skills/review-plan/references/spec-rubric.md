# Spec Review Rubric

Use this rubric when reviewing a **design spec** (file under `docs/superpowers/specs/`).

Spec review is a lighter pass than plan review — specs are abstract, so many gaps won't be visible until plan time. The goal here is to catch ambiguity, missing scope decisions, and untestable success criteria *before* `writing-plans` runs on top of a flawed foundation.

Walk every item top-to-bottom. Classify gaps using `gap-classification.md`.

---

## 1. Unambiguous requirements

Every requirement should have exactly one reasonable interpretation. Scan for phrasing like "handle errors gracefully", "performant", "robust" — these always hide decisions. Pin them down or flag them as ❓ Open questions.

## 2. Verifiable success criteria

For each goal, ask: *how would I test that this is met?* If the answer is "I'll know it when I see it," the criterion is not verifiable. Rewrite as something observable — a test passes, a metric crosses a threshold, a screen renders a specific state.

Unverifiable success criteria are 🚫 Blockers — the plan can't verify against them either.

## 3. Non-goals are stated explicitly

What is this design *not* doing? Specs that don't state non-goals invite scope creep at plan time. If non-goals are obvious from context, auto-fix by adding a "Non-goals" section. If they require a decision (is feature X in or out?), surface as ❓ Open question.

## 4. Edge cases and failure modes

Scan for:
- Empty / zero / nil / max boundary states
- Concurrent access, race conditions, partial failures
- Network failures, timeouts, auth expiry
- User actions that break the happy path

Unhandled failure modes in a spec are 💭 Assumptions (the spec implicitly assumes they won't happen) or 🚫 Blockers (the design will not work when they do).

## 5. Surfaced assumptions and constraints

What is taken for granted? Common categories:
- Existing code works the way you think
- An API behaves according to its docs
- Performance characteristics of a dependency
- User mental model / behavior patterns

Specs that don't surface assumptions push the discovery cost to execution time, which is the worst place to discover them. Flag unstated assumptions as 💭.

## 6. Right scope

Can this design be delivered as a single implementation plan (days to a couple weeks of focused work)? If it spans multiple independent subsystems, recommend decomposition *before* writing a plan. A monster spec produces a monster plan produces a monster execution failure.

Scope too big is a 🚫 Blocker. Scope suspiciously small (a one-liner spec) is a ⚠️ Risk that it's hiding complexity.

## 7. Consistent abstraction level

Specs should describe **what** and **why**, not **how** step-by-step. If you see "call `function_foo(x, y)`" in a spec, that's implementation leakage — belongs in the plan. Mixed abstraction levels are a ⚠️ Risk: readers can't tell what's a requirement vs. what's an arbitrary implementation choice.

## 8. Named dependencies

Does this design depend on:
- External systems, APIs, or vendor SDKs
- Work currently in flight elsewhere
- Configuration or infrastructure changes

Undeclared dependencies turn into execution surprises. Flag them as 💭 Assumptions or ❓ Open questions.

## 9. Companion — the `.html` pair exists and is current

Per rendering-specs-as-html, every spec/plan ships as an `.md` + `.html` pair. A missing or stale companion is a **trivial gap** — render or update it as part of the review (auto-fix), don't surface it as a decision.

## 10. Closing sections — "Not yet specified" and "Out of scope" both present

Every spec ends with both:

- **Not yet specified** — in-scope questions you can name but can't yet phrase sharply enough to plan. Don't pre-slice them into steps.
- **Out of scope** — consciously ruled out; returns only if the goal is redrawn.

A missing section where the content is obvious from the document is a **trivial gap** (auto-fix). A question sharp enough to state precisely belongs in a plan step or an ❓ Open question, never parked in "Not yet specified" as fog — flag that misfiling as a gap. Note the overlap with item 3: "Out of scope" and "Non-goals" may be the same section under either name; don't demand both.

---

## Specificity examples

✅ *"§Goals says 'make the balances API faster'. That's not verifiable. Recommend: 'p95 latency of GET /v2/balances < 250ms at 100 RPS on staging, measured by the existing k6 script.'"*

✅ *"Spec doesn't state whether paginated responses are in scope. If yes, the Portfolio aggregation described in §3 needs a different algorithm. Decide before planning."*

❌ *"The spec is ambiguous."*

❌ *"Needs more detail."*
