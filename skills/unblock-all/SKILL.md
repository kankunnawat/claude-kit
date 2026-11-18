---
name: unblock-all
description: >-
  Use when the user types /unblock-all, says "unblock" with no scope,
  "bring up my decisions", "what needs me" or "settle the done threads", when a chief of staff tick runs its flag pass,
  or when a check finds t3code threads waiting on the user. Sweeps every
  thread, this one included: answers what standing decisions already cover,
  files the rest on the user's to-do list (flag mode) or asks them one by
  one with AskUserQuestion, each with a recommendation (ask mode), relays
  the answers and settles finished threads. For this thread only, use
  unblock-here.
---

# Unblock all

One pass over every thread that waits on someone. Each ask becomes an answer
the thread can act on, or one short question for the user.
`unblock-here` is the same pass for the current thread only.
This skill was `unblock-decisions` before 2026-11-18 and `unblock-threads`
before 2026-11-14.
The Hermes and Grok Bot version of this pass is `unblock-decisions` in
`~/.secretary-skills`; this one uses the t3code MCP tools from a Claude Code or
Codex session.
In hausback-core, also read [references/hausback.md](references/hausback.md)
before collecting.
Triage and question wording follow
[the decision rules](references/decision-rules.md).
The rules shared with `cos` and `merge-agent` are in
[references/owner-contract.md](references/owner-contract.md).

## Modes

- **ask** (default when the user runs it). Steps 1 to 5 below. Start with
  this thread's own open decisions (step 1 of
  [unblock-here](../unblock-here/SKILL.md)), then sweep the
  other threads. When the user runs it inside the coordinating thread (the
  chief of staff), act on each answer directly in that thread instead of
  relaying it to yourself.
- **flag** (`/unblock-all flag`, or a chief of staff tick). Steps 1 and 2
  only, then:
  - answer bucket 1 and act on bucket 2 as usual;
  - put every bucket 3, 4 and 5 item on the user's to-do list once, with a
    link and the minutes it takes (skip an item already listed there); a
    project with no to-do list (only hausback-core has a board) gets its items
    in the "Needs you" list only, never on another project's list;
  - send each bucket 6 item back to its thread; never file it as a to-do,
    and count them in one "sent back for evidence: n" line of the list
    (outside the 8 lines; left out when n is 0);
  - ask nothing and never call `AskUserQuestion`;
  - end with a "Needs you" list of at most 8 lines, oldest blocker first, and
    a ping only if the project's ping rule allows one at this hour;
  - a coordinating thread runs this mode at each scheduled report and uses
    the "Needs you" list as that report's section, so the report and the
    to-do list never disagree.

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
- A thread whose newest user message is under 15 minutes old is being
  driven by the user right now. List it as "you are in it" and ask nothing
  about it.
- A thread with `pendingRequestCount > 0` has an approval or question waiting
  in its UI. Read it with `t3_pending_request` if available; otherwise link
  the thread and tell the user to answer it there.
- Status `completed` only means the last turn ended. Read the message. A thread
  is waiting when it asks someone to pick, approve or supply something ("pick
  one", numbered options, "waits on you", "for you", "I've stopped").
- Flag a session that needs the user's attention even when it asks nothing:
  - status `failed`, `interrupted` or `cancelled` on a thread the user drives
    or that owns an open PR;
  - a thread the user drives that stopped with work unfinished (its last
    message names a next step that waits on nobody else);
  - a running thread whose `updatedAt` is over 30 minutes old (likely stalled);
  - a thread that reports an account, budget or machine limit;
  - a thread that reports a tool or connector it needs is missing or asks
    for sign-in. Name the tool and the fix once; do not retest it in new
    sessions after two failures.
- Also collect: open PRs waiting on the user (flagged for owner review,
  CONCERN or BLOCK findings), the project's owner to-do and ask lists (see the
  project reference), and earlier questions you asked the user that are still
  unanswered in this session or in the session's own progress record.
- Count what each source returned before you triage. A source that returns
  nothing (no threads, no to-dos, no PRs) is re-read once another way before
  you treat it as empty.

## 2. Triage each ask

Follow "Triage each ask" in [the decision rules](references/decision-rules.md).

## 3. Present one batch

Follow "Present one batch" in the same file.

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
