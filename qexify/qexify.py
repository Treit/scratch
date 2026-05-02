"""
qexify - render a Markdown spec as a QEX-magazine-styled, single-file HTML article.

Inspired by ARRL QEX layout: serif body, sans masthead and headings, drop cap on
the lead paragraph, banded tables, auto-numbered H2 sections, narrow measure for
print, and a print stylesheet that drops the screen frame and uses the full page.

Inputs:
  - A Markdown file. YAML front matter with `title`, `description`, `author`,
    and `ms.date` is parsed and rendered as the doctitle, deck, and byline.
  - Optional `--mermaid` flag: any fenced ```mermaid ... ``` block is rendered
    via Mermaid.js (CDN) at view time. By default mermaid blocks are kept as
    plain code blocks so the output is fully offline.
  - Optional `--masthead` to override the masthead text (default: "DESIGN SPEC").
  - Optional `--issue` to override the right-hand masthead label
    (default: today's month and year).

Output: a single self-contained HTML file (no external CSS, no JS unless
`--mermaid` is set).

Usage:
  python qexify.py path/to/spec.md
  python qexify.py path/to/spec.md -o path/to/spec.html
  python qexify.py spec.md --mermaid --masthead "DESIGN SPEC" --issue "MAY 2026"

Dependencies: `markdown` (pip install markdown).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import html as _html
import re
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.stderr.write(
        "qexify: the 'markdown' package is required. Install with:\n"
        "  uv pip install markdown\n"
        "  (or)  pip install markdown\n"
    )
    sys.exit(2)


_FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_QUOTED_RE = re.compile(r"^\s*[\"'](.*)[\"']\s*$")
_H1_RE = re.compile(r"^# (.+?)$\n?", re.MULTILINE)
_MERMAID_BLOCK_RE = re.compile(r"```mermaid\n(.*?)\n```", re.DOTALL)


def _parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    """Strip and parse a YAML-ish front matter block.

    Only top-level scalar `key: value` lines are recognized; this is intentionally
    not a full YAML parser. Returns (metadata, body_without_front_matter).
    """
    m = _FRONT_MATTER_RE.match(text)
    if not m:
        return {}, text
    block = m.group(1)
    body = text[m.end():]
    meta: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        q = _QUOTED_RE.match(value)
        if q:
            value = q.group(1)
        if key:
            meta[key] = value
    return meta, body


def _extract_first_h1(body: str) -> tuple[str | None, str]:
    """Return (title or None, body with the first H1 removed)."""
    m = _H1_RE.search(body)
    if not m:
        return None, body
    title = m.group(1).strip()
    body = body[: m.start()] + body[m.end():]
    return title, body


def _replace_mermaid_blocks(body: str, enable_mermaid: bool) -> tuple[str, bool]:
    """Convert mermaid fenced blocks. Returns (body, used_mermaid)."""
    if enable_mermaid:
        used = {"v": False}

        def _sub(match: re.Match) -> str:
            used["v"] = True
            diagram = _html.escape(match.group(1))
            return f'<div class="mermaid">{diagram}</div>'

        body = _MERMAID_BLOCK_RE.sub(_sub, body)
        return body, used["v"]
    return body, False


_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{html_title}</title>
<style>
  html {{ background: #ece9df; }}
  body {{
    max-width: 7.0in;
    margin: 0.6in auto;
    padding: 0.6in 0.7in;
    background: #fff;
    color: #111;
    font-family: "Charter", "Iowan Old Style", "Georgia", serif;
    font-size: 10.5pt;
    line-height: 1.42;
    hyphens: auto;
    text-align: justify;
    box-shadow: 0 1px 3px rgba(0,0,0,0.18);
  }}
  @page {{ margin: 0.5in 0.55in; }}
  @media print {{
    html {{ background: #fff; }}
    body {{
      max-width: none;
      margin: 0;
      padding: 0;
      box-shadow: none;
      font-size: 10.5pt;
    }}
    a {{ color: #000; }}
    h2, h3, table, pre, figure {{ page-break-inside: avoid; }}
  }}
  h1, h2, h3, h4, h5, h6, .masthead, .caption, .figlabel, .byline, .doctitle {{
    font-family: "Helvetica Neue", "Helvetica", "Arial", sans-serif;
  }}
  .masthead {{
    border-top: 3px solid #000;
    border-bottom: 1px solid #000;
    padding: 6pt 0 4pt 0;
    margin-bottom: 22pt;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    font-size: 9pt;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    font-weight: 700;
  }}
  .masthead .issue {{ font-weight: 400; letter-spacing: 0.10em; }}
  .doctitle {{
    font-size: 22pt;
    font-weight: 700;
    line-height: 1.18;
    letter-spacing: -0.005em;
    margin: 0 0 8pt 0;
    text-align: left;
  }}
  .deck {{
    font-family: "Charter", "Iowan Old Style", "Georgia", serif;
    font-style: italic;
    font-size: 11.5pt;
    line-height: 1.38;
    margin: 0 0 14pt 0;
    color: #222;
    text-align: left;
    hyphens: none;
  }}
  .byline {{
    font-size: 8.5pt;
    text-transform: uppercase;
    letter-spacing: 0.10em;
    border-bottom: 1px solid #000;
    padding-bottom: 4pt;
    margin: 0 0 18pt 0;
    color: #333;
  }}
  body {{ counter-reset: h2num; }}
  h2 {{
    font-size: 11pt;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    border-bottom: 1px solid #000;
    padding-bottom: 2pt;
    margin: 22pt 0 8pt 0;
    counter-increment: h2num;
  }}
  h2::before {{
    content: counter(h2num) ".\\00a0\\00a0";
  }}
  h3 {{
    font-size: 10pt;
    font-weight: 700;
    margin: 14pt 0 4pt 0;
    text-transform: none;
    letter-spacing: 0;
  }}
  h4 {{
    font-size: 10pt;
    font-style: italic;
    font-weight: 400;
    margin: 12pt 0 2pt 0;
  }}
  p {{ margin: 0 0 7pt 0; }}
  .body-content > p:first-of-type::first-letter {{
    initial-letter: 3 2;
    -webkit-initial-letter: 3 2;
    font-weight: 700;
    margin-right: 4pt;
    font-family: "Helvetica Neue", "Helvetica", "Arial", sans-serif;
  }}
  ul, ol {{ margin: 4pt 0 8pt 0; padding-left: 18pt; }}
  li {{ margin: 1pt 0; }}
  table {{
    border-collapse: collapse;
    width: 100%;
    margin: 8pt 0 12pt 0;
    font-size: 9.5pt;
  }}
  th, td {{
    border-top: 1px solid #000;
    border-bottom: 1px solid #000;
    padding: 4pt 6pt;
    text-align: left;
    vertical-align: top;
  }}
  th {{
    background: #f5f2e8;
    border-top: 2px solid #000;
    border-bottom: 1px solid #000;
    font-family: "Helvetica Neue", "Helvetica", "Arial", sans-serif;
    font-size: 9pt;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }}
  tr:nth-child(even) td {{ background: #fafaf6; }}
  code {{
    font-family: "SFMono-Regular", "Consolas", monospace;
    font-size: 90%;
    background: #f5f2e8;
    padding: 0 2pt;
    border-radius: 2px;
  }}
  pre {{
    font-family: "SFMono-Regular", "Consolas", monospace;
    font-size: 8.5pt;
    line-height: 1.35;
    background: #f5f2e8;
    border-left: 2px solid #000;
    padding: 6pt 8pt;
    overflow-x: auto;
    margin: 8pt 0 12pt 0;
  }}
  pre code {{ background: none; padding: 0; }}
  a {{ color: #6b1f0a; text-decoration: none; border-bottom: 1px dotted #6b1f0a; }}
  a:hover {{ border-bottom-style: solid; }}
  hr {{ border: 0; border-top: 1px solid #000; margin: 18pt 0; }}
  blockquote {{
    border-left: 2px solid #b04a2f;
    margin: 8pt 0;
    padding: 2pt 0 2pt 12pt;
    color: #333;
    font-style: italic;
  }}
  figure {{
    margin: 10pt 0 14pt 0;
    border-top: 1px solid #000;
    border-bottom: 1px solid #000;
    padding: 10pt 0;
    background: #fff;
  }}
  figcaption {{
    font-family: "Helvetica Neue", "Helvetica", "Arial", sans-serif;
    font-size: 9pt;
    text-align: center;
    margin-top: 6pt;
    color: #333;
  }}
  .mermaid {{ text-align: center; }}
</style>
{mermaid_script}</head>
<body>
<div class="masthead">
  <span class="title">{masthead}</span>
  <span class="issue">{issue}</span>
</div>
{title_block}
<div class="body-content">
{body_html}
</div>
</body>
</html>
"""

