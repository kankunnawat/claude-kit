#!/usr/bin/env bash
# Guards the lesson: "`vercel domains inspect` lies about a serving domain."
# The verdict comes from an unsigned curl and parity with the local static build.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  deploy.sh <vercel-project> <public-host> [--scope <team-slug>] [--expect-robots <directives>] [--check-only]

  Builds locally, runs a project-pinned production Vercel build, checks its
  static entry, deploys that prebuilt output, and binds the public domain.
  Verifies an unsigned 200 and byte parity for every built static file.

  --expect-robots  require the exact normalized set of unscoped, value-free
                   directive names; otherwise report the observed header.
  --check-only     local rebuild and public verification only; prints the
                   preflight, deploy, and domain commands without running Vercel.
USAGE
}

if [ $# -lt 2 ]; then usage; [ $# -eq 1 ] && [ "$1" = "--help" ] && exit 0; exit 1; fi

project=$1; host=$2; shift 2
[ -n "$project" ] && [ -n "$host" ] || { echo 'project and public host must be non-empty' >&2; exit 1; }
[[ $project != -* && $host != -* ]] || { echo 'project and public host cannot be options' >&2; exit 1; }
scope=(); check_only=false; expect_robots=
while [ $# -gt 0 ]; do
  case $1 in
    --scope|--expect-robots)
      option=$1; value=${2:-}
      if [[ -z ${value//[[:space:]]/} || $value == -* ]]; then
        echo "$option requires a non-empty value" >&2; exit 1
      fi
      if [ "$option" = --scope ]; then scope=(--scope "$value"); else expect_robots=$value; fi
      shift 2
      ;;
    --check-only) check_only=true; shift ;;
    *) echo "unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

# ponytail: unscoped, value-free names; add a scope-aware parser only when project policy requires it.
normalize_robots() {
  printf '%s\n' "$1" | tr ',' '\n' | awk '{
    gsub(/^[[:space:]]+|[[:space:]]+$/, "")
    if ($0 == "") next
    value = tolower($0)
    if (value !~ /^[a-z][a-z0-9_-]*$/) { invalid = 1; next }
    print value
  } END { exit invalid }' | LC_ALL=C sort -u
}
if [ -n "$expect_robots" ]; then
  expected=$(normalize_robots "$expect_robots") || {
    echo '--expect-robots supports only unscoped directive names without values; use project verification for scoped or value-bearing directives' >&2; exit 1;
  }
  [ -n "$expected" ] || { echo '--expect-robots requires directive names' >&2; exit 1; }
fi

print_command() { printf '   '; printf '%q ' "$@"; printf '\n'; }
build_command=(vercel build --prod --project "$project" --yes ${scope[@]+"${scope[@]}"})
deploy_command=(vercel deploy --prebuilt --prod --project "$project" --yes ${scope[@]+"${scope[@]}"})
domain_command=(vercel domains add "$host" "$project" ${scope[@]+"${scope[@]}"})

echo "== local build"
npm run build
[ -f dist/index.html ] || { echo 'dist/index.html is missing' >&2; exit 1; }

if [ "$check_only" = true ]; then
  echo "== check-only: no Vercel commands run"
  print_command "${build_command[@]}"
  print_command "${deploy_command[@]}"
  print_command "${domain_command[@]}"
else
  echo "== host production build"
  if ! "${build_command[@]}"; then
    echo 'host production build failed; deployment was not attempted. Hand the owner this command:' >&2
    print_command "${build_command[@]}" >&2
    exit 1
  fi
  [ -f .vercel/output/static/index.html ] || {
    echo '.vercel/output/static/index.html is missing; check the host build configuration before deployment' >&2; exit 1;
  }
  echo "== deploy"
  if ! "${deploy_command[@]}"; then
    echo "production deploy refused. Hand the owner this command:" >&2
    print_command "${deploy_command[@]}" >&2
    exit 1
  fi
  echo "== domain"
  if ! output=$("${domain_command[@]}" 2>&1); then
    echo "$output"
    echo "$output" | grep -qi 'already' || { echo "adding $host failed" >&2; exit 1; }
    echo "   (already assigned: fine)"
  else
    echo "$output"
  fi
fi

echo "== unsigned response from https://$host/"
headers=$(curl -q -sS -o /dev/null -D - "https://$host/" | tr -d '\r') || { echo "no response from https://$host/" >&2; exit 1; }
status=$(printf '%s\n' "$headers" | awk '/^HTTP\// {status = $2} END {print status}')
robots=$(printf '%s\n' "$headers" | grep -i '^x-robots-tag:' || true)
echo "   HTTP $status"
echo "   ${robots:-x-robots-tag: (none)}"
[ "$status" = "200" ] || { echo "public address does not answer 200 without a sign-in" >&2; exit 1; }
if [ -n "$expect_robots" ]; then
  [ -n "$robots" ] || { echo "missing x-robots-tag; expected: $expect_robots" >&2; exit 1; }
  values=$(printf '%s\n' "$robots" | sed 's/^[^:]*://')
  observed=$(normalize_robots "$values") || {
    echo 'x-robots-tag comparison supports only unscoped directive names without values; use project verification for this header' >&2; exit 1;
  }
  [ "$observed" = "$expected" ] || {
    echo "robots directives differ; expected: $expect_robots; observed: $values" >&2; exit 1;
  }
fi

echo "== all static file parity"
response_file=$(mktemp)
trap 'rm -f "$response_file"' EXIT
checked=0
while IFS= read -r -d '' file; do
  relative=${file#dist/}
  path="/$relative"
  case $relative in
    index.html) path=/ ;;
    */index.html) path="/${relative%index.html}" ;;
  esac
  url_path=$(node -e 'process.stdout.write(process.argv[1].split("/").map(encodeURIComponent).join("/"))' "$path")
  curl -q -fsSL "https://$host$url_path" -o "$response_file" || { echo "cannot fetch $path from $host" >&2; exit 1; }
  cmp -s "$file" "$response_file" || { echo "served $path differs from the local build" >&2; exit 1; }
  checked=$((checked + 1))
done < <(find dist -type f -print0)
echo "   $checked built static files match"

echo "== verified: $host serves all static files from this build, unsigned, with ${robots:-x-robots-tag: (none)}"
