# Land PR skill: design

Date: 2026-11-25.
Status: needs Kan's approval.
Home: `skills/land-pr/` in this repo (claude-kit).

## Goal

Work stops today when the PR opens.
The review, the follow-up fixes and the merge are then a second job that Kan starts by hand, with a different verb in each repo.

Kan types `/land-pr` on a branch that has an open PR.
The session takes that one PR to merge-ready, or to merged where his guardrails let an agent merge.
It gets a review from a session that did not write the change, fixes what the review confirms, and gets the fixes reviewed once.
In a repo that declares its own PR gate, it follows that gate and adds nothing to it.

## Usage, written first

```text
/land-pr          # the open PR of the current branch
/land-pr 123      # that PR
```

What Kan sees first:

```text
PR: #123 "fix(sync): keep the cursor on retry", head 4f2a9c1
Gate: none declared here, so the built-in loop runs
Landing: allowed by your guardrails (solo repo, merge commit, pinned to the commit)
Worktree: recreated from the kept branch
```

What Kan sees at the end:

```text
Round 1: 6 findings: fixed 2, noted 3, dismissed 1
Round 2: 0 findings on the fix commits
Evidence: tests pass, CI green on 9be0d77
Verdict: PASS at 9be0d77, reviewed by a fresh session
Landed: merged into main as a1c3e55
Open for you: 1 note that needs its own ticket
```

## What exists today (grounding)

Every piece of this loop already exists.
No single verb starts from an open PR and runs them in order.

| Piece | What it does | What it lacks for this job |
|---|---|---|
| `sol-loop` (tstack) | Fresh reviewer, fix, re-review, three rounds | It does not push, watch CI or merge |
| `babysit-pr` (tstack) | Fixes CI failures and bot findings on an open PR | It has no verdict from a fresh reviewer |
| `merge-agent` | Checks the verdict at the exact head and merges under the guardrails | It never fixes, because a fix would make it the author and void its own review |
| `finish` | Commit, push, tracker, worktree cleanup | It runs only after Kan says the work is good |
| `full-send` (tstack) | Chains all of it from the current state to merged | It also grants full autonomy and the testing permission |
| `lead` | Review and two fix rounds across many worker sessions | It is built for a whole area, with separate sessions |

Two repos on GitHub already run the loop as their own gate.
Both follow the same order.
They tier the diff, review by tier, fix, review again, record a verdict at one commit, and land.

| | hausback-core | AlphaOS |
|---|---|---|
| Tier | `lane-ops tier`, T0 to T3 | `pnpm review tier`, T0 to T3 |
| Fix loop | BLOCK means a new head and a new verdict; CONCERN carries conditions | BLOCK means a new head and a new review |
| Verdict | `HB-REVIEW:` comment written by a tool | `AOS-REVIEW:` comment, checked by `pnpm review check` |
| Who signs | never the author's seat | a reviewer that did not write the change |
| Landing | the merge lane | `alphaos-merge` |

The triage labels and the one-round cap in the built-in loop come from a gate Kan already runs in a third repo, which is not on GitHub.

I ran `merge-agent.py doctor` on four repos on 2026-11-25.

| Repo | `gate_guide` | Guardrails name it | What `land-pr` does there |
|---|---|---|---|
| duopreneur/AlphaOS | found (`CLAUDE.md` Close-out) | yes | follows the repo's gate |
| duopreneur/hausback-core | found (`AGENTS.md`, 3 linked guides) | no | follows the repo's gate, stops at merge-ready |
| kankunnawat/dotfiles | none (`review_rules_hint` true) | yes, solo repo | built-in loop |
| kankunnawat/claude-kit | none | yes, solo repo | built-in loop |

`doctor` cannot read a repo that is not on GitHub.

`/finish` step 7 removes the ticket worktree once the PR is pushed, and two rule files say every workflow closes with `/finish`.
So the worktree is usually gone before the first review finding arrives.
The branch is kept, so the worktree can be rebuilt from it.

## Shapes considered

