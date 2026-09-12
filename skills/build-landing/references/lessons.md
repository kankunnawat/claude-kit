# Lessons

One line each, portable across sites and frameworks. The phase number is the checklist row that guards it. A lesson that names a product, a host team, or a portfolio convention belongs in the project context, not here.

## Phase 0, context

- The brief's seed is a seed. Record the owner's ruling back in the brief the same day, or the next site inherits the wrong default.
- Copy-forward of shared rules matches the exact heading line; a loose match duplicates the file.
- Rules that exist only in a branch are invisible. Scaffold and copy from current main only.

## Phase 1, guideline

- A cautious first pass costs a full redesign. Brainstorm to a written guideline, then references, then build only against the approved one.
- The header was never designed. Every component in the inventory gets a filled line; the template's default is a blank line.
- Placeholders that look finished get built on. A placeholder must look like one.
- Positioning is settled before the page is built: positioning, visual direction, interaction states, motion driver, idle behavior.
- Contrast fails on state changes, not on the palette. Measure every control state that changes ground.
- Feedback sits beside its controls in document order, before large diagrams.
- Removing a control can change the motion driver. Name autoplay or scroll; keep an accessible pause for autoplay.
- Interaction patterns are site-specific. One site's questionnaire rules do not replace another site's comparator.
- Accessibility designed in at the guideline stage costs nothing later: reduced motion, keyboard, JS off, native `details`.

## Phase 2, directions

- The owner decides from things on a screen, not from prose. Three options side by side, one tradeoff each, one recommendation.
- References carry visual qualities, not product direction. Borrow composition, typography, material, lighting, density, pacing, motion; keep audience, question, offer from the brief.
- Vet visual craft against the benchmark before owner review.

## Phase 3, prototype

- A static reference does not approve motion or mobile behavior. A loop that never stops, a nav that wraps, a 9.6px label: none is visible in a PNG.
- Judge the complete page after the hero. Repeated display-size supporting headings and generous spacing make a page long and flat.

## Phase 4, plan

- The plan carried the same floor violation three times. Lint the plan; fix the plan, not the implementations.

## Phase 5, build

- A visual rebuild keeps its working foundations: approved content, pure logic, articles, SEO safeguards.
- Review reports do not survive transit. Name the report file first; read the file, not the return value.
- The ledger is the only thing that survives compaction. Rulings go to the ledger as they happen; the resume pointer is rewritten last.
- Rules read at session start are gone by the sixth task. Re-read the phase row before entering the phase.
- Copy written inside the build gets read after deploy, and a copy fix then costs a redeploy and a recapture. Read every page against the copy bar before the build exits.
- A copy review that ends in a findings list ships nothing. The bar is met by the rewrite; findings are the owner's approval step, not the deliverable.
- Absolute and frequency words ("most", "every time", "almost always") stand in for measurements the page cannot show. The context names the words for its language; the script counts them; a person judges each.
- The search phrase belongs where a reader and a crawler both look first: title, primary heading, description, first paragraph, one subheading. Only the title and heading get checked by habit; name all five.
- A call-to-action heading is read against its own body. A heading that asks for a call above a body that says "look first" contradicts the page's tone.

## Phase 6, verify

- Dev mode hides build-only bugs. Check the built output at an explicit address and match the asset hash.
- Single-engine coverage cannot see fallback bugs. `@supports` around partially supported CSS.
- Unit tests protect the pure modules and nothing else. The browser harness is the test suite.
- Verification harnesses need verifying. Read the evidence, not the verdict.
- Wheel easing can swallow native keys. Start inertia, send scroll keys and modified keys, confirm the default is not cancelled.
- Emulation is not the device. Label emulated touch and simulated lifecycle as such.
- Build-mutating tests corrupt a served preview. Test, then build, then serve; never overlap.
- Measure the behavior under test, not the harness. Separate input, transition, and settling.
- Headless Chrome cannot produce a 390px capture on macOS. Viewport-pinned Playwright on system Chrome.
- Built HTML is one line. Count with `grep -o ... | wc -l`, never `grep -c`.

## Phase 7, deliver

- Platform facts cost round trips until written down. Verify team, permissions, and public response per project.
- Rules match team size. One owner and one agent commit to main.
- A CLI's domain inspection can lie about a serving domain. Verify with an unsigned request and hash parity.
