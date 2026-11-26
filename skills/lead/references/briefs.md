# Brief templates

Fill every `<blank>`. Keep every fixed line. One brief per session.
A brief is self-contained: the session knows nothing else.

## Lines every brief carries

```
You work for the <area> lead. Do the work yourself; no subagents.
No PR comments, no tracker calls (the connector may not load in a new
session; the task text is below).
Machine rule: <the area manual's machine rule, or none>. Check `uptime`
before any test run and wait if the 1-minute load is <max load: the
manual's limit, or this machine's core count> or more.
Run lint, test suites, browser checks and full proofs through
`verify-lane -- <command>`.
Check `df -g /` shows at least <min free> GiB free before anything that writes a lot.
Stage files by explicit path only. Never force-push. Delete with trash.
<the area's worker rules, word for word from its manual or the repo's rule
file>

Task (the owner's words or the tracker text, word for word): <key or short
name>, "<title>". "<body>"

End with exactly one message, then stop:
~/.t3/bin/t3 thread send <the area's inbox thread id, or the lead's thread
id> "<fixed report line>"
```

The Lane and Integration lane briefs are for batch mode only. A watch lead
uses Scout, Worker, Reviewer and Fix round. The Merge agent brief stands
alone: it carries none of the lines above.

## Scout (read-only pre-screen)

```
You are a read-only scout. No edits, commits, pushes or claims. No installs,
tests, builds or browser. Read with rg, git and gh only. Fetch the trunk and
say which sha you read.

Goal: <what the owner asked for>. Pre-screen <n> items so the lead can
start at most <m> workers.

For each ticket, with file:line evidence:
1. Still true on the trunk today? Already fixed or touched by a commit or an
   open PR?
2. The smallest correct fix and where it lives. Files, rough size, generated
   files it changes, gate baselines that move.
3. The proof it needs, and whether that proof can run under the machine rule
   now.
4. Risk and reviewer tier. Does it need the owner's review flag?
5. Conflicts with work in flight: <lane branches and their files>.
<ticket-specific questions>

End with a lane split: which tickets to run now, in what order, and what
each lane must not touch.

Report file: <record folder>/prescreen-<name>.md, verdict table at the top.
Report line: "Pre-screen <name> done: <path>. <key> <verdict, one line>. ...
Lanes: <split>."
```

## Worker (watch mode: opens the PR)

```
Worker <name> for <the item in plain words>. Branch named as the repo's
rules say, cut from the trunk at <full sha>, in your own worktree.

Read first: the repo's rule file and its PR gate, from the remote default
branch.

Done when: <what a user or caller can observe>.
Scope: <files or packages>. Not in scope: <list>.

Method: test first: show the new test red, then green. One logical change
per commit, subject 72 characters or fewer.

Proof at your head: <the checks the repo's gate names>, `git diff --check`.
Say what you did not run and why.

Visible change: capture <routes, states, viewports, languages> into
<local folder>/artifacts/<name>/ before you report, and list anything odd
you see in them.

Push the branch, no force. Open the PR the way the repo's close-out says,
against <base branch>. Never merge. Never arm auto-merge.
Report line: "<name>: PR <url>, head <full sha>. Done-when <met | not met>.
Red to green <lines>. Checks <summary>. Captures <n files, odd: list or
none>. Deviations <list or none>."
```

## Lane (batch only)

```
Lane <name> for <key> (<plain words>). Branch <type>/<area>/<key>-<slug>,
cut from the trunk at <full sha>, in your own worktree. No PR: push the
branch only.

Read first: <shared lane rules file>, then the scout report <path>,
section <key>.

Done when: <what a user or caller can observe>.
Scope: <files or packages>. Not in scope: <list>.
Must not touch: <files held by other lanes>.

Method: <the area's start step from its manual, if any> Test first:
show the new test red, then green. One logical change per commit, subject 72
characters or fewer.

Generated files: commit source only. If a bundle, compiled stylesheet or
lockfile must change, regenerate it locally for your own proof, leave it
modified and uncommitted, and write the regenerate command in your state
file. Never stage, stash or restore it.

Proof at your head: <named test files, one at a time>, <light gates>,
`git diff --check`. Say what you did not run and why.

UI change: capture <routes, states, viewports, languages> into
<record folder>/artifacts/<name>/ before you report, and list anything odd
you see in them.

State file: <record folder>/<name>.md with CURRENT STATE, red and green
lines, head, checks, and an "Integration lane runbook" section (regenerate
commands, checks that must be green after, capture list).

Push the branch, no force.
Report line: "<name>: ready, head <full sha>. Done-when <met | not met>.
Red to green <lines>. Checks <summary>. Captures <n files, odd: list or
none>. Deviations <list or none>."
```

