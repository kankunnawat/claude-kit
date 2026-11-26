---
name: unblock-all
description: >-
  Use when the user types /unblock-all, says "unblock" with no scope,
  "bring up my decisions", "what needs me" or "settle the done threads", when a chief of staff report runs its flag pass,
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
The Hermes and Grok Bot version of this pass has the same name in
`~/.secretary-skills`; this one uses the t3code MCP tools from a Claude Code or
Codex session.
Areas are listed in `cos/roster.md` of the brain repos your session's
rules name; each row names the area's repo, its state and its manual.
For an area whose manual has an "Unblock pass" section, read that section
before collecting.
An item belongs to the area whose repo owns its thread's checkout, its PR
or its ticket, whichever thread reports it.
**An area whose roster row is in state `hold` is skipped in both modes:**
send nothing to its threads, write nothing to its to-do list or board, ask
nothing about it and list none of its items. Count its waiting threads in
one "on hold: <area>, n waiting" line.
**An area that another machine's chief of staff covers is skipped the same
way.** That is an area whose lead runs on another machine, when that
machine's "Holder thread" cell in the roster names a thread. Send, file and
ask nothing for it; the list ends with that machine's count line, as the
`cos` skill's "The queue" says. While that cell names no thread, the area
is not skipped.
Triage and question wording follow
[the decision rules](references/decision-rules.md).
The rules shared with `cos`, `lead` and `merge-agent` are in
[references/owner-contract.md](references/owner-contract.md).

## Modes

- **ask** (default when the user runs it). Steps 1 to 5 below. Start with
  this thread's own open decisions (step 1 of
  [unblock-here](../unblock-here/SKILL.md)), then sweep the
  other threads. When the user runs it inside the thread that owns the
  next step (a lead for its own area, the chief of staff for the roster),
  act on that answer there instead of relaying it to yourself.
- **flag** (`/unblock-all flag`, or a chief of staff report). Steps 1 and 2
  only, then:
  - answer bucket 1 and act on bucket 2 as usual;
  - put every bucket 3, 4 and 5 item on its area's to-do list once, with a
    link and the minutes it takes (skip an item already listed there); an
    area whose manual names no to-do list gets its items in the "Needs you"
    list only, never on another area's list;
  - send each bucket 6 item back to its thread; never file it as a to-do,
    and count them in one "sent back for evidence: n" line of the list
    (outside the 8 lines; left out when n is 0);
  - ask nothing and never call `AskUserQuestion`;
  - end with one "Needs you" list across every area. It is the owner's one
    queue. Order: what blocks running work first, then reviews that are
    ready with their evidence, then the rest, oldest first. Each line: the
    area, the item in plain words, a link, a recommendation and the
    minutes it takes. Show at most 8 lines and count the rest;
  - an item that has stood unchanged in the list for three days and
    blocks nothing that runs moves to one "parked: n" line that names
    each in a few words with its link. It comes back when its facts
    change or the owner asks for it. A secret that may be exposed and
    anything with a date are never parked;
  - send a ping only if the area's manual has a ping rule that allows one
    at this hour;
  - the chief of staff runs this mode at each scheduled report and uses
    the list as the report's queue, so the report and the to-do lists
    never disagree.

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
  Never answer a merge approval question (`merge <repo>#<N> at <head>?`)
  with `respond`, even when a standing decision seems to cover it. Only the
  user's own click counts, so link the thread for them.
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
  CONCERN or BLOCK findings), the area's owner to-do and ask lists (see the
  area's manual), open PRs from a bot that nobody has touched for 7 days,
  as one line per area with a count, and earlier questions you asked the
  user that are still unanswered in this session or in the session's own
  progress record.
- Also collect open PRs in an active area that no unsettled thread owns;
  list each as ownerless.
- A top-level thread settled since the last pass, not by this session:
  read its last message once. Its open asks leave the queue and are
  counted once in a "dropped with a settle: n" line that names each in a
  few words. Three kinds stay, as ownerless items answered in the chief
  of staff thread: a secret that may be exposed, an open PR, and anything
  with a date.
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
  the next step. When a lead or another coordinating thread
  runs the workers, send to it, not to its workers. Tell it about
  anything you changed in its workers' threads (settles, closed to-dos).
- An answer that needs no action ("keep", "leave it") still goes to the
  thread that listed the item, so it stops listing it.
- Include the user's words, the option text they picked, and any limit that
  still applies. When the user typed their own answer, quote it word for word.
  Read the returned status to confirm the thread started.
  Never give the time of the user's answer unless you read the clock when it
  arrived; otherwise write "in this pass".
- Log each decision once in the area's decision record and give the
  lead its number, so it does not log it again.
- Keep one area's content out of another area's record.
- A decision that becomes a standing rule goes into the project's
  standing-decision index when that file is in your write scope; otherwise list
  it for the user.
- Skipped decisions stay open and are not re-asked in the same session unless
  they block everything.

## 5. Log and settle

- Log each decision in the session's progress record: time, thread, question,
  answer, who decided.
- Never settle a thread on your own judgment. List the threads that look
  finished (work done, no open question or pending request, no PR waiting on
  the thread's own next step) and ask the user before settling any. Settle
  only the ones they name, with `t3_thread_organize` action `settle`.
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
