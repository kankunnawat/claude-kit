#!/usr/bin/env bash
set -euo pipefail
if [ "${1:-}" = --help ]; then
  echo 'Usage: bash test-deploy.sh  # static parity fixture for deploy.sh'
  exit 0
fi

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
fixture=$(mktemp -d)
trap 'find "$fixture" -depth -delete' EXIT
mkdir -p "$fixture/bin" "$fixture/dist/_astro" "$fixture/dist/about" "$fixture/live"
printf 'home current\n' > "$fixture/dist/index.html"
printf 'about current\n' > "$fixture/dist/about/index.html"
printf 'body{}\n' > "$fixture/dist/_astro/site.css"
printf 'console.log("current")\n' > "$fixture/dist/_astro/site.js"
cp -R "$fixture/dist/." "$fixture/live/"

cat > "$fixture/bin/npm" <<'STUB'
#!/usr/bin/env bash
exit 0
STUB
cat > "$fixture/bin/curl" <<'STUB'
#!/usr/bin/env bash
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
  printf 'HTTP/1.1 200 OK\r\nx-robots-tag: noindex\r\n'
  exit 0
fi
path=${url#https://example.test}
case "$path" in /|*/) path="${path}index.html" ;; esac
cp "$LIVE_ROOT$path" "$output"
STUB
chmod +x "$fixture/bin/npm" "$fixture/bin/curl"

export PATH="$fixture/bin:$PATH" LIVE_ROOT="$fixture/live"
cd "$fixture"
bash "$script_dir/deploy.sh" fixture example.test --check-only > "$fixture/pass.log"
printf 'console.log("stale")\n' > "$fixture/live/_astro/site.js"
if bash "$script_dir/deploy.sh" fixture example.test --check-only > "$fixture/js.log" 2>&1; then
  echo 'stale JS passed' >&2; exit 1
fi
grep -Fq 'served /_astro/site.js differs' "$fixture/js.log"
cp "$fixture/dist/_astro/site.js" "$fixture/live/_astro/site.js"
printf 'about stale\n' > "$fixture/live/about/index.html"
if bash "$script_dir/deploy.sh" fixture example.test --check-only > "$fixture/html.log" 2>&1; then
  echo 'stale HTML passed' >&2; exit 1
fi
grep -Fq 'served /about/ differs' "$fixture/html.log"
printf 'pass: matching build; reject: stale JS; reject: stale nested HTML\n'
