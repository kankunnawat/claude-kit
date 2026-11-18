# One chief of staff, a lead per area: design

Date: 2026-11-18.
Status: needs Kan's approval.
Home: `skills/cos/`, a new `skills/lead/`, and `skills/unblock-all/` in this repo (claude-kit).
Owner rulings folded in on 2026-11-18: the synced state lives in the brain repos, and the chief of staff also covers Bitazza work.

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

## Where state lives

`~/Vault` is a plain folder on one Mac: no git, no sync.
A chief of staff that must work from any of Kan's machines cannot keep its rules there.
State splits in two.

**Synced through git, in the brain repos.** This is what a session on another machine needs to take over.

- The roster.
- Each area's manual, with Kan's standing rulings and the declined proposals.
- The chief of staff's record with its CURRENT STATE, committed at each report and at handoff, never at every tick.

**Local to the machine that runs the work.**

- Thread ids of workers, scheduled task ids and checkout paths. They mean nothing on another machine.
- Briefs, review reports, captures, the inbox log and the hold file.

There are two brain repos, split by responsibility.
Each holds a `cos/` folder with the same layout: `roster.md`, `areas/<area>.md`, `records/<date>.md`.

| Brain | Holds | Areas today |
|---|---|---|
| `kan-brain` | Personal and Duopreneur areas, and the holder line | hausback, alphaos, agentic-discovery |
| `btz-brain` | Bitazza areas | none yet; Kan adds them by name |

- One chief of staff reads both rosters and runs one queue.
- An area's rows, manual and record lines stay in its own brain. Nothing from one brain is copied into the other.
- A skill names neither repo. It says "the brain repos your session's rules name".
- A lead reads only its own area's brain. A Bitazza lead never opens `kan-brain`.

## The roster

One `cos/roster.md` per brain.
Together they are the only place that lists areas.
No skill holds a repo name.

```text
Holder: <CoS thread id> on <machine>, since <time>Z      (kan-brain only)
Reports: 08:00 and 23:30 Bangkok
Queue page: <url>

| Area | Repo | Mode | Provider | Manual | Lead thread | State |
|---|---|---|---|---|---|---|
| hausback | duopreneur/hausback-core | batch | default | areas/hausback.md | none | hold |
| alphaos | duopreneur/AlphaOS | watch | default | none | <id> on <machine> | active |
| agentic-discovery | duopreneur/agentic-discovery | watch | default | none | <id> on <machine> | active |
```

- **Provider** is what the lead and its workers start on.
  A Bitazza area names the work provider, so its sessions, commits and usage stay on the work side.
- The roster names repos, not paths.
  A session finds the checkout on its own machine from the repo name.
- There is one holder across all machines, never one per machine.

- **Mode `watch`** is the default.
  Work comes from Kan.
  The lead follows the repo's own rule file and PR gate.
  It needs no manual.
- **Mode `batch`** adds picking tickets from the tracker without being asked.
  It needs a manual, because the manual holds the tracker rules, the standing approvals and the machine limits.
- **State `hold`** means the lead launches nothing and the CoS reports one line for the area.
  The area's own hold file, where it has one, still rules inside the area.
- A repo with two checkouts has one row.

## On a second machine

- `/cos` pulls both brains and reads the holder line.
- The holder is on another machine: it says so and stops. Where t3 links the two machines, it reads and messages that thread from here.
- "Take over" moves the role to this machine. The new holder reads the synced records, re-verifies them, starts its own scheduled reports locally and rewrites the holder line.
- Leads move the same way, one area at a time, on Kan's word.

## `/cos`

One command, no arguments. It reads the roster and does the one thing that fits.

| State | Do |
|---|---|
| No roster | **Start.** Draft each brain's roster from the repos where Kan has open threads or open PRs, show them, write them on his yes. Bind the two reports to this thread. |
| The holder stopped | **Take over.** Re-verify each roster row against live state, re-bind the reports, log it. |
| This thread is the holder | **Status.** One line per area (state, in flight, oldest ask), then the queue. No launches. |
| Another live thread is the holder | Say which thread and stop. Take over only on "take over". |

