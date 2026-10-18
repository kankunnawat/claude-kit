---
name: blast-radius
description: "Manual only. Use for /blast-radius, 'what could this break', or a small diff you don't trust. Finds breakage beyond the diff and proves the one fact the change is safe because of by running real code."
disable-model-invocation: true
---

<!-- Adapted from pstack blast-radius (cursor/plugins@019a6a2, pstack v0.15.25), MIT, (c) 2026 Lauren Tan. See LICENSE-pstack. -->

# blast-radius

Listing callers is not the job. Grep does that. The job is the breakage grep won't show.
A writeup that sounds right proves nothing. Find the fact the change depends on and run it.

## Confidence ladder

For each fact the change's safety depends on, push it as far down as is cheap and say where it stopped.

1. Said so. Worthless alone.
2. Pointed at the line. A real `file:line` or the library's own source.
3. Walked the bad case step by step and showed it can't reach.
4. Ran it. A small script or test that calls the real code and fails loud if wrong.
5. Reproduced it in the running app.

## Steps

1. Read the diff, including what it now does differently that the diff doesn't spell out.
2. Find the one fact it's safe because of (e.g. "this call only drops already-dead cache entries"). Spend time here, not on a long list of maybes.
3. Look where grep stops: pinned library source and local patches, lifecycle and teardown timing, JSON/DB/wire formats, feature flags, other languages reading the same bytes, code three hops away.
4. Rate each risk by real likelihood and real cost. Keep confirmed risks. List checked-and-cleared ones separately. Never invent a caller or API. An empty search is still an answer.
5. Prove the one fact at step 4 of the ladder when cheap. Paste the result.

## Reply

- **What it does.** Including the non-obvious part.
- **Safe because.** The one fact, its ladder step, the proof, or `unproven`.
- **Risks.** How it breaks, `file:line`, likelihood and cost, how to check.
- **Cleared.** What was checked and why it's fine.
- **Before merge.** The cheapest test or repro that would catch the real bug.
