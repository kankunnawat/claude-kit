#!/usr/bin/env bash
# Runs the step 7 cleanup block of SKILL.md against a throwaway repo.
# Each case builds a bare origin, a main checkout and a linked worktree on a
# pushed branch, then runs the block from inside the worktree with a mock gh.
# The block is read from SKILL.md, never copied here.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
command -v jq >/dev/null || { echo "jq is required (the mock gh applies -q with it)"; exit 2; }
command -v git >/dev/null || { echo "git is required"; exit 2; }

T="$(mktemp -d)" || exit 2
# An empty T would make cd "" succeed and the EXIT trap delete the directory the test started in.
[ -n "$T" ] && [ -d "$T" ] || { echo "mktemp -d gave no usable directory"; exit 2; }
T="$(cd "$T" && pwd -P)" || exit 2
trap 'find "$T" -depth -delete 2>/dev/null' EXIT

BLOCK="$T/block.sh"
awk '/^7\. \*\*Clean up the ticket worktree/{s=1}
     s && /^ *```bash/{f=1; next}
     f && /^ *```/{exit}
     f{sub(/^   /, ""); print}' "$HERE/SKILL.md" > "$BLOCK"
grep -q 'git worktree remove' "$BLOCK" || { echo "could not extract the step 7 bash block from SKILL.md"; exit 2; }

