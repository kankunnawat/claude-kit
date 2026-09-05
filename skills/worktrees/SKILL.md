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

Before bulk audit, recovery, or cleanup, read `references/bulk-cleanup.md`.
If the reference is missing, that blocks the bulk operation; routine creation and
a separately authorized single-worktree removal remain available.
A keep/stale/remove report and approval come before bulk mutation.
Uncommitted work, live leases, a fresh registry, protected paths, and commit
retention remain mandatory guards.

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
