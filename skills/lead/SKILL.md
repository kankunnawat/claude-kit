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
| This thread is the lead | **Status.** A status reply, as the owner contract shapes it: the next action first, then in flight, waiting on others, and "holding new work" or "idle" when either holds. No launches. |
| Another live thread is the lead | Say which thread, and on which machine, and stop. Take over a running lead only when the owner says "take over". |

Start or take over:

1. Read the repo's rule file and PR gate from the remote default branch,
   never from the local checkout.
2. Read the area file `cos/areas/<area>.md` if it exists. A batch area's
   file is its manual; where the manual and this skill differ, the manual
   wins.
3. Re-verify every fact in the file's CURRENT STATE against live state.
4. Write this thread's id and machine into the roster row, commit and push.
   When the owner's order has a limit (one night, one batch), write the
   limit in the row's state note in his words. When this machine has no
   row in the Machines table, say so in the first status and ask the
   owner for one.
5. List the area's open PRs and threads and ask the owner which to adopt.
   Adopt none unasked.

A lead whose area is put on hold gives status only: no launches, no asks.

## What a lead does

1. **Take work.** From the owner, directly or relayed by the chief of
   staff, plus the open work the owner told you to adopt. An unclear item
   gets one read-only scout first.
2. **Check the queue and the machine.** Count the lines of "Open owner
   asks" in the area file's CURRENT STATE, never from memory. With three
   or more, start no new item: review, fix and hand over what already
   runs. A scout or a batch pick is a new item. Free slots may still go
   to work this lead brought or adopted that needs nothing from the
   owner: re-running a failed check, a fix round already allowed,
   evidence capture, or merging the base into its branch. An order the
   owner types in this thread is started all the same; hold and the
   machine budget still apply. Say "holding new work: n items
   wait on you" in the status and in the next report line.
   Then run `scripts/capacity.sh` with this machine's
   flags from the roster, plus `--quiet-hours` inside the roster's quiet
   hours and any stricter flags the area's manual names. Start at most the `slots` it prints at this
   wake. With queued work and room for three, start three. With `slots=0`,
   start nothing; the next worker report is the wake that tries again.
   With `night_mode=on`, list each ask in "Open owner asks" as usual, so
   it counts, and state it in this thread's last message, where the
   morning report's flag pass reads it. Send no question and no ping
   until night mode is off.
   Run heavy checks once per head after the fix rounds, as
   [night-mode](../night-mode/SKILL.md) says; the pace of other work is
   unchanged. The roster's quiet hours still set `--quiet-hours`.
3. **Launch.** One worker per item, each a separate top-level session in
   its own worktree, through `scripts/cos-launch.sh` (budget, thread,
   ledger row and log line in one command). An area whose roster row names
   a provider passes it with `--provider`. In watch mode the worker opens
   the PR the way the repo's own close-out says.
4. **Capture before review** for any change the owner can see. A text
   review passes defects a screenshot shows.
5. **Review.** First run the repo's own tier tool, from its PR gate
   guide, on the diff. With no gate guide or no tier tool, use the rows
   of
   [the gate-guide template](../merge-agent/references/gate-guide-template.md),
   as `land-pr` step 4 does. Then start the reviews that tier asks for: a
   fresh one-shot reviewer per review and per head, and at least one per
   head whatever the tier says. No reviewer wrote the change.
6. **Fix.** At most two rounds, each in a fresh context and each
   re-reviewed. A third needs the owner's go.
   When asking for it, recommend no: the PR stays a draft at BLOCK with
   its open findings listed, and the owner decides whether it is worth
   another round of reviews.
7. **Hand over.** Record the reviewer's verdict on the PR in the repo's
   own format, at the reviewed commit, with the evidence its gate asks
   for. Name the reviewer by its thread id, so a later session can read
   what it wrote: in the format's reviewer field, or on a second line of
   the same comment when the format has none. Then hand the PR to the merge agent, which accepts that verdict
   while the head has not moved.
   When no merge agent session is live for this repo: where the area's
   manual holds a standing approval to start one (owner contract,
   "Authority"), start it with the Merge agent brief through
   `scripts/cos-launch.sh` (bucket `review`) inside the machine budget.
   Otherwise, or when that merge agent stops for lack of a grant or ends
   without its report, ask the owner "start the merge agent in <repo>",
   linked to the PR: say it in this thread's last message, file it on
   the area's to-do list when the manual names one, and add its line
   first in "Open owner asks" for the count, linking that to-do or this
   thread. Without that written approval the lead only asks.
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

1. **Hold.** When the area has a hold file, run
   `../cos/scripts/hold-check.sh` on it first. On `hold=on`, do nothing
   else and reply one line. On exit 2, fix the path and run it again;
   never treat it as off. The owner's own message is still answered;
   on the owner's "resume", trash the hold file. A worker report that
   arrives on hold gets one Log line and no reply to the worker.
2. **Verify.** Fetch the trunk. Read the live state of the area's open PRs
   and running sessions. Never act on the record alone.
3. **Act.** The smallest set of moves that unblocks the most, inside the
   machine budget.
4. **Write.** Append one Log line, with the budget line when you
   considered a launch. Rewrite CURRENT STATE when it changed.
5. **Reply.** If nothing changed, one line.

Do not poll between wakes.

## State

A lead keeps its state where a new session, on any machine, can pick it up.

- **Area file:** `cos/areas/<area>.md` in the area's brain. Create it on
  start when the area has none, with the sections CURRENT STATE and Log,
  Log last because the log script appends to the end of the file.
  At the first tick of a day, run
  `scripts/cos-log.py --rotate <area-file>`, and stage each archive it
  prints with the area file.
  The owner's rulings for the area and its declined proposals live here
  too. CURRENT STATE keeps a list "Open owner asks", one line per
  decision the owner must make, never folded. Add a line when this thread
  or one of its workers raises an ask, or when a relay or the report's
  queue shows an ask of this area that is not listed. Remove it when the
  answer arrives or live state makes it stale. This list is the count
  only. Each line links the thread, PR or to-do that holds the ask; it is
  never a source for the queue. Pull before reading; commit and push at handoff and whenever
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

## Stand down

A lead is idle when nothing is in flight, no owner ask is open, and no PR
is open that this lead, or the lead before it, brought or adopted.
An idle lead says so in the status. On the owner's yes, rewrite CURRENT
STATE, delete this thread's timed wakes, clear the lead cell in the roster
row, commit, push and stop.
A lead that is not idle never stands down, and its thread is never
settled.

## Scripts

- `scripts/capacity.sh` prints `slots=N`, the readings behind it and
  `night_mode=on|off`. It reads the whole machine, so every area shares
  one budget.
  `scripts/test-capacity.sh` checks it against recorded readings.
- `scripts/cos-launch.sh` starts a session. It calls `capacity.sh` and
  refuses when there is no room. Run it with `--dry-run` first when the
  brief or the machine state is new.
- `scripts/cos-log.py <record> <text-file>` appends one timed Log line.
  `--rotate <record> [days]` moves Log lines older than seven days, or
  `days`, to a monthly archive beside the record.
  `scripts/test_cos_log.py` checks the rotation.

They avoid shell redirects into home paths and guard text the hooks
misread; do not replace them with one-liners.
