---
name: rendering-specs-as-html
description: Use when writing a design spec or implementation plan document (brainstorming or writing-plans output) before asking the user to review it, and when editing any existing spec/plan that has an .html companion — the pair must stay in sync
---

# Rendering Specs and Plans as HTML

## Overview

Every design spec and implementation plan ships as a **pair**: the canonical `.md` plus a standalone `.html` companion, committed together. The `.md` is the full spec. The `.html` is the page the user reviews: one decision, shown in pictures and plain words, that fits on a screen or two. It does not mirror the `.md` section by section.

## Pick the size

| The change alters architecture, data flow, access/security, or UI structure? | Render | Template |
|---|---|---|
| No (config, rule, dependency, single-function work, most plans) | **Card** | `card.html` |
| Yes | **Review page** | `review.html` |

## Page contract

The HTML is these parts, in this order:

1. **Header:** chips (tracker key, product area, "Needs your approval"), an `h1` that starts "Approve:" and states the decision in one plain sentence, one lede sentence.
2. **Body.**
   - Card: "What changes" as `+` added, `−` removed, `=` unchanged lines, beside "Risk → answer". Text only.
   - Review page: four panels, each led by a picture, then "Risk → answer" as text rows. Text under a picture says what the picture can't show.
     - **1 Today and 2 The change draw the same scene in the same layout.** Draw panel 1, copy it into panel 2, then change only what the change changes: red marks what fails in panel 1; the accent and green mark the change in panel 2. Each of the two panels holds exactly a kicker, an `h2`, one `.pic` and one `.words` block, so the template lines their pictures up. A change the user sees draws miniature screens (`.mini`); a change with no screen draws an svg diagram. A `.pic` may stack several screens or diagrams. Greenfield work draws the current reality in panel 1 ("none yet", the manual process being replaced).
     - **3 How it runs:** numbered steps. Draw a swimlane only when the order of messages between parts is the design itself (a handshake, a lock, a retry).
     - **4 Where it goes:** a block map, one row per kind of thing the spec names, with its count, holding `+` new, `~` changed, `−` removed and `=` unchanged blocks.
3. **Strip:** "Decided" tags, "Open · recommend X" tags (each open question with your recommendation), "Not yet specified" tags (each open question in the `.md`'s Not yet specified section, with no recommendation), and a final "Your reply" tag. Leave out a tag kind with no items.
4. **One line** "Not in this change:" (the `.md`'s Out of scope).
5. **Footer:** the repo-relative path of the `.md`.

Plain words in headings and body; identifiers appear only in small `code` next to the plain name.

## Pictures

- Inline SVG and HTML/CSS only. Miniature screens are wireframes built from the page tokens: the real labels and controls, made-up sample values where the value tells the story (an account that should not appear, a wrong fee), skeleton bars (`.sk`) for the rest, never real user data. Mark changed text with `del` and `ins`, a changed area with `.spot.bad` / `.spot.good` plus a `.note` label, and a step between screens with `.hop`. Mini text stays at 11 px or larger.
- **SVG colors come only from the template's svg classes:** `node`, `node-bad`, `node-new`, `node-fix`, `edge`, `edge-bad`, `edge-new`, `edge-ret`, `lifeline`; text `muted`, `mono`, `bad`, `good`, `fix`, `halo` (for a label over a line); arrowheads `url(#ah)`, `url(#ah-new)`, `url(#ah-bad)`. A `fill` or `stroke` hex attribute ignores the dark block and turns unreadable.
- Every picture shows a state, a change or a structure. Risk rows, headings and the strip carry no icons.

## Look

- **Base tokens follow the project.** If the project has a design system or design skill (Hausback: `hausback-design-taste`, tokens in `packages/ui`), copy its values into every base token of the template's `:root` block (background, surfaces, lines, ink levels, accent and its tints, fonts); derive a token the project lacks from its nearest value. No project tokens: keep the template's values.
- **Meaning tokens never change:** red = today / removed / what fails, green = new / decided, amber = open, the project accent = the change, inverted ink = "Your reply". Every color also carries a text label or marker (`+`, `−`, "Open"), so meaning never rests on hue alone.
- **Dark mode only when the project defines dark tokens:** keep the templates' dark block and put the project's dark values in its base half; its meaning half stays as shipped. No project dark tokens: delete the block, and the page is light only. A dark-first project keeps the same shape: its light values go in `:root`, its dark values in the dark block, and the page follows the reader's system setting.
- Self-contained: inline CSS and inline SVG only, no CDN links, no web fonts, no external assets, no screenshots, no emojis. Font stacks name the project font first and fall back to system fonts.
- Works at phone width: the templates' grids collapse to one column under 820 px, and everything inside a panel wraps.

## Rules

1. **Pair, same basename, same directory:** spec `…/specs/YYYY-MM-DD-<topic>-design.{md,html}`, plan `…/plans/YYYY-MM-DD-<topic>.{md,html}`. Project locations override the path, never the pairing.
2. **The `.md` ends with two sections:** **Not yet specified** (in-scope questions you can name but can't yet phrase sharply enough to plan; don't pre-slice them into steps) and **Out of scope** (consciously ruled out, returns only if the goal is redrawn). A question sharp enough to state precisely gets a plan step or an open question, never fog. The HTML shows them as the strip's "Not yet specified" tags and the "Not in this change" line.
3. **Look at the page before you deliver it:** run `bash <this skill's dir>/shoot.sh <page.html> <scratchpad dir>` and read every PNG it lists (light, dark, phone tiles). Fix what you see, then shoot again: labels that overlap or clip, dark text on a dark fill, panels 1 and 2 that don't line up, and any `WARN` the script prints.
4. **Deliver before the review gate:** write both files, commit them together, print the absolute path of the HTML and the `.md`, THEN ask for review.
5. **Explicit user opt-out only:** if the user says to skip the HTML now, say it is owed and complete the pair at the next doc step.
6. **Stay in sync at every review gate:** an `.md` edit that changes what the user approved (decisions, scope, the delta) updates the `.html` in the same commit. Mid-execution bookkeeping (deviation-log entries, progress ticks) may batch until the next delivery or review gate. A pair left stale past a review gate is a violation; if the change is material to an approval, re-deliver per rule 4.

## Common mistakes

- Transcribing every `.md` section into the HTML. The page carries the decision; the `.md` carries the depth.
- Panel 2 drawn as a new picture. The reader compares panel 1 and panel 2 side by side; a different layout breaks that.
- A swimlane for work inside one component. Numbered steps read faster.
- Taking the accent for a meaning color (for example, a red brand accent). The meaning tokens stay fixed; pick the accent from the project only for "the change".
- Tracker or process status in the strip ("unassigned", "In Progress"). The strip holds spec decisions and questions only.
