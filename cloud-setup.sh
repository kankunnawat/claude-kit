#!/bin/sh
# Provision a Claude Code or Codex cloud container toward a local setup:
# skills, the superpowers plugin, global rules, and the CLI tools the rules
# assume.
#
# Runs from a cloud environment's setup script — as root, with internet, before
# the agent launches. Every step is non-fatal and the script always exits 0,
# because a setup script that fails takes the whole session with it.

set -u

kit="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
log() { printf 'cloud-setup: %s\n' "$*"; }

# Create both agent homes and let install.sh populate whichever one the
# container actually runs. The directories do not exist yet at setup time.
mkdir -p "$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.agents/skills"

if "$kit/install.sh" >/dev/null 2>&1; then
  log "skills installed"
else
  log "skills FAILED"
fi

for f in "$HOME/.claude/CLAUDE.md" "$HOME/.codex/AGENTS.md"; do
  if [ -e "$f" ]; then
    log "rules: $f already exists, left alone"
  elif cp "$kit/CLOUD.md" "$f" 2>/dev/null; then
    log "rules: wrote $f"
  else
    log "rules: could not write $f"
  fi
done

# Superpowers. Claude keeps the plugin path so skills stay `superpowers:`-
# prefixed, matching a local install and the references inside `ship`. Codex
# uses a plain clone: `codex plugin add` needs a marketplace snapshot a fresh
# container does not have, and the CLI may not even be on PATH here, since the
# setup script runs as root before the agent launches.
sp_installed=0
if command -v claude >/dev/null 2>&1; then
  claude plugin marketplace add anthropics/claude-plugins-official >/dev/null 2>&1
  if claude plugin install -y superpowers@claude-plugins-official >/dev/null 2>&1; then
    log "superpowers installed for claude, prefixed"
    sp_installed=1
  else
    log "superpowers plugin install FAILED for claude, falling back to a clone"
  fi
else
  log "claude not on PATH, falling back to a clone"
fi

if [ ! -d "$HOME/.superpowers" ]; then
  git clone --depth 1 https://github.com/obra/superpowers "$HOME/.superpowers" >/dev/null 2>&1 \
    || log "superpowers clone FAILED"
fi

if [ -d "$HOME/.superpowers/skills" ]; then
  # Codex gets every skill. Its ruleset expects delegation — the execution
  # chain names subagent-driven-development, and the fan-out rule caps nesting
  # and rate rather than banning it. Claude is linked only when the plugin path
  # failed.
  for skill in "$HOME/.superpowers"/skills/*/; do
    name=$(basename "$skill")
    ln -sfn "${skill%/}" "$HOME/.codex/skills/$name"
    [ "$sp_installed" = 0 ] && ln -sfn "${skill%/}" "$HOME/.claude/skills/$name"
  done
  log "superpowers linked into codex skills$([ "$sp_installed" = 0 ] && echo ' and claude skills')"
fi

# ripgrep and fd. `trash` is macOS-only and has no cloud equivalent.
missing=""
command -v rg >/dev/null 2>&1 || missing="$missing ripgrep"
if ! command -v fd >/dev/null 2>&1 && ! command -v fdfind >/dev/null 2>&1; then
  missing="$missing fd-find"
fi
if [ -n "$missing" ]; then
  if command -v apt-get >/dev/null 2>&1; then
    apt-get update -qq >/dev/null 2>&1
    # shellcheck disable=SC2086
    if apt-get install -y -qq $missing >/dev/null 2>&1; then
      log "installed:$missing"
    else
      log "apt-get FAILED for:$missing"
    fi
  else
    log "no apt-get, missing:$missing"
  fi
fi

# Debian packages fd as fdfind; the rules and skills call it fd.
if ! command -v fd >/dev/null 2>&1 && command -v fdfind >/dev/null 2>&1; then
  ln -sf "$(command -v fdfind)" /usr/local/bin/fd 2>/dev/null && log "linked fd -> fdfind"
fi

if ! command -v ast-grep >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then
  if npm install -g @ast-grep/cli >/dev/null 2>&1; then
    log "installed ast-grep"
  else
    log "ast-grep FAILED"
  fi
fi

log "done"
exit 0
