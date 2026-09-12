---
name: build-landing
description: >-
  Use when building or rebuilding a marketing landing page or small content site
  from a brief, or when resuming one mid-build: before the first visual is
  drawn, before a build plan is written, and before delivery. Not for app
  screens, dashboards, or a single-component change.
---

# build-landing

Method and lessons for building a landing page.
The project context supplies the site: audience, copy, allowed claims, SEO, framework choice, delivery target.
This skill never hardcodes a product, language, keyword, framework, or host.

Scripts are plain Node 22 and bash with no install step. Each answers `--help`.

## Context resolution (phase 0, before anything else)

The context is the site repo's `docs/` plus one portfolio folder when the repo's CLAUDE.md or AGENTS.md names one.
Read from the context in this order: brief, invariants (claims, SEO, template contract, delivery target), ledger, lessons.
A standalone site has only `docs/brief.md`. Write it in phase 0 from `templates/brief.md` through a one-question-at-a-time interview.
Every later phase reads project rules from the context, never from this file.

## Phases

Re-read the row for the phase you are entering before you start it. Rules read at kickoff are gone by the sixth task.
One todo per checklist item. The exit artifact must exist before the next phase starts.

| # | Phase | Checklist | Script | Exit artifact |
|---|---|---|---|---|
| 0 | Context and stack | resolve the context; interview one question at a time: goal, audience, primary action, pages; propose the framework with reasons (Astro is the default for a content-first page: static HTML, an island only where a control holds state, markdown articles) and ask once whether to override; scaffold; link the host project | none | brief in place, `build` passes |
| 1 | Guideline | brainstorm the visual questions with the owner, visuals through the brainstorming skill's visual companion, no artifact per question; fill `references/component-inventory.md` with no blank line; type scale with the body and eyebrow floors as named px values; palette with a measured ratio for every state pair, including lifted, answered, hovered, and focused grounds | `contrast.mjs` | `docs/design-guideline.md` complete, `.impeccable.md` filled from it |
| 2 | Directions | three genuinely different static references on one `design` canvas, desktop and mobile each, one tradeoff each, one recommendation; compare each with the benchmark before the owner sees them; the owner picks | none | chosen reference named in the guideline |
| 3 | Prototype | working browser prototype of scroll, hero or key motion, header, and the first interaction at desktop and mobile widths; run it with reduced motion on; the owner reviews it in a browser | `verify.mjs` | prototype address and its checks JSON |
| 4 | Plan | `superpowers:writing-plans` as an md and html pair; run the lint; fix the plan, not the implementations | `plan-lint.mjs` | plan reviewed by `review-plan`, lint clean |
| 5 | Build | `superpowers:subagent-driven-development`; UI tasks through `codex-first` at medium effort; every dispatch names its report file first and the controller reads the file, not the return value; every ruling goes to the ledger as it happens | none | final review clean |
| 6 | Verify | production build served at an explicit address whose asset hash matches the build; desktop and mobile viewport-pinned; walk the page at mobile width as a first-time reader; the checks the context adds | `verify.mjs` | checks JSON all true, screenshots |
| 7 | Deliver | merge, push, deploy, public address, unsigned request, hash parity, ledger row per the context's convention | `deploy.sh` | public URL with evidence lines |
| 8 | Lessons | write lessons from `templates/lesson.md` and file them where the context says; each lesson becomes a checklist line or a script here, never a paragraph | none | lessons filed |

Phases 1 to 3 are taste and stay with the top-tier model. Phase 5 is where Codex builds. Phases 6 and 7 are scripts either harness runs.

## Gates that block

- Phase 1 blocks on a blank inventory line. The header is a component; "the template's default" is a blank line.
- Phase 2 blocks without three directions on one canvas. Descriptions produce questions; artboards produce rulings.
- Phase 3 blocks phase 4. A static reference approves nothing about motion, header, or mobile.
- Phase 4 blocks on lint output. A px value under the floor in the plan costs one ruling per task that carries it.
- Phase 6 blocks on dev-mode evidence. Serve the built output.
- Phase 7 blocks on a signed-in response. Public means an unsigned 200.

## Scripts

| Script | Use | Lesson it guards |
|---|---|---|
| `scripts/contrast.mjs fg bg [fg bg ...]` or `--file pairs.txt`, `--min 4.5` | WCAG ratio per pair, non-zero exit under the minimum | contrast fails on state changes, not on the palette |
| `scripts/plan-lint.mjs plan.md --body 17 --min 12 [--astro]` | px values under the floors, `grep -c` on built HTML, compound selectors without `:global()`, dispatches without a report file | the plan carried the same floor violation three times |
| `scripts/verify.mjs --url http://127.0.0.1:4403 --out evidence/ [--viewports 1440x900,390x844 --header header --anchor faq --outbound example.com --article /path/]` | overflow, console, sticky header, anchor offset, keyboard focus, `details`, reduced motion, JS off, outbound attribution, screenshots | dev mode hides build-only bugs; headless Chrome cannot capture 390px |
| `scripts/deploy.sh <project> <public-host> [--scope team] [--check-only]` | build, deploy, project domain, unsigned check, stylesheet hash parity; `--check-only` verifies a live host without the two remote writes | `vercel domains inspect` lies; a plain alias stays behind sign-in |

Read the evidence, not the verdict. The first run of any harness reports harness bugs as site failures.

## References

- `references/component-inventory.md`: the phase 1 inventory with required behaviors per component.
- `references/lessons.md`: portable lessons, one line each, with the phase each guards.
- `references/frameworks/astro.md`: gotchas the lint and the build phase read when the repo is Astro. Add one file per framework as they get used.
- `templates/brief.md`, `templates/lesson.md`.
