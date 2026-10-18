# CLAUDE.md

## Goal

This kit has two goals:

1. **Education: the decoder-only Transformer architecture.** Explain one forward pass (generation) and one training step of a GPT / Llama-style decoder-only model, with a concrete toy example, as PlantUML activity diagrams in four languages (English, 繁體中文, 日本語, 한국어). Accuracy matters more than brevity or style.
2. **A static GitHub Pages site with the UML view.** The diagrams are published as a static site that renders the PlantUML live in the browser and lets the reader switch language. No server, no Java, no pre-rendered SVG/PNG as the deliverable.

## Layout

- `transformer-study/`: the content. Diagram sources, `i18n/*.json`, generated `bundle/*.puml`. Its own `.claude/CLAUDE.md` has the diagram rules (multi-language checklist, accuracy checklist); read it before touching any diagram.
- `plant-uml-editor/`: the viewer/editor. Today a local tool (Node server + Java PlantUML). See its own `.claude/CLAUDE.md`.

## Static site (GitHub Pages): built 2026-10-17

- `site/` is the whole deliverable. `site/index.html` is the read-only viewer (diagram picker, language dropdown, zoom, SVG export; `?lang=ja&d=plantuml_training` in the URL). `site/vendor/` holds the pinned `@plantuml/core` 1.2026.6 build (MIT, TeaVM, with `viz-global.js`). `site/bundle/` is a copy of `transformer-study/bundle/`.
- After any diagram or translation change: `./site/sync.sh` (checks keys, rebuilds the bundles, copies them into `site/bundle/`). `.github/workflows/pages.yml` runs the same script and deploys `site/` on push to `main` (needs Pages source set to "GitHub Actions" in the repo settings).
- The page rewrites the bundle's `!$lang = "xx"` line from the dropdown; it never reads `i18n/`.
- Browser-build limit: images taller than 4096 px are refused. `plantuml_export` was split (2026-10-18) into an overview (`plantuml_export`, the layer loop shows one "Multi-Head Attention" and one "SwiGLU FFN" action each), `plantuml_attention` and `plantuml_ffn`; all 16 diagram/language combinations render at about 2000 px or less, so there is plenty of margin. `bundle.py` also generates `bundle/plantuml_full.puml` (the overview with the attention and FFN bodies stitched back in, one continuous diagram for studying; it is the only generation diagram the viewer lists; the overview and one-layer diagrams are authoring sources, not in the `DIAGRAMS` list). That one is back at about 3800-4060 px tall in the browser (zh-tw is at the limit and relies on the smaller-note retry), so keep adding detail to the sub-diagrams, not by growing the full view without checking zh-tw. The viewer still retries with a smaller note size if it gets "too large".
- Tested in a real browser: both diagrams render in en, zh-tw, ja, ko. Not yet done: a visual comparison against the jar output (the browser build emits more `<text>` elements, 275 vs 238 for generation, so the old text-count golden check does not apply).

## Editor: two modes

The local editor (`plant-uml-editor/`) stays as the authoring tool. The published page (`site/index.html`) is a separate **read-only viewer**: no editing UI, and it never calls `/render`, `/files` or `/config`.

| Control | Local (dev) | GitHub Pages |
|---|---|---|
| Language dropdown | yes | **yes** |
| Diagram picker (export / training) | yes | yes, a fixed list of the bundled diagrams |
| Zoom, SVG export | yes | optional, keep if cheap |
| Source textarea / view source | yes | **removed** |
| Open file, Save, saved-files list | yes | **removed** |
| Folder dropdown, re-render button | yes | **removed** |
| PNG export | server-rendered | only if done in the browser (canvas); otherwise removed |

Implementation rules:

- Choose the mode explicitly (for example a build flag, a separate `viewer.html`, or `?mode=viewer`), not by hiding elements with CSS. The published page must not ship the editing UI or call `/render`, `/files`, `/config`.
- Keep the local editor working for authoring; the viewer is an addition, not a rewrite.
- No npm dependencies or build step for the page itself if avoidable. A GitHub Actions workflow may run `transformer-study/bundle.py` and copy `bundle/` plus the two PlantUML files into the deploy folder.
- Language choice is remembered in `localStorage` (wrap in try/catch) and may also be in the URL (`?lang=ja`) so links can be shared.

## Working rules

- Diagram content changes follow `transformer-study/.claude/CLAUDE.md` (keys in `i18n/*.json`, all four languages, run `./render.sh`, commit regenerated `bundle/`).
- Keep every `.claude/CLAUDE.md` under 200 lines. When one grows past that, move a self-contained topic (for example Known Issues, Rendering, the live-editor notes) into `.claude/rules/<topic>.md` in the same folder.
- Never publish anything that sends diagram text to an external service; the browser build renders locally.
- Ask before pushing or changing anything outward-facing (repo settings, workflow triggers). Commits end with the `Co-Authored-By` line from the session attribution.

## Repo and deployment

- Repo: https://github.com/chronicqazxc/transformer-architecture-uml (branch `main`). The kit folder is the repo root. `origin` uses SSH (`git@github.com:chronicqazxc/transformer-architecture-uml.git`) because HTTPS has no credentials on this machine.
- Live site: https://chronicqazxc.github.io/transformer-architecture-uml/ . Pages source is set to "GitHub Actions" (not "Deploy from a branch"). A push to `main` redeploys; first deploy verified 2026-10-17 (all 8 diagram/language combinations render on the live URL).
- `.gitignore` leaves out `lib/plantuml.jar`, `node_modules/`, `.backup/`, `.DS_Store`, `.playwright-mcp/`. `transformer-study/out/` is committed but stale (rendered at the old font sizes) and the site does not use it; regenerate with `./render.sh plantuml_export plantuml_training` or delete it.
- Checking a deploy: the GitHub MCP tools can list runs and read job logs (`actions_list`, `get_job_logs`). Triggering a run (`actions_run_trigger`) needs the fine-grained token to have **Actions: Read and write** on this repo; the user added it. Large file pushes go through `git`, not the MCP file tools.
