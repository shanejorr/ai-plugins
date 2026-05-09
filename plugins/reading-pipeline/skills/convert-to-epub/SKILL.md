---
name: convert-to-epub
description: "Convert a Markdown file, PDF, or plain text into an EPUB or KEPUB e-book file. Use this skill whenever the user wants to turn a document into an e-reader-friendly format — phrases like 'make this into an epub', 'create a kepub', 'convert to epub', 'turn this PDF into a book', 'make this readable on my Kindle/Kobo', or any time the user mentions an .epub or .kepub.epub output. Also trigger when a user has just produced a Markdown summary (e.g., from summarize-research) and wants to read it on an e-reader. Accepts .md, .pdf, or .txt input. Default output format is EPUB (.epub); KEPUB (.kepub.epub) is available when the user is targeting a Kobo and wants reading stats / Kobo-specific typography."
---

# Convert to EPUB Skill

## Purpose

Convert a Markdown file, PDF, or plain-text file into an EPUB or KEPUB e-book file suitable for e-readers.

- **EPUB** (`.epub`): standard format, works on any e-reader (default).
- **KEPUB** (`.kepub.epub`): Kobo-specific naming. Same EPUB content, but the `.kepub.epub` extension tells Kobo devices to enable reading stats, annotations, and improved typography.

Default to **EPUB** unless the user specifies otherwise or is clearly targeting a Kobo.

## Inputs

This skill accepts three input types:

1. **Markdown file** (`.md`) — converted directly via the bundled script.
2. **PDF file** (`.pdf`) — text is extracted, lightly cleaned into Markdown, then converted.
3. **Plain text** (`.txt`) — treated as Markdown (the script's heading detection just won't fire if the text has no `#` headings; that's fine).

## Step 1: Identify the Input

Determine whether the input is Markdown/text or a PDF. Check the file extension. If unclear or the user only described the file, ask.

## Step 2A: If Input is Markdown or Plain Text — Convert Directly

Install dependencies if needed:

```bash
pip install ebooklib markdown --break-system-packages
```

Run the bundled converter:

```bash
python <skill-path>/scripts/md_to_epub.py <input> <output_path>
```

Behavior:
- The script auto-detects the title from the first H1 (`# Title`) and the author from a `**Authors:**` or `**Author:**` line, if present.
- Override with `--title "..."` and `--author "..."`.
- Output format is inferred from the output filename. If the filename ends in `.kepub.epub`, KEPUB is produced; if `.epub`, plain EPUB. **If neither, the script defaults to KEPUB**, so to get a default EPUB you must either pass an `.epub` filename or pass `--format epub`.
- Force a format with `--format epub` or `--format kepub`.

Examples:

```bash
# Default EPUB (this skill's default)
python scripts/md_to_epub.py summary_paper.md ./summary_paper.epub --format epub

# KEPUB for Kobo
python scripts/md_to_epub.py summary_paper.md ./summary_paper.kepub.epub

# Override title/author
python scripts/md_to_epub.py notes.md ./notes.epub --format epub \
    --title "Field Notes from Patagonia" --author "Shane Orr"
```

## Step 2B: If Input is PDF — Extract, Then Convert

PDFs need to be turned into Markdown first. Generally:

1. Run `pdftotext -layout <input.pdf> <tmp.txt>` to get reasonably structured text. Fall back to `pdftotext` without `-layout` if the layout output is too messy.
2. Convert the text into Markdown with sensible structure:
   - The paper or document title becomes a single `# Heading`.
   - Authors and metadata become a `**Authors:** ...` line directly under the title (the converter will pick this up).
   - Major section headers become `## Heading`.
   - Subsections become `### Heading`.
   - Body text becomes paragraphs separated by blank lines.
   - Tables, where reasonable to recover, become Markdown tables.
   - Drop running headers, page numbers, and footnote artifacts.
3. Save the cleaned Markdown to a temporary path (e.g., `/tmp/<name>.md`).
4. Run `md_to_epub.py` on that file, writing the output to the user's chosen destination.

Use judgment about how much cleanup is worth doing. For a research paper, mirror its structure. For a long-form article, paragraph breaks plus section headings are usually enough. If the PDF is mostly figures or scanned images, tell the user and suggest OCR or a different approach.

**Do NOT** summarize the PDF in this skill. This skill converts content into an e-book; it does not transform meaning. If the user wants a summary instead, point them to `summarize-research`.

## Step 3: Save and Confirm

Save the output to the user's current working directory by default; honor a user-specified path. Then print the absolute path so the user can open it.

## Filename and Naming Conventions

- Use snake_case.
- Keep total length under ~60 characters.
- For KEPUB, the full extension must be `.kepub.epub` (not just `.kepub`). Kobo requires both parts.
- For EPUB, just `.epub`.

## Limitations

- Equations: not preserved. LaTeX in source Markdown will pass through as raw text. For papers with heavy math, warn the user.
- Figures: not extracted from PDFs. Only text is converted.
- Footnotes from PDFs: usually appear inline as artifacts; clean them up during the PDF→Markdown step.
- Code blocks: rendered with monospace styling but no syntax highlighting.
