#!/usr/bin/env bash
# Print how many new agent sessions this machine has room for right now.
# Usage:
#   capacity.sh [--quiet-hours] [--max N] [--per-session N] [--swap-max PCT]
#               [--mem-min PCT] [--min-free-gib N] [--max-load N]
# The defaults are the starting numbers; a machine's own numbers come from its
# row in the roster and are passed as flags.
#   slots = floor((cores - load) / per-session), at most --max (1 in quiet hours)
#   slots = 0 when swap used >= --swap-max, memory free < --mem-min,
#           free disk < --min-free-gib, or load >= --max-load (an area's own
#           stricter ceiling; off unless given)
# It reads the whole machine, so every area shares one budget.
# Output is one line: slots=N followed by the readings, the night-mode switch
# and the reason. night_mode=on when the file verify-lane reads
# (${VERIFY_LANE_NIGHT:-~/.local/state/night-mode/until}) holds an epoch later
# than now, the same test as `night-mode status`; otherwise off. It changes no
# slot number.
# CAPACITY_READINGS="cores load swap_pct mem_free_pct free_gib" replaces the
# live readings (for the test).
set -euo pipefail

max=4 per=2 swap_max=75 mem_min=20 min_free=20 quiet=0 max_load=""
while [ $# -gt 0 ]; do
  case "$1" in
    --quiet-hours) quiet=1; shift ;;
    --max) max="$2"; shift 2 ;;
    --per-session) per="$2"; shift 2 ;;
    --swap-max) swap_max="$2"; shift 2 ;;
    --mem-min) mem_min="$2"; shift 2 ;;
    --min-free-gib) min_free="$2"; shift 2 ;;
    --max-load) max_load="$2"; shift 2 ;;
    *) echo "capacity: unknown argument: $1" >&2; exit 2 ;;
  esac
done
for n in "$max" "$per" "$swap_max" "$mem_min" "$min_free" ${max_load:+"$max_load"}; do
  [[ "$n" =~ ^[0-9]+$ ]] || { echo "capacity: limits must be whole numbers, got: $n" >&2; exit 2; }
done
[ "$per" -gt 0 ] || { echo "capacity: --per-session must be above 0" >&2; exit 2; }

busy="n/a"
if [ -n "${CAPACITY_READINGS:-}" ]; then
  read -r cores load swap_pct mem_free free <<< "$CAPACITY_READINGS"
else
  cores=$(sysctl -n hw.ncpu)
  load=$(sysctl -n vm.loadavg | awk '{print $2}')
  swap_pct=$(sysctl -n vm.swapusage | awk '{t=$3; u=$6; sub(/M/,"",t); sub(/M/,"",u); print (t > 0) ? int(u * 100 / t) : 0}')
  mem_free=$(memory_pressure | awk '/free percentage/ {sub(/%/,"",$NF); print $NF}')
  free=$(df -g / | awk 'NR==2 {print $4}')
  if command -v verify-lane > /dev/null 2>&1; then
    busy=$(verify-lane --status 2> /dev/null | grep -c 'pid=' || true)
  fi
fi
for n in "$cores" "$swap_pct" "$mem_free" "$free"; do
  [[ "$n" =~ ^[0-9]+$ ]] || { echo "capacity: could not read the machine (got: $cores $load $swap_pct $mem_free $free)" >&2; exit 1; }
done
[[ "$load" =~ ^[0-9]+(\.[0-9]+)?$ ]] || { echo "capacity: could not read the load (got: $load)" >&2; exit 1; }

[ "$quiet" -eq 1 ] && [ "$max" -gt 1 ] && max=1
slots=$(awk -v c="$cores" -v l="$load" -v p="$per" -v m="$max" 'BEGIN { s = int((c - l) / p); if (s < 0) s = 0; if (s > m) s = m; print s }')
reason="room for $slots"
[ "$slots" -eq 0 ] && reason="load $load on $cores cores"
if [ -n "$max_load" ] && awk -v l="$load" -v m="$max_load" 'BEGIN { exit !(l >= m) }'; then
  slots=0; reason="load $load at or over the area's ceiling $max_load"
fi
if [ "$swap_pct" -ge "$swap_max" ]; then slots=0; reason="swap ${swap_pct}% used"; fi
if [ "$mem_free" -lt "$mem_min" ]; then slots=0; reason="memory ${mem_free}% free"; fi
if [ "$free" -lt "$min_free" ]; then slots=0; reason="disk ${free} GiB free"; fi

night_mode=off
night_until=$(cat "${VERIFY_LANE_NIGHT:-$HOME/.local/state/night-mode/until}" 2> /dev/null || true)
if [[ "$night_until" =~ ^[0-9]+$ ]] && [ "$(date +%s)" -lt "$night_until" ]; then night_mode=on; fi

echo "slots=$slots load=$load cores=$cores swap=${swap_pct}% mem_free=${mem_free}% free=${free}GiB verify_lane_busy=$busy night_mode=$night_mode reason=\"$reason\""