## Reviewer (one-shot, fresh)

Run the repo's tier tool before the first reviewer starts (lead step 5).
One brief per review the tier asks for, and at least one per head.

```
You are a one-shot independent reviewer. You did not write this change.
Review only: no edits, commits, pushes, PR comments, labels or tracker
writes. No installs, tests, builds or browser.

Read first: <shared review rules file>, <tier checklist file>, the
worker's report or state file <path> (claims to verify, not trust).

Goal and done-when: <copied from the worker's brief>.
Tier: <the tier the repo's tier tool gave>. This review: <which of the
tier's reviews this one is>.
Range: <trunk full sha> .. <head full sha> on <branch>. <n> commits,
<n> files.
Known and expected, not a finding: <for example, generated pair not
committed by rule>.

Check, with commands and output quoted:
1. Scope: every changed file belongs to the done-when.
2. The change itself: <specific risks from the scout report>.
3. Tests assert what a user or caller observes; each new case would fail on
   the trunk; no assertion weakened or deleted.
4. Captures, if any: read each one against the done-when.
5. Light gates, each alone, exit code read unpiped: <list>.
6. Commits: subjects, no trailers, <project commit rules>.
7. Does it need the owner's review flag?

Report file: <record folder>/review-<name>.md, first line
`VERDICT: PASS|CONCERN|BLOCK at <short sha>`, then findings with file:line
marked MUST or SHOULD, what you verified, what you could not verify, and,
in batch mode, a list for the integration lane.
Report line: "review-<name>: <VERDICT> at <short sha>. Done-when <met | not
met>. <one line per finding or none>. Flag <agree | disagree>. Report
<path>"
```

## Merge agent (only under a standing approval, lead step 7)

```
You are the merge agent for <repo>, started by the <area> lead under this
standing approval, quoted from the area's manual: "<the approval line,
word for word>" (<its date>). Act inside its exact scope and no further.

Run /merge-agent as written, in this checkout. This brief names no PR to
merge and gives no merge instruction; the skill, the repo's gate guide
and the merge guard decide each PR.

End with exactly one message, then stop:
~/.t3/bin/t3 thread send <the area's inbox thread id, or the lead's thread
id> "merge-agent <repo>: <one line per PR, as the skill reports it>"
```

## Fix round

```
Fix round <1 | 2> of 2 for <key>, worker <name>. Fresh context, the
worker's own worktree, branch <branch>, pushed head <full sha>.

Read first: <the rules the first brief named>, the state file if there is
one, the review <path>.
State you inherit: <files modified and uncommitted on purpose, and why>.

Fix exactly these, each test-first in its own commit:
1. <finding, file:line, the observable test>
2. ...
Not in this round: <list, and who handles each>.

Proof, captures (recapture only what changed, names ending
`__after-fix<n>`), state file update, push: as in the first brief.
Report line: "<name> fix <n>: head <full sha>. <finding> <done | not done>
... Red to green <lines>. Checks <summary>. Deviations <list or none>."
```

## Integration lane (batch only)

```
Integration lane for <date>. Build branch <daily branch> from the fresh
trunk and open the single daily PR after <time>.

Inputs: <lane branch, head, state file, review file> for each lane.

Steps:
1. Put each lane's source commits on the daily branch. Drop lane commits
   that only carry generated files.
2. Reword subjects over 72 characters.
3. Regenerate every generated pair once, in one commit, with the commands
   from each lane's runbook. Re-run each lane's tests that depend on them.
4. Run the heavy proof under the machine rule: <typecheck, wide tests,
   off-machine runs>.
5. Take the captures the lane runbooks list, from the daily branch.
6. Own any gate baseline change, with the measured number.
7. PR text: what changed per ticket, proof, Deviations (copy each review's
   list), UI captures at the top. Flag it for owner review if any review
   said so.
Never merge. Never arm auto-merge.
Report line: "integration <date>: PR <url>, head <full sha>. Lanes in
<list>, held <list and why>. Proof <summary>. Flag <set | not needed>."
```
