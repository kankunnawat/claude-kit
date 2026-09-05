# Bulk worktree cleanup

Use this procedure only after the resident skill requires a keep/stale/remove report and approval.

`git worktree remove` deletes the checkout, not its branch or committed objects.
Uncommitted files are the immediate loss risk; sort on that before merge state.

## Classify

1. Ask GitHub for merge state in squash-merging repositories: `gh pr list --head "$branch" --state all --json number,state,mergedAt`.
   Do not trust `git cherry`, `git branch --merged`, or patch-id after a squash merge.
   A branch without a PR may have fed a collector; verify the collector merge commit against trunk and confirm a marker in a touched file.
2. Check uncommitted work with `git -C <wt> status --porcelain`.
   Any output goes in the stale bucket for the user's decision; list the files.
   Offer keep, remove generated dependencies only, or commit and push through an authorized workflow.
3. Check live processes and the repository's lease or claim ledger.
   The repository ledger owns paths when one exists.
4. Re-read `git worktree list --porcelain` immediately before mutation and assert protected paths are absent.
   Cross-check every directory against the registry because `git -C <dir>` can fall through to a parent repository.

Finish with `git worktree prune`, the runtime's approved recoverable deletion tool for unregistered leftovers, and a final `git worktree list`.
Do not use a broad recursive delete.
Branch-reference deletion remains a separate operation governed by the resident guard in `SKILL.md`.
