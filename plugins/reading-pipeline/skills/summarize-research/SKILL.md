---
name: summarize-research
description: "Summarize an academic research paper for an intelligent non-specialist audience and save the summary as a Markdown or PDF file. Accepts the paper as a PDF, plain text, or a URL (arXiv, journal, blog). Use this skill whenever the user asks for a summary, explanation, breakdown, or review of a research paper, academic article, journal article, preprint, or scientific study. Trigger phrases include 'summarize this paper', 'explain this paper', 'what does this paper say', 'break down this study', 'summarize this article', or any time the user supplies a paper (PDF/URL/text) and wants it explained. Do NOT use for summarizing non-academic documents like reports, whitepapers, or news articles."
---

# Summarize Research Skill

## Purpose

Produce a thorough, accessible summary of an academic research paper that reads as a standalone narrative document — essentially a simplified, self-contained version of the paper itself. The summary should never feel like a book report *about* the paper. It should feel like *the paper*, rewritten for a smart generalist audience. Output is a Markdown (`.md`) or PDF (`.pdf`) file.

## Step 1: Acquire the Paper Text

The input may be a PDF, plain text, or a URL. Identify which and extract the text accordingly.

### PDF input

Run `pdfinfo` and `pdftotext` to extract the text. If figures or tables matter (they usually do in research papers), also rasterize key pages with `pypdfium2` so you can inspect charts and diagrams visually. If the PDF is mostly scanned images, tell the user and suggest OCR.

### URL input

Use the `WebFetch` tool to retrieve the page. If the URL clearly points to a PDF (ends in `.pdf`, or the response content-type is `application/pdf`), download it with `curl -L -o /tmp/paper.pdf <URL>` and then extract as in the PDF case. arXiv abstract pages (`arxiv.org/abs/...`) also have a direct PDF link at `arxiv.org/pdf/...` — prefer that.

### Plain-text input

Read the file directly (or use the text the user pasted). No extraction needed.

## Step 2: Confirm the Output Format

If the user did not specify Markdown or PDF, **ask** which they want. Offer both: Markdown is editable and lightweight; PDF is print/share-ready and uses the project's standard formatting (0.2" margins, 14pt body font).

## Step 3: Analyze the Paper's Structure

Before writing, identify the paper's own section structure. The summary will mirror it. Note:
- The paper's actual section and subsection headings
- Which sections carry the most weight
- Where the paper introduces novel terminology or relies on assumed knowledge
- What the paper proposes as solutions, if anything

## Step 4: Write the Summary

### Narrative Voice and Framing

The summary is written **as though it were the paper itself**, not a commentary on the paper. It adopts the paper's perspective and makes its arguments directly.

**Do this:**
- "Autonomous AI agents face a critical vulnerability: the information environment itself."
- "We identify six categories of attack based on their target within the agent's operational cycle."
- "Content injection traps exploit the structural divergence between machine-parsed data and human-visible rendering."

**Not this:**
- "This paper argues that autonomous AI agents face a vulnerability."
- "The authors identify six categories."
- "The paper describes content injection traps as exploiting..."

The summary speaks in the paper's voice. Use "we" where the paper uses "we." Make claims directly rather than attributing them. The reader should feel they are reading the paper's own argument, just explained more clearly.

**One exception:** When you are adding your own knowledge — supplementary explanations, literature context, or limitations the paper does not acknowledge — clearly mark the shift. Use a brief parenthetical like "(To give additional context: ...)" or a short paragraph prefixed with "Beyond what is discussed here, ..." so the reader knows where the paper's content ends and your additions begin.

### Structure

The summary must include the following fixed elements, then mirror the paper's own sections for its body:

