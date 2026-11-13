---
name: unblock-threads
description: >-
  Use when this session acts as chief of staff over other t3code threads and the
  user asks what needs their decision, says "unblock", "bring up my decisions",
  or "settle the done threads", or when a check finds threads waiting on an
  answer. Collects every pending question across threads, answers what standing
  decisions already cover, asks the rest one by one with AskUserQuestion, each
  with a recommendation, relays the answers back, and settles finished threads.
---

# Unblock threads

One pass that turns every thread waiting on someone into either an answer the
thread can act on or one short, numbered question for the user.
The Hermes and Grok Bot version of this pass is `unblock-decisions` in
`~/.secretary-skills`; this one uses the t3code MCP tools from a Claude Code or
Codex session.
In hausback-core, also read [references/hausback.md](references/hausback.md)
before collecting.

## 1. Collect

Do this before asking anything.

- `t3_thread_list` with `allProjects`, `settled: false`, `includeSubagents:
  true`, `limit: 100`, then the next page with `cursor`. The result overflows
  to a file; filter it with jq, never read it whole:
  `jq -s '[.[].threads[]] | map(select(.parentThreadId == null))'`.
  Only top-level threads carry asks. Child threads belong to their parent.
- For each top-level thread, read the tail: `t3_thread_read` with
  `afterPosition: itemCount - 15`, `limit: 3`, `maxCharsPerItem: 4000`,
  `runLimit: 1`. Positions follow `itemCount`, so this lands on the last
  messages. If the last item is a short progress line, read a few items
  further on.
- A thread with `pendingRequestCount > 0` has an approval or question waiting
  in its UI. Read it with `t3_pending_request` if available; otherwise link
  the thread and tell the user to answer it there.
- Status `completed` only means the last turn ended. Read the message. A thread
  is waiting when it asks someone to pick, approve or supply something ("pick
  one", numbered options, "waits on you", "for you", "I've stopped").
- Also collect: open PRs waiting on the user (flagged for owner review,
  CONCERN or BLOCK findings), the project's owner to-do and ask lists (see the
  project reference), and earlier questions you asked the user that are still
  unanswered in this session or in the session's own progress record.

## 2. Triage each ask

Put every ask in exactly one bucket:

1. **Already answered.** Search the project's standing-decision index and
   decision records, the session's progress record, and the user's earlier
   answers in this conversation. If one covers the ask, answer the thread and
   cite the source. Do not ask the user again.
2. **Yours to decide.** Reversible, inside work the user already approved, and
   not reserved to the user: retry order, which of two equivalent approaches,
   running a capture or a re-check, queueing, closing a to-do whose target is
   gone. Decide, tell the thread, and list the call in one line of the user
   reply.
3. **The user's decision.** Product scope, architecture, anything written to an
   external tracker or posted under the user's name, messages to other people,
   merges, spending, real customer data, and anything the thread's own rules
   reserve for the user.
4. **Someone else must act.** Draft the message for the user to send (a
   paste-by-hand file, per the user's rules) instead of asking a question.
5. **Action for the user.** A review, a click in a UI, a setting only they can
   change. List it with the exact place to go; it is not a question.

Check live state before you keep an ask; an old message is not evidence:

- Search the tracker before asking to file something. It may already exist.
- Check each PR's state and mergeability. For a conflict, list the files
  (`git merge-tree --write-tree --name-only origin/<base> <head>`). A
  conflict in a docs file only changes the ask.
- A "review PR X" to-do is stale once X is merged or closed. A "decide a
  follow-up" to-do is not: it stays live while its item is open.
- A closed, unmerged PR may have a replacement. Look for one before you call
  its to-do stale.

Merge asks that share one root cause. Drop asks made stale by later events
(PR merged, slot freed, item closed).

## 3. Present one batch

Ask the decisions interactively, so the user answers them one by one:

- Use `AskUserQuestion`, one question per decision, at most 4 per call. With
  more than 4, ask the 4 that unblock the most first, then the rest in a
  second call after the answers come back.
- Each question stands on its own, since the dialog may hide your earlier
  text: what is blocked and why, with plain words next to every PR or ticket
  number, then the question in one sentence. Header chip `D1 <topic>`. Keep
  each question to 2 or 3 sentences.
- 2 to 4 options. Put the recommended option first, with "(Recommended)" at
  the end of its label. Each description gives its main pro or con and the
  fact that decides it, in one or two sentences. When an option approves an
  outward write, such as a tracker comment or a state change, say so in its
  description, so picking it is that approval.
- Bundle many stale-looking old asks into one question ("close all as stale"
  versus "go through them one by one") instead of one question each.
- Never use letters from a non-Latin script in labels.
- Order by how much work an answer unblocks, then by how cheap it is to answer.
- Never re-ask something the user declined or already answered.
- Only if `AskUserQuestion` is unavailable, fall back to one text reply:
  number the decisions D1, D2… with options 1, 2, 3, so "D1 2, D2 1" can't
  be misread.

The text reply around the questions is short: at most about 8 lines. It holds
a count line, the actions for the user, "decided by me" one-liners, and what
is waiting on other people. No per-thread narration.

## 4. Relay the answers

As soon as the user answers:

- Send each answer with `t3_thread_send` (mode `auto`) to the thread that owns
  the next step. When a coordinating thread (a chief of staff or orchestrator)
  runs the lanes, send to it, not to its lanes. Tell the coordinator about
  anything you changed in its lanes (settles, closed to-dos).
- Include the user's words, the option text they picked, and any limit that
  still applies. When the user typed their own answer, quote it word for word.
  Read the returned status to confirm the thread started.
- Log each decision once in the project's decision record and give the
  coordinator its number, so it does not log it again.
- Keep one project's content out of another project's record.
- A decision that becomes a standing rule goes into the project's
  standing-decision index when that file is in your write scope; otherwise list
  it for the user.
- Skipped decisions stay open and are not re-asked in the same session unless
  they block everything.

## 5. Log and settle

- Log each decision in the session's progress record: time, thread, question,
  answer, who decided.
- Settle a thread with `t3_thread_organize` action `settle` only when nothing
  is outstanding: its work is finished, it has no open question or pending
  request, and no PR still waits on its own next step.
  - Reviewer and scout threads: settle once their verdict or report reached
    the coordinator.
  - Lane threads: settle once their claim is complete and their commits are
    in the integration PR.
  - Setup or one-question threads the user drove by hand: settle once their
    work is done and the user asked to settle done threads.
- Never settle: a thread still running or waiting, a recurring loop (a cleanup
  or watch thread that ticks), a thread whose PR still needs its capture, fix
  or report, a thread on hold for someone else, this thread, or a child thread
  whose parent is another session you do not own.
- Re-list with `settled: false`, filter to top-level threads, and report the
  settled count from that list, not from memory.

## Guardrails

- No secrets in any thread message.
- Do not poll threads or children; read them when this pass runs or when a
  completion wakes you.
- Rules that need explicit approval (tracker writes under the user's name, PR
  comments on someone else's PR, merges) still need it; a relayed "1" covers
  only the exact action, target and scope the option named.
