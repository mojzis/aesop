#!/bin/sh
# art/pick.sh <id> [stamp] -- publish a roll (newest by default) as static/img/<id>.webp
set -eu
cd "$(dirname "$0")/.."
src=${2:+art/rolls/$1/$2.png}
src=${src:-$(ls art/rolls/"$1"/*.png | tail -1)}
magick "$src" -resize 512x512 -quality 82 "static/img/$1.webp"
echo "$src -> static/img/$1.webp"
