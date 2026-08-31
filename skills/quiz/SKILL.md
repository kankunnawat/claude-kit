---
name: quiz
description: Use only when the user explicitly says "quiz me" or asks for a comprehension check.
---

The user asked for a comprehension check on completed work.

1. **Scope the change.** Diff against the merge base; read any implementation-notes / Deviations files. Understand not just the diff but the existing code paths its behavior depends on — that's where skim-review fails.
2. **Write the report** (HTML to the scratchpad and render it; markdown inline if no renderer): context and intent, what was done and why, how it interacts with existing behavior, deviations from plan, risks and follow-ups. Write for someone who was away — intuition first, mechanics second.
3. **Quiz at the bottom:** 3–5 questions targeting what is least visible in the diff and riskiest if misunderstood. No trivia.
4. **Grade once.** Explain any misses with the relevant code. The user decides whether another round is useful.
