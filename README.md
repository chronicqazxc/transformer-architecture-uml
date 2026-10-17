# Decoder-only Transformer, as UML

**English · 繁體中文 · 日本語 · 한국어**

**Live site: https://chronicqazxc.github.io/transformer-architecture-uml/**

The original Transformer paper, [*Attention Is All You Need*](https://arxiv.org/pdf/1706.03762), was difficult for me to read.
So I taught myself the architecture with AI. I built this diagram step by step.
I asked questions, checked every shape and number, and corrected each error until the diagram was right.
This repo is the result. I share it for others who also find the paper difficult.

- The diagrams show one generation pass and one training step of a GPT / Llama-style model.
- The diagrams use a small example with real numbers.
- Each diagram has four languages: English, 繁體中文, 日本語, and 한국어.
- Use the language menu on the site to change the language.

## Change a diagram

1. Edit the text in `transformer-study/i18n/*.json`. Change all four languages.
2. Run `./site/sync.sh`.
3. Push to `main`. GitHub Actions deploys the site.

## License

[MIT](LICENSE)
