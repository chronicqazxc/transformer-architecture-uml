# transformer-study

Decoder-only (Llama-style) Transformer, drawn as PlantUML activity diagrams in four languages
(English, 繁體中文, 日本語, 한국어) from one source each.

- `plantuml_export.puml`: generation / inference flow. `plantuml_training.puml`: training flow.
- `i18n/*.json`: all visible text (en = source of truth and fallback).
- `bundle/*.puml`: generated, self-contained copies. Open one in any PlantUML editor; change the
  language by editing the `!$lang = "en"` line near the top. Do not edit by hand.
- `.claude/CLAUDE.md`: working rules for Claude Code (read this before changing anything).

## Run on a new PC
Needs Java 17+ (and python3). Then, from this folder:

    ./render.sh plantuml_export plantuml_training

It downloads `lib/plantuml.jar` on first run, checks the translation keys, rebuilds `bundle/`
and renders `out/<lang>/<name>.svg` and `.png`.

## Live preview with a language dropdown (plant-uml-editor, sibling folder)
Needs Node 18+ and Java. From the folder that contains both `transformer-study/` and `plant-uml-editor/`:

    cd plant-uml-editor
    PUML_BASE_DIRS=../transformer-study npm start        # then open http://localhost:8765

It downloads its own `lib/plantuml.jar` on first run. In the page pick the language, pick the
`transformer-study` folder in the folder dropdown, and open `plantuml_export.puml` or
`plantuml_training.puml` ("Open file..."). SVG/PNG export uses the selected language.
To preview a `bundle/*.puml` instead, no folder setting is needed (the dropdown edits its `!$lang` line).
