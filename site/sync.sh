#!/bin/bash
# Refresh site/bundle/ from the generated transformer-study/bundle/ (run ./render.sh or bundle.py there first).
# site/ is the whole GitHub Pages deliverable; vendor/ holds the pinned @plantuml/core 1.2026.6 build (MIT).
cd "$(dirname "$0")" || exit 1
python3 -I ../transformer-study/check_i18n.py >/dev/null || exit 1
python3 -I ../transformer-study/bundle.py || exit 1
mkdir -p bundle && cp ../transformer-study/bundle/*.puml bundle/ && echo "site/bundle updated"
