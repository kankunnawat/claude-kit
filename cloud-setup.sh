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

if command -v claude >/dev/null 2>&1; then
  claude plugin marketplace add anthropics/claude-plugins-official >/dev/null 2>&1
  if claude plugin install -y superpowers@claude-plugins-official >/dev/null 2>&1; then
    log "superpowers installed for claude"
  else
    log "superpowers FAILED for claude"
  fi
else
  log "claude not on PATH, skipping its plugin install"
fi

if command -v codex >/dev/null 2>&1; then
  if codex plugin add superpowers@claude-plugins-official >/dev/null 2>&1; then
    log "superpowers installed for codex"
  else
    log "superpowers FAILED for codex"
  fi
else
  log "codex not on PATH, skipping its plugin install"
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
