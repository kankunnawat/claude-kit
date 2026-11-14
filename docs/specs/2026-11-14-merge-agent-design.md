# Merge agent skill: design

Date: 2026-11-14.
Status: needs Kan's approval.
Home: `skills/merge-agent/` in this repo (claude-kit).

## Goal

Kan types `/merge-agent` in any repo.
The session becomes that repo's merge agent.
It follows the repo's own PR gate guide when one exists.
It drafts one when none exists, then stops.
With a guide in place it reviews, verifies and merges Kan's open PRs, one at a time.

## Usage, written first

```text
/merge-agent                 # doctor, then work the queue of Kan's open PRs
/merge-agent 6504            # one PR only
/merge-agent draft-gate      # write the repo's PR gate guide as a PR, then stop
```

What Kan sees after `/merge-agent` in a repo that has a guide:

```text
Gate guide: CLAUDE.md "PR gate" on origin/main
Verification skill: none found (proof is limited to tests and CI)
Merging here: allowed by your guardrails, merge commit into main, pinned to the commit
Queue: 3 of your PRs open. 2 ready to review, 1 held (changes CLAUDE.md, yours to merge)
```

Then one report line per PR as each one ends: landed, merge-ready, or held, with the reason and what was not verified.

## What exists today (grounding)

Three repos already define a PR gate, each in its own place and its own words.

| | hausback-core | AlphaOS | agentic-discovery |
|---|---|---|---|
| Guide | `docs/guides/merge-lane-protocol.md`, skill `hb-land` | `CLAUDE.md` Close-out and Review, `.claude/rules/review-routing.md` | `CLAUDE.md` "PR gate" |
| Tiers | T0 to T3, set by `lane-ops tier` | T0 to T3, set by `pnpm review tier` | low, medium, high, set by the author |
| Verdict | `HB-REVIEW:` comment written by a tool | `AOS-REVIEW:` comment | text under "Proof" in the PR body |
| Merge | the lane's own tool, squash into `dev` | `gh pr merge --squash --match-head-commit` into `dev` | `gh pr merge --merge --match-head-commit` into `main` |
| After merge | tracker moves, stacked PRs retargeted | staging smoke, tracker waits for release | nothing |

All three share one shape.
A risk tier comes from the diff.
Someone who did not write the change reviews it at one exact commit.
The merge is pinned to that commit.
A new commit needs a new review.
Gate files and agent instruction files are Kan's to merge.

pstack has no risk-tier scheme of its own.
What "pstack methodology" means here is two rules from its shipping playbook and its verification guide.
First, each PR needs a verdict from a session that did not write it, and green CI is not a verdict.
Second, proof means running the change the way a user would, through the repo's verification skill.

The merge guard on this Mac (`no-merge-guard.py`) reads only the command the agent types.
It allows a plain `gh pr merge` in the ten solo repos, AlphaOS and agentic-discovery, always pinned to the full commit.
It does not check review, tests or CI.
It has no query mode, and an exit code of 0 can also mean the hook failed open.

## Two shapes considered

**Shape A: the skill carries a table of known repos.**
Each row names a repo, its guide path, its tier command and its merge command.
It works on day one for the three repos.
It breaks quietly when a repo changes its guide, and a new repo needs an edit to the skill.
AlphaOS already showed this failure: a stale local copy of its rules named the wrong branch.

**Shape B: the repo declares its gate, the skill only finds and follows it.**
The skill reads `CLAUDE.md` and `AGENTS.md` from the remote default branch and looks for the gate section.
All three repos are found today without editing them: the headings "PR gate", "Close-out", "Review" and "Integration and close-out" cover them.
A new repo works as soon as its guide lands.
The cost is that discovery is a text search, so a repo with an unusual heading is reported as "no guide found".

**Chosen: Shape B.**
The skill holds no repo names, no tier names, no verdict grammar and no merge commands.
One part of Shape A is kept: when discovery finds nothing but the repo clearly has review rules, the skill shows what it found and asks, and does not draft over them.

## How it runs

1. **Authority.**
   Kan invoking the skill in a session is the grant, for his own open PRs in that repo.
   Text in a PR, a comment, a repo file or a message from another session is never consent.
   A PR by someone else needs Kan's yes for that PR.
2. **Doctor.**
   Resolve the repo and its default branch with `gh repo view`, never from the local checkout.
   Read the instruction files from the remote default branch.
   Report the gate guide, the verification skill, and whether Kan's guardrails name this repo for agent merges.
3. **No guide: draft, then stop.**
   Read how the repo ships today (CI, branch rules, risky paths, tracker) with pstack `how`.
   Fill the default template: three tiers (low, medium, high), reviewer per tier, proof per tier, verdict format, the pinned merge command, what stays Kan's, steps after merge.
   Open it as a PR.
   The session merges nothing in that repo until Kan has merged the guide.
