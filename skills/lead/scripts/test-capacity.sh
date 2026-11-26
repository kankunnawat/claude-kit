#!/usr/bin/env bash
# Self-check for capacity.sh against recorded readings. Reads nothing live.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
fails=0
# Every case reads a night-mode file under a temp dir, never the live one.
NIGHT_DIR="$(mktemp -d)"
trap 'rm -r "$NIGHT_DIR" 2>/dev/null' EXIT
export VERIFY_LANE_NIGHT="$NIGHT_DIR/until"
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
t "an area's load ceiling stops starts"  0 "10 6.2 10 60 60" --max-load 6
t "under the ceiling the budget rules"   2 "10 5.0 10 60 60" --max-load 6

if CAPACITY_READINGS="10 abc 10 60 60" "$HERE/capacity.sh" > /dev/null 2>&1; then
  echo "  FAIL an unreadable load must exit non-zero"; fails=$((fails+1))
else
  echo "  ok   an unreadable load exits non-zero"
fi

# n <name> <expected night_mode> <file content, or "missing">
n() {
  local name="$1" want="$2" content="$3" out got
  rm -f "$VERIFY_LANE_NIGHT"
  [ "$content" = missing ] || printf '%s\n' "$content" > "$VERIFY_LANE_NIGHT"
  out=$(CAPACITY_READINGS="10 1.5 10 60 60" "$HERE/capacity.sh" 2>&1)
  got=$(printf '%s' "$out" | sed -n 's/.* night_mode=\([a-z]*\) .*/\1/p')
  if [ "$got" = "$want" ] && [ "${out%% *}" = "slots=4" ]; then echo "  ok   $name"; else echo "  FAIL $name: want night_mode=$want and slots=4, got: $out"; fails=$((fails+1)); fi
}
now=$(date +%s)
n "no night-mode file is off"            off missing
n "an end time ahead is on, same slots"  on  "$((now + 3600))"
n "an end time passed is off"            off "$((now - 60))"
n "an unreadable file is off"            off "soon"

[ "$fails" -eq 0 ] && echo "all checks passed" || { echo "$fails failed"; exit 1; }