Kan adds or changes an area in plain words ("add AlphaOS", "hold hausback", "resume hausback").
The CoS edits the row, reads it back, and starts or stops nothing else.
Starting a lead thread for an area needs Kan's yes for that area, and room in the machine budget.
No lead starts when this change lands (owner ruling 2026-11-18: the machine is already full).

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
- A Bitazza item is one line like any other: plain words, a link and the minutes it takes.
  The page and the thread never carry code, customer data or secrets from any area.
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

## Machine budget

Owner ruling, 2026-11-18: dispatch matches the machine's health, "not too much, not too little".
Evidence from the same hour on the 10-core Mac: 1-minute load 20.3, swap 5.6 of 7.2 GB used, both `verify-lane` slots busy.
The machine was already past full, with no chief of staff work running.

Today each launch only checks a fixed ceiling that the caller passes in (`--max-load`, `--min-free-gib`).
That stops "too much" for one launch.
It knows nothing about the other areas, and it never says how much room is left, so it cannot prevent "too little".

**One budget per machine, read at every dispatch.**

- A new script, `lead/scripts/capacity.sh`, prints how many new sessions may start now, with the readings it used.
- It reads the whole machine: 1-minute load, core count, swap used, memory free, free disk and busy `verify-lane` slots.
  Every area therefore shares one budget without the leads talking to each other.
- The launch script calls it and refuses to start when it prints 0. The two fixed flags go away.
- A lead with queued work starts up to that many sessions at this wake, not one at a time. That is the "not too little" half.
- When it prints 0, the work waits. A finished worker's report is the wake that fills the freed slot.
  Work that has waited through a report shows in the queue as "waiting for the machine".
- The chief of staff's report shows the budget line for the machine it runs on.

**Starting numbers, to be tuned.** They are a guess, not a measurement.

```text
slots = floor((cores - load) / 2), at most 4
slots = 0 when any of: swap used 75% or more, memory free under 20%, free disk under 20 GiB
quiet hours: at most 1
```

- The "2" assumes one working session adds about 2 to the load. Nothing has measured that yet.
- Each launch already logs the load it started at. The retro compares that with the load 10 minutes later and proposes new numbers.
- The numbers live per machine in `kan-brain/cos/roster.md`, because a second machine has other cores and memory.
- An area's manual may be stricter than the machine's numbers, never looser. Hausback's Mac rules stay as written.
- Heavy checks still go through `verify-lane` and its 2 slots. This budget counts sessions, not test runs.

## Learning Kan's preferences

The retro stays in the CoS evening report, and it now reads every area.

- A lesson about one area becomes a proposal for that area's manual or the repo's guide.
- A lesson about how a skill works becomes a proposal for the skill.
- A preference that holds across areas becomes a rule proposal in `kan-brain/00-inbox/`, as that repo already requires.
  A Bitazza-only lesson goes to `btz-brain/00-inbox/`.
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
| `~/Vault/Outputs/hausback/cos-loop.md` (the Hausback manual) | `kan-brain/cos/areas/hausback.md`, moved whole. The old file is trashed after the move is read back. |
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

Hausback's local files keep their names and stay in `~/Vault/Outputs/hausback/`: `<date>-cos/cos.md`, `cos-inbox.md`, `cos-hold.md`, the morning queue, the sessions board and the board seat `cos`.
Renaming them would touch the board, the inbox thread and old records for no gain.
Only the manual moves, because it holds the rulings.
Its first line says the role is now the Hausback lead.

The two scheduled tasks bound to this thread become the CoS reports.
They keep their times.
Their prompts change to read the roster, cover every area, and print one line for an area on hold.
The Hausback manual's task table then says "none while on hold; the lead creates its own pair on resume".

## Rule changes this needs

Kan's ruling, 2026-11-18: the two brains are split to separate responsibility, not to wall off his own agent harness.
Three rule files say otherwise today. Each edit below is made only after Kan approves this spec.

