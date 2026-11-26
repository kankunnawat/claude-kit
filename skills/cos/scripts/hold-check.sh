#!/usr/bin/env bash
# Say whether a hold file is set. Run it first at every tick and every report.
# Usage: hold-check.sh <hold-file>
# No file: prints hold=off and exits 0.
# A file: prints "hold=on since <mtime, UTC> <first line>" and exits 3.
# A wrong call exits 2.
set -euo pipefail

[ $# -eq 1 ] || { echo "usage: hold-check.sh <hold-file>" >&2; exit 2; }
file=$1
if [ ! -e "$file" ]; then
  echo "hold=off"
  exit 0
fi
since=$(date -u -r "$file" +%Y-%m-%dT%H:%MZ)
first=$(head -n 1 "$file" 2> /dev/null || true)
echo "hold=on since $since $first"
exit 3
