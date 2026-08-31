#!/usr/bin/env bash
# Self-check for install.sh. Runs against a throwaway HOME; touches nothing real.
set -u
# Shells may export CLAUDE_CONFIG_DIR to select an account. install.sh honours
# it, so leaving it set would make this test write into a real config directory.
unset CLAUDE_CONFIG_DIR
KIT="$(cd "$(dirname "$0")" && pwd)"
fails=0
t() { if eval "$2"; then echo "  ok   $1"; else echo "  FAIL $1"; fails=$((fails+1)); fi; }

SANDBOX="$(mktemp -d)"
trap 'rm -r "$SANDBOX" 2>/dev/null' EXIT
mkdir -p "$SANDBOX/.claude/skills" "$SANDBOX/.codex/skills" "$SANDBOX/.agents/skills"

echo "case: fresh install into both targets"
HOME="$SANDBOX" "$KIT/install.sh" >/dev/null
t "ship linked into claude"  '[ -L "$SANDBOX/.claude/skills/ship" ]'
t "ship linked into codex"   '[ -L "$SANDBOX/.codex/skills/ship" ]'
t "ship linked into agents"  '[ -L "$SANDBOX/.agents/skills/ship" ]'
t "link is a whole dir"      '[ -d "$SANDBOX/.claude/skills/ship" ] && [ -f "$SANDBOX/.claude/skills/ship/SKILL.md" ] && [ ! -L "$SANDBOX/.claude/skills/ship/SKILL.md" ]'
t "all twelve installed"     '[ "$(ls "$SANDBOX/.claude/skills" | wc -l | tr -d " ")" = "12" ]'

echo "case: rerun is idempotent"
HOME="$SANDBOX" "$KIT/install.sh" >/dev/null
t "still twelve"             '[ "$(ls "$SANDBOX/.claude/skills" | wc -l | tr -d " ")" = "12" ]'
t "exit 0 on rerun"          'HOME="$SANDBOX" "$KIT/install.sh" >/dev/null'

echo "case: a stale symlink from another source is replaced"
ln -sfn /nonexistent/old/park "$SANDBOX/.claude/skills/park"
HOME="$SANDBOX" "$KIT/install.sh" >/dev/null
t "park repointed at kit"    '[ "$(readlink "$SANDBOX/.claude/skills/park")" = "$KIT/skills/park" ]'

echo "case: a real directory is never clobbered"
rm -f "$SANDBOX/.claude/skills/quiz"
mkdir -p "$SANDBOX/.claude/skills/quiz"; echo mine > "$SANDBOX/.claude/skills/quiz/SKILL.md"
HOME="$SANDBOX" "$KIT/install.sh" >/dev/null
t "real dir left alone"      '[ "$(cat "$SANDBOX/.claude/skills/quiz/SKILL.md")" = "mine" ]'

echo "case: a missing target dir is skipped, not created"
SANDBOX2="$(mktemp -d)"; mkdir -p "$SANDBOX2/.claude/skills"
HOME="$SANDBOX2" "$KIT/install.sh" >/dev/null
t "claude-only host works"   '[ -L "$SANDBOX2/.claude/skills/ship" ]'
t "codex dir not created"    '[ ! -d "$SANDBOX2/.codex/skills" ]'
t "agents dir not created"   '[ ! -d "$SANDBOX2/.agents/skills" ]'
rm -r "$SANDBOX2"

echo "case: --copy produces real dirs, not links"
SANDBOX3="$(mktemp -d)"; mkdir -p "$SANDBOX3/.claude/skills"
HOME="$SANDBOX3" "$KIT/install.sh" --copy >/dev/null
t "copy mode is a real dir"  '[ -d "$SANDBOX3/.claude/skills/ship" ] && [ ! -L "$SANDBOX3/.claude/skills/ship" ]'
rm -r "$SANDBOX3"

echo
[ "$fails" -eq 0 ] && echo "all checks passed" || echo "$fails check(s) failed"
exit "$fails"