| File | Today | After |
|---|---|---|
| `btz-brain/AGENTS.md`, Access | Only the work account's sessions read and write this repo. Other agents, the personal Claude Code among them, don't. | Adds: the chief of staff session and the leads it starts may read this repo and write only under `cos/` (Kan, 2026-11-18). Grok Bot, Hermes, Codex and personal bots still don't. |
| `btz-brain/AGENTS.md`, Access | Never copy its contents into `kan-brain` or any personal tool. | Never copy its contents into `kan-brain`. The chief of staff's queue may list a Bitazza item as one line with a link. |
| `kan-brain/AGENTS.md`, line 5 | Bitazza work lives in `btz-brain`, which only the work account's sessions read and write. | Same, plus: the chief of staff session may read it and write its `cos/` folder (Kan, 2026-11-18). |

What does not change:

- Bitazza content never goes into `kan-brain`.
- A work-side session never reads `kan-brain` or the personal memory.
- Bitazza leads and workers run on the work provider.
- No secrets, customer PII or customer account data in either brain, the queue or the status page.

## What changes for Hausback

- Its manual moves to `kan-brain/cos/areas/hausback.md` and gains the sections moved in from the two deleted reference files.
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
3. `lead/scripts/cos-launch.sh --dry-run --repo <agentic-discovery checkout>` prints the budget and starts nothing.
   `capacity.sh` is run against four recorded readings (idle, half loaded, today's 20.3 load, low disk) and prints 4, 2, 0 and 0.
4. `/lead` walked by hand against agentic-discovery reaches "read the gate from origin/main" with no write.
5. `/lead` walked against hausback-core finds the manual through the roster and stops on the hold.
6. `/cos` in this thread prints one status line per area and the queue.
7. The two scheduled tasks are read back with their new prompts and this thread as the bound thread.
8. `test-install.sh` and `test-portability.py` pass.
9. `git -C <kan-brain> grep -i bitazza -- cos/` prints nothing, and `btz-brain/cos/` names no Duopreneur area.
10. A fresh clone of both brains holds everything `/cos` reads before its first local write.
11. The resume steps above are walked on paper against the manual: every wake the manual names (01:00Z morning queue, record start, evening retro, inbox report) has an owner.
12. After the move commit, each moved passage is found word for word in its new file (`git diff -M --stat` plus `rg -F` on three sampled lines per file).

A new skill directory is linked by `install.sh`.
Kan runs nothing, but `/lead` is typeable only in a session started after the install.

## Order of work

Two commits, so the move can be checked by itself.

**Commit 1, a pure move. No behaviour changes.**

1. Create `skills/lead/` from today's `cos` text, scripts and briefs. `cos` keeps a short file that points at it.
2. Move the Hausback manual into `kan-brain/cos/areas/`, then move the Hausback text from both `hausback.md` files into it. Delete those two files and fix the links.
3. Run proof 1, 2, 3, 8 and 12. Run `install.sh`. Commit and push the kit and `kan-brain`.

**Commit 2, the new behaviour.**

4. Make the three rule edits above. Write both rosters: `kan-brain` with Hausback on hold and the two other areas with no lead yet, `btz-brain` with no areas.
5. Rewrite `skills/cos/` for the roster and the queue. Add watch mode and `/lead`'s table to `lead`.
   Add `capacity.sh` with its test, and make the launch script call it.
6. Update `unblock-all`, `unblock-here`, `owner-contract.md` and `README.md`.
7. Rewrite the two scheduled prompts.
8. Run the whole proof.

Steps 2, 4 and 7 write to the brain repos and the scheduler. The rest is in this repo.

## Not yet specified

- Whether Hausback's sessions board and day records should sync too.
  They hold numbered decisions and are local to one Mac today.
  The area is on hold, so this waits for "resume".
- Which Bitazza areas join first, and whether their repos already declare a PR gate.

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
- Setting up the kit, the brains or the t3 link on the personal MacBook.
  The design makes that machine able to take over; it does not prepare it.
