---
name: worktrees
description: Use when creating a git worktree, asking where worktrees should live, cleaning up worktrees after work merges, or auditing accumulated worktrees to reclaim disk space.
---

# worktrees

Parallel worktrees are the biggest throughput unlock — each one runs its own
session. This skill is the *housekeeping*: where they live, how to make one,
and the cleanup that keeps them from filling the disk.

## Path convention

Worktrees live **inside the repo** at `<repo>/.claude/worktrees/<branch-keyword>/`
— never as siblings of the main repo. Sibling layout pollutes the parent
directory as branches multiply.

Prefer Claude Code's native worktree tooling (`EnterWorktree`, or
`isolation: "worktree"` on an Agent spawn), which uses this layout
automatically. For manual creation, run from the main repo:

```bash
git worktree add .claude/worktrees/<branch-keyword> <branch>
```

`.claude/` should already be gitignored. To migrate existing sibling worktrees
into the convention, use `git worktree move` — don't re-clone. A parent
directory filling up with stray checkouts is the symptom of ignoring this.

## Cleanup discipline

**Clean up worktrees when done.** Once a worktree's work is merged (or
abandoned), remove it in the same session:

```bash
git worktree remove <path>
git branch -D <branch>
```

Leftover worktrees carry gigabytes of build products (SPM checkouts,
DerivedData) and have filled the disk before. Keep only branches the user
explicitly parks.

Safety net, not a substitute: if the machine runs a scheduled sweep job, it
removes clean + fully-merged worktrees under `.claude/worktrees/` and
`.worktrees/` and reports the rest, logging to its own configured path.

**It is blind in squash-merging repos** — it judges "merged" by commit
reachability (`rev-list --count HEAD --not --branches --remotes`), and a squash
merge creates a new commit, so a fully-landed branch still reads as
`keep — N unmerged commit(s)`. The failure is safe (it under-removes, never
over-removes) but it means such repos silently accumulate gigabytes and need the
manual audit below. It also leaves unregistered orphan dirs alone by design
(`orphan — inspect manually`).

## Auditing a pile of worktrees before a bulk cleanup

When worktrees have accumulated and the user wants space back, produce a
**keep / stale / remove report first** and let them approve it. The classification
rests on one fact:

> `git worktree remove` deletes the **checkout**, not the branch. Every commit
> survives in `.git`. **Only uncommitted files are losable** — sort on that, not
> on merge status.

Merge status decides whether you'd ever want the checkout *back*, not whether
removing it destroys anything. That distinction turns a scary bulk delete into a
routine one.

**1. Merge state — ask GitHub, never patch-id.** In a squash-merging repo
`git cherry` / `git branch --merged` / patch-id report every landed branch as
unlanded, because the squash commit shares no patch-id with the originals.

```bash
gh pr list --head "$branch" --state all --json number,state,mergedAt
```

A branch with no PR isn't automatically unlanded — it may have fed a collector
branch that shipped. Confirm by checking the collector's merge commit is an
ancestor of the trunk (`git merge-base --is-ancestor <mergeSha> origin/dev`) plus
a marker string from the work in the trunk's copy of a touched file.

**2. Uncommitted work — the only real risk.** `git -C <wt> status --porcelain`.
Non-empty ⇒ **stale bucket, user's call**, and list the files in the report.
Offer: keep as-is · trash only `node_modules` (most of the size, zero risk to the
dirty files) · commit+push so it becomes removable.

**3. Live sessions — check the lease, not just the process list.** A process
roster shows who's running; if the repo has its own lock/lease/claim ledger, that
is the authority over who owns a path. Check both and cite the lease.

**4. Re-read the registry immediately before removing.** Other sessions may be
sweeping concurrently — a list built minutes ago can be stale, and a removal you
didn't perform is indistinguishable from one you did. Build the removal list from
`git worktree list --porcelain` at execution time, and assert the protected paths
are absent from it before running anything.

Beware measurement artifacts: `git -C <dir>` on a directory that is *not* a
registered worktree silently falls through to the parent repo and reports **its**
status. Cross-check any dir against `git worktree list` before believing a dirty
count.

Finish with `git worktree prune`, `trash` (never `rm -rf`) for unregistered
leftover dirs, and `git worktree list` to confirm what remains.

### Deleting the branch refs afterwards is a separate, riskier job

Worktree removal keeps the commits; **`git branch -D` is what can orphan them.** Do
it only on request, and verify against a ref you are **keeping** — the trunk, or
the collector branch that shipped the work:

```bash
git merge-base --is-ancestor "$tip" origin/dev        # or the surviving collector
```

`rev-list --count "$tip" --not --exclude=refs/heads/"$b" --branches --remotes`
looks like the right check and **lies when you delete a set**: siblings cover each
other, so every branch reads `0 unique` right up until you delete them all and
dissolve the mutual coverage. Measured per-branch, decided per-set.

Save `git for-each-ref --format='%(objectname) %(refname:short) %(contents:subject)'`
to a file first — objects survive ~30 days, so `git branch <name> <sha>` restores
anything the check got wrong.

## Related rules that stay resident

These live in your global rules, not here — they must hold before any worktree
exists: subagents that modify files always work in their own worktree
(read-only subagents don't need one); solo repos work directly on `main` and
merge a worktree back to `main` rather than opening a feature branch in the
shared tree.
