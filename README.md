# claude-kit

Kan's personal skills for Claude Code and Codex. These are the workflow verbs
that follow me between machines and repositories, so they live here instead of
in a dotfiles repo: `ship`, `park`, `pickup`, `finish`, `worktrees`,
`review-plan`, and friends.

Several of them extend [superpowers](https://github.com/obra/superpowers)
rather than replace it. `ship` drives the superpowers chain end to end;
`park` and `pickup` add the handoff that chain needs when a session runs out
of context halfway through. If you use superpowers, these sit on top of it. If
you don't, most of them still stand alone.

## What's in it

| Skill | What it does |
|---|---|
| `ship` | Runs an approved spec end to end: `superpowers:writing-plans` → `review-plan` → `superpowers:subagent-driven-development` → review. Stops at the PR boundary. |
| `park` | Freezes an in-flight chain to disk before you clear context. Not the built-in `/rewind`. |
| `pickup` | Resumes from that state, including work parked in a git worktree. |
| `review-plan` | Adversarial rubric pass over a plan or spec. Finds the gaps before execution does. |
| `finish` | Runs the repository's declared close-out ritual: commit, push, and whatever its `Close-out:` line specifies. |
| `whats-next` | Read-only position check against the repository's tracker. Answers where you are without starting work. |
| `worktrees` | Where worktrees live, how they get created, and when they get cleaned up. |
| `rendering-specs-as-html` | Keeps every spec and plan as a synced `.md` + `.html` pair. |
| `no-ai-slop` | Edits or audits a draft for AI writing patterns without flattening the voice. |
| `define-goal` | Defines measurable completion goals for Claude Code and Codex. |
| `pick-driver` | Decides who drives a task: interactive turns, a `/goal`, or a `/loop` prompt file. Drafts the goal line or loop file when one wins. |
| `semantic-computer-use` | Drives native macOS apps through the accessibility tree instead of pixel clicking. |
| `quiz` | Comprehension check, only when you ask for one. |

Skill names are deliberately unprefixed, so a skill can refer to another by
bare name and behave identically on every machine.

## Install

```bash
git clone https://github.com/kankunnawat/claude-kit ~/.claude-kit
~/.claude-kit/install.sh
```

Each skill is symlinked as a whole directory into `~/.claude/skills`,
`~/.codex/skills`, and `~/.agents/skills`. Whichever directory does not exist
is skipped, so a machine with only one agent needs no flags. Rerun the script
after a `git pull`; it is idempotent.

`CLAUDE_CONFIG_DIR` is honoured if you run Claude Code under a non-default
config directory. Pass `--copy` instead of symlinking, for containers where
the clone path is temporary.

## Cloud sessions

Two setup scripts, depending on how much you want.

**Skills only.** Paste this into the environment's setup script field, for
Claude Code on the web or for Codex cloud:

```bash
#!/bin/bash
mkdir -p ~/.claude/skills
git clone --depth 1 https://github.com/kankunnawat/claude-kit ~/.claude-kit \
  && ~/.claude-kit/install.sh
true
```

For a Codex cloud environment, substitute `~/.codex/skills` in the `mkdir`.

**Skills, superpowers, rules, and CLI tools.** `cloud-setup.sh` is the same
script for both clouds. It creates the agent homes, installs the skills,
installs [superpowers](https://github.com/obra/superpowers), writes `CLOUD.md`
as `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md` if those do not already
exist, and installs `rg`, `fd`, and `ast-grep`:

```bash
#!/bin/bash
git clone --depth 1 https://github.com/kankunnawat/claude-kit ~/.claude-kit \
  && ~/.claude-kit/cloud-setup.sh
true
```

Every step is non-fatal and the script always exits 0. A setup script that
exits non-zero fails the session, so an unguarded failure would stop sessions
from starting at all. Read its log lines in the provisioning output to see
which steps landed.

Superpowers goes in two ways. Claude gets the plugin, so its skills keep the
`superpowers:` prefix that a local install and the `ship` skill both expect.
Codex gets a plain clone of `obra/superpowers` symlinked into
`~/.codex/skills`, because `codex plugin add` needs a marketplace snapshot that
a fresh container does not have, and the CLI may not be on `PATH` at all when
the setup script runs. Both agents get every skill. The clone is also Claude's
fallback if the plugin install fails.

`CLOUD.md` is a portable subset of a local ruleset: response shape, workflow,
philosophy, code quality, testing, security, commits. It carries nothing
machine-specific, and a project's own CLAUDE.md or AGENTS.md overrides it.

Configure this once per environment, not once per repository.

Verified in the tested 2026-09-01 Claude Code cloud and Codex cloud profiles:
skills, rules, CLI tools, and superpowers installed successfully. Those profiles
allowed anonymous public-repository reads during setup. Verify the active
environment's network and checkout order before relying on that behavior.

If the active Codex profile exposes **Post setup caching**, use **Reset cache**
after changing the setup script. Verify the control exists before relying on it.

The tested Claude Code cloud profile cached the filesystem after its first run.
It reran setup when the script or network configuration changed, or after its
snapshot expired. Verify current cache behavior before estimating propagation.

The `mkdir` in the skills-only script is load-bearing. A setup script runs as
root before the agent launches, so the skills directory does not exist yet,
and `install.sh` skips a target directory that is missing. Without it the
script installs nothing and still reports success. `cloud-setup.sh` does its
own `mkdir`, which is why its setup script is one line shorter.

## Contributing

Skills are plain Markdown: `skills/<name>/SKILL.md` plus any supporting files.
Open a pull request. Run `./test-install.sh` before pushing if you touched
`install.sh`.
