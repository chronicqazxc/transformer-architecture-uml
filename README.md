# Decoder-only Transformer, as UML

**English · 繁體中文 · 日本語 · 한국어**

One forward pass (generation) and one training step of a GPT / Llama-style decoder-only Transformer,
walked through with a concrete toy example (`["cat", "on", "desk"]`) as PlantUML activity diagrams.

**Live site: https://chronicqazxc.github.io/transformer-architecture-uml/**

## Why this exists

The original Transformer paper, [*Attention Is All You Need*](https://arxiv.org/pdf/1706.03762), was hard
for me to read. So I taught myself the architecture with AI, building this diagram step by step: asking
questions, checking every shape and number, and fixing what was wrong until it was right. This repo is the
result, shared in case it helps someone else who finds the paper difficult too. It has two goals:

1. **Accuracy first.** Every number in the toy example (scores, scaling, causal mask, softmax,
   attention map, `Z = Attention_Map × V`) is recomputed and kept consistent end to end. The diagrams follow
   modern decoder-only conventions: pre-norm RMSNorm, RoPE on Q/K, SwiGLU FFN, KV cache, and they call
   out where these differ from the original 2017 "Attention Is All You Need" design.
2. **Learn it in your own language.** Understanding an architecture is hard enough without also
   translating the vocabulary. Every label, note and legend is available in four languages.

The diagrams target modern decoder-only models (GPT / Llama style) rather than the paper's original
encoder-decoder design, and they mark each place where the two differ.

## Internationalization (i18n)

| Language | Code |
|---|---|
| English (source of truth, fallback) | `en` |
| 繁體中文 | `zh-tw` |
| 日本語 | `ja` |
| 한국어 | `ko` |

- **One diagram source, four languages.** Each diagram is written once. All visible text lives in
  `transformer-study/i18n/<lang>.json`, so the structure, colors and numbers cannot drift between languages.
- **Switch language in the viewer** with the dropdown. Your choice is remembered, and you can share a link
  such as `?lang=ja&d=plantuml_training`.
- **Enforced parity.** `check_i18n.py` fails the build if any language is missing a key, and the deploy
  workflow runs it, so a half-translated diagram cannot be published.
- **Numbers are translated too.** A numeric fix is checked in every language's notes, because values and
  explanations are repeated there.

Want to add a language? Copy `en.json` to a new file, translate the values, and register the code (see
[Contributing a translation](#contributing-a-translation)).

## The diagrams

| Diagram | Covers |
|---|---|
| `plantuml_export` (generation) | Tokens → embeddings → N layers (RMSNorm, attention with RoPE and causal mask, residual, SwiGLU FFN) → LM head → sampling, prefill vs decode, KV cache |
| `plantuml_training` | Batch with shifted targets, forward pass, cross-entropy loss, backward pass, AdamW, evaluation |

Colors mean the same thing in both: input = light blue, RMSNorm = yellow, attention = blue,
residual = orange, FFN = green, LM head = purple. Training adds loss = red, gradients = pink,
optimizer = gray, evaluation = green.

## Repository layout

```
site/                 The whole GitHub Pages deliverable (static, read-only viewer)
  index.html          Diagram picker, language dropdown, zoom, SVG export
  vendor/             Pinned @plantuml/core build: PlantUML renders in your browser
  bundle/             Generated, self-contained diagrams (copied from transformer-study/bundle)
  sync.sh             Check translations, rebuild bundles, copy into site/bundle
transformer-study/    The content
  plantuml_*.puml     Diagram sources
  i18n/*.json         All visible text, one file per language
  bundle/             Generated, do not edit by hand
plant-uml-editor/     Local authoring tool (Node server + Java PlantUML)
```

## How the site works

The page renders PlantUML **locally in your browser** (no server, no Java, and no diagram text is sent to
any external service). It loads a bundled `.puml`, rewrites its `!$lang = "xx"` line from the dropdown, and
draws the SVG.

## Working on it

**After any diagram or translation change**, from the repo root:

    ./site/sync.sh

This checks that all languages have the same keys, rebuilds `bundle/`, and copies it into `site/bundle/`.
Pushing to `main` runs the same script in GitHub Actions and deploys `site/` to GitHub Pages.

**Preview the site locally:**

    cd site && python3 -m http.server 8000      # then open http://localhost:8000

**Author with the local editor** (live preview, language dropdown, PNG/SVG export). Needs Node 18+ and Java:

    cd plant-uml-editor
    PUML_BASE_DIRS=../transformer-study npm start     # http://localhost:8765

**Render with the PlantUML jar** (needs Java 17+ and python3):

    cd transformer-study && ./render.sh plantuml_export plantuml_training

### Contributing a translation

1. Copy `transformer-study/i18n/en.json` to `<code>.json` and translate every value (keep the keys).
2. Add the language code where the others are listed: `LANGS` in `transformer-study/bundle.py`, the language list in `transformer-study/check_i18n.py`, and the dropdown, `LANGS`, `TITLE` and diagram names in `site/index.html`.
3. Run `./site/sync.sh`; it fails if any key is missing.

For corrections to the diagrams themselves: say what is wrong and why, and include the recomputed numbers.
Accuracy matters more than brevity or style.

## Known limits

- The browser build refuses images taller than 4096 px. The viewer retries with smaller note text, which
  the Traditional Chinese generation diagram needs. Splitting that diagram into attention and FFN
  sub-diagrams is the planned fix before adding more notes.
- PNG export is not available on the published site (SVG export is).

## License

PlantUML core (`site/vendor/`) is MIT-licensed. No license has been chosen yet for the diagrams and
text; add one before inviting contributions.
