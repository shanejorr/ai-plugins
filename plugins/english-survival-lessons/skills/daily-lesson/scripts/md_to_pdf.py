#!/usr/bin/env python3
"""
Convert a Markdown file to PDF with Shane's house PDF formatting standard.

Standard (applies to every PDF this plugin produces):
  - Page margins: 0.2 inch on all four sides
  - Body font: 14pt serif (Georgia / Times New Roman)
  - Heading scale matches Shane's other PDF outputs for visual consistency

Usage:
    python md_to_pdf.py input.md output.pdf

Renders via weasyprint (preferred) or pandoc + weasyprint as fallback.

Install:
    pip install markdown weasyprint --break-system-packages
    # On macOS, weasyprint may also need: brew install pango cairo gdk-pixbuf libffi
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

try:
    import markdown
except ImportError:
    print("ERROR: markdown not installed. Run: pip install markdown --break-system-packages")
    sys.exit(1)


CSS = """
@page {
    size: letter;
    margin: 0.2in;
}
body {
    font-family: "Georgia", "Times New Roman", serif;
    font-size: 14pt;
    line-height: 1.5;
    margin: 0;
}
h1 { font-size: 1.5em; margin-top: 0.8em; margin-bottom: 0.4em; }
h2 { font-size: 1.3em; margin-top: 0.8em; margin-bottom: 0.4em; }
h3 { font-size: 1.1em; margin-top: 0.6em; margin-bottom: 0.3em; }
h4, h5, h6 { font-size: 1em; margin-top: 0.5em; margin-bottom: 0.25em; }
p { margin: 0.4em 0; }
table { border-collapse: collapse; width: 100%; margin: 0.8em 0; font-size: 0.9em; }
th, td { border: 1px solid #999; padding: 0.4em 0.6em; text-align: left; vertical-align: top; }
th { background-color: #f0f0f0; font-weight: bold; }
blockquote { margin: 0.8em 0; padding-left: 0.8em; border-left: 3px solid #ccc; color: #555; }
code { font-family: "Menlo", "Consolas", monospace; font-size: 0.9em; background: #f5f5f5; padding: 0.1em 0.3em; }
pre { background: #f5f5f5; padding: 0.8em; overflow-x: auto; font-size: 0.85em; }
pre code { background: transparent; padding: 0; }
hr { border: none; border-top: 1px solid #ccc; margin: 1em 0; }
ul, ol { margin: 0.4em 0; padding-left: 1.5em; }
li { margin: 0.15em 0; }
dl dt { font-weight: bold; margin-top: 0.4em; }
dl dd { margin-left: 1.5em; margin-bottom: 0.4em; }
img { max-width: 100%; }
"""


def md_to_html(md_text: str) -> str:
    body_html = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "toc", "md_in_html"],
    )
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>{CSS}</style>
</head>
<body>
{body_html}
</body>
</html>"""


def render_with_weasyprint(html: str, output_path: str) -> bool:
    try:
        from weasyprint import HTML
    except ImportError:
        return False
    HTML(string=html).write_pdf(output_path)
    return True


def render_with_pandoc(md_path: str, output_path: str) -> bool:
    if not shutil.which("pandoc"):
        return False
    with tempfile.NamedTemporaryFile("w", suffix=".css", delete=False) as f:
        f.write(CSS)
        css_path = f.name
    try:
        subprocess.run(
            [
                "pandoc",
                md_path,
                "-o",
                output_path,
                "--pdf-engine=weasyprint",
                "--css",
                css_path,
            ],
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"pandoc failed: {e}")
        return False
    finally:
        os.unlink(css_path)


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to PDF (0.2in margins, 14pt body)")
    parser.add_argument("input", help="Input markdown file")
    parser.add_argument("output", help="Output PDF path")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: input not found: {args.input}")
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        md_text = f.read()
    html = md_to_html(md_text)

    if render_with_weasyprint(html, args.output):
        print(f"Created (weasyprint): {args.output}")
        return
    if render_with_pandoc(args.input, args.output):
        print(f"Created (pandoc): {args.output}")
        return

    print("ERROR: Neither weasyprint nor pandoc is available.")
    print("Install one of:")
    print("  pip install weasyprint --break-system-packages")
    print("  brew install pandoc weasyprint   # macOS")
    sys.exit(1)


if __name__ == "__main__":
    main()
