#!/bin/bash
# Render a spec page in light, dark and at phone width, so you can look at it before delivery.
# usage: bash shoot.sh <page.html> [outdir]    (outdir defaults to a new temp dir)
# Needs the playwright CLI and Google Chrome; headless Chrome alone can't go below 500 px wide.
set -euo pipefail
page="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
out="${2:-$(mktemp -d)}"
mkdir -p "$out"
name="$(basename "$page" .html)"
shot() { local tag="$1"; shift; playwright screenshot --channel chrome --full-page "$@" "file://$page" "$out/$name-$tag.png" >/dev/null; }

shot light --viewport-size "1280, 800" --color-scheme light
shot dark --viewport-size "1280, 800" --color-scheme dark
shot phone-full --viewport-size "390, 844" --color-scheme light

w="$(magick identify -format %w "$out/$name-phone-full.png")"
if [ "$w" -gt 390 ]; then echo "WARN: the page is ${w}px wide on a 390px phone; something does not wrap" >&2; fi

# Cut the tall phone shot into tiles that stay readable when viewed.
magick "$out/$name-phone-full.png" -crop x1400 +repage "$out/$name-phone-%d.png"
ls "$out/$name"-light.png "$out/$name"-dark.png "$out/$name"-phone-[0-9]*.png
