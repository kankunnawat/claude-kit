#!/usr/bin/env bash
set -euo pipefail
if [ "${1:-}" = --help ]; then
  echo 'Usage: bash test-deploy.sh  # local target, preflight, static parity, and robots fixtures'
  exit 0
fi

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
fixture=$(mktemp -d)
trap 'printf "fixture retained: %s\n" "$fixture"' EXIT
artifacts=${BUILD_LANDING_CHECKS_DIR:-}
if [ -n "$artifacts" ]; then
  mkdir -p "$artifacts"
  artifacts=$(cd -- "$artifacts" && pwd)
fi
mkdir -p "$fixture/bin" "$fixture/dist/_astro" "$fixture/dist/about" "$fixture/live"
printf 'home current\n' > "$fixture/dist/index.html"
printf 'about current\n' > "$fixture/dist/about/index.html"
printf 'body{}\n' > "$fixture/dist/_astro/site.css"
printf 'console.log("current")\n' > "$fixture/dist/_astro/site.js"
printf '<svg>current</svg>\n' > "$fixture/dist/brand mark.svg"
printf 'font current\n' > "$fixture/dist/_astro/site.woff2"
cp -R "$fixture/dist/." "$fixture/live/"

cat > "$fixture/bin/npm" <<'STUB'
#!/usr/bin/env bash
printf 'npm' >> "$CALLS_LOG"
printf ' <%s>' "$@" >> "$CALLS_LOG"
printf '\n' >> "$CALLS_LOG"
[ "$*" = 'run build' ]
STUB
cat > "$fixture/bin/vercel" <<'STUB'
#!/usr/bin/env bash
set -euo pipefail
printf 'vercel' >> "$CALLS_LOG"
printf ' <%s>' "$@" >> "$CALLS_LOG"
printf '\n' >> "$CALLS_LOG"
operation=$1; shift
if [ "$operation" = domains ]; then
  [ "$*" = 'add example.test fixture-project --scope fixture-scope' ]
  echo 'domain bound'
  exit 0
fi
project= scope= prod=false prebuilt=false yes=false
while [ "$#" -gt 0 ]; do
  case "$1" in
    --project) project=${2:-}; shift 2 ;;
    --scope) scope=${2:-}; shift 2 ;;
    --prod) prod=true; shift ;;
    --prebuilt) prebuilt=true; shift ;;
    --yes) yes=true; shift ;;
    *) echo "unexpected Vercel argument: $1" >&2; exit 1 ;;
  esac
done
[ "$project" = fixture-project ] && [ "$scope" = fixture-scope ] && [ "$prod" = true ] && [ "$yes" = true ] || {
  echo 'Vercel target or required flags differ' >&2; exit 1;
}
case "$operation" in
  build)
    [ "$HOST_BUILD_FAIL" = 0 ] || { echo 'fixture host build failed' >&2; exit 1; }
    if [ "$HOST_OUTPUT_MISSING" = 0 ]; then
      mkdir -p .vercel/output/static
      cp dist/index.html .vercel/output/static/index.html
    fi
    ;;
  deploy)
    [ "$prebuilt" = true ] && [ -f .vercel/output/static/index.html ] || exit 1
    echo 'prebuilt deployed'
    ;;
  *) exit 1 ;;
esac
STUB
cat > "$fixture/bin/curl" <<'STUB'
#!/usr/bin/env bash
set -euo pipefail
printf 'curl' >> "$CURL_LOG"
printf ' <%s>' "$@" >> "$CURL_LOG"
printf '\n' >> "$CURL_LOG"
output= url= headers=false
while [ "$#" -gt 0 ]; do
  case "$1" in
    -D) headers=true; shift 2 ;;
    -o) output=$2; shift 2 ;;
    https://*) url=$1; shift ;;
    *) shift ;;
  esac
done
if [ "$headers" = true ]; then
  printf 'HTTP/1.1 %s fixture\r\n' "$HTTP_STATUS"
  [ -z "$ROBOTS_HEADERS" ] || printf '%s\n' "$ROBOTS_HEADERS" | sed 's/$/\r/'
  printf '\r\n'
  exit 0
