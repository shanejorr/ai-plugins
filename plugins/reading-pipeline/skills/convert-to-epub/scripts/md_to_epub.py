#!/usr/bin/env python3
"""
Convert a Markdown file to EPUB or KEPUB for e-readers.

Usage:
    python md_to_epub.py input.md output.epub
    python md_to_epub.py input.md output.kepub.epub
    python md_to_epub.py input.md output.epub --title "Title" --author "Author"

Format is determined by the output filename:
- *.kepub.epub -> KEPUB (Kobo-specific, enables reading stats and annotations)
- *.epub       -> standard EPUB (works on any e-reader)

If only a base name is given, defaults to .kepub.epub. Override with --format epub.
"""

import argparse
import os
import re
import sys
import uuid

try:
    from ebooklib import epub
except ImportError:
    print("ERROR: ebooklib not installed. Run: pip install ebooklib --break-system-packages")
    sys.exit(1)

try:
    import markdown
except ImportError:
    print("ERROR: markdown not installed. Run: pip install markdown --break-system-packages")
    sys.exit(1)


def md_to_html(md_text: str) -> str:
    """Convert markdown text to HTML with tables and fenced code support."""
    return markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "toc", "md_in_html"],
    )


def resolve_output_path(output_path: str, fmt: str | None) -> str:
    """Decide on the final output path based on extension and --format flag."""
    if fmt == "kepub":
        if not output_path.endswith(".kepub.epub"):
            base = output_path[:-5] if output_path.endswith(".epub") else output_path
            output_path = base + ".kepub.epub"
    elif fmt == "epub":
        if output_path.endswith(".kepub.epub"):
            output_path = output_path[: -len(".kepub.epub")] + ".epub"
        elif not output_path.endswith(".epub"):
            output_path = output_path + ".epub"
    else:
        # No --format flag; infer from extension. Default to .kepub.epub if neither.
        if not (output_path.endswith(".epub") or output_path.endswith(".kepub.epub")):
            output_path = output_path + ".kepub.epub"
    return output_path


def create_epub(
    md_path: str,
    output_path: str,
    title: str | None = None,
    author: str | None = None,
    fmt: str | None = None,
):
    """Create an EPUB or KEPUB from a markdown file."""
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Auto-detect title from first H1 if not provided
    if not title:
        m = re.search(r"^#\s+(.+)$", md_text, re.MULTILINE)
        if m:
            title = m.group(1).strip()
        else:
            title = os.path.splitext(os.path.basename(md_path))[0].replace("_", " ").title()

    if not author:
        # Try the explicit "**Authors:**" or "**Author:**" pattern
        m = re.search(r"\*\*Authors?:\*\*\s*(.+)", md_text)
        author = m.group(1).strip() if m else "Unknown"

    # Build the epub
    book = epub.EpubBook()
    book.set_identifier(str(uuid.uuid4()))
    book.set_title(title)
    book.set_language("en")
    book.add_author(author)
    book.add_metadata("DC", "publisher", "Claude")

    # CSS for clean e-reader formatting
    css = epub.EpubItem(
        uid="style",
        file_name="style/default.css",
        media_type="text/css",
        content="""
body {
    font-family: serif;
    line-height: 1.6;
    margin: 1em;
}
h1 { font-size: 1.5em; margin-top: 1em; margin-bottom: 0.5em; }
h2 { font-size: 1.3em; margin-top: 1em; margin-bottom: 0.4em; }
h3 { font-size: 1.1em; margin-top: 0.8em; margin-bottom: 0.3em; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.9em; }
th, td { border: 1px solid #999; padding: 0.4em 0.6em; text-align: left; }
th { background-color: #f0f0f0; font-weight: bold; }
blockquote { margin: 1em 0; padding-left: 1em; border-left: 3px solid #ccc; color: #555; }
code { font-family: monospace; font-size: 0.9em; background: #f5f5f5; padding: 0.1em 0.3em; }
pre { background: #f5f5f5; padding: 1em; overflow-x: auto; }
hr { border: none; border-top: 1px solid #ccc; margin: 1.5em 0; }
p { margin: 0.5em 0; }
dl dt { font-weight: bold; margin-top: 0.5em; }
dl dd { margin-left: 1.5em; margin-bottom: 0.5em; }
""".encode("utf-8"),
    )
    book.add_item(css)

    # Split markdown into chapters by H2 headings.
    sections = re.split(r"(?=^## )", md_text, flags=re.MULTILINE)

    chapters = []
    toc = []

    for i, section in enumerate(sections):
        if not section.strip():
            continue

        heading_match = re.match(r"^##\s+(.+)$", section, re.MULTILINE)
        if heading_match:
            section_title = heading_match.group(1).strip()
        elif i == 0:
            # Pre-H2 content (title, metadata, anything above the first H2)
            section_title = title
        else:
            section_title = f"Section {i}"

        html_content = md_to_html(section)

        chapter_html = f"""<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{section_title}</title>
    <link rel="stylesheet" type="text/css" href="style/default.css"/>
</head>
<body>
{html_content}
</body>
</html>"""

        safe_name = re.sub(r"[^a-zA-Z0-9]", "_", section_title.lower())[:40]
        chapter = epub.EpubHtml(
            title=section_title,
            file_name=f"ch_{i:02d}_{safe_name}.xhtml",
            lang="en",
        )
        chapter.content = chapter_html.encode("utf-8")
        chapter.add_item(css)

        book.add_item(chapter)
        chapters.append(chapter)
        toc.append(chapter)

    book.toc = toc
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + chapters

    output_path = resolve_output_path(output_path, fmt)
    epub.write_epub(output_path, book, {})
    print(f"Created: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to EPUB or KEPUB")
    parser.add_argument("input", help="Input markdown file")
    parser.add_argument("output", help="Output file path (.epub or .kepub.epub)")
    parser.add_argument("--title", help="Book title (auto-detected from H1 if omitted)")
    parser.add_argument("--author", help="Author name (auto-detected from **Authors:** line if omitted)")
    parser.add_argument(
        "--format",
        choices=["epub", "kepub"],
        help="Force output format. If omitted, inferred from output filename; defaults to kepub.",
    )
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    create_epub(args.input, args.output, title=args.title, author=args.author, fmt=args.format)


if __name__ == "__main__":
    main()
