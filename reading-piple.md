# Reading Pipeline Plugin

## Overview

`reading-pipeline` is a dual-platform Claude Code and Codex/ChatGPT Work plugin for turning research and other written material into e-reader-ready files. It covers the full path from creating or summarizing content, through EPUB/KEPUB conversion, to delivery through Google Drive folders that sync with a Kobo Color or reMarkable Paper Pro.

The plugin is version `0.5.0` and contains five user-invocable skills:

1. `research-topic`
2. `summarize-research`
3. `convert-to-epub`
4. `send-to-reader`
5. `send-chat-to-kobo`

The skills form a small pipeline rather than five unrelated commands. Two skills create reading material, one converts material into an e-book, one delivers files, and one coordinates conversion and delivery for content already present in a chat.

```text
Topic request ───────────────> research-topic ───────> Markdown report
Academic paper ──────────────> summarize-research ──> Markdown or PDF summary
Existing Markdown/text/PDF ─────────────────────────> convert-to-epub ──> EPUB/KEPUB
Ready PDF/EPUB/KEPUB ───────────────────────────────────────────────────> send-to-reader
Markdown report or summary ─> convert-to-epub ──────> send-to-reader ───> e-reader
Selected chat content ──────> send-chat-to-kobo ────> KEPUB + upload ──> Kobo
```

## Skill Summary

| Skill | Primary job | Accepted input | Main output |
|---|---|---|---|
| `research-topic` | Produce a broad, current, citation-rich topic report | A research question or topic | Markdown report |
| `summarize-research` | Rewrite one academic paper for a smart non-specialist | PDF, URL, plain-text paper, or pasted text | Markdown or PDF summary |
| `convert-to-epub` | Turn a document into an e-reader format | Markdown, text, or PDF | `.epub` or `.kepub.epub` |
| `send-to-reader` | Convert when needed and upload to a device-specific Drive folder | PDF, EPUB, KEPUB, Markdown, or text | File uploaded for Kobo or reMarkable sync |
| `send-chat-to-kobo` | Package selected conversation content and send it to Kobo | A response or section from the current chat | KEPUB uploaded to the Kobo folder |

## Skills in Detail

### `research-topic`

This skill handles broad research requests rather than individual papers. It builds an internal research brief, searches in multiple rounds, favors primary and authoritative sources, and writes a standalone report for an intermediate reader at approximately upper-level undergraduate depth.

Its default report includes an executive summary, learning objectives, key terminology, foundational concepts, topic-specific analysis, debates and limitations, current research frontiers, practical implications, further reading, and references. Claims are cited inline with readable Markdown links.

The report is saved as `research_<topic>.md`. The Markdown is deliberately constrained to headings, paragraphs, lists, blockquotes, fenced code, and simple tables so it can pass cleanly into `convert-to-epub` or `send-to-reader`.

Use this skill for requests such as “research battery recycling in depth.” Do not use it when the main task is explaining one supplied academic paper; that belongs to `summarize-research`.

### `summarize-research`

This skill handles a single academic paper supplied as a PDF, URL, plain-text file, or pasted text. It extracts and inspects the paper, mirrors the paper's own structure, and rewrites the content as a clear standalone narrative for a non-specialist.

The summary includes:

- a short executive summary;
- definitions of important concepts and terminology;
- an accessible version of each substantive paper section;
- the paper's evidence and important quantitative results; and
- a separate critical assessment covering evidence strength, assumptions, limitations, and placement in the literature.

The narrative generally adopts the paper's own voice instead of repeatedly saying “the paper argues” or “the authors say.” Any additional context supplied by the model must be clearly distinguished from the paper's claims.

The user chooses Markdown or PDF. Markdown is saved directly as `summary_<title>.md`. PDF output is generated from temporary Markdown by `scripts/md_to_pdf.py`, using WeasyPrint when available and a Pandoc-based fallback. The PDF stylesheet uses letter-size pages, 0.2-inch margins, 14-point serif body text, and formatting for tables, code, quotations, and headings.