| Shape | Verdict |
|---|---|
| Fold the loop into `/finish` | No. `/finish` runs after Kan confirms the work, and the loop is how the work gets there. The skill is also 231 lines already. |
| Fold it into `merge-agent` | No. Its verdict only counts from a session that did not write the change, and a fix makes it the author. |
| Add a reviewer step to `babysit-pr` | No. tstack skills install unchanged, so the edit would be lost on the next install. |
| Say "full send" on the open PR | Works today for an unattended run. It carries the autonomy and testing grants, which an attended run does not need. |
| A thin skill that composes the others | Chosen. |

## How it runs

1. **Find the PR and its worktree.**
   Take the PR number, or the open PR of the current branch.
   When the branch has no worktree, recreate one from the kept branch with the `worktrees` skill.
   Stop when the PR belongs to another author, unless Kan says yes for that PR.
2. **Doctor.**
   Run `merge-agent.py doctor`, which reads the remote default branch.
   Its output picks one of three paths, and no repo name appears in the skill.
   - A gate guide exists: follow the repo's gate (step 3).
   - No gate guide: run the built-in loop (steps 4 to 8).
   - The repo is not on GitHub, or the doctor cannot read it: print the repo's own gate command for Kan to type, and stop.
3. **A repo with a gate guide.**
   Read the whole guide and every file it points to.
   Do what the guide gives the author to do, with the repo's own tier command, reviews and verdict format.
   - The guide lets a fresh reviewer session sign: run the tier's reviews with fresh reviewers, fix what blocks, and record the verdict in the repo's format.
   - The guide forbids the author's seat to sign: ask for the review the guide names, wait with the `babysit-pr` watcher, fix each blocking item, and push. The reviewer's seat signs.
   Then go to step 9.
   The cap in step 6 applies only where the guide sets none.
4. **Round 1: one fresh review of the whole PR.**
   The reviewer is a session that did not write the change.
   It gets the diff range and the full head SHA, never the author's conclusions, and its brief forbids edits and merges.
   Read CI results and bot findings on the head in the same pass, under the `babysit-pr` rules.
5. **Triage.**
   Give every finding one label.
   - **Fix**: a confirmed bug or security hole, in code this PR changed or now calls differently. You can name the line and the input that breaks it.
   - **Note**: real, but outside this PR's change, or a preference. Listed for Kan only when he must decide or it needs a ticket.
   - **Dismiss**: wrong or not confirmable. Counted, not listed.
   Only Fix changes code.
6. **Fix, then round 2.**
   Save the head before the first fix commit.
   Commit each fix on the branch, never amend, never force-push.
   Push, then get one fresh review of the fix commits only.
   There is no round 3.
   A confirmed bug in the fix commits gets fixed, and the verdict is then NOT YET until Kan asks for one more review of that range.
7. **Evidence.**
   Run the repo's tests and linters for the touched area, heavy ones through `verify-lane`.
   Required CI checks must be green on the final head.
8. **Verdict.**
   The verdict names the last head a reviewer read.
   PASS needs all of these: that head is the PR's current head, no Fix is open, and the evidence is green.
   Anything else is NOT YET with the blocking item.
   Record it as one PR comment in the line shape of `merge-agent`'s gate-guide template.
   The line gives the result, the full head SHA, the reviewer and the finding counts.
9. **Land.**
   Open the guardrails file at the lines the doctor reports and read the whole rule.
   Where the rule lets an agent merge this PR, run `merge-agent.py precheck <pr> --reviewed-head <full SHA>`, then type the pinned merge command.
   A repo with a gate guide lands through `merge-agent` or the lane skill its guide names.
   Everywhere else, stop at merge-ready with the PR link, the head SHA and the exact command for Kan.
   Never `--auto`, never `--admin`, and never around a refusal from the merge guard.
10. **Close out.**
    Run `/finish` for the tracker, the worktree cleanup and the daily log.
    Step 7 of `/finish` removes the worktree as it does today, whether the PR merged or waits for Kan.

## What changes outside the new skill

