#!/usr/bin/env bash
# Self-check for hold-check.sh against a temp hold file. Reads nothing live.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -r "$TMP" 2>/dev/null' EXIT
fails=0
# t <name> <expected exit> <expected output pattern> [args...]
t() {
  local name="$1" want_code="$2" pattern="$3"; shift 3
  local out code
  out=$("$HERE/hold-check.sh" "$@" 2>&1); code=$?
  if [ "$code" = "$want_code" ] && [[ "$out" =~ $pattern ]]; then echo "  ok   $name"; else echo "  FAIL $name: want exit $want_code and /$pattern/, got exit $code: $out"; fails=$((fails+1)); fi
}

t "no hold file is off"                  0 '^hold=off$' "$TMP/hold.md"
printf 'Discussion with the owner\nmore\n' > "$TMP/hold.md"
t "a hold file is on with its first line" 3 '^hold=on since [0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}Z Discussion with the owner$' "$TMP/hold.md"
: > "$TMP/empty.md"
t "an empty hold file is still on"       3 '^hold=on since [0-9-]+T[0-9:]+Z $' "$TMP/empty.md"
t "no argument is a wrong call"          2 '^usage'

[ "$fails" -eq 0 ] && echo "all checks passed" || { echo "$fails failed"; exit 1; }
