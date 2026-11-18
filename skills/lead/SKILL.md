---
name: lead
description: >-
  Use when the user types /lead in a repo, says "be the lead here", "take
  over as lead", "hand off the lead" or "lead status", or when the chief of
  staff starts a session as an area's lead. The session runs one area's work:
  it starts workers and fresh reviewers as separate sessions within the
  machine budget, gathers evidence, and brings open PRs to merge-ready for the
  merge agent. A batch area's lead also picks up tickets on its own. Not for
  overseeing every area (use cos) and not for merging (use merge-agent).
---

# Lead

One session leads one area: a repo the owner works in.
It turns work into open PRs at merge-ready, each with a fresh review and its
evidence.
It never implements in its own thread, never reviews its workers' code and
never merges.

The chief of staff ([cos](../cos/SKILL.md)) sits above every lead and runs
the owner's one queue.
The rules all these skills share (authority, reaching the owner, the report
line, improving the rules) are in
[the owner contract](../unblock-all/references/owner-contract.md).
Read it once per session.

## `/lead`

Run it in the area's checkout.
Read `cos/roster.md` in each brain repo your session's rules name and find
the row whose repo is this checkout's `origin`.
From then on use only the brain that lists the area.

| State | Do |
|---|---|
| No row for this repo | Say so and stop. The owner adds an area through the chief of staff. |
| Row in state `hold`, and this thread is not its lead | Say the area is on hold and since when, and stop. Take no role. |
| Row, no lead or the lead stopped | **Start or take over.** Steps below. |
| This thread is the lead | **Status.** Five lines: status, in flight, needs the owner, waiting on others, next. No launches. |
| Another live thread is the lead | Say which thread, and on which machine, and stop. Take over a running lead only when the owner says "take over". |

Start or take over:

1. Read the repo's rule file and PR gate from the remote default branch,
   never from the local checkout.
2. Read the area file `cos/areas/<area>.md` if it exists. A batch area's
   file is its manual; where the manual and this skill differ, the manual
   wins.
3. Re-verify every fact in the file's CURRENT STATE against live state.
4. Write this thread's id and machine into the roster row, commit and push.
5. List the area's open PRs and threads and ask the owner which to adopt.
   Adopt none unasked.

A lead whose area is put on hold gives status only: no launches, no asks.

## What a lead does

1. **Take work.** From the owner, directly or relayed by the chief of
   staff, plus the open work the owner told you to adopt. An unclear item
   gets one read-only scout first.
2. **Check the machine.** Run `scripts/capacity.sh` with this machine's
   flags from the roster, plus `--quiet-hours` inside the roster's quiet
   hours. Start at most the `slots` it prints at this
   wake. With queued work and room for three, start three. With `slots=0`,
   start nothing; the next worker report is the wake that tries again.
3. **Launch.** One worker per item, each a separate top-level session in
   its own worktree, through `scripts/cos-launch.sh` (budget, thread,
   ledger row and log line in one command). An area whose roster row names
   a provider passes it with `--provider`. In watch mode the worker opens
   the PR the way the repo's own close-out says.
4. **Capture before review** for any change the owner can see. A text
   review passes defects a screenshot shows.
5. **Review.** A fresh one-shot reviewer per head. It did not write the
   change.
6. **Fix.** At most two rounds, each in a fresh context and each
   re-reviewed. A third needs the owner's go.
7. **Hand over.** Record the reviewer's verdict on the PR in the repo's
   own format, at the reviewed commit, with the evidence its gate asks
   for. Then hand the PR to the merge agent, which accepts that verdict
   while the head has not moved.
8. **Report.** One report line per finished unit, as the owner contract
   words it. Keep no private ask list: what waits on the owner reaches the
   one queue through `unblock-all`.

Brief templates: [references/briefs.md](references/briefs.md). Fill the
blanks; keep every fixed line.
How sessions start and send on this Mac, and what the shell guards block:
[references/sessions.md](references/sessions.md).

A new session may lack the tracker connector, so paste the ticket text into
the brief. When a tool fails in two new sessions, stop retesting, tell the
owner the fix, and file one to-do.

## Two modes

The roster row names the mode.

- **watch** (the default). Work comes only from step 1. The lead wakes on
  an owner message, a relayed answer or a worker's report. It has no timer.
- **batch.** The lead also picks tickets from the tracker and runs lanes
  into one integration PR. Read [references/batch.md](references/batch.md)
  and the area's manual. A batch lead keeps the timed wakes its manual
  names.

## Tick

Every wake is a tick.

1. **Verify.** Fetch the trunk. Read the live state of the area's open PRs
   and running sessions. Never act on the record alone.
2. **Act.** The smallest set of moves that unblocks the most, inside the
   machine budget.
3. **Write.** Append one Log line, with the budget line when you
   considered a launch. Rewrite CURRENT STATE when it changed.
4. **Reply.** If nothing changed, one line.

Do not poll between wakes.

## State

A lead keeps its state where a new session, on any machine, can pick it up.

- **Area file:** `cos/areas/<area>.md` in the area's brain. Create it on
  start when the area has none, with the sections CURRENT STATE and Log,
  Log last because the log script appends to the end of the file.
  The owner's rulings for the area and its declined proposals live here
  too. Pull before reading; commit and push at handoff and whenever
  CURRENT STATE changes, not at every tick.
- **Local:** briefs, review reports, captures and the list of worker
  thread ids go in a folder on this machine, which the area file names.
  Thread ids mean nothing on another machine and stay out of the area
  file. A manual may name its own record
  home; then use that.
- Worker reports go to the area's inbox when its manual names one,
  otherwise to this thread.

## Handoff

Write it when the manual's handover trigger fires, when the context is
close to full, or when the owner says "hand off".
Rewrite CURRENT STATE so a new session needs nothing else: each worker's
name, branch, head, fix rounds used and next step; open owner asks; pending
approvals with their exact scope; anything held.
Commit and push it. Then stop launching.

## Scripts

- `scripts/capacity.sh` prints `slots=N` and the readings behind it. It
  reads the whole machine, so every area shares one budget.
  `scripts/test-capacity.sh` checks it against recorded readings.
- `scripts/cos-launch.sh` starts a session. It calls `capacity.sh` and
  refuses when there is no room. Run it with `--dry-run` first when the
  brief or the machine state is new.
- `scripts/cos-log.py <record> <text-file>` appends one timed Log line.

They avoid shell redirects into home paths and guard text the hooks
misread; do not replace them with one-liners.
