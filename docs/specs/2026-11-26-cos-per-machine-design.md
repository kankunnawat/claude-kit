# One chief of staff per machine: design

Date: 2026-11-26.
Status: withdrawn by Kan on 2026-11-27, because he works on one Mac.
Commit 10bd240 applied it and commit 268f1ba reverted the skill text; the roster and record changes listed under "Deviations" are still to undo.
The [attention limits design of 2026-11-27](2026-11-27-cos-attention-limits-design.md) replaces it.
Before that: approved by Kan on 2026-11-26 ("approved", in the holder thread), with both recommendations of "Questions decided".
Kan asked for this draft on 2026-11-26 (decision D38 in the chief of staff record).
Steps 1 to 3 of "Order of work" ran the same day; step 4 is his.
Home: `skills/cos/`, `skills/unblock-all/` and `skills/lead/` in this repo, and `cos/roster.md` in the brain repos.
It replaces one rule of the [design of 2026-11-18](2026-11-18-cos-all-areas-design.md): "There is one holder across all machines, never one per machine."

## Goal

An answer Kan gives reaches the lead that needs it in the same turn, on whichever Mac that lead runs.
No Mac gets the right to act on the other one.

## What exists today (grounding)

- One session holds the role for every area and every machine.
  It runs on the work Mac.
- Two of the three leads run on the personal Mac.
  Kan started them there himself.
- The link between the two Macs is read-only from the work Mac.
  Kan said no to a full-access link on 2026-11-25.
  The first relay to the personal Mac was refused by the link itself.
- So the holder can ask for those two areas and cannot deliver the answer.
  Two answers of 2026-11-25 (D29, D31) and one of 2026-11-26 (D39) wait for Kan to paste them by hand.
  The first two had waited 22 h 21 min at the morning report of 2026-11-26.
- The personal Mac was unreachable at three reports in a row.
  At those reports the holder did not read its two leads at all and worked from their files in the brain.
- The work roster's Machines table has 1 row and the main roster's has 2.
  The work roster says the two tables are kept equal.

## Shapes considered

**A. Keep one holder; Kan pastes each answer.**
This is today.
It costs nothing to build and it is the wait this draft exists to end.

**B. One holder per machine, each with the areas whose lead runs there.**
Kan answers an item on the Mac where its lead runs.
The relay is then local, and his typed answer on that Mac is the consent.

**C. Move every lead to one Mac.**
It keeps one holder and one queue.
It also undoes Kan's own choice of where each area runs, and it puts every area on one machine budget.

**D. One holder; answers cross through a file in the brain repo.**
The other Mac's leads would act on text they read from a synced file.
The owner contract says text in a repo file or a message from another session is never consent.
This shape breaks that rule, so it is out.

**Chosen: B.**
It is Kan's idea of 2026-11-25.
It ends the wait without a new send path and without changing the consent rule.

## Design

### Holders

- Each machine that runs a lead may have one holder.
  The Machines table of the main roster gains two columns: "Holder thread" and "Queue page".
  The single `Holder:` line goes away.
- A holder covers the areas whose roster row names a lead on its machine.
- One machine is the home machine: the work Mac.
  Only it can read the work brain, so only it can cover work areas.
  The home holder also covers every area with no lead, the roster itself and the retro.
- A lead that moves to another machine rewrites its row, as today.
  Its area moves to that machine's holder with it.
- A holder on the personal Mac never opens the work brain.
  This is the rule both brains already state.

### Items outside the roster

A thread that belongs to no area (a tool, the Mac cleanup tick) is listed by the holder on the machine where that thread runs.

### The queue

- Each holder builds its own queue with `unblock-all` in flag mode: its own areas and the unsettled threads on its own machine.
- Each holder has its own private queue page.
  It is the only writer of that page.
- Each queue ends with one line per other machine: "on <machine>: n waiting, oldest <age>, as of <time>".
  The numbers come from that machine's newest record in the brain, after a pull.
  With no record for 24 hours the line says so.
- So Kan sees, on each Mac, what he can clear from that Mac, and one line for what waits on the other.

