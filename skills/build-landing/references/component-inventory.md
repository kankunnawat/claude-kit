# Component inventory

Phase 1 fills one row per component in `docs/design-guideline.md`. A blank cell blocks phase 2. "The template's default" is a blank cell.

| Component | Decide and write down |
|---|---|
| Header | sticky or not; height per breakpoint; brand treatment (mark only until named); link set with destinations; the one primary action and where it sits at every width; mobile pattern (native `details` or other) and how it works with JS off; hide-on-scroll rule if any; anchor offset (`scroll-margin-top`); reduced-motion treatment |
| Hero | owns the first screen; the object or composition; motion driver (autoplay, pointer, scroll, none) and idle behavior; the static frame for reduced motion and JS off; fixed-aspect box, no layout shift; mobile composition with text, with the main action never below decorative staging |
| Primary interaction | purpose and form; initial state; progression (explicit Next or live); changing earlier answers; summary; reset; where feedback sits (beside the controls, in document order); keyboard model; JS-off content |
| Sections | count from the content; ground per section with at least three strong grounds, one dark or saturated; rhythm (poster vs reading, padding per breakpoint); heading scale per level with named floors; eyebrow rule; reveal motion and its reduced-motion treatment |
| FAQ or disclosure | native `details`; keyboard; open state styling; how many |
| Call-to-action band | one, loud; ground; the outbound link component and attribution |
| Footer | dark; attribution line; links |
| Secondary page | same system, simpler; header and footer shared; heading scale; column width; closing band |
| Ordinary scrolling | native or an enhancement with a reason; wheel, trackpad, touch, keyboard, anchors, focus, history all preserved; no long pinned scenes |
| Contrast | every text-on-ground pair and every state pair (hover, focus, answered, lifted, open) with its ratio from `scripts/contrast.mjs` |
| Type floors | body px, eyebrow px, smallest allowed px anywhere, as named values the plan lint reads |
