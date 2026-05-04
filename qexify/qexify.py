"""
qexify - render a Markdown spec as a QEX-magazine-styled, single-file HTML article.

Inspired by ARRL QEX layout: serif body, sans masthead and headings, drop cap on
the lead paragraph, banded tables, auto-numbered H2 sections, narrow measure for
print, and a print stylesheet that drops the screen frame and uses the full page.

Inputs:
  - A Markdown file. YAML front matter with `title`, `description`, `author`,
    and `ms.date` is parsed and rendered as the doctitle, deck, and byline.
  - Optional `--no-mermaid` flag: by default, fenced ```mermaid ... ``` blocks
    are rendered via Mermaid.js (CDN) at view time. Pass `--no-mermaid` to
    keep them as plain code blocks for fully offline output.
  - Optional `--masthead` to override the left-hand masthead label. If not
    given, qexify infers a label from front-matter (`masthead` or `kind`),
    then by keyword-scanning the H1, top of the body, and filename
    ("benchmark" -> BENCHMARK, "changelog" -> CHANGELOG, "design spec" ->
    DESIGN SPEC, etc.). Falls back to "ARTICLE".
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
    from pygments.formatters import HtmlFormatter as _PygmentsHtmlFormatter
    _PYGMENTS_AVAILABLE = True
except ImportError:
    _PYGMENTS_AVAILABLE = False

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
_H2_MANUAL_NUM_RE = re.compile(r"^(##[ \t]+)\d+(?:\.\d+)*\.?[ \t]+", re.MULTILINE)
_HTML_H2_RE = re.compile(r"<h2\b[^>]*>", re.IGNORECASE)
_HTML_P_OPEN_RE = re.compile(r"<p\b([^>]*)>", re.IGNORECASE)
_HTML_CLASS_ATTR_RE = re.compile(r'class\s*=\s*"([^"]*)"', re.IGNORECASE)
_HTML_TABLE_RE = re.compile(r"<table\b[^>]*>.*?</table>", re.IGNORECASE | re.DOTALL)
_HTML_FIRST_TR_RE = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.IGNORECASE | re.DOTALL)
_HTML_TH_TD_OPEN_RE = re.compile(r"<t[hd]\b", re.IGNORECASE)

_WIDE_TABLE_THRESHOLD = 8  # columns at or above this count are flagged "wide"

# Masthead inference rules. First match wins. Order: most specific first.
_MASTHEAD_RULES: tuple[tuple[str, str], ...] = (
    (r"\bpost[\s\-]?mortem\b", "POST-MORTEM"),
    (r"\bretrospective\b", "RETROSPECTIVE"),
    (r"\bbenchmarkdotnet\b", "BENCHMARK"),
    (r"\brelease[\s\-]+notes?\b", "RELEASE NOTES"),
    (r"\bchangelog\b", "CHANGELOG"),
    (r"\brfc[\s\-:]+\d+\b", "RFC"),
    (r"\bdesign[\s\-]+spec(ification)?s?\b", "DESIGN SPEC"),
    (r"\bdesign[\s\-]+doc(ument)?s?\b", "DESIGN DOC"),
    (r"\bspecification\b", "SPECIFICATION"),
    (r"\bproposal\b", "PROPOSAL"),
    (r"\btutorial\b", "TUTORIAL"),
    (r"\bhow[\s\-]?to\b", "HOW-TO"),
    (r"\brunbook\b", "RUNBOOK"),
    (r"\bplaybook\b", "PLAYBOOK"),
    (r"\bguide\b", "GUIDE"),
    (r"\bbenchmark\w*\b", "BENCHMARK"),
    (r"\b(readme)\b", "README"),
)
_MASTHEAD_PATTERNS = tuple(
    (re.compile(pattern, re.IGNORECASE), label) for pattern, label in _MASTHEAD_RULES
)


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


def _strip_h2_manual_numbers(body: str) -> str:
    """Remove leading manual section numbers from H2 lines.

    `## 1. Overview` becomes `## Overview` so CSS counters do not double-number.
    Leaves H3+ alone (manual subsection numbers are commonly desired).
    """
    return _H2_MANUAL_NUM_RE.sub(r"\1", body)


def _add_class(attrs: str, cls: str) -> str:
    m = _HTML_CLASS_ATTR_RE.search(attrs)
    if m:
        existing = m.group(1).split()
        if cls in existing:
            result = attrs
        else:
            new = " ".join(existing + [cls])
            result = attrs[: m.start()] + f'class="{new}"' + attrs[m.end():]
    else:
        result = f'{attrs} class="{cls}"' if attrs else f' class="{cls}"'
    if result and not result.startswith((" ", "\t")):
        result = " " + result
    return result


def _tag_lead_paragraph(html: str) -> str:
    """Add ``class="lead"`` to the paragraph that should carry the drop cap.

    Picks the first ``<p>`` that follows the first ``<h2>`` so pseudo-front-matter
    paragraphs above the first section do not steal the drop cap. Falls back to
    the first ``<p>`` overall when the document has no ``<h2>``.
    """
    h2 = _HTML_H2_RE.search(html)
    search_from = h2.end() if h2 else 0
    p = _HTML_P_OPEN_RE.search(html, search_from)
    if not p:
        return html
    new_attrs = _add_class(p.group(1), "lead")
    return html[: p.start()] + f"<p{new_attrs}>" + html[p.end():]


def _wrap_tables(html: str) -> tuple[str, bool]:
    """Wrap each ``<table>`` in a scrollable ``<div class="table-wrap">``.

    Tables with column count at or above ``_WIDE_TABLE_THRESHOLD`` also get a
    ``wide`` class. Returns ``(html, has_wide_table)`` so the caller can flip
    the whole document into a wider layout when any wide table is present.
    """
    has_wide = False

    def _wrap(match: re.Match) -> str:
        nonlocal has_wide
        table = match.group(0)
        first_tr = _HTML_FIRST_TR_RE.search(table)
        cols = (
            len(_HTML_TH_TD_OPEN_RE.findall(first_tr.group(1)))
            if first_tr
            else 0
        )
        is_wide = cols >= _WIDE_TABLE_THRESHOLD
        if is_wide:
            has_wide = True
        wide_cls = " wide" if is_wide else ""
        return f'<div class="table-wrap{wide_cls}">{table}</div>'

    return _HTML_TABLE_RE.sub(_wrap, html), has_wide


_PYGMENTS_LIGHT_STYLE = "friendly"
_PYGMENTS_DARK_STYLE = "monokai"


def _pygments_css() -> str:
    """Generate scoped Pygments stylesheets for light and dark themes.

    Returns an empty string when Pygments is unavailable. Light styles apply
    by default; dark styles are gated behind ``:root[data-theme="dark"]`` so
    the dark-mode toggle picks them up. The container ``background`` rule
    that Pygments emits is dropped so the article's existing ``--code-bg``
    flows through.
    """
    if not _PYGMENTS_AVAILABLE:
        return ""

    light = _PygmentsHtmlFormatter(style=_PYGMENTS_LIGHT_STYLE).get_style_defs(
        ".highlight"
    )
    dark = _PygmentsHtmlFormatter(style=_PYGMENTS_DARK_STYLE).get_style_defs(
        ':root[data-theme="dark"] .highlight'
    )
    bg_rule = re.compile(
        r"^[^{]*\.highlight\s*\{[^}]*\}",
        re.MULTILINE,
    )
    light = bg_rule.sub("", light, count=1)
    dark = bg_rule.sub("", dark, count=1)
    return (
        "  /* Pygments syntax highlighting (light) */\n"
        + light
        + "\n  /* Pygments syntax highlighting (dark) */\n"
        + dark
    )


def _infer_masthead(
    meta: dict[str, str],
    h1_title: str | None,
    body: str,
    source_path: Path | None,
) -> str:
    """Pick a masthead label without one being explicitly provided.

    Priority: front-matter ``masthead`` (or ``kind``) > keyword scan over the
    H1, top of body, filename, and parent directory > ``"ARTICLE"`` fallback.
    """
    explicit = (meta.get("masthead") or meta.get("kind") or "").strip()
    if explicit:
        return explicit.upper()

    haystack_parts: list[str] = []
    if h1_title:
        haystack_parts.append(h1_title)
    haystack_parts.append(body[:3000])
    if source_path is not None:
        haystack_parts.append(source_path.name)
        haystack_parts.append(source_path.parent.name)
    haystack = "\n".join(haystack_parts)

    for pattern, label in _MASTHEAD_PATTERNS:
        if pattern.search(haystack):
            return label
    return "ARTICLE"


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
  :root {{
    --bg-page: #ece9df;
    --bg-body: #fff;
    --fg: #111;
    --fg-muted: #333;
    --fg-dim: #222;
    --rule: #000;
    --accent: #6b1f0a;
    --accent-bar: #b04a2f;
    --code-bg: #f5f2e8;
    --table-stripe: #fafaf6;
    --shadow: 0 1px 3px rgba(0,0,0,0.18);
  }}
  :root[data-theme="dark"] {{
    --bg-page: #0e0d0b;
    --bg-body: #1a1916;
    --fg: #e8e4d8;
    --fg-muted: #c9c4b6;
    --fg-dim: #d4cfc0;
    --rule: #e8e4d8;
    --accent: #e89478;
    --accent-bar: #d6724f;
    --code-bg: #25231e;
    --table-stripe: #211f1b;
    --shadow: 0 1px 3px rgba(0,0,0,0.6);
  }}
  html {{ background: var(--bg-page); }}
  body {{
    max-width: 8.5in;
    margin: 0.6in auto;
    padding: 0.6in 0.85in;
    background: var(--bg-body);
    color: var(--fg);
    font-family: "Charter", "Iowan Old Style", "Georgia", serif;
    font-size: 10.5pt;
    line-height: 1.42;
    hyphens: auto;
    text-align: justify;
    box-shadow: var(--shadow);
  }}
  body.wide-layout {{ max-width: 12.0in; }}
  .theme-toggle {{
    position: fixed;
    top: 10px;
    right: 14px;
    z-index: 100;
    font-family: "Helvetica Neue", "Helvetica", "Arial", sans-serif;
    font-size: 8.5pt;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    background: var(--bg-body);
    color: var(--fg);
    border: 1px solid var(--rule);
    padding: 4pt 8pt;
    cursor: pointer;
    border-radius: 2px;
    opacity: 0.85;
  }}
  .theme-toggle:hover {{ opacity: 1; }}
  @page {{ margin: 0.5in 0.55in; }}
  @page wide {{ size: landscape; margin: 0.4in 0.5in; }}
  @media print {{
    :root {{
      --bg-page: #fff;
      --bg-body: #fff;
      --fg: #111;
      --fg-muted: #333;
      --fg-dim: #222;
      --rule: #000;
      --accent: #000;
      --accent-bar: #000;
      --code-bg: #f5f2e8;
      --table-stripe: #fafaf6;
      --shadow: none;
    }}
    body {{
      max-width: none;
      margin: 0;
      padding: 0;
      box-shadow: none;
      font-size: 10.5pt;
    }}
    a {{ color: #000; }}
    .theme-toggle {{ display: none; }}
    h2, h3, table, pre, figure {{ page-break-inside: avoid; }}
    .table-wrap {{ overflow-x: visible; }}
    .table-wrap.wide {{ page: wide; }}
    .table-wrap.wide > table {{ font-size: 8pt; }}
    .table-wrap.wide th,
    .table-wrap.wide td {{ padding: 3pt 5pt; }}
    body.wide-layout {{ page: wide; }}
    body.wide-layout .table-wrap.wide > table {{ font-size: 9pt; }}
  }}
  h1, h2, h3, h4, h5, h6, .masthead, .caption, .figlabel, .byline, .doctitle {{
    font-family: "Helvetica Neue", "Helvetica", "Arial", sans-serif;
  }}
  .masthead {{
    border-top: 3px solid var(--rule);
    border-bottom: 1px solid var(--rule);
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
    color: var(--fg-dim);
    text-align: left;
    hyphens: none;
  }}
  .byline {{
    font-size: 8.5pt;
    text-transform: uppercase;
    letter-spacing: 0.10em;
    border-bottom: 1px solid var(--rule);
    padding-bottom: 4pt;
    margin: 0 0 18pt 0;
    color: var(--fg-muted);
  }}
  body {{ counter-reset: h2num; }}
  h2 {{
    font-size: 11pt;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    border-bottom: 1px solid var(--rule);
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
  .body-content p.lead::first-letter {{
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
    margin: 0;
    font-size: 9.5pt;
  }}
  .table-wrap {{
    overflow-x: auto;
    margin: 8pt 0 12pt 0;
  }}
  .table-wrap > table {{ margin: 0; }}
  th, td {{
    border-top: 1px solid var(--rule);
    border-bottom: 1px solid var(--rule);
    padding: 4pt 6pt;
    text-align: left;
    vertical-align: top;
  }}
  th {{
    background: var(--code-bg);
    border-top: 2px solid var(--rule);
    border-bottom: 1px solid var(--rule);
    font-family: "Helvetica Neue", "Helvetica", "Arial", sans-serif;
    font-size: 9pt;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }}
  tr:nth-child(even) td {{ background: var(--table-stripe); }}
  code {{
    font-family: "SFMono-Regular", "Consolas", monospace;
    font-size: 90%;
    background: var(--code-bg);
    padding: 0 2pt;
    border-radius: 2px;
  }}
  pre {{
    font-family: "SFMono-Regular", "Consolas", monospace;
    font-size: 8.5pt;
    line-height: 1.35;
    background: var(--code-bg);
    border-left: 2px solid var(--rule);
    padding: 6pt 8pt;
    overflow-x: auto;
    margin: 8pt 0 12pt 0;
  }}
  pre code {{ background: none; padding: 0; }}
  div.highlight, div.highlight pre {{ background: transparent; }}
/*PYGMENTS_CSS*/
  a {{ color: var(--accent); text-decoration: none; border-bottom: 1px dotted var(--accent); }}
  a:hover {{ border-bottom-style: solid; }}
  hr {{ border: 0; border-top: 1px solid var(--rule); margin: 18pt 0; }}
  blockquote {{
    border-left: 3px solid var(--accent-bar);
    margin: 8pt 0;
    padding: 6pt 10pt 6pt 12pt;
    color: var(--fg);
    background: var(--code-bg);
    text-align: left;
    hyphens: manual;
    font-style: normal;
  }}
  blockquote p {{ margin: 0 0 6pt 0; }}
  blockquote p:last-child {{ margin-bottom: 0; }}
  figure {{
    margin: 10pt 0 14pt 0;
    border-top: 1px solid var(--rule);
    border-bottom: 1px solid var(--rule);
    padding: 10pt 0;
    background: var(--bg-body);
  }}
  figcaption {{
    font-family: "Helvetica Neue", "Helvetica", "Arial", sans-serif;
    font-size: 9pt;
    text-align: center;
    margin-top: 6pt;
    color: var(--fg-muted);
  }}
  .mermaid {{ text-align: center; }}
</style>
{mermaid_script}<script>
  (function() {{
    try {{
      var saved = localStorage.getItem('qexify-theme');
      if (saved === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
    }} catch (e) {{}}
  }})();
</script>
</head>
<body{body_class}>
<button class="theme-toggle" type="button" id="qexifyThemeToggle" aria-label="Toggle dark mode">Dark</button>
<script>
  (function() {{
    var btn = document.getElementById('qexifyThemeToggle');
    function label() {{
      var dark = document.documentElement.getAttribute('data-theme') === 'dark';
      btn.textContent = dark ? 'Light' : 'Dark';
    }}
    label();
    btn.addEventListener('click', function() {{
      var dark = document.documentElement.getAttribute('data-theme') === 'dark';
      if (dark) {{
        document.documentElement.removeAttribute('data-theme');
        try {{ localStorage.setItem('qexify-theme', 'light'); }} catch (e) {{}}
      }} else {{
        document.documentElement.setAttribute('data-theme', 'dark');
        try {{ localStorage.setItem('qexify-theme', 'dark'); }} catch (e) {{}}
      }}
      label();
      if (window.mermaid && document.querySelector('.mermaid')) {{
        location.reload();
      }}
    }});
  }})();
</script>
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
    "<script>(function(){"
    "var dark=document.documentElement.getAttribute('data-theme')==='dark';"
    "mermaid.initialize({startOnLoad:true,theme:dark?'dark':'neutral'});"
    "})();</script>\n"
)


def render(
    md_text: str,
    *,
    masthead: str | None = None,
    issue: str | None = None,
    enable_mermaid: bool = True,
    source_path: Path | None = None,
) -> str:
    meta, body = _parse_front_matter(md_text)
    h1_title, body = _extract_first_h1(body)
    body = _strip_h2_manual_numbers(body)
    body, used_mermaid = _replace_mermaid_blocks(body, enable_mermaid)

    body_html = markdown.markdown(
        body,
        extensions=[
            "tables",
            "fenced_code",
            "sane_lists",
            "attr_list",
            "codehilite",
        ],
        extension_configs={
            "codehilite": {
                "css_class": "highlight",
                "guess_lang": False,
                "noclasses": False,
            },
        },
        output_format="html5",
    )
    body_html = _tag_lead_paragraph(body_html)
    body_html, has_wide_table = _wrap_tables(body_html)

    if masthead is None:
        masthead = _infer_masthead(meta, h1_title, body, source_path)

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

    rendered = _TEMPLATE.format(
        html_title=_html.escape(title),
        masthead=_html.escape(masthead),
        issue=_html.escape(issue),
        title_block=title_block,
        body_html=body_html,
        mermaid_script=_MERMAID_SCRIPT if used_mermaid else "",
        body_class=' class="wide-layout"' if has_wide_table else "",
    )
    return rendered.replace("/*PYGMENTS_CSS*/", _pygments_css())


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
        default=None,
        help=(
            "Left-hand masthead label. If omitted, qexify infers from the "
            "front-matter 'masthead' / 'kind' key, then by scanning the H1, "
            "top of the body, and filename for keywords like 'design spec', "
            "'benchmark', 'changelog', etc. Falls back to 'ARTICLE'."
        ),
    )
    p.add_argument(
        "--issue",
        default=None,
        help="Right-hand masthead label (default: current month and year).",
    )
    p.add_argument(
        "--mermaid",
        dest="mermaid",
        action="store_true",
        default=True,
        help="Render fenced ```mermaid blocks via Mermaid.js (default).",
    )
    p.add_argument(
        "--no-mermaid",
        dest="mermaid",
        action="store_false",
        help="Keep mermaid blocks as plain code blocks for fully offline output.",
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
        source_path=src,
    )
    out.write_text(html_out, encoding="utf-8")
    sys.stdout.write(f"Wrote {out} ({len(html_out):,} chars)\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
