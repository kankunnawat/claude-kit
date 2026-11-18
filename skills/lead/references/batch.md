# Batch mode

Read this only when the roster row says `batch`.
A batch lead does everything in the lead skill, and also picks up tickets
without being asked.
The area's manual holds the tracker, the standing approvals, the report
times and any limit stricter than the machine's. Where the manual and this
file differ, the manual wins.

## Lane pattern

These steps wrap the lead skill's "What a lead does".

1. **Pick.** Read candidate tickets from the tracker in this session.
2. **Pre-screen.** One read-only scout answers, per ticket: still true on
   the trunk, smallest correct fix and where it lives, proof needed and
   whether it can run now, risk and reviewer tier, conflicts with work in
   flight. It ends with a lane split.
3. **Approve.** Ask the owner for the tracker moves by key. Launch only
   after the moves are written and read back.
4. **Launch, capture, review, fix.** As the lead skill says, one lane per
   item. A lane pushes its branch and opens no PR.
5. **Integrate.** One integration lane builds the single daily branch from
   the fresh trunk, regenerates every generated file once, runs the heavy
   proof, and opens the one PR.
6. **Close.** Make the tracker moves a written standing approval covers,
   ask the owner to settle finished threads (never settle one unasked), and
   list every write in the next report.

Two rules the brief templates carry, because both cost a round:

- **Lanes commit source only.** Generated pairs (bundles, compiled
  stylesheets, lockfiles) are regenerated locally for the lane's own proof
  and left uncommitted. Only the integration lane commits them. No claim on
  a generated file changes hands between lanes.
- **Paste the ticket text into the brief.**

## Timed wakes

A batch lead runs the scheduled reports its manual names, bound to its own
thread, in the area's own project so the binding is not refused.
Each scheduled prompt checks the area's hold file first and stops when it
exists.
The reports are the area's own. The chief of staff's report shows one line
for the area and links to them.

## Numbers

Track per day, counted from the record and from git, never from memory:
lanes landed, fix rounds per lane, and lane reports that needed a ruling
from the lead.
