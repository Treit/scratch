# qexify

Render a Markdown spec as a QEX-magazine-styled, single-file HTML article.

Inspired by the layout of QEX (the ARRL technical journal): serif body in a
narrow measure, sans masthead and headings, banded tables, auto-numbered H2
sections, and a print stylesheet that drops the screen frame and uses the full
page. An optional drop cap on the lead paragraph is available via `--drop-cap`.

## Install

```powershell
uv pip install markdown pygments
```

`pygments` is optional. If absent, qexify still works but code blocks render
without syntax colors.

## Usage

```powershell
python qexify.py path\to\spec.md
python qexify.py path\to\spec.md -o path\to\spec.html
python qexify.py spec.md --no-mermaid --masthead "DESIGN SPEC" --issue "MAY 2026"
python qexify.py spec.md --drop-cap   # opt into the QEX-style drop cap
python qexify.py README.md           # masthead auto-inferred from content
```

The script is self-contained and emits a single HTML file with no external CSS.
By default, fenced ```mermaid``` code blocks render at view time via Mermaid.js
loaded from a CDN. Pass `--no-mermaid` to keep them as plain code blocks if you
need the output to be fully offline.

## Front matter

YAML front matter at the top of the Markdown source is parsed and rendered as a
title block between the masthead and the body. Recognized keys:

| Key | Rendered as |
|-----|-------------|
| `title` | Article title (22pt Helvetica) |
| `description` | Italic deck/standfirst paragraph |
| `author` | Byline (joined with `&middot;`) |
| `ms.date` or `date` | Byline |
| `status` | Byline (e.g., `draft`) |
| `masthead` or `kind` | Left-hand masthead label (overrides inference) |

Quoted and unquoted scalar values are both accepted. Only top-level scalars are
recognized; this is intentionally not a full YAML parser.

## Behavior notes

- The first H1 in the body is stripped because `title` already provides one.
- H2 sections are auto-numbered via CSS counters.
- The lead paragraph can optionally carry a CSS drop cap. Pass `--drop-cap`
  to enable it; off by default. When enabled, qexify tags the first paragraph
  after the first `<h2>` with `class="lead"` so pseudo-front-matter prose
  above the first section does not steal the cap. Documents with no `<h2>`
  fall back to the very first paragraph.
- Manual section numbers on `## H2` headings (e.g., `## 1. Overview`) are
  stripped before rendering so the auto-numbering counter does not produce
  doubled labels like "1. 1. Overview". H3+ are left alone.
- The masthead label (top-left) defaults to a context-aware inference:
  front-matter `masthead` / `kind` -> keyword scan over the H1, top of the
  body, and filename ("benchmark", "changelog", "design spec", "rfc",
  "post-mortem", "guide", etc.) -> `"ARTICLE"` fallback. Override with
  `--masthead "WHATEVER"`.
- Tables are wrapped in `<div class="table-wrap">`. Wide tables (8+ columns)
  get a `wide` class. **If any wide table is present, the whole document
  flips to a "wide layout"**: the article body widens to 10.5 inches on
  screen (so the table fits with no scrollbar) and prints in **landscape**.
  If no wide tables are present the layout stays portrait at the normal 7-inch
  measure. Documents with a single wide table inside an otherwise narrow doc
  still scroll horizontally on screen as a fallback.
- Inline SVG, raw HTML, tables, fenced code, and `attr_list` syntax all pass
  through.
- Fenced code blocks get **syntax highlighting** via Pygments + the
  `codehilite` Markdown extension. Specify the language in the fence
  (e.g., ```` ```python ````, ```` ```csharp ````, ```` ```bash ````). Light
  mode uses the `friendly` Pygments style; dark mode uses `monokai`. Languages
  without a fence tag are not auto-detected (the `guess_lang` option is off
  to avoid false positives) and render as plain code. The block's background
  stays the same cream paper color from the article theme - only the token
  colors change.
- A print stylesheet sets `@page` margins to 0.5"/0.55" and removes the screen
  frame so the article uses the full printable area.
- A small `Dark` / `Light` toggle button in the top-right corner switches the
  page palette. Light is the default; the choice persists per-origin via
  `localStorage`. The toggle is hidden in print, and printing always uses the
  light palette regardless of the on-screen state.
