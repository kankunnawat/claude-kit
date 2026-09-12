# Astro

Read in phase 4 (plan lint with `--astro`) and phase 5 (build) when the repo is Astro.

- Astro stamps its scope id on every compound selector in a page or component style block. An element rendered by a child component (a link component, a slot) carries no scope id, so `.col > .btn` matches nothing in built CSS. Write `.col > :global(.btn)`.
- Keep `animation-timeline` in a separate rule from the `animation` shorthand. The build's CSS transformer folds them into one shorthand Chrome rejects; dev mode does not, so the bug appears only in the built site.
- Partially supported CSS (scroll-driven animation, `::details-content`) goes behind `@supports`. An animation shorthand whose timeline rule is dropped runs for 0s and sticks on its end keyframe.
- A top-level `const top` in a classic inline `<script is:inline>` throws "Identifier 'top' has already been declared": `window.top` is unforgeable. Name it something else.
- `astro preview` refuses to start when another preview is running anywhere on the machine. Serve `dist/` with any static server at an explicit address instead.
- Content collections: articles are markdown with frontmatter the template contract names; keep the collection schema in `src/content.config.*` in step with it.
- Islands only where a control holds state. Everything else ships as static HTML so the JS-off check passes for free.