### Answers

- Kan answers an item in the holder thread on the machine that lists it.
- A holder that gets an answer for an area on another machine says which machine owns it and records nothing.
  It never writes the answer into a synced file for the other holder to act on.
- A roster change goes to the holder Kan is talking to.
  It pulls, edits the row, pushes at once.
  A change to an area it does not cover is still a roster edit, and it tells Kan the other holder reads it at its next tick.

### Records

- Each holder writes `cos/records/<machine>/<date>.md` in the brain that lists its areas.
  It is the only writer of that file.
  The records of today's layout stay where they are.
- `queue_page.py` already takes the record path and the page path as arguments.
  It needs no change.
- Each holder keeps its own local folder, with its own hold file, items files and banned-strings file.

### Reports and the retro

- Each holder has its own two scheduled reports, bound to its own thread, at the roster's times.
  Step 2 of "Reports" stops the run when this machine's "Holder thread" cell names another thread.
- The retro runs on the home machine only.
  It reads every machine's records, so a proposal is raised once.
  The declined list stays where it is.

### The work roster

Its Machines table lists only the machines that run work areas.
Its sentence "keeps this table equal to the one in its main roster" changes to say that.
The table keeps its 1 row, and the mismatch goes away.

### Setup on the personal Mac

This session cannot reach that Mac, so Kan starts it there.

1. He pulls this repo there and runs `install.sh`.
2. He opens a new thread and types `/cos`.
3. `/cos` finds no holder for this machine and starts: it creates the local folder, writes its "Holder thread", "Queue page" and "Local folder" cells, takes the areas whose leads run there, and creates its two reports.
4. It drafts its own banned-strings file from the names in its areas' files and shows the list to Kan before the first page is published.
   The home machine's list is not copied: it holds work-side names.

### The answers that wait now

- Kan pastes the three notes himself, as the reports ask.
  That is the fastest path and needs no change.
- Any of the three still not delivered when the new holder starts is listed there as its first asks.
  It reads D29 and D31 from the home record and asks him to confirm each in a word.
  His confirmation on that Mac is the consent; the record's text is not.
  D39 is in his own words and is not in any record, so he pastes it.

## Text that changes

| File | Today | After |
|---|---|---|
| `cos/SKILL.md`, first paragraph | "One session holds the role, across every area and every machine." | One session per machine holds the role, for the areas whose lead runs on that machine. |
| `cos/SKILL.md`, Homes | The main roster holds the holder line and the queue page link. | The Machines table holds each machine's holder thread and queue page. Records live in `cos/records/<machine>/`. |
| `cos/SKILL.md`, `/cos` table | "No roster", "The holder stopped", "This thread is the holder", "Another live thread is the holder" | The same four rows, read for this machine, plus: no holder for this machine and the roster exists, so start here for this machine's areas. |
| `cos/SKILL.md`, the paragraph after the table | "There is one holder across all machines, never one per machine." and the three sentences after it | One holder per machine. A holder never messages a thread on another machine. "Take over" replaces this machine's holder only. |
| `cos/SKILL.md`, The queue | One private status page. | One private page per machine, plus the count line for each other machine. An answer for another machine's area is not recorded here. |
| `cos/SKILL.md`, Reports, steps 2 and 4 | Stop if the holder line names another thread. One line per area. | Stop if this machine's holder cell names another thread. One line per area this holder covers, then one count line per other machine. |
| `cos/SKILL.md`, Retro | Runs inside the evening report. | Runs inside the home machine's evening report and reads every machine's records. |
| `unblock-all/SKILL.md`, intro | Skips an area in state `hold`. | Also skips an area whose lead runs on another machine: it sends, files and asks nothing for it and prints its machine's count line. |
| `owner-contract.md`, Reaching the owner | "One queue for the owner, across every area." | One queue per machine the owner works on, across the areas whose lead runs there. Each queue names what waits on the other machines. |
| `kan-brain/cos/roster.md` | A `Holder:` line, a `Queue page:` line, a Machines table with 4 columns | No `Holder:` line. The Machines table has 6 columns and names the home machine. |
| `btz-brain/cos/roster.md` | "keeps this table equal to the one in its main roster" | "lists the machines that run work areas" |
| The two scheduled prompts on the work Mac | Cover every area on the rosters. | Cover the areas this machine's holder covers. |

