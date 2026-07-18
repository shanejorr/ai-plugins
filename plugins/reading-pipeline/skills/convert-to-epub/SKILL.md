---
name: convert-to-epub
description: "Convert a Markdown file, PDF, or plain text into an EPUB or KEPUB e-book file. Use this skill whenever the user wants to turn a document into an e-reader-friendly format — phrases like 'make this into an epub', 'create a kepub', 'convert to epub', 'turn this PDF into a book', 'make this readable on my Kindle/Kobo', or any time the user mentions an .epub or .kepub.epub output. Also trigger when a user has just produced a Markdown summary (e.g., from summarize-research) and wants to read it on an e-reader. Accepts .md, .pdf, or .txt input. Default output format is EPUB (.epub); KEPUB (.kepub.epub) is available when the user is targeting a Kobo and wants reading stats / Kobo-specific typography."
user-invocable: true
disable-model-invocation: false
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

Optional — to render Mermaid diagrams to images (see [Diagrams](#diagrams-mermaid-and-similar)), also install the Mermaid CLI:

```bash
npm install -g @mermaid-js/mermaid-cli   # provides `mmdc`
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
- **Mermaid (and similar) diagrams are rendered to images and embedded automatically** — the reader sees the picture, not the diagram source. See [Diagrams](#diagrams-mermaid-and-similar) below.

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

## Diagrams (Mermaid and similar)

If the source Markdown contains diagrams written as fenced code blocks, the converter renders each one to an image and embeds it in the book, so the final EPUB shows the **visualization, not the diagram code**. A ` ```mermaid ` block is always eligible; the Kroki backend additionally handles ` ```plantuml `, ` ```graphviz `/` ```dot `, and more. Ordinary (non-diagram) code fences like ` ```python ` are left as code, untouched.

Choose how diagrams are rendered with `--diagram-backend`:

- **`auto`** (default) — render Mermaid with the local Mermaid CLI (`mmdc`) if it is installed; otherwise leave the diagram as a code block and print a warning. This is the private, offline-friendly default.
- **`mmdc`** — require the local Mermaid CLI (`npm install -g @mermaid-js/mermaid-cli`). Mermaid only.
- **`kroki`** — POST the diagram source to a [Kroki](https://kroki.io) server and embed the returned image. No local install and it covers many diagram languages, **but the diagram source leaves the machine.** Point at a self-hosted instance with `--kroki-url` to keep it private.
- **`none`** — skip rendering; leave every diagram as a fenced code block (the old behavior).

A diagram that fails to render (missing tool, syntax error, network failure) is **left as its original code block** — nothing is ever dropped.

Other useful flags:

- `--diagram-format {png,svg}` — image format. **PNG (default)** is the most e-reader-compatible; SVG is sharper but not supported by every reader (and Mermaid's SVG text labels render inconsistently on some devices).
- `--mermaid-theme {default,neutral,dark,forest}` — Mermaid theme for local rendering.
- `--diagram-background <color>` — background for locally rendered diagrams (default `white`, so labels stay legible in dark-mode readers; use `transparent` to blend in).
- `--diagram-scale <n>` — PNG scale factor for local rendering; higher is crisper (default `2`).

```bash
# Default: render Mermaid locally to embedded PNGs
python scripts/md_to_epub.py design_doc.md ./design_doc.epub --format epub

# No local install; let Kroki render Mermaid/PlantUML/GraphViz (source goes to kroki.io)
python scripts/md_to_epub.py design_doc.md ./design_doc.epub --format epub \
    --diagram-backend kroki

# Keep diagrams as raw code blocks
python scripts/md_to_epub.py design_doc.md ./design_doc.epub --format epub \
    --diagram-backend none
```

If a diagram is left as code because `mmdc` is missing, the converter prints an install hint. Install the Mermaid CLI and re-run, or pass `--diagram-backend kroki`.

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
- Diagrams: Mermaid fenced code blocks are rendered to embedded images (PlantUML, GraphViz, and others too via `--diagram-backend kroki`). This needs `mmdc` (local) or a Kroki server; without either, diagrams stay as code blocks. Only fenced-code diagrams are handled — image figures embedded in a PDF are not extracted (see below).
- Figures: not extracted from PDFs. Only text is converted.
- Footnotes from PDFs: usually appear inline as artifacts; clean them up during the PDF→Markdown step.
- Code blocks: rendered with monospace styling but no syntax highlighting.
