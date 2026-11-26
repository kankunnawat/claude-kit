# Landing path and status shape: design

Date: 2026-11-27.
Status: approved by the owner on 2026-11-27 ("approve, go").
Home: `skills/unblock-all/`, `skills/lead/`, `skills/cos/`, `skills/land-pr/`, `skills/finish/` and `.github/workflows/ci.yml` in this repo.

## Goal

A PR that is ready lands without waiting for the owner to notice it.
A thread is settled only when nothing it owns is left open.
Every status reply starts with the one thing the owner should do.

## Evidence

From the chief of staff records, 2026-11-18 to 2026-11-26.

- A merge-ready PR sat 31 h because no merge agent session was open.
- A lead thread was settled with PRs open; 3 PRs had no owner for 49 h 12 min.
- The lead launched reviews before running the repo's tier tool on 2026-11-20 and 2026-11-25.
- The hold file was skipped after an owner question on 2026-11-20 and 2026-11-26.
- Two merge agent rule proposals were lost when its thread was settled.
- The owner asked twice which threads could be settled.
- The owner said replies were too long or too technical in at least 5 threads.
- CI does not run three of the repo's own tests.

## Design

### A. One status shape, and the round 2 notes

1. The owner contract gets a "Status reply" section: the first line is the next action for the owner, or "nothing needs you"; at most six lines; no headers; plain words; blockers only when real. Open asks are never folded.
   `lead` and `cos` point to it.
   The `cos` report opens with the same next-action line.
2. The plain-words rule moves to the contract's "Reaching the owner".
   The decision rules point to it and keep their 8-line cap for a question.
3. The contract names `land-pr`: in its header, in the pipeline table, and in "Merging", because `land-pr` merges under the same guardrails.
4. The round 2 notes N4 to N9 are fixed in the skills, and N1 to N3 in the two older specs. Each note is listed under "Round 2 notes" below.
5. A lead runs the repo's tier tool before it starts any review, and starts the reviews that tier asks for.
   With no gate guide or no tier tool it uses the gate-guide template's rows. Each head gets at least one fresh reviewer, whatever the tier says.
6. A settle keeps an unanswered rule proposal.
7. The unblock pass in flag mode prints "looks finished: n", counted without the threads it may never settle, and names each.
8. The sessions reference says the plain launch form runs the session default, not a model.

### B. Close the gaps between review, merge and settle

1. A lead that hands over a PR when no merge agent runs starts one where the area's manual has a written standing approval for that; otherwise it asks the owner first.
   The approval counts only in the manual part of the area file, in the owner's own words, with its date. The merge agent starts with a fixed brief that quotes it, names no PR and asks for no merge.
   When that merge agent stops for lack of a grant or does not report, the lead asks. The ask is said in the lead's last message and filed on the area's to-do list.
2. `land-pr` accepts a verdict already recorded on the PR in place of its own round 1 review only when all hold: it is in the repo's format (with no guide, the template's verdict line), it is a pass, it names this exact head SHA, and it names its reviewer by a session id this session can read; that session did not write the change and its own last verdict is that pass at that head.
   Anything else runs round 1. A NOT YET is always recorded.
3. `finish` does not settle a thread while a PR it opened or pushed to is still open, unless a live lead owns that repo.

### C. Scripts and CI

1. `capacity.sh` prints whether night mode is on. It changes no slot number.
   A lead with night mode on still lists each ask, so it counts, but sends no question and no ping until night mode is off. It runs heavy checks once per head.
2. A new `hold-check.sh` makes "check the hold file first" one command, run first at each tick and report. An empty path or a missing folder is a wrong call, not "hold=off". A lead trashes its hold file on the owner's "resume".
3. CI runs the merge agent, queue page and capacity tests, and the two new tests.

### D. Free slots and short logs

1. A lead held at three owner asks may still use free slots on work it brought or adopted that needs nothing from the owner. It starts no new item.
2. `cos-log.py --rotate` moves Log lines older than seven days to a monthly archive beside the area file.
   It reads only the Log section, moves the lines directly under a moved line with it, prints each archive path, and adds no duplicate when it runs again after a failed run.

## Decisions (the owner, 2026-11-27)

- One status shape, held in the owner contract.
- A lead starts a merge agent only under a written standing approval; otherwise it asks.
- `land-pr` may accept a recorded verdict in place of its own round 1 review.
- No change to the merge guard, the hooks or `merge-agent.py`.