# Mock tools. gh answers `pr view <branch> --json ... [-q expr]` from MOCK_PR_*.
# lsof prints nothing: a real system-wide scan is slow and not hermetic.
mkdir -p "$T/bin" "$T/home"
ln -s "$(command -v jq)" "$T/bin/jq"
ln -s "$(command -v git)" "$T/bin/git"
cat > "$T/bin/gh" <<'MOCK'
#!/usr/bin/env bash
[ "${1:-} ${2:-}" = "pr view" ] || { echo "mock gh: unsupported: $*" >&2; exit 1; }
[ "${MOCK_PR_STATE:-none}" != none ] || { echo "no pull requests found for branch \"$3\"" >&2; exit 1; }
q=.
while [ $# -gt 0 ]; do case "$1" in (-q|--jq) q=$2; shift;; esac; shift; done
json=$(jq -n --arg u "$MOCK_PR_URL" --arg s "$MOCK_PR_STATE" --arg h "$MOCK_PR_HEAD" '{url:$u, state:$s, headRefOid:$h}')
if [ "$q" = . ]; then printf '%s\n' "$json"; else printf '%s\n' "$json" | jq -r "$q"; fi
MOCK
printf '#!/bin/sh\nexit 0\n' > "$T/bin/lsof"
chmod +x "$T/bin/gh" "$T/bin/lsof"

# Clean environment: isolated HOME, no user or system git config.
run() {
  env -i HOME="$T/home" PATH="$T/bin:/usr/bin:/bin:/usr/sbin:/sbin" TMPDIR="$T" \
    GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 \
    GIT_AUTHOR_NAME=test GIT_AUTHOR_EMAIL=test@example.invalid \
    GIT_COMMITTER_NAME=test GIT_COMMITTER_EMAIL=test@example.invalid \
    "$@"
}

fails=0
ok() { echo "  ok   $1"; }
bad() { echo "  FAIL $1"; printf '%s\n' "$OUT" | sed 's/^/       | /'; fails=$((fails+1)); }

# fixture <case>: sets C (case dir), MAIN, WT, BR, HEAD_SHA.
fixture() {
  C="$T/$1"; BR="ticket-$1"; MAIN="$C/main"; WT="$C/wt"
  mkdir -p "$C"
  run git init -q --bare -b main "$C/origin.git"
  run git init -q -b main "$MAIN"
  run git -C "$MAIN" remote add origin "$C/origin.git"
  echo base > "$MAIN/README"
  run git -C "$MAIN" add README
  run git -C "$MAIN" commit -q -m base
  run git -C "$MAIN" push -q origin main
  run git -C "$MAIN" worktree add -q -b "$BR" "$WT"
  echo change > "$WT/change.txt"
  run git -C "$WT" add change.txt
  run git -C "$WT" commit -q -m change
  run git -C "$WT" push -q origin "$BR"
  HEAD_SHA=$(run git -C "$WT" rev-parse HEAD)
}

# cleanup <state> <pr head> [VAR=value ...]: runs the block inside the worktree.
cleanup() {
  local state=$1 head=$2; shift 2
  OUT=$(cd "$WT" && run MOCK_PR_STATE="$state" MOCK_PR_HEAD="$head" \
    MOCK_PR_URL="https://example.invalid/pr/1" "$@" bash "$BLOCK" 2>&1)
}

branch_kept() { run git -C "$MAIN" rev-parse -q --verify "refs/heads/$BR" >/dev/null; }

echo "case a: PR open"
fixture a
cleanup OPEN "$HEAD_SHA"
if [ -d "$WT" ]; then ok "worktree stays"; else bad "worktree stays"; fi
case "$OUT" in (*"PR is open"*) ok "output says the PR is open";; (*) bad "output says the PR is open";; esac

echo "case b: PR open, land-pr close-out"
fixture b
cleanup OPEN "$HEAD_SHA" LAND_PR_CLOSE_OUT=1
if [ ! -d "$WT" ]; then ok "worktree removed"; else bad "worktree removed"; fi
if branch_kept; then ok "branch kept"; else bad "branch kept"; fi

echo "case c: PR merged, origin branch deleted, PR head is HEAD"
fixture c
run git -C "$MAIN" push -q origin --delete "$BR"
cleanup MERGED "$HEAD_SHA"
if [ ! -d "$WT" ]; then ok "worktree removed"; else bad "worktree removed"; fi
if branch_kept; then ok "branch kept"; else bad "branch kept"; fi

echo "case d: PR closed"
fixture d
cleanup CLOSED "$HEAD_SHA"
if [ ! -d "$WT" ]; then ok "worktree removed"; else bad "worktree removed"; fi
if branch_kept; then ok "branch kept"; else bad "branch kept"; fi

echo "case e: PR merged, PR head is not HEAD"
fixture e
run git -C "$MAIN" push -q origin --delete "$BR"
cleanup MERGED 0000000000000000000000000000000000000000
if [ -d "$WT" ]; then ok "worktree stays"; else bad "worktree stays"; fi
case "$OUT" in (*"PR ended at"*) ok "output says the PR ended at another commit";; (*) bad "output says the PR ended at another commit";; esac

echo "case f: PR open, land-pr close-out, a commit not pushed"
fixture f
echo more > "$WT/more.txt"
run git -C "$WT" add more.txt
run git -C "$WT" commit -q -m more
cleanup OPEN "$HEAD_SHA" LAND_PR_CLOSE_OUT=1
if [ -d "$WT" ]; then ok "worktree stays"; else bad "worktree stays"; fi
case "$OUT" in (*"push first"*) ok "output says push first";; (*) bad "output says push first";; esac

echo "case g: no PR"
fixture g
cleanup none ""
if [ -d "$WT" ]; then ok "worktree stays"; else bad "worktree stays"; fi
case "$OUT" in (*"no PR for"*) ok "output says there is no PR";; (*) bad "output says there is no PR";; esac

echo "case h: no PR, land-pr close-out"
fixture h
cleanup none "" LAND_PR_CLOSE_OUT=1
if [ -d "$WT" ]; then ok "worktree stays"; else bad "worktree stays"; fi
case "$OUT" in (*"no PR for"*) ok "output says there is no PR";; (*) bad "output says there is no PR";; esac

echo "case i: PR merged, PR head is not HEAD, land-pr close-out"
fixture i
run git -C "$MAIN" push -q origin --delete "$BR"
cleanup MERGED 0000000000000000000000000000000000000000 LAND_PR_CLOSE_OUT=1
if [ -d "$WT" ]; then ok "worktree stays"; else bad "worktree stays"; fi
case "$OUT" in (*"PR ended at"*) ok "output says the PR ended at another commit";; (*) bad "output says the PR ended at another commit";; esac

echo
[ "$fails" -eq 0 ] && echo "all checks passed" || echo "$fails check(s) failed"
exit "$fails"
