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

1. The owner contract gets a "Status reply" section: the first line is the next action for the owner, or "nothing needs you"; at most six lines; no headers; plain words; blockers only when real.
   `lead` and `cos` point to it.
   The `cos` report opens with the same next-action line.
2. The plain-words rule moves to the contract's "Reaching the owner".
   The decision rules point to it and keep their 8-line cap for a question.
3. The contract names `land-pr`: in its header, in the pipeline table, and in "Merging", because `land-pr` merges under the same guardrails.
4. The round 2 notes N4 to N9 are fixed in the skills, and N1 to N3 in the two older specs.
5. A lead runs the repo's tier tool before it starts any review, and starts the reviews that tier asks for.
6. A settle keeps an unanswered rule proposal.
7. The unblock pass in flag mode prints "looks finished: n".
8. The sessions reference names the owner's route table, not a model.

### B. Close the gaps between review, merge and settle

1. A lead that hands over a PR when no merge agent runs starts one where the area's manual has a written standing approval for that; otherwise it asks the owner first.
2. `land-pr` accepts a passing verdict already recorded at the PR's head, by a reviewer who did not write the change, in place of its own round 1 review.
3. `finish` does not settle a thread while a PR it opened or pushed to is still open, unless a live lead owns that repo.

### C. Scripts and CI

1. `capacity.sh` prints whether night mode is on. It changes no slot number.
   A lead with night mode on holds its owner asks for the morning and runs heavy checks once per head.
2. A new `hold-check.sh` makes "check the hold file first" one command, run first at each tick and report.
3. CI runs the merge agent, queue page and capacity tests, and the two new tests.

### D. Free slots and short logs

1. A lead held at three owner asks may still use free slots on adopted work that needs nothing from the owner. It starts no new item.
2. `cos-log.py --rotate` moves Log lines older than seven days to a monthly archive beside the area file.

## Decisions (the owner, 2026-11-27)

- One status shape, held in the owner contract.
- A lead starts a merge agent only under a written standing approval; otherwise it asks.
- `land-pr` accepts a recorded verdict on the same terms as the merge agent.
- No change to the merge guard, the hooks or `merge-agent.py`.

## Deviations

- None yet.

## Not yet specified

- How a lead tells that a merge agent session is live for its repo, beyond reading the thread list.
- Whether the status shape should also bind `land-pr` and `merge-agent` reports.

## Out of scope

- A daily fresh thread for the chief of staff.
- How many reviewers re-review a fix.
- A check that a PR's base is fresh.
- Any change to `merge-agent.py`, the merge guard, hooks, dotfiles or brain repos.