## Deviations

- The work is five commits (this pair, then A to D). This list is updated in commit D, not in the commit that added the pair.
- `cos-launch.sh` keeps its model default. The value is not only a ledger label: with `--provider` it goes to the thread start. Only the sessions reference was reworded.
- "Rebasing a branch the lead brought" became "merging the base into" it. A rebase of a pushed branch needs a force-push, which the briefs and the merge agent forbid.
- `hold-check.sh` stops everything on `hold=on` except the owner's own message, which is still answered, and a lead's report, which still gets its one log line. Without that, "resume" could never clear a hold.
- The chief of staff keeps a "no" to "stand it down?" in the report's items file, because `queue_page.py` rebuilds CURRENT STATE at every report.
- The older spec's roster item stays in "Not yet specified" with the words "done 2026-11-27", so notes N1 and N3 agree.
- The `cos` records are one file per day, so the rotation sentence there covers only a record still written to after its day.
- `land-pr` does not record an accepted verdict a second time; its report names that verdict's reviewer. The contract's "Review" bullet names `land-pr` beside the merge agent.
- The "looks finished" count sits outside the 8 lines of the "Needs you" list, like the other count lines.
- Note N6: the lead skill and the unblock pass keep the categorical rule, a roster-named thread is never settled. The one way out is in `cos`: the owner's message names a failed or interrupted lead thread by title or id, the cell is cleared and its open PRs are listed as having no lead. Then the normal settle rules apply.
- `land-pr`'s test for a recorded verdict is stricter than the merge agent's. It also needs the repo's format (the template's verdict line with no guide), a reviewer session id this session can read, and that session's own last verdict. It has no "not a pass" branch: any other verdict runs round 1. So the Decisions line no longer says "on the same terms as the merge agent".
- The owner contract's "Review" bullet points to `land-pr` step 5, so the two do not contradict.
- The rule that a standing approval sits in the manual part of the area file, in the owner's own words, is in the owner contract. So it binds every standing approval, tracker writes too, not only the merge agent start.
- The "start the merge agent" ask is filed on the area's to-do list only when the manual names one. Otherwise the lead's last message holds it, which the unblock pass reads.
- A worker report that arrives while a lead is on hold gets one Log line and no reply to the worker. The chief of staff's own hold still gives a lead's report a one-line reply.
- The Merge agent brief stands alone. The lines every other brief carries forbid PR comments, which a merge agent records as verdicts.
- `cos-log.py --rotate`: "directly under" means the unstamped lines after a moved line, up to a blank line, a stamped line or the next heading. `rotated=` counts lines, sub-lines included. A rerun skips an entry the archive already holds.

## Round 2 notes

From the round 2 review of the attention-limits change (2026-11-27).

- N1: the undo list left out the two scheduled report prompts. Fixed: both older specs say the roster and the prompts were done on 2026-11-27.
- N2: the two specs disagreed about the moved record, and the withdrawn pair still handed the owner a step. Fixed: one record rule, and the step is struck.
- N3: the new spec pair was out of step: an old idle test, two dates for the roster edit, a missing "Left for later" item. Fixed in both files.
- N4: the ask count covered the lead's own tree, not the area. Fixed: a line is added when a relay or the queue shows an unlisted ask of the area.
- N5: the over-three line was worded per roster and sat outside the report steps. Fixed: "across the rosters", and a clause in Reports step 4.
- N6: a dead lead thread had no written way out. Fixed in `cos` only: the owner names the thread, and its cell is cleared.
- N7: "started all the same" had no stated limit. Fixed: an owner's order starts inside hold and the machine budget.
- N8: the chief of staff could not judge "idle" from what it reads, and a "no" had no home. Fixed: it reads the lead's last status, and keeps a "no" in CURRENT STATE.
- N9: the "Open owner asks" list sat beside three "no second list" rules. Fixed: the list is the count only and never a source for the queue.

## Not yet specified

- How a lead tells that a merge agent session is live for its repo, beyond reading the thread list.
- Whether the status shape should also bind `land-pr` and `merge-agent` reports.

## Out of scope

- A daily fresh thread for the chief of staff.
- How many reviewers re-review a fix.
- A check that a PR's base is fresh.
- Any change to `merge-agent.py`, the merge guard, hooks, dotfiles or brain repos.
