#!/usr/bin/env bash
# Install claude-kit skills into the Claude and Codex skill directories.
#
# Each skill is linked as a WHOLE DIRECTORY, never as a symlinked SKILL.md
# inside a real directory: Codex's scanner silently skips that second form.
#
# Idempotent. Replaces any symlink it finds (including one pointing at an old
# source such as ~/.dotfiles) so migration is automatic; never touches a real
# directory, so a hand-authored local override wins.
set -eu

KIT="$(cd "$(dirname "$0")" && pwd)"
MODE=link
[ "${1:-}" = "--copy" ] && MODE=copy

# Links are absolute: the source repo is outside ~/.claude, so a relative link
# would be fragile.
#
# ~/.agents/skills is the cross-agent convention dir that Codex setup also
# publishes to. It is a third target, not an alias for ~/.codex/skills.
targets="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills $HOME/.codex/skills $HOME/.agents/skills"
installed=0 skipped=0

for target in $targets; do
  # A host with only one agent installed is normal — skip, don't create.
  [ -d "$target" ] || { echo "skip: $target does not exist"; continue; }

  for src in "$KIT"/skills/*/; do
    [ -d "$src" ] || continue
    name="$(basename "$src")"
    dest="$target/$name"

    # -L first: a dangling symlink fails -e, and must still be replaced.
    if [ ! -L "$dest" ] && [ -e "$dest" ]; then
      echo "skip: $dest is a real directory, leaving it alone"
      skipped=$((skipped + 1))
      continue
    fi

    rm -f "$dest"
    if [ "$MODE" = copy ]; then
      cp -R "${src%/}" "$dest"
    else
      ln -s "${src%/}" "$dest"
    fi
    installed=$((installed + 1))
  done
done

echo "claude-kit: $installed installed, $skipped skipped"
