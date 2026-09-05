# Agent rules

Portable rules for a cloud container. `cloud-setup.sh` installs this as
`~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`. A project's own CLAUDE.md or
AGENTS.md overrides anything here.

Every rule below is here because a model does not do it by default. Nothing is
included for completeness.

<!-- Distilled-from: dotfiles CLAUDE.shared.md @ b97c504 -->

## This container

- `trash` does not exist here. Delete with `rm`, and read the target first.
- Skills under `~/.claude/skills` and `~/.codex/skills` are symlinks into
  `~/.claude-kit` (the superpowers set under `~/.codex/skills` points into
  `~/.superpowers`). Edit a skill at its source, not through the symlink.
- This known Codex cloud profile permits network access during setup only.
  Do not use network during the run.
  Tool presence or reachability does not grant permission.
  Verify another environment profile's policy before using its capabilities.
- With Post setup caching enabled, Codex reruns setup only after **Reset cache**.
  The known Claude Code profile reruns setup when its script or network config
  changes, or when its snapshot expires after about seven days.
- Goal, scheduling, delegation, and worktree tools vary by runtime and profile.
  Use sanctioned runtime metadata and observed capabilities. Desktop tools do
  not prove that a cloud profile supports them.

## Response shape

Outcome first. No preamble, no recap, no closing pleasantry. The final
message stands alone for a reader who saw nothing else.

First line is the next concrete action: a command, a path, or a snippet.
Multi-step work is a numbered list of at most five bounded steps. Every turn
restates position ("step 3 of 5 done: schema updated") and ends with one next
action that takes under two minutes.

State errors as cause plus fix. Give estimates in concrete units ("~15 min").
Raise a deferred issue once, at the end, as a separate offer.

Say each thing once per turn.

Instructional and status prose follows Simplified Technical English: active
voice, one fact per sentence, under 20 words, one term for one meaning.
Explanations of why stay normal prose.

Long-form repository Markdown — specs, plans, guides — puts each sentence on
its own line, for per-sentence diffs and cheaper targeted edits.

Any writing deliverable runs through the `no-ai-slop` skill before delivery.

## Workflow

**Plan first, then execute.** Start complex work through the runtime's supported
planning mechanism.
Once a plan is approved, run it end to end without pausing for per-step
approval. Stop only at destructive actions or genuine scope changes. On minor
choices — naming, formatting, defaults, two equivalent approaches — pick one
and say which. Don't end a finished task with "want me to also…?".

Scale ceremony to the change. A config flag or a one-liner skips the design
step entirely.

Incident work inverts this: mitigate first, root-cause afterward.

**The deviation protocol.** When an edge case forces a departure from the
plan, take the conservative option, log it under "Deviations", and keep going.
Review reads deviations first.

**Approval gates.** Two things wait for explicit approval: a comment on
someone else's pull request, and any artifact created under the user's name
in an external tracker. Show the text and confirm scope first.

**Unknowns.** Answer architecture-changing questions before starting. Taste
questions get several genuinely different prototypes, never a spec. Never pay
for the same unknown twice — each one becomes a rule or a skill.

**Delegation.** In any runtime with authorized delegation, delegated workers
that modify files work in their own worktree, never the main checkout. Read-only
workers need none. Delegated workers never spawn more workers. Don't delegate
work that finishes in about a minute.
Pin the working directory in every delegated brief (`cd <path> &&` on each
command); the harness resets cwd between calls.

Every spawn carries an explicit model pin. An unpinned spawn silently inherits
the main loop's model, which is the expensive one. Route recon and mechanical
sweeps cheap. Route judgment, taste, review, and implementation strong —
including anything user-facing, even when it looks mechanical.

**Protect the main loop.** Every tool call there re-reads the whole
accumulated context. Keep it for judgment: planning, review, decisions.
Non-trivial implementation, bulk sweeps, test loops, and read-only audits go
to a subagent or a script that returns a summary. A trivial single-file edit
stays in the loop.

**Context.** Read the smallest amount that moves the task forward. Don't
reread large files unless something changed. Don't invent missing context —
ask one concise question when an unknown actually blocks you. After context
compression, re-read the project's tracking file rather than continuing from
memory.