_MERMAID_SCRIPT = (
    '<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js">'
    "</script>\n"
    "<script>mermaid.initialize({startOnLoad:true,theme:'neutral'});</script>\n"
)


def render(
    md_text: str,
    *,
    masthead: str = "DESIGN SPEC",
    issue: str | None = None,
    enable_mermaid: bool = False,
) -> str:
    meta, body = _parse_front_matter(md_text)
    h1_title, body = _extract_first_h1(body)
    body, used_mermaid = _replace_mermaid_blocks(body, enable_mermaid)

    body_html = markdown.markdown(
        body,
        extensions=["tables", "fenced_code", "sane_lists", "attr_list"],
        output_format="html5",
    )

    title = meta.get("title", "").strip() or h1_title or "Document"
    description = meta.get("description", "").strip()
    author = meta.get("author", "").strip()
    date = meta.get("ms.date", "").strip() or meta.get("date", "").strip()
    status = meta.get("status", "").strip()

    title_parts: list[str] = [
        f'<div class="doctitle">{_html.escape(title)}</div>'
    ]
    if description:
        title_parts.append(f'<p class="deck">{_html.escape(description)}</p>')
    byline_bits = [b for b in (author, date, status) if b]
    if byline_bits:
        byline = " &middot; ".join(_html.escape(b) for b in byline_bits)
        title_parts.append(f'<div class="byline">{byline}</div>')
    title_block = "\n".join(title_parts)

    if issue is None:
        issue = _dt.date.today().strftime("%B %Y").upper()

    return _TEMPLATE.format(
        html_title=_html.escape(title),
        masthead=_html.escape(masthead),
        issue=_html.escape(issue),
        title_block=title_block,
        body_html=body_html,
        mermaid_script=_MERMAID_SCRIPT if used_mermaid else "",
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="qexify",
        description="Render a Markdown spec as a QEX-magazine-styled HTML article.",
    )
    p.add_argument("input", type=Path, help="Path to the Markdown source file.")
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output HTML path. Defaults to the input with a .html extension.",
    )
    p.add_argument(
        "--masthead",
        default="DESIGN SPEC",
        help="Left-hand masthead label (default: DESIGN SPEC).",
    )
    p.add_argument(
        "--issue",
        default=None,
        help="Right-hand masthead label (default: current month and year).",
    )
    p.add_argument(
        "--mermaid",
        action="store_true",
        help="Render fenced ```mermaid blocks via Mermaid.js (adds a CDN script tag).",
    )
    args = p.parse_args(argv)

    src: Path = args.input
    if not src.exists():
        sys.stderr.write(f"qexify: input not found: {src}\n")
        return 1

    out: Path = args.output or src.with_suffix(".html")
    md_text = src.read_text(encoding="utf-8")
    html_out = render(
        md_text,
        masthead=args.masthead,
        issue=args.issue,
        enable_mermaid=args.mermaid,
    )
    out.write_text(html_out, encoding="utf-8")
    sys.stdout.write(f"Wrote {out} ({len(html_out):,} chars)\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
