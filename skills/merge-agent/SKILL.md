---
name: merge-agent
description: >-
  Use when the user types /merge-agent, says "be the merge agent" or "review and merge my open PRs", or asks "does this repo have a PR gate". The session becomes this repo's merge agent: it finds the repo's own PR gate guide on the remote default branch and follows it to review, verify and merge the user's open PRs one at a time. With no guide, it drafts one as a PR and stops. Not for deploys, releases, or other people's PRs by default.
---

# merge-agent

The repo declares its PR gate. This skill finds that gate and follows it.
It holds no repo names, tier names, verdict formats or merge commands of its own.
A repo with no gate gets a drafted guide, and nothing merges there until the user merges that guide.

Read [the owner contract](../unblock-decisions/references/owner-contract.md) first.
It holds the rules this skill shares with the others: authority and consent, who owns review, merging and tracker writes, the report line, and how a lesson becomes a rule.
This file keeps only the merge agent's own job.

## Usage

```text
/merge-agent                 # doctor, then work the queue of your open PRs
/merge-agent 123             # one PR only
/merge-agent draft-gate      # write the repo's PR gate guide as a PR, then stop
```

## The script

`merge-agent.py` sits next to this file. Call it by that path with `python3`, from the target repo's checkout or with `--repo owner/name`.
Never `cd` into the skill directory first: without `--repo`, the script reads the repo of the working directory.
It prints JSON. On failure it prints `error` and `next`; do what `next` says.

- `doctor [--repo owner/name]`: the default branch, the gate guide (file, heading, line, files it points to), a `review_rules_hint`, the verification skill, the guardrails lines that name this repo, and whether the merge guard exists.
- `queue [--repo]`: your open PRs, oldest first, with full head SHA, base, draft state, labels, checks on the head, `held_files` and `hold_reasons`.
- `precheck <pr> [--repo] [--reviewed-head <full SHA>] [--approved-author LOGIN]`: state, author, head, base, checks on that exact head, held files, labels, and `ok_to_proceed` with its `reasons` and `warnings`.

The script only reads. It never merges, posts, labels or pushes.
You type every write yourself, so the merge guard judges it.

## How it runs

1. **Scope.**
   The user's own open PRs in this repo.
   A PR by someone else needs the user's yes for that PR.
2. **Doctor.**
   Run `doctor`. It reads the repo and its instruction files from the remote default branch, never from the local checkout.
   Report four lines, then act on them:

   ```text
   Gate guide: <file> "<heading>" on origin/<branch>
   Verification skill: <path>, or none found (proof is limited to tests and CI)
   Merging here: allowed by your guardrails, <how the guide merges>, or not named: stop at merge-ready
   Queue: <n> of your PRs open. <k> ready to review, <m> held (<reason>)
   ```

   - `guardrails_name_repo` false or `"unknown"`, or `guard_present` false: the agent does not merge here. Every PR stops at merge-ready.
   - `guardrails_name_repo` true is a hint. Open the guardrails file at each line number in `guardrails_lines` and read the whole rule around it, with every limit it lists.
     The rule says whether an agent may merge here, into which branch, how, and for which PRs. A rule that refuses the repo means stop at merge-ready.
   - The guide or the guardrails say this repo lands through its own lane tool or skill: hand over to that skill now and stop. Run none of the steps below, and name no command.
   - `review_rules_hint` true with no gate guide: show what you found and ask where the gate lives. Do not draft over it.
   - No verification skill: warn once, and name in each report what was not proven by running the change.
     Offer the pstack create-verification-skill skill (`~/.agents/pstack/skills/create-verification-skill/SKILL.md`). Do not create it unasked.
3. **No guide: draft, then stop.**
   Read `~/.agents/pstack/skills/how/SKILL.md` and use it to learn how the repo ships today: CI, branch rules, risky paths, tracker.
   Fill `references/gate-guide-template.md` from those facts. Every `[bracket]` gets a real value or is cut.
   Put the guide where the repo's agents already read rules, as a section of `CLAUDE.md` or `AGENTS.md`.
   Open it as a PR on a feature branch. That PR waits for the user.
   Merge nothing in this repo until the user has merged the guide.
   `draft-gate` in a repo that already has a guide reports that guide and stops.