fi
[ "$HTTP_STATUS" = 200 ] || exit 22
path=${url#https://example.test}
path=${path//%20/ }
case "$path" in /|*/) path="${path}index.html" ;; esac
cp "$LIVE_ROOT$path" "$output"
STUB
chmod +x "$fixture/bin/npm" "$fixture/bin/vercel" "$fixture/bin/curl"

export PATH="$fixture/bin:$PATH" LIVE_ROOT="$fixture/live"
export CALLS_LOG="$fixture/calls.log" CURL_LOG="$fixture/curl.log"
export HTTP_STATUS=200 HOST_BUILD_FAIL=0 HOST_OUTPUT_MISSING=0
export ROBOTS_HEADERS='x-robots-tag: noindex, nofollow'
cd "$fixture"
fails=0
fixture_project=fixture-project; fixture_host=example.test
check() {
  local name=$1; shift
  if "$@"; then echo "pass: $name"; else echo "FAIL: $name" >&2; fails=$((fails + 1)); fi
}
no_call() { ! grep -Fq "$1" "$CALLS_LOG"; }
run_case() {
  local name=$1 want=$2 message=$3 status=0
  shift 3
  : > "$CALLS_LOG"
  : > "$CURL_LOG"
  bash "$script_dir/deploy.sh" "$fixture_project" "$fixture_host" --scope fixture-scope "$@" > "$fixture/$name.log" 2>&1 || status=$?
  if [ "$want" = pass ]; then check "$name exits successfully" test "$status" -eq 0
  else check "$name rejects" test "$status" -ne 0; fi
  [ -z "$message" ] || check "$name gives the failing path or policy" grep -Fq "$message" "$fixture/$name.log"
  if [ -n "$artifacts" ]; then
    cp "$fixture/$name.log" "$artifacts/$name.log"
    cp "$CALLS_LOG" "$artifacts/$name.calls"
    cp "$CURL_LOG" "$artifacts/$name.curl"
    printf '%s\n' "$status" > "$artifacts/$name.exit"
  fi
}

run_case matching pass '' --check-only
check 'check-only calls no Vercel command' no_call 'vercel'
check 'check-only rebuilds locally' grep -Fxq 'npm <run> <build>' "$CALLS_LOG"
check 'filename with spaces is fetched as one encoded URL' grep -Fq '<https://example.test/brand%20mark.svg>' "$CURL_LOG"
check 'check-only prints pinned preflight' grep -Fq 'vercel build --prod --project fixture-project --yes --scope fixture-scope' "$fixture/matching.log"
check 'check-only prints pinned prebuilt deploy' grep -Fq 'vercel deploy --prebuilt --prod --project fixture-project --yes --scope fixture-scope' "$fixture/matching.log"
check 'check-only prints pinned domain binding' grep -Fq 'vercel domains add example.test fixture-project --scope fixture-scope' "$fixture/matching.log"

run_case production pass ''
cat > "$fixture/want.calls" <<'CALLS'
npm <run> <build>
vercel <build> <--prod> <--project> <fixture-project> <--yes> <--scope> <fixture-scope>
vercel <deploy> <--prebuilt> <--prod> <--project> <fixture-project> <--yes> <--scope> <fixture-scope>
vercel <domains> <add> <example.test> <fixture-project> <--scope> <fixture-scope>
CALLS
check 'production builds, deploys prebuilt output, and binds the supplied target in order' cmp -s "$fixture/want.calls" "$CALLS_LOG"

export HOST_BUILD_FAIL=1
run_case host-build-fails fail ''
check 'failed host build attempts the pinned preflight' grep -Fq 'vercel <build> <--prod> <--project> <fixture-project>' "$CALLS_LOG"
check 'failed host build performs no deployment' no_call 'vercel <deploy>'
check 'failed host build performs no domain write' no_call 'vercel <domains>'
export HOST_BUILD_FAIL=0 HOST_OUTPUT_MISSING=1
if [ -f .vercel/output/static/index.html ]; then
  mv .vercel/output/static/index.html "$fixture/previous-host-index.html"
fi
run_case host-output-missing fail '.vercel/output/static/index.html'
check 'missing host output performs no deployment' no_call 'vercel <deploy>'
check 'missing host output performs no domain write' no_call 'vercel <domains>'
export HOST_OUTPUT_MISSING=0

printf 'console.log("stale")\n' > "$fixture/live/_astro/site.js"
run_case stale-js fail 'served /_astro/site.js differs' --check-only
cp "$fixture/dist/_astro/site.js" "$fixture/live/_astro/site.js"
printf 'about stale\n' > "$fixture/live/about/index.html"
run_case stale-html fail 'served /about/ differs' --check-only
cp "$fixture/dist/about/index.html" "$fixture/live/about/index.html"
for asset in 'brand mark.svg' '_astro/site.woff2'; do
  name=svg; [ "$asset" != '_astro/site.woff2' ] || name=font
  printf 'stale\n' > "$fixture/live/$asset"
  run_case "stale-$name" fail "served /$asset differs" --check-only
  mv "$fixture/live/$asset" "$fixture/missing-$name"
  run_case "missing-$name" fail "cannot fetch /$asset" --check-only
  cp "$fixture/dist/$asset" "$fixture/live/$asset"
done

export HTTP_STATUS=401
run_case unsigned-non200 fail 'does not answer 200' --check-only
export HTTP_STATUS=200 ROBOTS_HEADERS='X-Robots-Tag: NOFOLLOW,  NoIndex, nofollow'
run_case robots-normalized pass '' --check-only --expect-robots ' noindex , NOFOLLOW , noindex '
export ROBOTS_HEADERS=$'X-Robots-Tag: nofollow\nx-robots-tag: NOINDEX\nX-Robots-Tag: noindex'
run_case robots-multiple-rows pass '' --check-only --expect-robots 'noindex, nofollow'
export ROBOTS_HEADERS=
run_case robots-missing fail 'missing x-robots-tag' --check-only --expect-robots 'noindex, nofollow'
run_case robots-not-required pass 'x-robots-tag: (none)' --check-only
export ROBOTS_HEADERS='x-robots-tag: index, follow'
run_case robots-wrong fail 'robots directives differ' --check-only --expect-robots 'noindex, nofollow'
export ROBOTS_HEADERS='x-robots-tag: noindex, nofollow, noarchive'
run_case robots-extra fail 'robots directives differ' --check-only --expect-robots 'noindex, nofollow'
export ROBOTS_HEADERS='x-robots-tag: noindex'
run_case robots-partial fail 'robots directives differ' --check-only --expect-robots 'noindex, nofollow'
export ROBOTS_HEADERS='x-robots-tag: googlebot: noindex, nofollow'
run_case robots-scoped fail 'unscoped directive names' --check-only --expect-robots 'noindex, nofollow'
run_case robots-scoped-observed pass '' --check-only

for option in --scope --expect-robots; do
  name=${option#--}
  run_case "$name-missing" fail "requires a non-empty value" "$option"
  check "$name missing value fails before build or writes" test ! -s "$CALLS_LOG"
  run_case "$name-empty" fail "requires a non-empty value" "$option" ''
  check "$name empty value fails before build or writes" test ! -s "$CALLS_LOG"
  run_case "$name-next-flag" fail "requires a non-empty value" "$option" --check-only
  check "$name next flag fails before build or writes" test ! -s "$CALLS_LOG"
  run_case "$name-single-dash" fail "requires a non-empty value" --check-only "$option" -x
  check "$name single-dash option fails before build or writes" test ! -s "$CALLS_LOG"
done
run_case robots-empty-directives fail 'requires directive names' --expect-robots ' , '
check 'empty robots directives fail before build or writes' test ! -s "$CALLS_LOG"
run_case robots-scoped-expectation fail 'unscoped directive names' --expect-robots 'googlebot: noindex'
check 'scoped expectation fails before build or writes' test ! -s "$CALLS_LOG"
fixture_project=
run_case project-empty fail 'project and public host must be non-empty'
check 'empty project fails before build or writes' test ! -s "$CALLS_LOG"
fixture_project=fixture-project; fixture_host=
run_case host-empty fail 'project and public host must be non-empty'
check 'empty public host fails before build or writes' test ! -s "$CALLS_LOG"
fixture_project=--unknown; fixture_host=example.test
run_case project-option fail 'project and public host cannot be options' --check-only
check 'project option fails before build or writes' test ! -s "$CALLS_LOG"
fixture_project=fixture-project; fixture_host=-x
run_case host-option fail 'project and public host cannot be options' --check-only
check 'host option fails before build or writes' test ! -s "$CALLS_LOG"

echo "fixture failures: $fails checks"
[ "$fails" -eq 0 ]
