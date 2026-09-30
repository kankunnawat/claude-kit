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

Scripts are plain Node 22 and bash with no install step, except that `verify.mjs` needs Playwright (local or global) and Chrome. Each answers `--help`.

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
| 1 | Guideline | brainstorm the visual questions with the owner, visuals through the brainstorming skill's visual companion, no artifact per question; fill `references/component-inventory.md` with no blank line, including open and close animation, JS-off and reduced-motion states, rapid reversal, and an artwork-integrated stop and restart affordance when motion needs a control; type scale with the body and eyebrow floors as named px values; palette with a measured ratio for every state pair, including lifted, answered, hovered, and focused grounds | `contrast.mjs` | `docs/design-guideline.md` complete, `.impeccable.md` filled from it |
| 2 | Directions | three genuinely different static references on one `design` canvas, desktop and mobile each, one tradeoff each, one recommendation; compare each with the benchmark before the owner sees them; the owner picks | none | chosen reference named in the guideline |
| 3 | Prototype | production-built browser prototype of scroll, hero or key motion, header, and the first interaction at desktop and mobile widths; check open and close, rapid reversal, JS off, and reduced motion; when timing matters, observe an intermediate frame and elapsed duration, not just the end state; the owner reviews it in a browser | `verify.mjs` | prototype address and its checks JSON |
| 4 | Plan | `superpowers:writing-plans` as an md and html pair; run the lint; fix the plan, not the implementations | `plan-lint.mjs` | plan reviewed by `review-plan`, lint clean |
| 5 | Build | `superpowers:subagent-driven-development`; UI tasks through the current runtime's authorized configured roles; preserve required high-taste roles and explicit model selections; every dispatch names its report file first and the controller reads the file, not the return value; every ruling goes to the ledger as it happens; before exit, read every page's copy against the copy bar and rewrite to it, one page at a time | `verify.mjs --phrase` | final review clean, copy bar met on every page |
| 6 | Verify | production build served at an explicit address whose asset hash matches the build; desktop and mobile viewport-pinned; walk the page at mobile width as a first-time reader; test both directions and rapid reversal of motion, JS off, reduced motion, and keyboard and touch controls; when timing matters, observe an intermediate frame and elapsed duration; the checks the context adds | `verify.mjs` | checks JSON all true, screenshots and motion observations |
| 7 | Deliver | complete the project's authorized delivery endpoint; merge, push, or deploy only within that authority; when publishing, pin the approved host target, verify its build output before deployment, then verify the public address with an unsigned request, all static file parity, and any context-supplied robots expectation; record evidence in the declared ledger | chosen host tooling; `deploy.sh` for Vercel only | requested artifact or URL with applicable evidence |
| 8 | Lessons | write lessons from `templates/lesson.md` and file them where the context says; record local lessons; change shared skills or scripts only when explicitly authorized | none | lessons filed |

Phases 1 to 3 retain approved visual gates and the required taste role. Phase 5 uses configured roles; either runtime can run supported verification and authorized delivery tools.

## Gates that block

- Phase 1 blocks on a blank inventory line. The header is a component; "the template's default" is a blank line.
- Phase 2 blocks without three directions on one canvas. Descriptions produce questions; artboards produce rulings.
- Phase 3 blocks phase 4. A static reference approves nothing about motion, header, or mobile.
- Phase 4 blocks on lint output. A px value under the floor in the plan costs one ruling per task that carries it.
- Phase 5 blocks on copy nobody has read against the bar. The bar is principle, the context fills it in: the page's search phrase in the places the context names (title, primary heading, description, first paragraph, one subheading by default); the context's permitted claims verbatim and nothing beyond them; no absolute or frequency word standing in for a measurement the page cannot show; one term per concept across every page; every call-to-action heading matching its own body; every generated summary or result qualitative unless the context permits a score. A findings list is not the exit; the rewrite is.
- Phase 6 blocks on dev-mode or end-state-only motion evidence. Serve the built output and inspect movement in progress.
- When phase 7 includes publishing, a signed-in response fails public verification. Public means an unsigned 200.

## Scripts

| Script | Use | Lesson it guards |
|---|---|---|
| `scripts/contrast.mjs fg bg [fg bg ...]` or `--file pairs.txt`, `--min 4.5` | WCAG ratio per pair, non-zero exit under the minimum | contrast fails on state changes, not on the palette |
| `scripts/plan-lint.mjs plan.md --body 17 --min 12 [--astro]` | px values under the floors, `grep -c` on built HTML, compound selectors without `:global()`, dispatches without a report file | the plan carried the same floor violation three times |
| `scripts/verify.mjs --url http://127.0.0.1:4403 --out evidence/ [--viewports 1440x900,390x844 --header header --anchor faq --outbound example.com --article /path/ --phrase "search phrase" --absolutes w1,w2]` | overflow, console, sticky header, anchor offset, keyboard focus, `details`, reduced motion, JS off, outbound attribution, screenshots; `--phrase` asserts placement on the page at `--url` (one run per page), `--absolutes` counts context-named words as a warning for a person to judge | dev mode hides build-only bugs; headless Chrome cannot capture 390px; copy written inside the build was read only after deploy |
| `bash scripts/deploy.sh <project> <public-host> [--scope team] [--expect-robots directives] [--check-only]` | Vercel only: local build, project/scope-pinned production host build, static-entry check, prebuilt deployment, domain binding, unsigned check, and byte parity for all static files; `--expect-robots` compares unscoped, value-free directive names supplied by context; otherwise the header is observed; `--check-only` rebuilds locally and verifies the public site without running Vercel, and prints the preflight, deployment, and domain commands | local build success does not prove the host output; HTML/CSS/JS parity can miss stale artwork and fonts |
| `bash scripts/test-deploy.sh` | local fake-tool fixture: target binding, failed or missing host output, check-only behavior, all static parity, and normalized robots expectations; rejects stale or missing assets and unsigned non-200 responses | delivery guards need failing-then-passing regression evidence |

Read the evidence, not the verdict. The first run of any harness reports harness bugs as site failures.

## References

- `references/component-inventory.md`: the phase 1 inventory with required behaviors per component.
- `references/lessons.md`: portable lessons, one line each, with the phase each guards.
- `references/frameworks/astro.md`: gotchas the lint and the build phase read when the repo is Astro. Add one file per framework as they get used.
- `templates/brief.md`, `templates/lesson.md`.
