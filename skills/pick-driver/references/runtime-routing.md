# Persistent driver runtime routing

Read this reference only when goal, loop, or scheduled execution is under consideration.

## Detect the runtime

Use sanctioned runtime metadata first, then confirm the observable tool inventory.
A product or model name alone does not prove goal, scheduling, delegation, review, or delivery support.
If the required mechanism is missing, do not claim persistence; continue authorized interactive work.
If the configured required reviewer is unavailable, report that blocker before integration.

## Goal

In Claude Code, return a paste-ready `/goal <condition>` line.
The harness activates it only when the user sends that line first in its own message.
`/goal` shows status, and `/goal clear` clears the goal.
In Claude Code, `/clear` clears both the goal and loop.
Non-interactive Claude may use `claude -p "/goal <condition>"` only when that sanctioned interface is available.
Keep the condition one paragraph under 4,000 characters.
The Claude goal judge reads only the conversation transcript, so the proof command must run inline rather than only into a report file.

In Codex, use observable goal tools and the `define-goal` active-goal checks.
Do not create persistent state for a draft or ordinary implementation.

The condition stays under the runtime's observed limit and names evidence visible to its judge.

## Loop or scheduler

Use a loop only when the runtime exposes a sanctioned scheduler or wake mechanism.
The prompt file is the program; runtime state, disk, git, and trackers determine current position.
The loop never edits its own program.
Include, in order: mission, canonical inputs, derived state, pre-decided rulings, one idempotent unit per wake, output contract, caps, and stop states.
Never store a hand-written current-position field in the prompt.
Caps include context, wall-clock time, max-wakes, and one repair round before the loop parks.
Each wake advances one unit or proves it is waiting, records evidence, states position, and schedules the next supported wake.
Use worker notifications as the primary signal; a 1200-second-or-longer wake is fallback pacing, and CI polling is approximately 480 seconds.
Workers write reports to files; independent reviewers judge their work.

Both unattended drivers preserve approval gates, scope, cost caps, and stop conditions.
A campaign ends a session at a handoff boundary and resumes only through the supported runtime mechanism.
