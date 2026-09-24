---
name: rendering-specs-as-html
description: Use when writing a design spec or implementation plan document (brainstorming or writing-plans output) before asking the user to review it, and when editing any existing spec/plan that has an .html companion — the pair must stay in sync
---

# Rendering Specs and Plans as HTML

## Overview

Every design spec and implementation plan ships as a **pair**: the canonical `.md` plus a standalone `.html` companion, committed together. The `.md` is the full spec. The `.html` is the page the user reviews: one decision, told in plain words, that fits on a screen or two. It does not mirror the `.md` section by section.

## Pick the size

| The change alters architecture, data flow, access/security, or UI structure? | Render | Template |
|---|---|---|
| No (config, rule, dependency, single-function work, most plans) | **Card** | `card.html` |
| Yes | **Review page** | `review.html` |

## Page contract

The HTML is these parts, in this order:

1. **Header:** chips (key, area, "Needs your approval"), an `h1` that starts "Approve:" and states the decision in one plain sentence, one lede sentence.
2. **Body.**
   - Card: "What changes" as `+` added, `−` removed, `=` unchanged lines, beside "Risk → answer".
   - Review page: four panels. 1 Today (the before picture), 2 The change (the after picture), 3 How it runs (numbered steps), 4 Where it goes (what it touches and what stays). Then "Risk → answer". Panels 1 and 2 are the before → after delta and are required; greenfield work shows the current reality in panel 1 ("none yet", the manual process being replaced).
3. **Strip:** "Decided" tags, "Open · recommend X" tags (each open question with your recommendation), "Not yet specified" tags (each such `.md` item as written, with no recommendation), and a final "Your reply" tag.
4. **One line** "Not in this change:" (the `.md`'s Out of scope).
5. **Footer:** the path of the `.md`.

Plain words in headings and body; identifiers appear only in small `code` next to the plain name.

## Look

- **Base tokens follow the project.** If the project has a design system or design skill (Hausback: `hausback-design-taste`, tokens in `packages/ui`), copy its background, surface, line, ink, muted, accent and font values into the template's base `:root` block. No project tokens: keep the template's values.
- **Meaning tokens never change:** red = today / removed / what fails, green = new / decided, amber = open / needs an answer, the project accent = the change, inverted ink = "Your reply". Every color also carries a text label or marker (`+`, `−`, "Open"), so meaning never rests on hue alone.
- **Dark mode only when the project defines dark tokens:** then add a `@media (prefers-color-scheme: dark)` block that redefines the base tokens. Otherwise the page is light only.
- Self-contained: inline CSS and inline SVG only, no CDN links, no web fonts, no external assets, no screenshots, no emojis. Font stacks name the project font first and fall back to system fonts.
- Works at phone width: the templates' grids collapse to one column under 820 px; keep it that way.

## Rules

1. **Pair, same basename, same directory:** spec `…/specs/YYYY-MM-DD-<topic>-design.{md,html}`, plan `…/plans/YYYY-MM-DD-<topic>.{md,html}`. Project locations override the path, never the pairing.
2. **The `.md` ends with two sections:** **Not yet specified** (in-scope questions you can name but can't yet phrase sharply enough to plan; don't pre-slice them into steps) and **Out of scope** (consciously ruled out, returns only if the goal is redrawn). A question sharp enough to state precisely gets a plan step or an open question, never fog. The HTML shows them as the strip's "Not yet specified" tags and the "Not in this change" line.
3. **Deliver before the review gate:** write both files, commit them together, print the absolute path of the HTML and the `.md`, THEN ask for review.
4. **Explicit user opt-out only:** if the user says to skip the HTML now, say it is owed and complete the pair at the next doc step.
5. **Stay in sync at every review gate:** an `.md` edit that changes what the user approved (decisions, scope, the delta) updates the `.html` in the same commit. Mid-execution bookkeeping (deviation-log entries, progress ticks) may batch until the next delivery or review gate. A pair left stale past a review gate is a violation; if the change is material to an approval, re-deliver per rule 3.

## Common mistakes

- Transcribing every `.md` section into the HTML. The page carries the decision; the `.md` carries the depth.
- Taking the accent for a meaning color (for example, a red brand accent). The meaning tokens stay fixed; pick the accent from the project only for "the change".
- A review page with only the after picture. Panels 1 and 2 are both required.
