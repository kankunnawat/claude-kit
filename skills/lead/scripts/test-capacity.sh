#!/usr/bin/env bash
# Self-check for capacity.sh against recorded readings. Reads nothing live.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
fails=0
# t <name> <expected slots> <"cores load swap% mem_free% free_gib"> [flags...]
t() {
  local name="$1" want="$2" readings="$3"; shift 3
  local out got
  out=$(CAPACITY_READINGS="$readings" "$HERE/capacity.sh" "$@" 2>&1)
  got=$(printf '%s' "$out" | sed -n 's/^slots=\([0-9]*\) .*/\1/p')
  if [ "$got" = "$want" ]; then echo "  ok   $name"; else echo "  FAIL $name: want $want, got: $out"; fails=$((fails+1)); fi
}

t "idle machine fills to the cap"        4 "10 1.5 10 60 60"
t "half loaded leaves room for two"      2 "10 5.0 10 60 60"
t "2026-11-18 reading: load past cores"  0 "10 20.33 77 56 60"
t "low disk stops every start"           0 "10 1.5 10 60 15"
t "full swap stops every start"          0 "10 1.5 75 60 60"
t "low memory stops every start"         0 "10 1.5 10 19 60"
t "quiet hours allow one"                1 "10 1.5 10 60 60" --quiet-hours
t "a machine's own cap is honoured"      2 "10 1.5 10 60 60" --max 2
t "a bigger machine gets more room"      4 "16 5.0 10 60 60"

if CAPACITY_READINGS="10 abc 10 60 60" "$HERE/capacity.sh" > /dev/null 2>&1; then
  echo "  FAIL an unreadable load must exit non-zero"; fails=$((fails+1))
else
  echo "  ok   an unreadable load exits non-zero"
fi

[ "$fails" -eq 0 ] && echo "all checks passed" || { echo "$fails failed"; exit 1; }
