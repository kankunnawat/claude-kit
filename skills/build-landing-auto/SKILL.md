---
name: build-landing-auto
description: >-
  Use when building or rebuilding a marketing landing page or small content site
  with configurable review checkpoints or a hands-free request. Not for app
  screens, dashboards, or a single-component change.
---

# Build landing auto

**REQUIRED:** Load `build-landing` and follow its phases, artifacts, scripts, and quality gates.
If unavailable, report the dependency and stop.
This wrapper changes decision ownership only.

## Set review ownership

Default to 75%.
An explicit "hands-free" or "fully automatic" request selects 100% unless the user specifies a level.
Explicit checkpoints and stop conditions override the preset, including "review-only" and "stop-after prototype".
Record the preset, checkpoints, and delivery endpoint in project notes before drawing visuals.

| Preset | Brief | Static direction | Browser prototype |
|---|---|---|---|
| 50% checkpoints | User reviews | User chooses | User reviews |
| 75% direction review | Agent drafts | User chooses | Agent evaluates |
| 100% hands-free | Agent fills from context | Agent chooses and records | Agent evaluates |

For an unsupported percentage or preset name, ask which listed schedule the user intends.
Continue gathering context while waiting.

At 50%, the brief review permits direction work.
The direction choice permits the prototype; prototype acceptance permits planning and the full build.
At 75%, prepare the brief and visual alternatives, then pause for the direction choice.
After that choice, evaluate the prototype, build, review, repair, verify, and deliver within authority.
At 100%, own routine decisions through delivery.

Apply ownership to routine interviews, framework choices, visual questions, and approvals in `build-landing` and its creative subskills.
At delegated checkpoints, record `agent-selected` or `agent-evaluated` with the preset and evidence.
Use the required artifact or ledger.
Never label an agent decision as owner approval.
Reuse exact approvals for matching actions, targets, and scope without asking again.

## Keep every quality gate

Retain all base artifacts, including visual alternatives, inventory, guideline, production-built prototype, reviewed Markdown/HTML plan, delivery evidence, and lessons.
Run contrast, plan lint, real copy and claims review with required rewrites, and production-build browser verification.
Keep desktop/mobile, motion, reduced-motion, JS-off, keyboard, touch, and asset-hash checks.
Read lint output even when it exits successfully.
Resolve every `CONFIRM` row with a recorded ruling before advancing.
Rule only on delegated decisions; unresolved user decisions wait for the user.

## Resolve context and authority

Use project facts, supported execution roles, required isolation, and actual permission gates.
Optional provider routes create no mandatory external dependency or sharing authority.
Ask a concise question for missing essential business facts or release authority.
Continue independent work while waiting; dependent gates stay blocked.
Do not invent claims or form recipients.
Without a named endpoint in the request or project context, deliver a verified local preview.
Exact prior push/deploy approval carries through to its matching endpoint.
Before outward actions, verify current repository and host destinations against approved targets.
Publishing retains unsigned public checks and built-asset parity.
Report a tool rejection and its reason; do not bypass it.

100% never grants indexing, domain purchases, tracker writes, or persistent-goal activation.
Use `define-goal` and the supported runtime only when the user explicitly requests a goal.
For invocation, endpoint, goal, and portfolio examples, read [references/usage.md](references/usage.md) when needed.
