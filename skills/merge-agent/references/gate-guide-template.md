# PR gate guide template

The merge-agent skill fills this template when a repo has no PR gate guide.
Replace every `[bracket]` with a fact about this repo, or cut the line.
Paste the result as a `## PR gate` section in the file the repo's agents already read (`CLAUDE.md` or `AGENTS.md`).
Open it as a pull request. It waits for [owner], like every change to a gate.

Everything below the line is the guide.

---

## PR gate

Every pull request body carries a risk line and a reason:

```
Risk: low|medium|high
Safe because: <one sentence>
```

The author sets the tier.
The highest row that matches any file or behavior in the diff wins.
A reviewer or the merge agent who disagrees with the tier raises it, never lowers it.

| Tier | The diff has | Who reviews | Proof before merge |
|---|---|---|---|
| Low | Only docs, tests, comments or UI copy. No runtime behavior changes. | A fresh review of the full diff passes at the head commit. | CI is green on the head commit. |
| Medium | A behavior change in [main source paths] that fits no high row. | A fresh review passes at the head commit. | The low proof. The change runs the way a user would use it, with [verification skill or command]. The PR body shows that proof. |
| High | A file under [migration, deploy and CI paths]. Code that writes or deletes [customer or user] data. Sign-in, sessions, roles, tokens or secrets. [Money rules, if any.] A change to this guide. | The medium review, plus [a second independent reviewer, or the owner]. | The medium proof, run on [a copy of real data or a staging cell]. It writes nothing to a live system. |

### Fresh review

- A fresh review comes from a session or person that did not write the change.
- The reviewer gets the diff range and the head commit, not the author's conclusions.
- The review passes with 0 blocker and 0 important findings left open.
- A minor finding is fixed or listed under "Known gaps" in the PR body.
- The review names the commit it read.

### Verdict format

The verdict goes [in the PR body under "Proof", or in a PR comment that starts with `[PREFIX]:`].
It names the head commit, the tier, the reviewer and the finding counts:

```
[Verdict line, for example: Proof: PASS at <full SHA>, tier medium, reviewer <who>, 0 blocker, 0 important, 1 minor]
```

### A new commit needs a new review

The review, the proof and the merge bind to one full head SHA.
A commit after the reviewed one needs a review of the new range before merge.
Proof from an older commit is reported as carried over, with that commit.

### Merge

- [Owner], [other maintainers] or an agent merges once the gate for the tier passes at the head commit.
- An agent merges only where the owner's guardrails allow it.
- Use [a merge commit, or squash]. [Say what this repo never does.]
- Pin the head: `[the repo's merge command, with --match-head-commit <full SHA>]`.
- Never use `--auto` or `--admin`. Never enable auto-merge.
- For stacked pull requests, merge from the bottom.
  After each merge, change the next pull request's base to `[default branch]` and wait for CI before you merge it.

### What always waits for the owner

A pull request that changes any of these waits for [owner]. An agent does not merge a change to its own gate.

- This guide, wherever it lives.
- `CLAUDE.md` or `AGENTS.md`, at any depth.
- Anything under `.claude/`, `.agents/` or `.github/`, at any depth.
- [Other paths this repo holds back, such as release files or schema migrations.]

A flag or hold label on a pull request stops the merge. Only [owner] adds or removes it.

### After merge

- [Steps that follow a merge here, such as a staging check, a tracker move or retargeting a stacked PR. Write "Nothing." if there are none.]
- The merge agent writes nothing to the tracker. Its landing report names the move, and [the coordinator, or the owner] makes it.