The Markdown form is the natural handoff to `convert-to-epub`; either Markdown or the finished PDF can be passed to `send-to-reader`.

### `convert-to-epub`

This skill converts Markdown, plain text, or PDF into an e-book:

- `.epub` is the default skill-level choice and works across e-readers.
- `.kepub.epub` is used for Kobo. In this plugin it is EPUB content with Kobo's expected compound extension, which enables Kobo-specific handling such as reading statistics and typography.

Markdown and text are processed by `scripts/md_to_epub.py`, which uses `markdown` and `ebooklib`. The converter:

- detects the title from the first level-one heading;
- detects the author from an `**Author:**` or `**Authors:**` line;
- splits the book into chapters at level-two headings;
- builds an EPUB table of contents and navigation document; and
- applies an e-reader-oriented stylesheet.

The output filename controls the format. A name ending in `.kepub.epub` produces KEPUB naming, while `.epub` produces standard EPUB. If the caller supplies neither extension and does not specify `--format`, the script itself defaults to KEPUB; the skill avoids that ambiguity by explicitly using `.epub` for its default.

PDF conversion is a two-stage model-assisted process. The skill extracts the PDF's text with `pdftotext`, cleans it into structured Markdown, and then runs the Markdown converter. It preserves meaning rather than summarizing it. Scanned PDFs need OCR, and figures, equations, and complex footnotes are not reliably preserved.

### `send-to-reader`

This skill is the delivery layer. It targets either a Kobo Color or a reMarkable Paper Pro through a device-specific Google Drive folder.

Ready-to-read `.pdf`, `.epub`, and `.kepub.epub` files are uploaded unchanged. Markdown and text are converted first through the sibling converter:

- Kobo receives `.kepub.epub`.
- reMarkable receives `.epub`.

The skill then calls `scripts/upload_to_gdrive.py`. The uploader resolves a folder ID in this order:

1. the `--folders-config` command-line argument;
2. `READING_PIPELINE_FOLDERS_CONFIG`;
3. `~/.config/send-to-reader/folders.json`; or
4. the legacy in-plugin `config/folders.json`.

OAuth client credentials live at `~/.config/gdrive-oauth/gdrive_credentials.json`, and the cached token lives at `~/.config/gdrive-oauth/gdrive_token.pickle`. Keeping both folder IDs and credentials outside the plugin prevents personal configuration from being published or erased by a plugin upgrade.

The first upload opens a browser for Google authorization. Later uploads normally reuse the cached refresh token. The script reports actionable errors for missing configuration, placeholder folder IDs, inaccessible Drive folders, and permission failures.

The Google Drive upload is only the delivery handoff. The file appears on the device when its Drive integration or sync process next runs.

### `send-chat-to-kobo`

This is an orchestration skill with no unique conversion or upload implementation. It finds the response or subsection selected by the user, writes that content unchanged to temporary Markdown, and gives it a sensible title. It then delegates to:

1. `convert-to-epub`, producing a `.kepub.epub`; and
2. `send-to-reader`, targeting the `kobo` device key.

This is the shortest route for requests such as “send your last response to my Kobo.” It preserves existing headings, lists, code blocks, tables, and quotations instead of rewriting or summarizing the selected content.

Use `send-to-reader` directly for an existing file or for reMarkable delivery. Use `convert-to-epub` directly when conversion is wanted without upload.

## How the Skills Work Together

### Research a topic and read it on an e-reader

1. `research-topic` creates a citation-rich Markdown report.
2. If the user only wants a local e-book, `convert-to-epub` creates EPUB or KEPUB.
3. If the user wants delivery, `send-to-reader` converts the Markdown to the correct device format and uploads it.

Because `send-to-reader` already converts Markdown, callers do not need to invoke `convert-to-epub` separately unless they also want to keep or inspect the local e-book before uploading.

### Summarize a paper and send it