4. **Guide found: one PR at a time.**
   Read the whole guide from the remote branch, plus every file it points to.
   Read `~/.agents/pstack/skills/poteto-mode/playbooks/shipping.md` for one verdict per patch and landing a stack from the bottom.
   Read this kit's `finish` skill (`../finish/SKILL.md`) for "green is not safe".
   Where either one differs from the user's guardrails or the repo's guide, the guardrails and the guide win, on every point.
   Three points always hold: the merge is pinned and never automatic, a branch is never force-pushed, and a verdict never carries to a new head, even when `git patch-id` matches.
   Run `queue`, then for each PR, oldest first and a stack from the bottom up.
   With a PR number (`/merge-agent 123`), skip `queue` and run these steps on that PR only:
   1. **Pre-check.** Run `precheck <pr>`. Read the reasons in this order.
      Another author: stop and ask the user about that PR by number, before any review or verification. After their yes, pass `--approved-author <that login>` on every `precheck` of that PR, and on no other PR.
      Held files or a hold label: review and verify it, then stop at merge-ready (step 5).
      A base that is not the branch the guide merges into: report it and go on to the next PR.
      Any other reason: report it and go on to the next PR. A merged PR or a moved head is reported, never acted on.
      A file the guide points to that `held_files` missed still holds the PR.
   2. **Tier.** Use the repo's tool or rule. Recompute it from the diff. You may raise the author's tier, never lower it.
   3. **Review.** Look for the verdict the PR's opener recorded, in the repo's own format.
      Accept it only when all of these hold: it is a pass by the guide's own rule, it names this exact full head SHA, it names its reviewer, and that reviewer did not write the change.
      Then do not review again.
      A recorded verdict at this head that is not a pass stops the PR. Report it as held; do not review around it.
      No verdict, a verdict at another commit, a verdict that names no reviewer, a reviewer who wrote the change, or any doubt about who recorded it: get a fresh review.
      A fresh review that is not a pass by the guide's own rule also stops the PR. Record it, report the PR as held, and go on to the next one.
      A fresh review is a session that did not write the change, given the diff range and the head SHA, not the author's conclusions.
      Sign only what the guide lets the merge agent sign.
   4. **Verify.** Run the checks the guide names for that tier. Run heavy checks through the machine's shared lane tool when it has one.
      For a behavior change, run it as a user with the repo's verification skill.
      Proof carried over from an older commit is reported as carried over, with that commit.
   5. **Verdict.** When you reviewed again, record it in the repo's own format, with the repo's own tool when it has one.
   6. **Merge.** Run `precheck <pr> --reviewed-head <full SHA>` again, with the SHA the accepted verdict names.
      There must be a passing verdict at that SHA, accepted or fresh. `ok_to_proceed` must be true, the base must be the branch the guide merges into, and the tier's checks must pass on that head.
      A `warnings` entry about no checks on the head stops the merge unless the guide needs no checks for this tier.
      Then type the guide's pinned merge command yourself, with the full head SHA. Never auto-merge, never use admin rights.
      Read the PR back and confirm it merged into the base the guide names.
   7. **After merge.** Do only what the guide lists, except tracker writes.
      Write nothing to the tracker. Report the landing with the tracker move it calls for, so the coordinator makes it.
5. **Stop at merge-ready** when the guardrails do not name the repo, when there is no guard, when the guard refuses, or when the PR holds files or labels.
   The report gives the PR link, the head SHA and the guide's exact command for the user to run.
   A refusal from the guard is never worked around.
6. **Maintain.** A landing that teaches a rule the guide lacks becomes a proposal, per the owner contract. Never keep the rule inside this skill.

## Authority rules

- This skill grants nothing. The user's guardrails file and the merge guard decide where an agent may merge.
- `queue` never lists other authors.
- A PR that changes a gate guide, `CLAUDE.md`, `AGENTS.md`, `.claude/`, `.agents/` or `.github/` waits for the user. This includes the guide this skill drafts.
- Never add or remove a flag or hold label unless the repo's guide gives the merge agent that step.
- A new commit after the review needs a new review of the new range.
- The script never writes. A merge run inside a script would pass the guard unseen.

## Report

One line per PR as each one ends, in the owner contract's report line: landed, merge-ready or held, the commit, what was not verified, and what waits on whom.
A landing names the tracker move it leaves for the coordinator.
End with what is still open: held PRs, PRs waiting for the user's command, and any guide edit proposed.
