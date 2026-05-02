# qexify

Render a Markdown spec as a QEX-magazine-styled, single-file HTML article.

Inspired by the layout of QEX (the ARRL technical journal): serif body in a
narrow measure, sans masthead and headings, drop cap on the lead paragraph,
banded tables, auto-numbered H2 sections, and a print stylesheet that drops
the screen frame and uses the full page.

## Install

```powershell
uv pip install markdown
```

## Usage

```powershell
python qexify.py path\to\spec.md
python qexify.py path\to\spec.md -o path\to\spec.html
python qexify.py spec.md --no-mermaid --masthead "DESIGN SPEC" --issue "MAY 2026"
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

Quoted and unquoted scalar values are both accepted. Only top-level scalars are
recognized; this is intentionally not a full YAML parser.

## Behavior notes

- The first H1 in the body is stripped because `title` already provides one.
- H2 sections are auto-numbered via CSS counters.
- The lead paragraph gets a CSS drop cap. The selector targets
  `.body-content > p:first-of-type`, so the title block does not interfere.
- Inline SVG, raw HTML, tables, fenced code, and `attr_list` syntax all pass
  through.
- A print stylesheet sets `@page` margins to 0.5"/0.55" and removes the screen
  frame so the article uses the full printable area.
- A small `Dark` / `Light` toggle button in the top-right corner switches the
  page palette. Light is the default; the choice persists per-origin via
  `localStorage`. The toggle is hidden in print, and printing always uses the
  light palette regardless of the on-screen state.