1. `summarize-research` acquires and analyzes the paper.
2. It creates either a Markdown or PDF summary.
3. A Markdown summary can be converted to EPUB/KEPUB or passed directly to `send-to-reader` for automatic conversion.
4. A PDF summary can be uploaded directly to either device.

If reflowable e-reader text is the goal, Markdown followed by EPUB/KEPUB is the better path. PDF is more appropriate when fixed page layout or sharing is more important.

### Convert an existing document

For local conversion only, `convert-to-epub` accepts Markdown, text, or PDF. For delivery, `send-to-reader` accepts ready-made e-books and PDFs directly, and it automatically converts Markdown or text.

### Send part of a conversation

`send-chat-to-kobo` owns this complete workflow. It selects the chat content, creates temporary Markdown, requests KEPUB conversion, and requests Kobo delivery. Its instructions explicitly avoid duplicating the converter or uploader logic.

## Routing Guide

| User intent | Skill to start with |
|---|---|
| “Research this subject in depth” | `research-topic` |
| “Explain or summarize this academic paper” | `summarize-research` |
| “Turn this file into an EPUB/KEPUB” | `convert-to-epub` |
| “Send this file to my Kobo/reMarkable” | `send-to-reader` |
| “Send your last answer to my Kobo” | `send-chat-to-kobo` |

The important routing boundary is between broad topic research and single-paper summarization. The other boundary is between conversion only and conversion plus delivery.

## Dependencies and Configuration

The plugin uses external command-line and Python dependencies rather than bundling a runtime.

| Function | Dependencies |
|---|---|
| EPUB/KEPUB creation | `ebooklib`, `markdown` |
| PDF text extraction | `pdfinfo`, `pdftotext`; optional rasterization support for visual inspection |
| PDF generation | `markdown`, `weasyprint`; Pandoc is an alternate entry path |
| Google Drive upload | `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib` |

Drive delivery also requires:

- a Google Cloud project with the Drive API enabled;
- OAuth credentials for a desktop application;
- a folder-ID mapping for `kobo` and/or `remarkable`; and
- write access to the selected folders for the authorized Google account.

The repository provides `config/folders.example.json`, but real folder IDs and OAuth secrets must remain outside the repository.

## Review Notes

The plugin's main design is sound: responsibilities are separated cleanly, Markdown is used as the interchange format, and the higher-level skills reuse conversion and upload behavior instead of reimplementing it. The Claude and Codex plugin manifests and the Claude marketplace entry all report version `0.5.0`.

The review also found several items that should be reconciled in a future update:

1. **Google Drive OAuth scope mismatch.** `send-to-reader/SKILL.md` and `credentials/README.md` describe the narrower `drive.file` scope, but `upload_to_gdrive.py` requests the full `https://www.googleapis.com/auth/drive` scope. The implemented scope controls the actual permission request, so either the script should be narrowed or the documentation should explicitly describe the broader access.
2. **Outdated folder setup path.** `credentials/README.md` tells the user to copy the folder template to the plugin's `config/folders.json`. The skill and uploader correctly prefer `~/.config/send-to-reader/folders.json`, which survives plugin upgrades and should be the documented destination everywhere.
3. **Platform-specific EPUB publisher metadata.** `md_to_epub.py` hard-codes the EPUB publisher as `Claude`, even though the plugin also supports ChatGPT Work and Codex. A neutral plugin name or configurable publisher would better match the dual-platform packaging.
4. **PDF fallback wording.** `md_to_pdf.py` describes Pandoc as a fallback, but its Pandoc command still selects WeasyPrint as the PDF engine. Pandoc alone is therefore not an independent fallback when WeasyPrint is unavailable.
5. **KEPUB implementation boundary.** The converter changes the filename to `.kepub.epub` but does not perform additional Kobo-specific content transformation. This matches the current skill documentation, but users should understand that the plugin produces Kobo-recognized EPUB naming rather than a separately post-processed KEPUB package.

These issues do not change how the five skills are intended to compose, but resolving them would make setup, permissions, metadata, and failure behavior more predictable.

