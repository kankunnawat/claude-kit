---
name: night-mode
description: Use when the user says "night mode", "going to sleep", "work quietly", "no fan noise" or "queue it overnight", or says "day mode" or "I'm up" to end it. Keeps every agent on this Mac working while heavy checks wait for a cool machine and run one at a time, so the fans stay low. It only limits heavy checks; it never starts, kills or approves anything.
---

# Night mode

Agent thinking, reading, reviewing and writing cost the Mac almost nothing.
The fans come from heavy checks: test suites, linters, browser checks,
Docker runs and builds. Night mode limits only those.

The `night-mode` command holds the switch and `verify-lane` obeys it.
Read each one's header comment for what it does. Do not message other
threads about night mode: every heavy check already goes through
`verify-lane`, and its wait message tells the caller what to do.

## On

1. Run `night-mode on`. It ends by itself at the next 08:00.
   Pass a time for a different end: `night-mode on 06:30`.
2. Run `night-mode status` and keep the output.
3. Reply with: the end time, the load, what is still running, and the
   limits below that apply right now.

Start it about 15 minutes before the user sleeps when you can. Checks that
are already running finish at full speed, and fans lag behind the heat.

## While it is on

- Keep working at full pace on everything that is not a heavy check.
- Finish all fix rounds first, then run the heavy checks once per head.
- A check that waits in line is not a failure. Run it in the background and
  lengthen its timeout; never retry it or go around `verify-lane`.
- Hold anything that needs the user for the morning. Do not ping them.

## Off

`night-mode off` ends it at once. Queued checks start at the normal pace.
It also ends by itself at the end time.

## Morning

Read `~/.local/state/night-mode/log`: one line per heavy check that
started or waited under night mode, with how long it waited. Report waits
over an hour as a bottleneck.

## Limits

Say these plainly when they apply; never claim the Mac is silent.

- A heavy command run without `verify-lane` is not limited.
- A GitHub Actions runner on the Mac runs CI jobs outside `verify-lane`.
  Each push can wake it.
- Checks already running when night mode starts keep going.
- The Mac may stay warm for other reasons (the user's apps, scheduled
  jobs). Then heavy checks wait until the end time.
