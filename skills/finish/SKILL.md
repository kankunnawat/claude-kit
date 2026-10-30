---
name: finish
description: >-
  Use when the user confirms the work is good and wants it closed out (/finish, "ship it", "commit and push") — runs the project's declared Close-out ritual: commit, push, and whatever the "Close-out:" line in CLAUDE.md/AGENTS.md specifies. Not for unverified work.
---

# finish

Venue-agnostic close-out verb: the workflow is invariant, the project supplies
the specifics. **Only run once the user has confirmed the work is good** — never
to force closure on unverified work.

## Steps

1. **Resolve the ritual.** Look for a `Close-out:` line in the project's
   CLAUDE.md / AGENTS.md (repo root, then parents). Read it from the base
   branch on the remote (`git show origin/<base>:CLAUDE.md`); a local checkout
   can lag behind the rules. No line → default ritual:
   commit + push, nothing else. A project may declare other rituals (release,
   hotfix) with their own trigger words. /finish runs Close-out only and never
   continues into another ritual's steps unless the user used that ritual's
   trigger. Resolve the completion endpoint against the
   user's current instructions. Then resolve context the ritual needs: ticket
   key (branch name → conversation → recent commits), current branch, base
   branch. For required repository or deployment steps, resolve the repository
   owner, name, and visibility, plus the host project, account, and stable address.
   Take those targets from project guidance and the user's instructions.

2. **Prove tracker consistency.** When GitHub issues are in scope, fetch every
   issue targeted by `Closes`/`Fixes` and inspect its body live. If any checklist
   item remains unchecked, fail closed: use `Refs` and leave it open unless the
   user explicitly confirms closure or every remaining item is moved to linked
   trackers.
   Classify parent/umbrella versus leaf issues, and search semantic
   cross-references for the ticket/PR, including dependency prose without
   checkbox syntax. In issue bodies, explicitly mark each completed dependency:
   check its existing box or convert its dependency line to a checked item.

3. **Preflight.** Run the project's tests/linters for the touched area if the
   ritual or repo rules require green-before-commit. Review the full diff —
   check nothing unrelated or secret is staged; unrelated work gets unstaged,
   not shipped along.
   A fix in a repo with a test suite carries at least one regression check for
   the fixed path. Scripts written to prove the fix get committed or folded
   into the suite, never discarded. A new check must fail when the fix is
   reverted — a check that can only pass proves nothing.

   Dispatch ledger: when `ledger-log` is on `PATH`, list open rows for this
   branch —
   `cat "$HOME/Library/Mobile Documents/com~apple~CloudDocs/claude-memory/ledger/"*.jsonl | jq -sr --arg b "$(git rev-parse --abbrev-ref HEAD)" '[group_by(.id)[] | max_by(.ts)] | map(select(.branch==$b and .verdict==null)) | .[].id'`
   — and stop on any output: ask for the verdict and record it with
   `ledger-log verdict <id> approve|nits|changes|redo` before the commit. A
   branch with no rows passes; main-loop-only work is not gated.

   **Green is not safe.** When the close-out merges a PR or ships a
   multi-file or behavior-changing diff, get a verdict from an agent that did
   not write the code: a fresh-context reviewer (the `reviewer` agent,
   `/code-review`, or `@codex review`) runs or reads the change against the
   approved head and returns `PASS`, `PASS+NOTES`, or `FAIL`. Trivial
   reversible config, one-line, or copy edits skip this. Green CI and an
   approving bot comment are not verdicts. A verdict covers a patch: a /ship
   final whole-branch review already counts when its `git patch-id` matches
   the current diff; if the head moved, re-verify on any real change. `FAIL`
   stops the close-out; report it.

4. **Prove frontend changes visually.** If the shipped diff changes a
   user-facing frontend, the PR must carry visual evidence before merge.
   First check what images are already attached (e.g. by /ship): if they
   match the final diff and render, verify and move on — don't recapture.
   Text-only evidence (measurement tables, smoke counts, audit output) never
   satisfies this step; capture before merge. If images are missing or stale
   (the diff changed since capture), capture the final
   implemented app itself with representative synthetic/test data. Generated
   images, mockups, and design references do not satisfy this proof. Cover
   desktop, mobile, and each materially changed state needed for review (for
   example list and detail).
   Resolve the capture harness and attachment mechanism from the project's
   CLAUDE.md/AGENTS.md and memory store — projects differ (seeded local dev +
   gist embeds, Playwright recording as a PR comment, signed sim build,
   proof-agent report gate). No declared convention → default: capture with
   the repo's usual harness and attach as GitHub user-attachments. Either
   way, verify every image/video actually renders in the PR.

