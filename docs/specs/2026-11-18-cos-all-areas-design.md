# One chief of staff, a lead per area: design

Date: 2026-11-18.
Status: needs Kan's approval.
Home: `skills/cos/`, a new `skills/lead/`, and `skills/unblock-all/` in this repo (claude-kit).

## Goal

Kan works from one queue instead of switching between dozens of threads.
One chief of staff (CoS) session oversees every area he works on.
Each area has one lead session that runs the work there.
Everything Kan must decide or review reaches him in one prioritized list, with the evidence attached.
Every change still passes the same human review and the same merge gates.

The shape comes from the post that started `/cos`: one lead agent per area of focus, a chief of staff agent over them, one prioritized queue, and a system that keeps learning the owner's preferences.
Picking up ticket batches without being asked is something Kan added for Hausback.
It is one lead's working style, not what the chief of staff is.

## What exists today (grounding)

- `cos/SKILL.md` describes one holder per project.
  That holder plans, launches lanes and reviewers, reports twice a day and runs a retro.
  In the terms above it is a lead, and it is named chief of staff.
- Only one project can use it.
  `cos/SKILL.md` line 19 names `references/hausback.md`, and a project with no reference file "has no CoS yet".
- Hausback's working style is written into the generic text without its name.
  Lane step 8 assumes one daily integration branch.
  Steps 1, 3 and 9 assume a tracker.
  The brief templates say "No PR" for every lane.
  agentic-discovery and AlphaOS land one PR at a time through their own gates, so that pattern does not fit them.
- `unblock-all` already sweeps every project's threads and ends with one "Needs you" list.
  It is the seed of the single queue.
  Two lines tie it to Hausback: line 24 (the reference file) and line 44 ("only hausback-core has a board").
- `owner-contract.md` says "One 'Needs you' list per project".
  That is the opposite of one queue.
- This thread holds the Hausback role today, from a scratch project.
  Two scheduled reports are bound to it.
  Their prompts name the Hausback manual path and the old skill name `unblock-decisions`.
- The Hausback loop is on hold by Kan's order of 2026-11-18.
- Kan's preferences already have a home: the `kan-brain` repo.
  Its `AGENTS.md` says a rule change is proposed in `00-inbox/rule-proposal-YYYY-MM-DD.md` and Kan decides.

## Two shapes considered

**Shape A: one chief of staff per project, found through a per-project manual.**
This was the first draft.
It makes several chiefs of staff, each really a lead.
It gives Kan one "Needs you" list per project.
It carries Hausback's lane steps, tracker moves and brief blanks into every project through a manual template.

**Shape B: one chief of staff over all areas, one lead per area, one queue.**
The CoS keeps a roster and the queue and does no area work.
A lead runs one area and follows that repo's own rules.
Batch pickup is an option a lead reads only when the roster says so.

**Chosen: Shape B.**
It matches the post, and it removes the per-project copies instead of generalizing them.

## Roles

| Role | How many | Does | Never |
|---|---|---|---|
| Chief of staff (`cos`) | One, in any thread | Keeps the roster, runs the one queue, relays Kan's answers, reports twice a day, proposes rule and preference changes | Implements, reviews code, merges, picks tickets, launches lanes |
| Lead (`lead`) | One per area, in a thread inside that area's checkout | Turns work into open PRs at merge-ready, with a fresh review and evidence | Merges, reviews its own workers' code, asks Kan in a private list |
| Merge agent (`merge-agent`) | As today | Lands an open PR where the guardrails name the repo | Unchanged |
| Unblock pass (`unblock-all`) | As today | Builds the queue and carries answers | Unchanged |

Workers, reviewers and scouts stay separate top-level sessions that a lead starts.
A worker never starts another worker.

## The roster

One file in the vault: `~/Vault/Outputs/cos/roster.md`.
It is the only place that lists areas.
No skill holds a repo name.

```text
Holder: <CoS thread id>, since <time>Z
Reports: 08:00 and 23:30 Bangkok, scheduled task ids <id>, <id>
Queue page: <url>

| Area | Repo | Checkout | Mode | Manual | Lead thread | State |
|---|---|---|---|---|---|---|
| hausback | duopreneur/hausback-core | ~/Code/duopreneur/hausback-core | batch | ~/Vault/Outputs/hausback/cos-loop.md | none | hold |
| alphaos | duopreneur/AlphaOS | ~/Code/duopreneur/AlphaOS | watch | none | <id> | active |
| agentic-discovery | duopreneur/agentic-discovery | ~/Personal/development/agentic-discovery | watch | none | <id> | active |
```

- **Mode `watch`** is the default.
  Work comes from Kan.
  The lead follows the repo's own rule file and PR gate.
  It needs no manual.
- **Mode `batch`** adds picking tickets from the tracker without being asked.
  It needs a manual, because the manual holds the tracker rules, the standing approvals and the machine limits.
- **State `hold`** means the lead launches nothing and the CoS reports one line for the area.
  The area's own hold file, where it has one, still rules inside the area.
- A repo with two checkouts has one row.
  The row names the checkout its lead starts in.

## `/cos`

