#!/bin/sh
# art/pick.sh <id> [stamp] -- publish a roll (newest by default) as public/static/img/<id>.webp
# Square plates → 512×512; wide group plates → 1200×630 (og:image size).
set -eu
cd "$(dirname "$0")/.."
src=${2:+art/rolls/$1/$2.png}
src=${src:-$(ls art/rolls/"$1"/*.png | tail -1)}
if [ "$(magick identify -format '%[fx:w==h]' "$src")" = 1 ]; then
  magick "$src" -resize 512x512 -quality 82 "public/static/img/$1.webp"
else
  magick "$src" -resize 1200x630^ -gravity center -extent 1200x630 -quality 82 "public/static/img/$1.webp"
fi
echo "$src -> public/static/img/$1.webp"
