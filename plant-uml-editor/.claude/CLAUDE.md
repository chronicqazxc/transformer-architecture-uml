# PlantUML Editor

## Goal
A local PlantUML edit-and-preview tool, replacing the online editors (which are awkward to use). Runs entirely on this machine; no diagram text is sent to any external service.

## Run
Needs Node 18+ and Java. `npm start` (or `node server.js`; downloads `lib/plantuml.jar` on first run if missing) → http://localhost:8765 (override with `PORT=...`).

For multi-language diagrams that read `i18n/*.json` (Wayne's `transformer-study`), also set the folder allowlist, paths separated by `:`:
`PUML_BASE_DIRS=../transformer-study npm start`

## Architecture
- `server.js` — zero-dependency Node server, bound to 127.0.0.1 only.
  - `POST /render?format=svg|png&lang=en|zh-tw|ja|ko&dir=<id>` — body is PlantUML source; pipes it through `java -jar lib/plantuml.jar -pipe`. `lang` maps to a `-DLANG_ZH_TW=1` / `-DLANG_JA=1` / `-DLANG_KO=1` flag (`en` = no flag); diagrams opt in with `!ifdef`, so plain diagrams are unaffected. `dir` selects the java working directory by id (default `default` = the editor folder); unknown `lang` or `dir` → HTTP 400.
  - `GET /config` — the selectable folders, `{dirs:[{id,name}]}`.
  - Always passes `-DPLANTUML_LIMIT_SIZE=16384` (a JVM property): PlantUML otherwise silently cuts images taller than 4096 px, which drops the legend of tall diagrams.
  - Working directory: relative `%load_json("i18n/en.json")` / `!include` paths resolve against java's cwd, not the diagram's location, so the cwd must be the folder that holds `i18n/`. Folders come ONLY from the server-side `PUML_BASE_DIRS` allowlist (ids = folder names); the request never supplies a path.
  - `GET /files`, `GET|PUT /files/<name>.puml` — save/load in `diagrams/` (names validated).
  - Adds `-Playout=smetana` when Graphviz `dot` is not installed (currently the case); `brew install graphviz` gives the standard layout.
- `public/index.html` — single-file UI (also: language dropdown and project-folder dropdown, both remembered in localStorage; changing either re-renders; exported files get a `.<lang>` suffix, e.g. `plantuml_export.ja.svg`): textarea editor (left), live SVG preview (right, debounced 300 ms), zoom, SVG/PNG export, Open file… / Save write directly to a local `.puml` via the File System Access API (Chrome/Edge; other browsers fall back to `diagrams/`), save/open from `diagrams/`, Cmd/Ctrl+S, localStorage autosave.
- `lib/plantuml.jar` — downloaded from the PlantUML GitHub releases (latest); not hand-edited. Requires Java (17 installed).
- `diagrams/` — user's saved `.puml` files.

## Multi-language diagrams (how the dropdown works)
- Two kinds of diagram are supported. (1) Source diagrams (`plantuml_export.puml`) read `i18n/*.json`; they need the right folder selected and use the `-D` language flag. (2) Bundled diagrams (`bundle/*.puml` from transformer-study, generated, self-contained) have a line `!$lang = "en"` under the marker `CHANGE THE LANGUAGE HERE`; the page rewrites that line from the dropdown before sending, so they work in the default folder with no i18n files.
- `%getenv` is blocked by PlantUML's default security profile, so the language travels as a `-D` define, never as an environment variable.
- A source diagram rendered in the wrong folder shows its own message "i18n/en.json not found ...", not a blank image. Render errors from PlantUML are shown in the preview.
- Test without a browser: start with `PORT=8799 PUML_BASE_DIRS=<folder> node server.js`, then `curl -X POST --data-binary @file.puml 'http://127.0.0.1:8799/render?format=svg&lang=ja&dir=<id>'`.
- Packaging for another PC: zip the folder WITHOUT `lib/` (jar), `node_modules/` and `.backup/`; the jar downloads on first start.

## Conventions
- Keep it dependency-free (no npm packages, no build step) unless there is a strong reason.
- Keep the server local-only; never bind to 0.0.0.0.
- Never accept a filesystem path from a request (working folders come only from `PUML_BASE_DIRS`); validate `lang` against the fixed list.

## Ideas / not done yet
- Syntax highlighting / line numbers (e.g. CodeMirror), render-error line markers.
- Pan/drag in preview, dark mode, multiple tabs.