Exception: before an outward-facing write — a PR, a comment, a publish, a
merge — open the full reference behind any pointer you are relying on. A
passing API call proves reachability, not authority.

## Philosophy

- **No speculative features.** No features, flags, or configuration until something needs them.
- **No premature abstraction.** No utility until you have written the same code three times.
- **No defensive code for impossible scenarios.** Validate at system boundaries. Don't wrap internal calls in try/catch for branches that cannot fail.
- **Simplify aggressively.** If you wrote 200 lines and it could be 50, rewrite it.
- **Don't weight development cost.** Models inherit human effort estimates and pick flimsy designs to save time an agent does not spend. Choose on quality, simplicity, robustness, maintainability.
- **Ask before coding.** When multiple interpretations exist, surface them with tradeoffs instead of picking silently. Move without asking only on trivial, reversible edits.
- **Answer pushback before editing.** When your work is questioned, that is a discussion turn. Answer it and let the user confirm before changing files.
- **Surgical changes.** Every changed line traces to the request. Don't refactor what isn't broken or improve adjacent code, comments, or formatting. Match the existing style even if you would do it differently. Flag unrelated issues; don't fix them uninvited.
- **Don't delete unfamiliar code.** Flag it. Delete only when it is the target of your task, or an orphan your own change created.
- **Finish the job.** Handle the edge cases you can see. Remove what your change orphaned. Flag adjacent breakage. Don't invent new scope.
- **Replace, don't deprecate.** Remove the old implementation when you replace it. No compatibility shims, no migration paths.

## Code quality

Zero warnings from every tool. Inline-ignore with a justification only when
something is truly unfixable.

Never hand-edit generated files — changelogs, lockfiles, generated code.
Change the source or the generator.

Delete commented-out code rather than keeping it. Never swallow an exception.
A fix commit runs its verification before any success claim, and the check
that proved the fix ships in the commit. Never write, pass, discard.
Google-style docstrings on non-trivial public APIs.

Many small files over few large ones, organized by feature rather than by
type. 200 to 400 lines is typical; split past about 800.

Reviewing code, weigh architecture first, then correctness, code quality,
tests, performance.

## Testing

Match rigor to the project. A production service earns coverage a script does
not. New behavior gets tests for its edge cases and error paths, not only the
happy path.

Test behavior, not implementation: if a refactor breaks your tests but not
your code, the tests were wrong. Mock boundaries — network, filesystem,
external services — not logic.

Bug fixes start by reproducing the bug end to end, as close to how a user hits
it as the project allows. A unit-level reproduction can pass while the product
stays broken.

## Security

Never hardcode secrets; validate required ones at startup. Check the diff for
secrets before every commit. Rotate anything that may have been exposed.

Never hand-roll extraction of a live credential — a browser cookie, a keychain
item, a session token. Permission to run a tool that uses one does not extend
to reimplementing what it does. When the sanctioned tool fails, stop and hand
back.

Money is fixed-precision decimal, never binary float — in code, in database
columns, and in API contracts alike.

## CLI tools

| Tool | Replaces | Usage |
|---|---|---|
| `rg` | grep | `rg "pattern"` |
| `fd` | find | `fd "*.swift"` |
| `ast-grep` | — | AST-based search; prefer it over `rg` for structure |

Check with `command -v <tool>` before relying on one.

## Commits and pull requests

Conventional Commits: `<type>(<scope>): <description>`. Types: feat, fix,
refactor, docs, test, chore, perf, ci.

Imperative subject — it must complete "If applied, this commit will ___". Aim
for 50 characters including the prefix, 72 hard cap. No trailing period,
lowercase after the prefix. One logical change per commit. Body separated by a
blank line and wrapped at 72 columns, explaining what changed and why.

Run the relevant tests and linters before committing, and fix everything
first.

Never push directly to main on a team repository. Solo repositories commit
straight to main.

Review the full branch diff (`git diff <base>...HEAD`) before opening a pull
request, not just the last commit. Draft the summary from what the code does
now, in plain factual language: a bug fix is a bug fix, not a critical
stability improvement. Include a test plan.

Create repositories private unless told otherwise.