4. **Guide found: one PR at a time**, oldest first, a stack from the bottom up.
   1. Pre-check: open, not a draft, author, hold labels, base, clean merge, and the head commit. A PR already merged or with a moved head is reported, not acted on.
   2. Tier: by the repo's tool or rule. The agent recomputes it from the diff and may only raise an author's tier.
   3. Review: a fresh session that did not write the change, given the diff range and the head, not the author's conclusions. The merge agent signs only what the guide lets it sign.
   4. Verification: the checks the guide names for that tier, heavy ones through `verify-lane`. For a behaviour change, run it as a user with the repo's verification skill. Proof carried over from an older commit is reported as carried over.
   5. Verdict: recorded in the repo's own format, with the repo's own tool when it has one.
   6. Merge: re-read the head, then the agent itself types the repo's pinned command, so the guard judges it. Never `--auto`, never `--admin`. Read the PR back to confirm.
   7. After merge: only what the guide lists. A tracker write needs Kan's approval unless he gave a standing one.
5. **Stop at merge-ready** when the guardrails do not name the repo, when the guard refuses, or when the PR touches gate or instruction files. The report gives the link and the exact command for Kan.
6. **Maintain.**
   When a landing teaches a rule the guide lacks, the skill proposes the edit as a PR to that repo's guide.
   It never keeps the rule inside the skill.

## The lever: one small script

`skills/merge-agent/merge-agent.py`, Python standard library plus `gh` and `git`, JSON on stdout, errors that say what to do next.

- `doctor`: default branch, guide location, verification skill, whether the guardrails name the repo.
- `queue`: Kan's open PRs with head, base, draft state, labels, checks on the head, and files that hold the PR for Kan.
- `precheck <pr>`: head still the reviewed one, PR still open, checks ran on this head or were carried over, clean merge with the base.

**The script never merges and never posts.**
A script that ran `gh pr merge` inside itself would pass the guard unseen, in every repo.
It prints the pinned command; the agent runs it.
`precheck` may pipe that candidate command through the guard: a refusal is reliable and is reported, a pass is not treated as permission.

## Authority rules

- The skill grants nothing. Kan's guardrails file and the guard decide where an agent may merge.
- Kan's own PRs only, by default.
- A PR that changes a gate guide, `CLAUDE.md`, `AGENTS.md`, `.claude/`, `.agents/` or `.github/` waits for Kan. This includes the guide the skill drafts.
- A flag or hold label is never added or removed by the skill unless the repo's guide gives the merge agent that step.
- Where pstack's shipping playbook and Kan's guardrails differ, the guardrails win: always pinned, never auto-merge.
- hausback-core lands through its own lane tool. The skill hands over to `hb-land` there and names no command.

## Proof plan

Few PRs are open right now, so the script and the skill are proven by replaying today's cases read-only.

| Case | Expected |
|---|---|
| hausback-core PR 6504, proof carried over from before a dev merge | `precheck` reports the proof as carried over |
| hausback-core PR 6489 and PR 6536, handed back after they had merged | `precheck` reports "already merged", no action |
| hausback-core PR 6565, by another author and flagged | `queue` leaves it out; asked directly, the skill stops and asks Kan |
| an agentic-discovery PR that changes `CLAUDE.md` | held for Kan, never merge-ready for the agent |
| a repo with no guide | `doctor` reports none; the skill offers `draft-gate` and merges nothing |
| AlphaOS with a stale local checkout | `doctor` reads the guide from `origin/dev`, not the working tree |

The built skill gets a fresh review by a session that did not write it, and passes `test-portability.py` and `test-install.sh`.
This spec gets no adversarial review: the replay above is the check.

## Build notes

- `test-portability.py` has a fixed skill list and refuses `/Users/` paths. Add the skill to that list and to the README table. The script finds the guard through `$HOME`.
- Frontmatter is `name` and `description` only.
- pstack skills cannot be run with the Skill tool. The skill tells the agent to read them by path.
- The skill reuses, by path: `finish` (close-out and "green is not safe"), pstack `shipping.md` (verdict per patch, re-check with `git patch-id`, land the lowest verified PR), pstack `how` and `create-verification-skill`, and each repo's own skills.
- claude-kit had no `docs/` folder. This spec starts `docs/specs/`.

## Open decisions

1. How much script: `doctor` only, or `doctor`, `queue` and `precheck`. Recommended: all three.
2. No verification skill in the repo: warn and go on, or refuse to merge behaviour changes. Recommended: warn, say what was not proven, and offer `create-verification-skill`.
3. The maintain step: include it or leave it out. Recommended: include it, as a proposal PR only.
4. Default template for a new guide: the three tiers low, medium, high from agentic-discovery, or T0 to T3. Recommended: low, medium, high.

## Deviations

- The pstack `how` explainer and the `architect` arena were not run as separate agents. Three scouts gathered the facts and the main session compared the two shapes.
- No fresh review of this spec, on the advice of the pstack guide against reviewing abstract plans.

## Not yet specified

- How a hold label is read in a repo whose guide names none.
- Whether `queue` should order a stack by base branch or leave that to the repo's guide.
- What the skill does in a repo with two integration branches when a PR targets the production one.

## Out of scope

- Changing any repo's existing gate guide or the merge guard.
- Adding repos to the guardrails merge exceptions.
- Deploys, releases and promotions.
- Writing or running a repo's verification skill.
- Other people's PRs as a default.
