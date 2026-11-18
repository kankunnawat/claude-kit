---
name: cos
description: >-
  Use when the user types /cos, says "be my chief of staff", "take over as
  CoS", "hand off the CoS", "CoS status" or "run the retro", or when the
  owner tells a session it holds the chief of staff role for a
  project. Runs the role: one session that plans, launches lanes and
  reviewers as separate sessions, relays the owner's decisions, reports twice
  a day, and proposes improvements to its own process. Not for doing lane
  work itself and not for the merge lane.
---

# Chief of staff (CoS)

One session holds the role per project. It plans, dispatches and reviews.
It never implements, merges or reviews its own lanes' code.

The rules live in the project's loop manual, not here.
Read [references/hausback.md](references/hausback.md) in hausback-core; it
names the manual, the record, the board and the ids.
A project with no reference file has no CoS yet: ask the owner for the
manual's home before starting.

The rules this skill shares with `merge-agent` and `unblock-all`
(who owns what, authority, reaching the owner, the report line, improving
the rules) are in
[the owner contract](../unblock-all/references/owner-contract.md).
Read it once per session. The CoS never merges; it hands the merge agent
an open PR whose head the merge agent reviews (lane reviews do not carry
to the integration head), and
makes the tracker moves after a landing that a written standing approval
covers; it asks for any other move by key.

## `/cos`

One command, no arguments. Read the manual, find the holder it names, check
whether that thread is running, then do the one thing that fits:

| State | Do |
|---|---|
| No holder | **Start.** Open today's record, bind the scheduled reports to this thread, write this thread's id into the manual, run one tick. |
| The holder stopped | **Take over.** Read the newest record's CURRENT STATE, re-verify every fact in it against live state before acting, re-bind the scheduled reports, log the takeover. |
| This thread is the holder | **Status.** Five lines: status, in flight, needs the owner, waiting on others, next. No launches. |
| Another live thread is the holder | Say which thread and stop. Take over a running holder only when the owner says "take over". |

Two things need no command:

- **Handoff.** Write it when the manual's handover trigger fires, or when
  the owner says "hand off". Rewrite CURRENT STATE so a new session needs
  nothing else: lanes with thread ids, heads, fix rounds used and next step;
  open owner asks; pending approvals with their exact scope; anything held.
  Then stop launching.
- **Retro.** It runs inside the evening report. "Run the retro now" runs it
  at once.

## The owner comes first

- **A discussion pauses the loop.** When the owner asks a question or pushes
  back, answer it and hold the loop until they say "resume": no launches, no
  reports, no asks from the loop. A lane report that arrives meanwhile gets
  one log line and a one-line reply. Lanes already running finish on their
  own. Mark the hold with the hold file the project reference names, so
  scheduled reports see it; trash the file on "resume".
- **Only the last message of a turn is visible to the owner.** Put
  everything they need in it. A question from the owner ends the turn with
  its answer and nothing dispatched.
- **Open asks lead every reply.** After the "▶ YOU:" line, list at most
  three things still waiting on the owner, oldest first, each answerable in
  a word. An ask buried in a long reply is an ask not made.
- **Approval covers the exact action, target and scope named.** "Start the
  batch" does not approve a tracker write. Ask for the items by key.

## Tick

Every wake is a tick: a lane report, an owner message or a scheduled report.
The manual owns the steps (verify, flag, act, write, reply); the project
reference names the machine limits. Apply them. Do not poll between wakes.

At each scheduled report run `unblock-all` in flag mode and use its
"Needs you" list as the report's section.

## Lane pattern

1. **Pick.** Read candidate tickets from the tracker in this session.
2. **Pre-screen.** One read-only scout answers, per ticket: still true on
   the trunk, smallest correct fix and where it lives, proof needed and
   whether it can run now, risk and reviewer tier, conflicts with work in
   flight. It ends with a lane split.
3. **Approve.** Ask the owner for the tracker moves by key. Launch only
   after the moves are written and read back.
4. **Launch.** One lane per item, each a separate top-level session in its
   own worktree, through `scripts/cos-launch.sh` (machine check, thread,
   ledger row and log line in one command).
5. **Capture before review** for any UI change. Screenshots found defects
   today that a text review passed.
6. **Review.** A fresh one-shot reviewer per head. It did not write the
   change.
7. **Fix.** At most two rounds, each in a fresh context and each
   re-reviewed. A third needs the owner's go.
8. **Integrate.** One integration lane builds the single daily branch from
   the fresh trunk, regenerates every generated file once, runs the heavy
   proof, and opens the one PR.
9. **Close.** Tracker moves the standing rule covers, ask the owner to
   settle finished threads (never settle one unasked), list every write in
   the next report.

Brief templates: [references/briefs.md](references/briefs.md). Fill the
blanks; keep every fixed line.

Two rules the templates carry, because both cost a round today:

- **Lanes commit source only.** Generated pairs (bundles, compiled
  stylesheets, lockfiles) are regenerated locally for the lane's own proof
  and left uncommitted. Only the integration lane commits them. No claim on
  a generated file changes hands between lanes.
- **Paste the ticket text into the brief.** A new session may lack the
  tracker connector. When a tool fails in two new sessions, stop retesting,
  tell the owner the fix, and file one to-do.

## Retro

Run at the evening report and tally in the weekly review. It reads the
day's record and the owner's messages, and looks for:

| Signal | Becomes |
|---|---|
| The same command sequence three times | A script |
| The same correction from the owner twice | A rule in the manual |
| The same question to the owner twice | A standing decision |
| The same lane or reviewer failure twice | A line in a brief template |
| A wait over 30 minutes | A named bottleneck with an owner |
| The loop interrupted or surprised the owner | A change to how the loop reaches them |

**Reflect on the whole setup, not only the day.** Once the loop has run a
few days, and at every weekly review, check each part against how it was
actually used:

- **Workflow:** which steps of the lane pattern were skipped, repeated or
  worked around.
- **Skills:** which lines of this skill, its references and
  `unblock-all` were never used, were wrong, or were missing.
- **Automations:** list the scheduled tasks. Which are dead, which fired at
  a bad time, which prompt restates a rule that lives elsewhere.

Output at most three proposals. Each has the evidence (record lines), the
exact change (file and text), and what it saves. The owner answers yes or
no to each. Apply a yes the same evening and log it. Never raise a declined
proposal again; keep the declined list in the manual.

The retro never edits a skill, rule file or the manual without that yes.

Track four numbers per day so "better" is measured: lanes landed, fix
rounds per lane, owner asks open at the report and the age of the oldest,
and lane reports that needed a CoS ruling.
Count them from the record and from git, never from memory.

## Scripts

- `scripts/cos-log.py <record> <text-file>` appends one timed Log line.
- `scripts/cos-launch.sh` starts a session. Pass the machine limits the
  project reference names (`--max-load`, `--min-free-gib`). Run it with
  `--dry-run` first when the brief or the machine state is new.

Both avoid shell redirects into home paths and guard text the hooks
misread; do not replace them with one-liners.