One command, no arguments. It reads the roster and does the one thing that fits.

| State | Do |
|---|---|
| No roster | **Start.** Draft the roster from the repos where Kan has open threads or open PRs, show it, write it on his yes. Bind the two reports to this thread. |
| The holder stopped | **Take over.** Re-verify each roster row against live state, re-bind the reports, log it. |
| This thread is the holder | **Status.** One line per area (state, in flight, oldest ask), then the queue. No launches. |
| Another live thread is the holder | Say which thread and stop. Take over only on "take over". |

Kan adds or changes an area in plain words ("add AlphaOS", "hold hausback", "resume hausback").
The CoS edits the row, reads it back, and starts or stops nothing else.
Starting a lead thread for an area needs Kan's yes for that area.

Kept from today's skill, unchanged in meaning: the owner comes first (a discussion pauses automation, only the last message is visible, open asks lead, approval covers the exact action), handoff, and the retro.

## The queue

There is one queue for Kan, across every area.

- It is a view, rebuilt at each pass, never a second store.
  Each item still lives in exactly one place: a thread, a PR, or the area's own to-do list.
- `unblock-all` builds it.
  The pass keeps sweeping every project.
  For an area whose manual names a to-do list and a ping rule, it uses them.
  An area with none gets its items in the queue only.
- Order: what blocks running work first, then reviews that are ready with their evidence, then the rest, oldest first.
- Each line: the area, the item in plain words, a link, a recommendation, and the minutes it takes.
- **A review item for a change Kan can see carries its screenshots.**
  It also carries a recording where the area's rules say how to make one.
  A review item with no evidence is a bucket 6 item: it goes back to its thread and reaches Kan only with the evidence.
- Home: one private status page, updated in place at every report, plus the same list in the CoS thread.
- Kan clears it in batches from the CoS thread.
  The CoS relays each answer to the lead that owns the next step, with his words quoted.
  A merge approval that names the repo (`merge AlphaOS#N`) records from the CoS thread: `merge-approval.py` takes the repo from the typed name when one is given.

## `/lead`

Run in an area's checkout.
It matches the git remote to a roster row.

| State | Do |
|---|---|
| No row for this repo | Say so and stop. Kan adds the area through the CoS. |
| Row, no lead or the lead stopped | **Start or take over.** Read the repo's rule file and gate from the remote default branch, read the manual if the row names one, write this thread's id into the row. |
| This thread is the lead | **Status.** Five lines. No launches. |
| Another live thread is the lead | Say which and stop. |

What every lead does:

1. Takes work from Kan, directly or relayed by the CoS.
   On start it lists the area's open PRs and threads and asks Kan which to adopt.
   It drives the ones he names, and its own, to merge-ready. It adopts none unasked.
2. Starts one worker session per item in its own worktree, with a self-contained brief.
3. Captures evidence for any change Kan can see, before review.
4. Gets a fresh one-shot review per head. At most two fix rounds, each re-reviewed.
5. Opens the PR the way the repo's own close-out says, and hands it to the merge agent.
6. Ends each finished unit with one report line. It keeps no private ask list.

What only a batch lead does, read from `lead/references/batch.md`:

- Picks tickets from the tracker and pre-screens them with a scout.
- Asks Kan for the tracker moves by key before a lane starts.
- Runs lanes that open no PR, and one integration lane that opens the single daily PR.
- Makes the tracker moves a written standing approval covers.

A watch lead wakes on a message from Kan, a relayed answer, or a worker's report.
It has no timer.
A batch lead also keeps the timed wakes its manual names.

## Learning Kan's preferences

The retro stays in the CoS evening report, and it now reads every area.

- A lesson about one area becomes a proposal for that area's manual or the repo's guide.
- A lesson about how a skill works becomes a proposal for the skill.
- A preference that holds across areas becomes a rule proposal in `kan-brain/00-inbox/`, as that repo already requires.
- Nothing is edited without Kan's yes. A declined proposal is recorded and never raised again.

Leads read `kan-brain` as their rules already tell them to, so one accepted preference reaches every area.

## Where each piece of today's text goes

| Today | After |
|---|---|
| `cos/SKILL.md` holder table, owner-first rules, handoff, retro | Stay in `cos/SKILL.md`, rewritten for the roster |
| `cos/SKILL.md` tick and lane pattern steps 2, 4 to 7 | `lead/SKILL.md` |
| `cos/SKILL.md` lane steps 1, 3, 8, 9 and the two brief rules | `lead/references/batch.md` |
| `cos/references/briefs.md` | `lead/references/briefs.md`, with a worker brief that opens a PR and the batch briefs marked as batch only |
| `cos/references/hausback.md` sessions and guard traps | `lead/references/sessions.md` (true on this Mac for every area) |
| `cos/references/hausback.md` homes, tracker, repo rules, brief blanks, limits | The Hausback manual |
| `unblock-all/references/hausback.md` | A "Unblock pass" section of the Hausback manual |
| `cos/scripts/cos-launch.sh`, `cos-log.py` | `lead/scripts/`, same code |
| `owner-contract.md` "One 'Needs you' list per project" | "One queue for the owner, across every area" |
| `owner-contract.md` "a per-project reference file inside a skill" | "A skill holds no repo names and no per-project file" |
| `briefs.md` first fixed line "You work for the chief of staff (CoS)" | "You work for the <area> lead" |
| `owner-contract.md` pipeline row for `cos`, and "the coordinator (`cos`)" | A `lead` row with today's text, and a new `cos` row: keeps the roster and the queue |
| `unblock-all` "coordinating thread (the chief of staff)" | Area answers go to that area's lead. The CoS acts directly on answers about the roster. |
| `README.md` row for `cos` | Rewritten, plus a row for `lead` |
| `merge-agent` "the coordinator" | Unchanged. It names no skill, and the lead is the coordinator it means. |
| Hausback manual sections Reports, Pings, Scheduled tasks | Stay in the manual. They are the Hausback lead's own reports. Only the task table changes (see below). |

