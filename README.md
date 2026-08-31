# claude-kit

Portable Claude Code and Codex skills. Workflow verbs that are not tied to any
one project or machine: `ship`, `park`, `pickup`, `finish`, `worktrees`,
`review-plan`, `no-ai-slop`, and friends.

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

Add one line to your cloud environment's setup script, for Claude Code on the
web or for Codex cloud:

```bash
git clone --depth 1 https://github.com/kankunnawat/claude-kit ~/.claude-kit && ~/.claude-kit/install.sh
```

This is configured once per environment, not once per repository.

## Contributing

Skills are plain Markdown: `skills/<name>/SKILL.md` plus any supporting files.
Open a pull request. Run `./test-install.sh` before pushing if you touched
`install.sh`.

Skill names are deliberately unprefixed, so a skill can refer to another by
bare name and behave identically on every machine.