| File | Change |
|---|---|
| `README.md` | One table row for `land-pr`. |

Nothing else changes.
`/finish` keeps removing the worktree when the PR is pushed, and `land-pr` rebuilds it in step 1 when it is gone.
The rule files keep "every workflow closes with `/finish`".
`land-pr` runs only when Kan types it, so no workflow chains into it.

`land-pr` needs no script of its own.
It reads through `merge-agent.py doctor` and `precheck`, and the session types every write so the merge guard judges it.
I read the script: `precheck` does not need a gate guide, but I have not run it on a PR in a repo without one.

## Authority rules

- This skill grants nothing. The guardrails file and the merge guard decide where an agent may merge.
- A repo's gate guide wins over this skill on every point.
- The author's session never signs where the repo's guide forbids it.
- A verdict binds to one full head SHA. A commit after the last review means NOT YET.
- A PR that changes a gate guide, `CLAUDE.md`, `AGENTS.md`, `.claude/`, `.agents/` or `.github/` stops at merge-ready for Kan.
- Comments on another person's PR and tracker writes under Kan's name keep their own approval rule.

## Proof plan

A skill is prose, so the proof is behavior on real PRs.

| Case | Passes when |
|---|---|
| A PR in claude-kit, no gate guide | The loop runs, the verdict comment names the final head, and the merge is pinned to that head |
| A PR in AlphaOS | The skill runs `pnpm review tier` and posts an `AOS-REVIEW:` line, and writes no verdict format of its own |
| A PR in hausback-core | The skill posts no verdict and stops at merge-ready |
| A branch whose worktree `/finish` removed | The worktree comes back from the kept branch before round 1 |
| `precheck` on a PR in a repo with no gate guide | It returns `ok_to_proceed` with no error |
| Round 2 finds a bug in a fix | The bug is fixed and the verdict is NOT YET, with no third review started |
| A reviewer suggests a quick style fix | It is labelled Note and no code changes |

The build follows pstack's skill-authoring playbook, and each case above is run once before the skill is linked by `install.sh`.

## Open decisions

1. In a solo repo with no gate guide, does `land-pr` merge the PR itself after a PASS, or stop at merge-ready?
   The solo-repo rule in the guardrails already lets an agent merge its own PR after an independent review and green tests.
   `merge-agent` takes the stricter line and merges nothing in a repo with no guide.
2. Does `/finish` keep removing the worktree when the PR opens?
   Keeping it changes no existing skill or rule, and `land-pr` pays the cost of a rebuild, which means reinstalling dependencies in a large repo.
   Moving the cleanup to after the verdict saves that rebuild.
   It also leaves a worktree on disk for every PR that `land-pr` never runs on, such as a PR `ship` opened or a lead's worker PR.

## Deviations

- The approved default moved worktree cleanup to after the gate and edited two rule files. Review of the draft found that this strands a worktree for every PR `land-pr` never runs on, so the spec now recommends no change there and asks it as open decision 2.
- The spec lives in claude-kit beside the `merge-agent` spec, not in dotfiles `docs/` as first proposed. The skill ships from claude-kit, and the dotfiles checkout was behind its remote with an unrelated uncommitted file.
- The hausback owner shared a newer developer page on 2026-11-23 that this session could not open. The hausback column above comes from `docs/runbooks/review.md` on `origin/dev`, last verified 2026-11-02.

## Not yet specified

- What the author's session does in hausback-core while it waits for a signer, once the 2026-11-23 page is read against the runbook.
- How a bot finding that arrives after round 2 is handled without a third review.
- Whether a repo with `review_rules_hint` true and no gate guide should stop and ask where its gate lives, as `merge-agent` does.

## Out of scope

- Changing any repo's gate, tier rule or verdict format.
- A tier rule for repos that have none. The built-in loop runs one review for every PR.
- Chaining `land-pr` onto `ship`, `file-pr` or any other workflow.
- Releases, deploys and stacked PRs.
- Working a queue of PRs. That is `merge-agent` and `lead`.
- Other people's PRs by default.
