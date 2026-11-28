#!/usr/bin/env bash
# Start one session for a lead: machine budget, thread, ledger row, log line.
# Usage:
#   cos-launch.sh --title T --brief FILE --bucket implement|review \
#     --task TEXT --record RECORD.md \
#     [--worktree FULL_SHA] [--repo DIR] [--provider P] [--model ID] \
#     [--dry-run] [-- CAPACITY_FLAGS...]
# The machine budget comes from capacity.sh next to this file; a start is
# refused when it prints slots=0. Flags after -- go to capacity.sh (the
# machine's numbers from the roster, --quiet-hours).
# --model only labels the ledger row unless --provider is given; then both go
# to the thread start, for an area whose roster row names a provider.
# An implement lane needs --worktree (new lane) or --repo (a fix round in the
# lane's existing worktree), so it never starts in the shared checkout.
# Exits non-zero if a check or the start fails. A start that returns no
# thread id may still have left a thread: check `t3 thread list`.
# Once the thread runs, a ledger or log failure only warns; thread= is always printed.
set -euo pipefail

title="" brief="" bucket="" task="" record="" worktree="" repo="$PWD" repo_set=0
model="claude-opus-5-5" provider="" dry=0
capacity_flags=()
while [ $# -gt 0 ]; do
  case "$1" in
    --title) title="$2"; shift 2 ;;
    --brief) brief="$2"; shift 2 ;;
    --bucket) bucket="$2"; shift 2 ;;
    --task) task="$2"; shift 2 ;;
    --record) record="$2"; shift 2 ;;
    --worktree) worktree="$2"; shift 2 ;;
    --repo) repo="$2"; repo_set=1; shift 2 ;;
    --model) model="$2"; shift 2 ;;
    --provider) provider="$2"; shift 2 ;;
    --) shift; capacity_flags=("$@"); break ;;
    --dry-run) dry=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

fail() { echo "cos-launch: $1" >&2; exit 1; }

[ -n "$title" ] && [ -n "$bucket" ] && [ -n "$task" ] || fail "--title, --bucket and --task are required"
[ -s "$brief" ] || fail "brief missing or empty: $brief"
[ -f "$record" ] || fail "record not found: $record"
case "$bucket" in implement|review) ;; *) fail "bucket must be implement or review" ;; esac
if [ -n "$worktree" ] && ! [[ "$worktree" =~ ^[0-9a-f]{40}$ ]]; then
  fail "--worktree needs a full 40-character sha"
fi
if [ "$bucket" = implement ] && [ -z "$worktree" ] && [ "$repo_set" -eq 0 ]; then
  fail "an implement lane needs --worktree, or --repo set to its existing worktree"
fi
[ -d "$repo" ] || fail "repo not found: $repo"
git -C "$repo" rev-parse --git-dir > /dev/null 2>&1 || fail "not a git repo: $repo"
if [ "$bucket" = implement ] && [ -z "$worktree" ] &&
  [ "$(git -C "$repo" rev-parse --path-format=absolute --git-dir)" = "$(git -C "$repo" rev-parse --path-format=absolute --git-common-dir)" ]; then
  fail "--repo is the shared checkout; an implement lane needs its own worktree"
fi
brief=$(cd "$(dirname "$brief")" && pwd -P)/$(basename "$brief")
record=$(cd "$(dirname "$record")" && pwd -P)/$(basename "$record")
grep -q 't3 thread send' "$brief" || fail "brief has no report line (t3 thread send)"

# One budget for the whole machine, shared by every area.
budget=$("$(dirname "$0")/capacity.sh" ${capacity_flags[@]+"${capacity_flags[@]}"}) || fail "machine budget could not be read"
echo "$budget title=$title worktree=${worktree:-none}"
room=1
case "$budget" in "slots=0 "*) room=0 ;; esac
if [ "$dry" -eq 1 ]; then
  [ "$room" -eq 1 ] && echo "dry run: nothing started" || echo "dry run: nothing started; a real start would be refused now"
  exit 0
fi
[ "$room" -eq 1 ] || fail "no room on this machine now: $budget"
load=$(printf '%s' "$budget" | sed -n 's/.* load=\([0-9.]*\) .*/\1/p')
free=$(printf '%s' "$budget" | sed -n 's/.* free=\([0-9]*\)GiB .*/\1/p')

# The plain form runs the t3 default model; refuse when it is not the model
# the ledger row will name, so no session starts on a model nobody chose.
if [ -z "$provider" ]; then
  t3_default=$(jq -r '.defaultModelSelection.model // empty' "$HOME/.t3/userdata/settings.json" 2> /dev/null || true)
  [ "$t3_default" = "$model" ] || fail "t3 default model is '${t3_default:-unreadable}', not $model; set the t3 default or pass --provider and --model"
fi

args=(thread start --title "$title")
[ -n "$worktree" ] && args+=(--worktree "$worktree")
[ -n "$provider" ] && args+=(--provider "$provider" --model "$model")
args+=(--json . -)
out=$(cd "$repo" && "$HOME/.t3/bin/t3" "${args[@]}" < "$brief") || fail "thread start failed"
thread=$(printf '%s' "$out" | jq -r '.threadId // empty')
[ -n "$thread" ] || fail "thread start returned no threadId"

echo "thread=$thread"

ledger=$(cd "$repo" && "$HOME/.local/bin/ledger-log" start --bucket "$bucket" --model "$model" --effort high --task "$task" | tail -n 1) || ledger=""
[ -n "$ledger" ] || echo "cos-launch: WARNING no ledger id; open the row by hand for $thread" >&2

line=$(mktemp) || {
  echo "cos-launch: WARNING log line not written; add it by hand for $thread" >&2
  echo "ledger=${ledger:-none}"
  exit 0
}
printf 'Started "%s" thread %s (ledger %s) at load %s, %s GiB free. Task: %s\n' \
  "$title" "$thread" "${ledger:-none}" "$load" "$free" "$task" > "$line"
python3 "$(dirname "$0")/cos-log.py" "$record" "$line" > /dev/null ||
  echo "cos-launch: WARNING log line not written; add it by hand for $thread" >&2
trash "$line" 2>/dev/null || true

echo "ledger=${ledger:-none}"
