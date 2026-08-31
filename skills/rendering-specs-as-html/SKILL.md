---
name: rendering-specs-as-html
description: Use when writing a design spec or implementation plan document (brainstorming or writing-plans output) before asking the user to review it, and when editing any existing spec/plan that has an .html companion — the pair must stay in sync
---

# Rendering Specs and Plans as HTML

## Overview

Every design spec and implementation plan ships as a **pair**: the canonical `.md` plus a standalone styled `.html` companion. Both are committed together; the HTML path is reported to the user to open in a browser. The user reviews the HTML, not the terminal markdown.

## The Rules

1. **Pair, same basename, same directory:**
   - Spec: `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` + `.html`
   - Plan: `docs/superpowers/plans/YYYY-MM-DD-<topic>.md` + `.html`
   - Project-specific spec locations override the path, never the pairing.
2. **HTML is self-contained:** inline CSS only, no CDN links, no external assets, no screenshots. Start from `template.html` in this skill directory (dark glass theme: near-black with subtle glow, frosted cards, violet/emerald accents, numbered sections). No emojis anywhere — callout labels are styled text.
3. **Before → after diagram** is required whenever the change alters architecture, data flow, or UI structure — as the first content section after the TL;DR:
   - Backend/system work → side-by-side **system-design** diagram (components + data flow).
   - Frontend work → side-by-side **app-design view** (UI structure mock in HTML/CSS).
   - Both columns required. A target-state-only diagram is a violation — the point is the delta.
   - Use the `.ba` grid from the template; mark removed components with `.fbox.dead`, label new vs kept vs removed parts with `.pill.new` / `.pill.keep` / `.pill.gone`.
   - Greenfield work that builds structure has a before column too: the current reality — "none yet", the manual process being replaced, or the adjacent system being extended. Never omit the column.
   - Plans that change none of those (config/rule/dependency/single-function work) skip the diagram — the pair still ships, as a plain render. This is an objective test, not a hurry escape: if components, data flow, or UI structure move, the diagram is owed.
4. **Approaches considered** render as option cards (`.approach`), chosen one marked `.approach.win`.
5. **Deliver before the review gate:** Write both files → commit together → print the absolute path of the HTML (and the canonical `.md`) for the user to open in a browser. THEN ask the user to review.
6. **Explicit user opt-out:** if the user explicitly says to skip the HTML right now, defer it — say it's owed, and complete the pair at the next doc step (e.g. with the plan). Never silently drop it; "user seems busy" is not an opt-out.
7. **Every spec/plan ends with two sections**, in both the `.md` and the `.html`:
   **Not yet specified** — in-scope questions you can name but can't yet phrase
   sharply enough to plan; don't pre-slice them into steps — and **Out of scope** —
   consciously ruled out, returns only if the goal is redrawn. A question sharp enough
   to state precisely gets a plan step or an open question, never fog.
8. **The pair stays in sync at every review gate:** edits to the `.md` that change what the user approved (review decisions, scope changes) update the `.html` in the same commit — including the before→after diagram if the delta changed. Mid-execution bookkeeping appends (deviation-log entries, progress ticks) may batch: defer the re-render to the next delivery or review gate, one render covering all accumulated edits. A pair left stale past a review gate is a violation. If the change is material to something the user approved, re-deliver the updated HTML per rule 5.

## Common Mistakes

| Mistake | Reality |
|---|---|
| HTML written to `/tmp` only | The HTML is committed next to the `.md` — it is part of the doc, not a throwaway render |
| Diagram shows only the target state | Before AND after columns, side by side. The reader needs the delta |
| "User is in a hurry, skip the HTML" | The HTML IS the review artifact — skipping it slows the user down, not speeds up |
| Rendering only the spec, not the plan | Both spec and plan get the pair treatment |
| Linking external CSS/fonts/mermaid CDN | File must open offline as-is; inline everything |
| Markdown dumped into `<pre>` | Real HTML structure: numbered `h2`, tables, callouts, flow boxes per the template |
| Spec `.md` edited mid-implementation, HTML left stale | The HTML is what the user approved — a stale pair records approval of a doc that no longer exists. Update both in the same commit |