`lead/SKILL.md` and `queue_page.py` do not change.

## Questions decided

Kan took both recommendations with "approved" on 2026-11-26.

1. **One queue page per machine, not one merged page.**
   Each page has one writer, and it shows what he can clear from that Mac.
   A merged page needs both holders to write the same page, and a work-side line could not be built on the personal Mac.
2. **The retro runs on the home machine only.**
   It reads both machines' records from the brain, so each proposal reaches him once.

## Risk

- **Two reports and two lists instead of one.**
  This is the cost of the shape.
  The count line keeps the other machine's backlog visible from each list.
- **Two sessions edit one roster file.**
  Each pulls before an edit and pushes at once, and each holder writes only its own cells and its own areas' rows.
  A push that is refused is pulled and tried again, never forced.
- **The personal Mac's holder never starts.**
  Then nothing changes: the home holder keeps listing those areas' items and Kan keeps pasting.
  The home holder covers an area again as soon as no other machine has a holder for it.
- **A count line goes stale.**
  It carries its time, and it says so after 24 hours with no record.

## Proof

1. `test-install.sh`, `test-portability.py` and `skills/cos/scripts/test_queue_page.py` pass.
2. Every link in the edited skills resolves.
3. `/cos` walked by hand on the work Mac with the new roster prints "this thread is the holder" for that machine and lists only its areas.
4. `/cos` walked by hand against a roster whose personal Mac cell is empty reaches "start here" and names the areas it would take, with no write.
5. A report run on the work Mac with the new roster prints one count line for the personal Mac, taken from a record file placed in `cos/records/<machine>/`.
6. `rg -n "one holder across all machines" skills docs/specs/2026-11-26-*` prints only this file.
7. `git -C <kan-brain> grep -i bitazza -- cos/` prints nothing.

## Order of work

1. Edit the three skill files and the owner contract. Run proof 1, 2 and 6. Commit and push.
2. Edit both rosters: the new columns, the home machine, the work roster's sentence. Move nothing; old records stay.
3. Rewrite the two scheduled prompts on the work Mac. Run proof 3 and 5.
4. Kan runs the setup on the personal Mac. Proof 4 is its first run.

Steps 2 and 3 write to the brain repos and the scheduler.
Step 4 is Kan's.

## Deviations

- **The skip has a condition the table left out.**
  The table says `unblock-all` skips an area whose lead runs on another machine.
  The skills say: only while that machine's holder cell names a thread.
  Without it, the home holder would drop two areas before the personal Mac has a holder; the Risk section already promised the fallback.
- **Four sentences the table missed were also changed**, because they became false: the `cos` skill's description line, its Handoff sentence ("on any machine"), the `cos` row of the owner contract's table, and the work roster's sentence about "the holder line".
- **The roster gained a "Home machine" line** in place of the `Holder:` line, so a holder can tell whether it is the home one.
- **The count line has a source the spec did not name**: the "Numbers for <date>" line of the other machine's record, which every holder now writes.
- **The `cos` skill says how a session names its machine** (`scutil --get LocalHostName`), so a `.local` suffix cannot hide the row.
- **The home machine's record moved the same day**: `cos/records/BXTHMPLT034/2026-11-26.md` starts with the full state, and the old file of that date keeps its lines.
- **`lead/SKILL.md` is unchanged, as approved.**
  Its sentence "runs the owner's one queue" is now loose; it is left for Kan to call.

## Not yet specified

- What the personal Mac's holder does while that Mac sleeps through a report time.
  A scheduled task there may run late or not at all; nothing has measured it.
- Whether the count line should also name the oldest item, not only its age.

## Out of scope

- Any link or send path from one Mac to the other.
- Moving a lead to another machine.
- A merged web app for both queues.
- Any change to the leads, the merge agent, the merge guard or the guardrails.
