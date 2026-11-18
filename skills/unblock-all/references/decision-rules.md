# Decision rules

Shared by `unblock-here` (this thread) and `unblock-all` (every thread).
A rule both need lives here, once.

## Triage each ask

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
6. **Not ready to ask.** The ask rests on a claim nobody has measured or
   checked. Send it back to its thread for the measurement. It reaches the
   user only with the evidence attached.

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

## Present one batch

Ask with `AskUserQuestion`: one question per decision, at most 4 per call.
With more than 4, ask the 4 that unblock the most, then the rest after the
answers come back.

Keep every question and option short. The user reads them on a phone.

- **Question:** at most two sentences and about 40 words. First what is
  blocked, with plain words next to every PR or ticket number. Then the
  question. It stands on its own: the dialog may hide your earlier text.
- **Header chip:** `D1 <topic>`, one or two words.
- **Options:** 2 to 4. Label of 1 to 4 words, not counting the marker; the
  recommended one first, ending in "(Recommended)". Description of one
  sentence: the fact that decides it, or its main cost.
- **Outward writes:** an option that approves an outward write (a tracker
  write, a comment, a state change, a merge, a message to someone, spending)
  adds a second sentence starting "Approves:". Picking it is that approval,
  for that action, target and scope only.
- **Cut:** background the user already knows, a restated question, hedging,
  internal file names, and any option nobody would pick.
- **Plain words:** if the user answers "I don't understand", the question
  failed. Ask it again once in everyday words with a concrete example; it
  is still unanswered, so this is not a re-ask.
- Bundle many stale-looking old asks into one question ("close all as
  stale" or "review one by one").
- Questions from an earlier pass that are still unanswered come first,
  marked "still open", with their age. Drop one only when live state made it
  stale.
- Order by how much work an answer unblocks, then by how cheap it is to
  answer.
- Never re-ask what the user declined or already answered.
- Never use letters from a non-Latin script in labels.
- Never send the user to a PR, a doc or a board to answer. Link one only
  when the answer needs their eyes on an artifact or a UI.
- Without `AskUserQuestion`, send one text reply: number the decisions D1,
  D2 and the options 1, 2, 3, so "D1 2, D2 1" cannot be misread.

The reply around the questions is at most about 8 lines: a count line, the
actions for the user, "decided by me" one-liners, and what waits on other
people. No per-thread narration.