```
# [Paper Title]
**Authors:** [list]  
**Published:** [journal/venue, date]  
**DOI/Link:** [if available]

## Executive Summary
[3–5 sentences. Plain language. No jargon. What is the core contribution, what was found, why it matters. A busy person reads only this and walks away informed.]

## Key Concepts and Terminology
[A reference table or definition list explaining every major technical concept, piece of jargon, acronym, and novel term the paper relies on. Include concepts the paper assumes the reader knows but a generalist would not. Include novel terms the paper coins — these are especially important since the reader cannot look them up elsewhere. Use your own knowledge to explain concepts the paper does not adequately define.

This section exists so the reader can consult it as needed while reading the narrative. It is a reference, not part of the narrative flow.]

---

## [Mirror the paper's own sections here]

Use the paper's actual section and subsection headings. Rewrite the content of each section in accessible language, preserving the paper's argumentative structure and logical flow. Within each section:

- Explain technical concepts inline when they first appear, even if they are also in the Key Concepts table
- Preserve the paper's evidence and citations — report empirical findings, statistics, and referenced studies
- Use tables when they help (e.g., to summarize a taxonomy, compare methods, present results across conditions)
- If a section is very long or dense, condense it, but do not skip it

---

## Critical Assessment

[This section is NOT mirrored from the paper — it is your addition. Clearly frame it as such. Cover:]

### Strength of Evidence
How confident should a reader be in the findings? Consider sample sizes, effect sizes, replication, robustness checks. Distinguish well-supported claims from speculative ones.

### Key Assumptions
What does the paper take for granted that could change the interpretation if wrong?

### Limitations
What do the authors acknowledge? What significant limitations do they not acknowledge but should?

### Placement in the Literature
How does the paper fit into the broader field? What prior work does it build on? How does it differ from or extend related studies? Use both the paper's own discussion and your own knowledge. If your knowledge of the subfield is limited, say so.
```

### Writing Guidelines

- **Audience:** An intelligent person with no specialist background in the paper's field. Think: a journalist, a policymaker, a professional from another discipline.
- **Tone:** Clear, direct, factual. The tone should match the paper's own register but simplified. If the paper is formal, stay somewhat formal. If it is conversational, reflect that. Never hype. Never hedge unnecessarily.
- **Length:** Thorough but not padded. A typical summary will be 1,500–3,000 words depending on the paper's complexity. Dense papers get longer summaries; thin papers get shorter ones.
- **Tables:** Use markdown tables when they aid understanding — taxonomies, result comparisons, concept definitions. Do not reproduce every table from the paper; synthesize and simplify.
- **Your own knowledge:** You are expected to supplement the paper where needed — explaining technical concepts, placing the work in literature, noting unacknowledged limitations. Always make it clear when you are adding your own knowledge versus restating the paper's content.
- **Jargon:** Define on first use inline, even if it also appears in the Key Concepts table. The narrative should be readable without flipping to the reference table.

Use only standard Markdown — headings, bold/italic, tables, lists, blockquotes, fenced code. No HTML, no front matter. The output is meant to be readable as-is and to feed cleanly into downstream conversion (e.g., the `convert-to-epub` skill).

## Step 5: Save the Output

Filename: `summary_<snake_case_title>.{md,pdf}`. Snake_case, ≤60 characters total, strip diacritics and special characters. Examples:

- `summary_attention_is_all_you_need.md`
- `summary_polygenic_scores_cognitive_ability.pdf`

Save to the user's current working directory by default. If the user specifies an output path or directory, honor it.

### If output is Markdown

Use the `Write` tool to save the file directly.

### If output is PDF

1. Write the Markdown to a temp file (e.g., `/tmp/<basename>.md`).
2. Run the bundled converter:

   ```bash
   python <skill-path>/scripts/md_to_pdf.py /tmp/<basename>.md <output.pdf>
   ```

The script uses `weasyprint` (preferred) or pandoc as a fallback. Both render with the project's PDF formatting standard: **0.2 inch margins on all sides**, **14pt body font**, serif typography. These are baked into the script — no flags needed.

Install dependencies on first use:

```bash
pip install markdown weasyprint --break-system-packages
```

If `weasyprint` won't install (it has a few system-level deps on some platforms — `pango`, `cairo`, `gdk-pixbuf`), fall back to pandoc:

```bash
brew install pandoc weasyprint   # macOS
# or: apt install pandoc weasyprint  (Linux)
```

The script will detect which path to use.

## Step 6: Confirm

Print the absolute path of the saved file so the user can open it.
