#!/usr/bin/env bash
# Start one CoS session: machine check, thread, ledger row, log line.
# Usage:
#   cos-launch.sh --title T --brief FILE --bucket implement|review \
#     --task TEXT --record RECORD.md [--worktree FULL_SHA] [--repo DIR] \
#     [--model ID] [--dry-run]
# --model only labels the ledger row; the thread runs on the t3 default.
# An implement lane needs --worktree (new lane) or --repo (a fix round in the
# lane's existing worktree), so it never starts in the shared checkout.
# Exits non-zero, with nothing left behind, if a check or the start fails.
# Once the thread runs, a ledger or log failure only warns; thread= is always printed.
set -euo pipefail

title="" brief="" bucket="" task="" record="" worktree="" repo="$PWD" repo_set=0
model="claude-opus-5-5" dry=0
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
brief=$(cd "$(dirname "$brief")" && pwd -P)/$(basename "$brief")
record=$(cd "$(dirname "$record")" && pwd -P)/$(basename "$record")
grep -q 't3 thread send' "$brief" || fail "brief has no report line (t3 thread send)"

# Machine limits. Quiet hours are 17:00 to 01:00 UTC (00:00 to 08:00 Bangkok).
hour=$((10#$(date -u +%H)))
if [ "$hour" -ge 17 ] || [ "$hour" -lt 1 ]; then mode="quiet"; limit=6; else mode="day"; limit=12; fi
load=$(sysctl -n vm.loadavg | awk '{print $2}')
free=$(df -g / | awk 'NR==2 {print $4}')
awk -v l="$load" -v m="$limit" 'BEGIN { exit !(l < m) }' || fail "load $load is not under $limit ($mode)"
[ "$free" -ge 20 ] || fail "free disk ${free} GiB is under 20 GiB"

echo "mode=$mode load=$load free=${free}GiB title=$title worktree=${worktree:-none}"
if [ "$dry" -eq 1 ]; then echo "dry run: nothing started"; exit 0; fi

args=(thread start --title "$title")
[ -n "$worktree" ] && args+=(--worktree "$worktree")
args+=(--json . -)
out=$(cd "$repo" && "$HOME/.t3/bin/t3" "${args[@]}" < "$brief") || fail "thread start failed"
thread=$(printf '%s' "$out" | jq -r '.threadId // empty')
[ -n "$thread" ] || fail "thread start returned no threadId"

echo "thread=$thread"

ledger=$(cd "$repo" && "$HOME/.local/bin/ledger-log" start --bucket "$bucket" --model "$model" --effort high --task "$task" | tail -n 1) || ledger=""
[ -n "$ledger" ] || echo "cos-launch: WARNING no ledger id; open the row by hand for $thread" >&2

line=$(mktemp)
printf 'Started "%s" thread %s (ledger %s) at load %s, %s GiB free. Task: %s\n' \
  "$title" "$thread" "${ledger:-none}" "$load" "$free" "$task" > "$line"
python3 "$(dirname "$0")/cos-log.py" "$record" "$line" > /dev/null ||
  echo "cos-launch: WARNING log line not written; add it by hand for $thread" >&2
trash "$line" 2>/dev/null || true

echo "ledger=${ledger:-none}"
