# Attention limits for the chief of staff: design

Date: 2026-11-27.
Status: approved by Kan on 2026-11-27 ("approve, go").
Home: `skills/cos/`, `skills/lead/` and `skills/unblock-all/references/owner-contract.md` in this repo.
It replaces the [per-machine design of 2026-11-26](2026-11-26-cos-per-machine-design.md), which Kan withdrew on 2026-11-27.

## Goal

Kan's attention is the bottleneck when many agent sessions run.
He talks to one chief of staff.
An area is a project he works in, and it has a lead only while it is busy.
The limits come from what waits on him, not from how many sessions the Mac can run.

## Evidence

From the chief of staff records in `kan-brain/cos/records/`, each line opened before it was cited.

- The alphaos lead logged 45 session starts on 2026-11-20 (`2026-11-20.md:45`; the lead is named at line 11).
  The next evening, open owner asks counted one by one came to 17 (`2026-11-21.md:45`).
- Of the 15 queue lines of the morning of 2026-11-23, 0 closed through a reply in the holder thread (`2026-11-23.md:54`).
- Three open alphaos PRs had no owning session for 49 h 12 min (`2026-11-23.md:55`), after the lead thread was settled at 15:34Z on 2026-11-21 (`2026-11-23.md:13`).
- Two answers waited 29 h 03 min, because their leads ran on the other Mac and the holder could not send there (`BXTHMPLT034/2026-11-26.md:20`).
- "Start the <area> lead" through the chief of staff was used for 0 of 3 leads (`2026-11-25.md:42`).

So sessions were started faster than Kan could answer them, and leads on a second Mac left answers waiting.

## Design

1. **One chief of staff, on one Mac.**
   The commit before this spec reverts the per-machine change.
   Machine budgets (the Machines table, the `capacity.sh` flags) stay as they are.
2. **A lead only while its area is busy.**
   The chief of staff's report names an active area with no lead that has two or more unsettled top-level threads or an open PR of Kan's: "busy with no lead: type /lead in its checkout".
   It names a lead with nothing in flight, no open PR and no open ask: "idle lead: stand it down?".
   Kan types the word; the chief of staff starts and stops no lead for these.
   A lead stands down on his yes, and never while a PR it brought is open.
3. **Limits set by what waits on Kan.**
   A lead starts no new item while three of its area's items wait on him.
   It counts them from the area file's CURRENT STATE after the tick's Verify step.
   At most three areas are active at once; an "add" or "resume" that would make a fourth asks which area to hold.

## Decisions (Kan, 2026-11-27)

- One chief of staff on one Mac.
- A lead only while a project is busy.
- The two limits: three owner asks per area, three active areas.
- Both numbers are a starting guess; the retro may propose to change them.

## Not in this change

- The roster edit and moving the two leads to this Mac. The chief of staff thread does that when Kan resumes it.
- The record written under `cos/records/BXTHMPLT034/` stays where it is.

## Deviations

None yet.

## Not yet specified

- What the retro reads to judge the two numbers, beyond the two it already tracks (asks open and the oldest age).
- Whether an ask that blocks nothing running should count toward a lead's three.

## Out of scope

- Config flags or new scripts for the limits.
- Any change to the machine budget or `capacity.sh`.
- A chief of staff that starts or stops leads on its own.
