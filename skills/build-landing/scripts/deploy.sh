#!/usr/bin/env bash
# Guards the lesson: "`vercel domains inspect` lies about a serving domain."
# The verdict comes from an unsigned curl and CSS-hash parity with the local build.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  deploy.sh <vercel-project> <public-host> [--scope <team-slug>] [--check-only]

  Builds, deploys to production, adds the public domain, then verifies:
  an unsigned 200 with its x-robots-tag, and CSS-hash parity between the
  local dist/ and the served homepage.

  --check-only  build and verify only; prints the deploy commands instead of running them.
USAGE
}

if [ $# -lt 2 ]; then usage; [ $# -eq 1 ] && [ "$1" = "--help" ] && exit 0; exit 1; fi

project=$1; host=$2; shift 2
scope=(); check_only=false
while [ $# -gt 0 ]; do
  case $1 in
    --scope) scope=(--scope "$2"); shift 2 ;;
    --check-only) check_only=true; shift ;;
    *) echo "unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

echo "== build"
npm run build

deploy_command="vercel deploy --prod --yes ${scope[*]:-}"
domain_command="vercel domains add $host $project ${scope[*]:-}"

if [ "$check_only" = true ]; then
  echo "== check-only: skipping the two remote writes"
  echo "   $deploy_command"
  echo "   $domain_command"
else
  echo "== deploy"
  if ! vercel deploy --prod --yes ${scope[@]+"${scope[@]}"}; then
    echo "production deploy refused. Hand the owner this command:" >&2
    echo "   $deploy_command" >&2
    exit 1
  fi
  echo "== domain"
  if ! output=$(vercel domains add "$host" "$project" ${scope[@]+"${scope[@]}"} 2>&1); then
    echo "$output"
    echo "$output" | grep -qi 'already' || { echo "adding $host failed" >&2; exit 1; }
    echo "   (already assigned: fine)"
  else
    echo "$output"
  fi
fi

echo "== unsigned response from https://$host/"
headers=$(curl -s -o /dev/null -D - "https://$host/" | tr -d '\r') || { echo "no response from https://$host/" >&2; exit 1; }
status=$(printf '%s' "$headers" | awk 'NR==1 {print $2}')
robots=$(printf '%s' "$headers" | grep -i '^x-robots-tag:' || echo 'x-robots-tag: (none)')
echo "   HTTP $status"
echo "   $robots"
[ "$status" = "200" ] || { echo "public address does not answer 200 without a sign-in" >&2; exit 1; }

echo "== CSS hash parity"
css() { grep -o 'href="[^"]*\.css"' | sort -u; }
local_css=$(css < dist/index.html)
served_css=$(curl -s "https://$host/" | css)
echo "   local:  $(echo "$local_css" | tr '\n' ' ')"
echo "   served: $(echo "$served_css" | tr '\n' ' ')"
[ "$local_css" = "$served_css" ] || { echo "served CSS does not match the local build: the live site is not this build" >&2; exit 1; }

echo "== verified: $host serves this build, unsigned, with $robots"