Hausback keeps its file and seat names: `cos-loop.md`, `<date>-cos/cos.md`, `cos-inbox.md`, `cos-hold.md` and the board seat `cos`.
Renaming them would touch the board, the inbox thread and old records for no gain.
The manual's first line says the role is now the Hausback lead.

The two scheduled tasks bound to this thread become the CoS reports.
They keep their times.
Their prompts change to read the roster, cover every area, and print one line for an area on hold.
The Hausback manual's task table then says "none while on hold; the lead creates its own pair on resume".

## What changes for Hausback

- Its manual gains a `Repo:` line and the sections moved in from the two deleted reference files.
- Its lead is the role this thread holds today.
  With the area on hold there is no Hausback lead thread, and none starts until Kan says "resume".
- Its board, inbox thread, hold file, lane rules, standing approvals and Mac rules are untouched.
- This thread becomes the CoS for all areas.

## When Hausback resumes

Nothing here runs until Kan says "resume hausback".

1. The CoS sets the row to `active` and trashes the hold file, as today.
2. Kan says yes to starting the lead. It starts in a thread inside the hausback-core project, so its scheduled tasks bind without the cross-project refusal this thread hit.
3. `/lead` there reads the manual, takes the role, and writes its thread id into the roster row and the manual.
4. It creates its own morning and evening tasks from the manual's "Reports" section. The morning queue, the day record and the Hausback status page stay with it.
5. It sends the inbox thread its id, so lane reports wake the lead, not the CoS.
6. The CoS report shows one Hausback line with a link to the lead's own report. Hausback items reach the one queue through the unblock pass, as every area's do.

## Proof

1. Every link in the edited skills resolves, and each `SKILL.md` has `name` and `description`.
2. `rg -i hausback skills/cos skills/lead skills/unblock-all skills/unblock-here` prints nothing.
3. `lead/scripts/cos-launch.sh --dry-run --repo <agentic-discovery checkout>` passes its machine check and starts nothing.
4. `/lead` walked by hand against agentic-discovery reaches "read the gate from origin/main" with no write.
5. `/lead` walked against hausback-core finds the manual through the roster and stops on the hold.
6. `/cos` in this thread prints one status line per area and the queue.
7. The two scheduled tasks are read back with their new prompts and this thread as the bound thread.
8. `test-install.sh` and `test-portability.py` pass.
9. The resume steps above are walked on paper against the manual: every wake the manual names (01:00Z morning queue, record start, evening retro, inbox report) has an owner.
10. After the move commit, each moved passage is found word for word in its new file (`git diff -M --stat` plus `rg -F` on three sampled lines per file).

A new skill directory is linked by `install.sh`.
Kan runs nothing, but `/lead` is typeable only in a session started after the install.

## Order of work

Two commits, so the move can be checked by itself.

**Commit 1, a pure move. No behaviour changes.**

1. Create `skills/lead/` from today's `cos` text, scripts and briefs. `cos` keeps a short file that points at it.
2. Move the Hausback text from both `hausback.md` files into its manual, then delete them and fix the links.
3. Run proof 1, 2, 3, 8 and 10. Run `install.sh`.

**Commit 2, the new behaviour.**

4. Write the roster (Hausback on hold, the two other areas with no lead yet).
5. Rewrite `skills/cos/` for the roster and the queue. Add watch mode and `/lead`'s table to `lead`.
6. Update `unblock-all`, `unblock-here`, `owner-contract.md` and `README.md`.
7. Rewrite the two scheduled prompts.
8. Run the whole proof.

Steps 2, 4 and 7 include vault and scheduler writes. The rest is in this repo.

## Not yet specified

- A local web app for the queue, with keyboard shortcuts and voice, like the one in the post.
  The status page comes first; the app is worth designing once the queue has run for a week.
- How a lead records a video demo.
  Each area would need its own capture path, and none exists yet.
- Whether a watch lead should also poll its area on a timer.
  Today's rule is no heartbeat, and nothing yet shows it is needed.

## Out of scope

- Any change to hausback-core, AlphaOS or agentic-discovery files.
- Any change to the merge agent, the merge guard or the guardrails.
- Resuming Hausback.
- A manual for AlphaOS or agentic-discovery.
  A watch area needs none.