5. **Execute in order.** `/finish` approves declared repository and host setup,
   push, and any deploy the Close-out ritual itself declares, when resolved
   targets match the user's instructions. A project rule that reserves
   production changes (promote, rollback, alias, host settings) to the user's
   explicit request overrides this: stop and report instead.
   Reuse approval for the same action, target, and scope.
   Merge exactly the head the user approved (`gh pr merge --match-head-commit
   <full SHA>` or the host's equivalent). A head that moved after approval,
   even with fixes, needs new approval; silence is not approval.
   If scope is missing or conflicts with user instructions, complete useful
   preflight and ask only for the unresolved scope before the external write.
   Other outward-facing actions need approval except `git push` to the usual
   remote and step 4's evidence upload when images show only synthetic or test
   data (declared route or the user-attachments default).
   Comments on another person's PR and artifacts or transitions created under
   the user's name in an external tracker always need content-and-scope approval
   (count, targets, and owner).

   Provision missing prerequisites for the resolved ritual:

   - Reuse the matching repository; create it private unless the user expressly
     requests public visibility. Set `origin` and verify its owner and visibility.
   - Reuse the matching host project; create and link it in the resolved account
     through sanctioned tools. Verify the link targets that account and project.

   Complete all close-out bookkeeping — tracker edits, ledger/status-doc
   updates — *before* the first PR push, so it rides the same commit set.
   Never trigger another full CI run solely for tracker or ledger edits; rerun
   only after substantive changes or a failed-gate repair. Typical steps a
   ritual declares:

   - commit (project's commit convention, ticket key in subject)
   - push (branch policy per the ritual — direct vs feature branch + PR)
   - deploy (when declared; for CLI-hosted sites, run the host's deploy command)
   - tracker update (e.g. Jira comment + matching status transition — use the
     project's declared comment shape)
   - status-doc/memory updates

   For public deployment, verify the intended build at the stable address and
   the project's indexing rules. A Git push alone does not deploy a CLI-hosted site.
   Skip optional steps whose precondition is absent (no ticket key → no tracker
   step; say so). A required remote or host project that is missing needs the setup above.
   After merge, re-read the tracker state and checklist; reopen
   an umbrella that was auto-closed with unchecked work and report the repair.

6. **Post-merge tail.** Rituals with steps *after* the merge — deploy
   verification, live smoke, tracker → Done, worktree cleanup — are the part a
   cleared session loses: the merge feels like the end, and only bookkeeping
   is left. Treat the tail as its own phase.
   - Before merging, list the outstanding tail steps in your report so they
     survive into the next context.
   - /finish is re-entrant: invoked on an already-merged branch, skip to the
     tail and run only what is outstanding.
   - Never report the close-out complete while a tail step is outstanding —
     name what remains.
   - A workflow checkpoint is not the requested task's completion boundary.
     Continue an already-authorized tail in the same task. Stop and report the
     incomplete state only when new authority or a real blocker is required.

   Required check failures trigger diagnosis and an in-scope repair. Do not
   integrate until every required check passes. Resolve deployment authority
   through step 5; implementation approval alone does not grant it.

7. **Clean up the ticket worktree.** Last step once the PR is open and the
   branch is pushed, so a finished ticket stops costing disk (worktrees with
   SPM checkouts and DerivedData filled the disk before). Every workflow ends
   here: pstack arena/swarm and tstack full-send/file-pr/babysit-pr close with
   /finish. Run the block below from inside the worktree. It is idempotent: a
   re-run, or a run in the main checkout, only reports.
   - Removes the worktree only when origin's branch tip equals local HEAD, a
     PR exists, no gitignored file (`.env`, local config) exists only here,
     and no process other than this session (herdr, t3, codex, cc, editors)
     has files or cwd inside it.
   - Uncommitted work is backed up first to `wip/backup-<name>` through a temp
     index, and the remote SHA is verified; removal then still waits, because
     `git worktree remove` refuses dirty trees and `--force` is never used.
   - Keeps the branch, never deletes any branch, never uses `--force`, never
     merges. Report what was removed and the freed size, or the skip reason.

   ```bash
   ( set -u
   skip() { echo "CLEANUP SKIPPED: $*"; exit 0; }
   WT=$(git rev-parse --show-toplevel) || skip "not in a git worktree"
   WT=$(cd "$WT" && pwd -P)
   CD=$(cd "$(git rev-parse --git-common-dir)" && pwd -P)
   MAIN=$(git -C "$CD" worktree list --porcelain | sed -n '1s/^worktree //p')
   [ "$WT" != "$MAIN" ] || skip "$WT is the main checkout, not a ticket worktree"
   B=$(git rev-parse --abbrev-ref HEAD); NAME=$(basename "$WT"); H=$(git rev-parse HEAD)
   [ "$B" != HEAD ] || skip "detached HEAD"
   # 1. Pushed and in a PR: remote tip must equal local HEAD.
   R=$(git ls-remote origin "refs/heads/$B" | cut -f1)
   [ "$R" = "$H" ] || skip "origin/$B (${R:-missing}) != HEAD ($H); push first"
   PR=$(gh pr view "$B" --json url -q .url 2>/dev/null) || PR=
   [ -n "$PR" ] || skip "no PR for $B"
   # 2. Gitignored files that exist nowhere else (.env, local config). Rebuildable caches are fine.
   REGEN='(^|/)(node_modules|\.build|build|DerivedData|SourcePackages|Pods|dist|\.next|\.turbo|\.swiftpm|__pycache__|\.venv|target|coverage|\.DS_Store)(/|$)'
   UNIQUE=$(git ls-files --others --ignored --exclude-standard --directory | grep -Ev "$REGEN" | while IFS= read -r f; do
     f=${f%/}; if [ -d "$WT/$f" ]; then diff -rq "$WT/$f" "$MAIN/$f" >/dev/null 2>&1 || echo "$f/"
     else cmp -s "$WT/$f" "$MAIN/$f" || echo "$f"; fi; done)
   [ -z "$UNIQUE" ] || skip "ignored files exist only here (copy them out first): $(echo $UNIQUE)"
   # 3. Uncommitted work: back up to wip/backup-<name> with a temp index, verify on origin.
   if [ -n "$(git status --porcelain)" ]; then
     TMP=$(mktemp); cp "$(git rev-parse --git-path index)" "$TMP"
     GIT_INDEX_FILE=$TMP git add -A && T=$(GIT_INDEX_FILE=$TMP git write-tree); rm -f "$TMP"
     D=$(git log -1 --format=%cI HEAD)
     C=$(GIT_AUTHOR_DATE=$D GIT_COMMITTER_DATE=$D git commit-tree "$T" -p "$H" -m "wip backup of $NAME ($B)")
     git push -q origin "${C}:refs/heads/wip/backup-${NAME}" || skip "backup push failed"
     [ "$(git ls-remote origin "refs/heads/wip/backup-$NAME" | cut -f1)" = "$C" ] || skip "backup verify failed"
     echo "backed up uncommitted work to wip/backup-$NAME ($C)"
     skip "worktree has uncommitted changes; backed up, but git worktree remove refuses dirty trees and --force is never used. Commit or drop them, then re-run"
   fi
   # 4. No live process (herdr, t3, codex, cc, editors) holds files or cwd inside it. Own session ancestry excluded.
   cd "$CD" || skip "cannot cd to $CD"
   ME=" $$ "; p=$$; while [ "$p" -gt 1 ]; do p=$(ps -o ppid= -p "$p" | tr -d ' '); ME="$ME$p "; done
   USERS=$(lsof -nP -Fpcn 2>/dev/null | awk -v w="$WT" '/^p/{pid=substr($0,2)} /^c/{cmd=substr($0,2)} /^n/{n=substr($0,2); if (n==w || index(n, w"/")==1) print pid" "cmd}' | sort -u | while read -r pid cmd; do case "$ME" in (*" $pid "*) ;; (*) echo "${pid}:${cmd}";; esac; done)
   [ -z "$USERS" ] || skip "in use by: $(echo $USERS)"
   # 5. Remove from the common dir, prune, keep the branch.
   KB=$(du -sk "$WT" | cut -f1)
   git worktree remove "$WT" || skip "git worktree remove refused"
   git worktree prune
   echo "removed $WT (branch $B kept, PR $PR), freed ~$((KB/1024)) MB"
   )
   ```

8. **Report** what was done in one short block: commit hash, branch/PR, tracker
   actions taken or skipped and why, worktree cleanup result, plus deployment address and verification
   when required by the completion endpoint.

9. **Log the day.** When the loaded instructions declare a `Daily-log:`
   location, append this close-out to today's file there, following that
   location's own rules for date and format. One bullet per item: what
   shipped (commit, PR), tracker actions, and what stays open. Facts from the
   report only; no secrets or customer data. No declaration → skip and say so.

## Declaring a ritual (for CLAUDE.md authors)

One line, imperative, ordered:

```
Close-out: commit to main + push; if an issue key is in scope, post a tracker comment (RCA/solution shape) + matching status transition.
```
