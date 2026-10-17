#!/bin/bash
# Render the diagram(s) in every language: out/<lang>/<name>.svg and .png
# Also writes bundle/<name>.puml: self-contained versions (translations inlined, one language line)
# usage: ./render.sh [name ...]      (default: plantuml_export)
#        PLANTUML_JAR=/path/to/plantuml.jar ./render.sh   (default: lib/plantuml.jar, auto-downloaded)
# Paths inside the .puml are relative to the working directory, so we cd here first.
cd "$(dirname "$0")" || exit 1
# plantuml.jar: PLANTUML_JAR if set, else lib/plantuml.jar (downloaded on first run; needs Java 17+).
JAR="${PLANTUML_JAR:-$PWD/lib/plantuml.jar}"
if [ ! -f "$JAR" ]; then
  [ -n "$PLANTUML_JAR" ] && { echo "PLANTUML_JAR=$PLANTUML_JAR not found"; exit 1; }
  command -v java >/dev/null || { echo "Java is required (brew install openjdk, or any JDK 17+)"; exit 1; }
  echo "lib/plantuml.jar missing, downloading from the PlantUML GitHub releases..."
  mkdir -p lib && curl -fSL -o "$JAR" https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar || { rm -f "$JAR"; exit 1; }
fi
python3 -I check_i18n.py || exit 1
python3 -I bundle.py || exit 1
NAMES=("$@"); [ ${#NAMES[@]} -eq 0 ] && NAMES=(plantuml_export)
for name in "${NAMES[@]}"; do
  for pair in "en:" "zh-tw:-DLANG_ZH_TW=1" "ja:-DLANG_JA=1" "ko:-DLANG_KO=1"; do
    lang=${pair%%:*}; define=${pair#*:}
    mkdir -p "out/$lang"
    for fmt in svg png; do
      # shellcheck disable=SC2086
      java -DPLANTUML_LIMIT_SIZE=16384 -Djava.awt.headless=true -jar "$JAR" $define -t$fmt -o "$PWD/out/$lang" "$name.puml" || exit 1
    done
    echo "rendered out/$lang/$name.{svg,png}"
  done
done
