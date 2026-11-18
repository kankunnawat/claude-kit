---
name: unblock-here
description: >-
  Use when the user types /unblock-here, or says "bring the decisions here",
  "ask me here", "ask me in this thread" or "what do you need from me here".
  Collects this thread's own open decisions and asks them in the thread with
  AskUserQuestion, each with a recommendation, then acts on the answers. For
  every thread at once, use unblock-all.
---

# Unblock here

Ask the user this thread's open decisions, in this thread, and act on the
answers. `unblock-all` is the same pass over every thread.
Triage and question wording follow
[the decision rules](../unblock-all/references/decision-rules.md). Read that
file before asking.
Authority and how to reach the owner follow
[the owner contract](../unblock-all/references/owner-contract.md).
In hausback-core, the board commands for recording an answer are in
[the hausback reference](../unblock-all/references/hausback.md).

## 1. Collect

Only this conversation. No thread sweep.

- Questions you left for the user that are still unanswered.
- "Owner ruling needed" lists in a file or PR you wrote.
- To-dos or tickets you filed that are really a decision.
- Work you left unfinished because it needs the user's word: a flagged PR,
  an unapproved tracker write, a scope choice.

Read live state before you keep an ask: PR state, the tracker, the file.
An old message is not evidence.

## 2. Triage and ask

Sort each ask with the six buckets of the decision rules.
Decide what is yours to decide and say so in one line.
Measure a bucket 6 item in this thread first, then ask it with the evidence.
Ask bucket 3 as one batch. Draft the message for bucket 4. List bucket 5
with the exact place to go.

## 3. Act

- Act on each answer in this thread, in the same turn.
- Record it where the question lived: the PR, the decision file, the to-do.
- An option the user picked approves only the action, target and scope it
  named.
- End with what was done per decision and what, if anything, still waits on
  the user.
