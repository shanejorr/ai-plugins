---
name: research-topic
description: "Research a topic in depth and create a current, citation-rich Markdown report for an intermediate reader at upper-level undergraduate depth. Use this skill when the user asks for deep research, a comprehensive research report, a literature review, a literature-grounded topic overview, a course-level treatment, an explainer on how a technology, protocol, or tool works, or broad and deep coverage of a subject rather than a summary of one supplied paper. Match sources to the topic — scholarly literature for scientific subjects, official documentation and specifications for technical ones — explain specifics with casual analogies and metaphors, and produce output compatible with convert-to-epub and send-to-reader. Do NOT use when the primary task is to summarize a particular research paper; use summarize-research instead."
user-invocable: true
disable-model-invocation: false
---

# Research Topic

## Purpose

Create a standalone research report that gives an intermediate reader both a wide map of a topic and a close view of its machinery. Depending on the request, the deliverable is an explanatory report, a literature review, or a technology explainer — each with the breadth and depth of an upper-level undergraduate course unit, written like an informed guide rather than a textbook committee.

Save the report as standard Markdown so the sibling `convert-to-epub` and `send-to-reader` skills can turn it into an e-book and deliver it without cleanup.

## 1. Define the Research Question

Extract the topic, the user's goal, any boundaries, and the desired emphasis from the request. Default to:

- an intermediate reader who knows the basic vocabulary but not the specialist literature;
- international scope unless the subject implies a region;
- emphasis on the current state of knowledge, with older work included when foundational;
- a balanced explanatory report, not an argument for a predetermined conclusion.

Ask concise clarifying questions only when a missing choice would materially change the research, such as an ambiguous topic, jurisdiction, time period, or disciplinary lens. Ask no more than three at once. If the request is already specific, begin without reconfirming it.

## 2. Build a Research Brief

Before searching, turn the request into a concrete internal brief. Include:

1. The central question and scope boundaries.
2. The topic type and report mode (below).
3. The concepts and prerequisite ideas the reader needs.
4. The topic's foundations, mechanisms, methods, major subfields, applications, debates, limitations, and active frontier.
5. Cross-disciplinary connections that materially improve understanding.
6. The evidence needed for each major section and the likely primary sources.
7. The report structure, expected depth, and source cutoff date.

### Topic type and report mode

Classify the topic, because the classification determines which sources count as authoritative:

- **Scholarly** — subjects where peer-reviewed literature is the ground truth (battery recycling, polygenic scores, sentencing reform).
- **Technology / practitioner** — tools, protocols, frameworks, and systems where specifications, official documentation, and maintainer writing are the ground truth (a database engine, a protocol, an API standard). Academic literature on these subjects is often thin, dated, or skewed toward one niche; do not let it dominate the report.
- **Mixed** — subjects with both a research literature and a practitioner ecosystem (vector search, spaced repetition). Draw on both hierarchies and make clear which kind of source supports which claim.

Separately, pick the report mode: a **report** (the default — explains the topic itself) or a **literature review** (organized around the literature — who found what, where the field agrees and disagrees, and what remains open). Use literature-review mode when the user asks for one by name or clearly wants a survey of the research rather than an explanation of the subject.

Treat the topic as a landscape: map the mountain ranges before inspecting individual rocks. Do not let the first plausible search result dictate the outline.

## 3. Conduct Deep Research

Stay in the loop as the synthesizer, and use the strongest research tools exposed by the current platform:

- Drive the brief yourself with the available search, page-fetching, browser, and document tools, following citations to primary sources and synthesizing only once the evidence base is broad enough.
- When a search MCP such as Tavily is connected, prefer it as the retrieval engine: use its search tool at the most thorough depth setting and its page-extract tool to pull primary sources.
- Do the reasoning, verification, and writing yourself rather than delegating synthesis to a black-box research agent. A native Deep Research feature or an agentic research tool (for example ChatGPT Deep Research or Tavily's `tavily_research`) may be used for a single fast scouting pass to surface landmark sources and subtopics; treat its output as leads to verify, not as the report. Never claim that native Deep Research ran when it did not.
- Research means reading, not running. Do not install software, execute code, or start services to test the subject of the report. Base technical claims and examples on official documentation and other written sources.

Search in rounds: establish terminology and landmark work, investigate each major subtopic, then run targeted searches for recent developments, disagreements, replications, and missing perspectives. Revise the outline when the sources reveal that the initial map was wrong or incomplete.

### Keep a source log

Maintain a working source log in a scratch file alongside the research. Every time you read a source that may be cited, append an entry: title, authors or organization, year, venue or site, URL or DOI, version or spec revision where relevant, and a one-line note on which claims it supports. Long research sessions lose early context; the log is the durable record.

Build every inline citation and the final References section from this log only. Never cite a source known only from a search-result snippet — read the page, the document, or at minimum the abstract before the source can appear in the report.

### Evidence priorities

For **scholarly** topics, prefer sources in this order, adapting to the field:

1. Peer-reviewed original research, systematic reviews, meta-analyses, and scholarly books from reputable academic presses.
2. Current conference proceedings and preprints in fast-moving fields; label preprints and distinguish them from peer-reviewed findings.
3. Standards, specifications, official technical documentation, government data, and reports from authoritative research institutions.
4. High-quality secondary analysis for context or explanation.

For **technology / practitioner** topics, prefer:

1. The official specification, documentation, source repository, release notes, and changelogs.
2. Engineering blogs, design documents, and conference talks by the maintainers or creators.
3. Peer-reviewed papers where they genuinely exist and remain relevant, such as a foundational systems paper.
4. High-quality independent practitioner analysis and benchmarks, checked against the current version.
5. Community sources (issue trackers, Q&A sites, forums) as leads and as evidence of real-world pain points, labeled as anecdotal.

For **mixed** topics, use both hierarchies and attribute claims to the right kind of source.

In every mode, use tertiary summaries, marketing pages, SEO content, and unsourced commentary only to discover better sources, not as the backbone of the report. A maintainer's documentation is a primary source; the same organization's promotional copy is not. Prefer the original paper or official publication over a page describing it.

Prioritize recent sources for the current state of the field, but retain older ones that established a theory, method, or result. Record publication dates and search through the present date. For fast-moving claims, verify that a newer source has not superseded an older one. For technology topics, record the software version or specification revision each claim describes and check whether the current release has changed the behavior.

Triangulate important or contested claims. Represent meaningful disagreements instead of flattening them into false consensus. Separate established findings, reasonable interpretations, emerging evidence, and speculation. Never invent a citation, DOI, quotation, statistic, or access date.

### When to stop, and thin or blocked evidence

- Stop searching at saturation: when new rounds mostly return sources already in the log and stop surfacing new subtopics. As a rough scale, a default-length report usually rests on 25–50 distinct quality sources; a shorter report on fewer.
- If an important source is paywalled, work from its abstract plus a reputable secondary description of it, and label that clearly.
- If the literature or documentation is genuinely sparse, say so in the report and write a shorter one. Never pad to reach a length.
- Note explicitly in the report anything within scope that could not be covered.

## 4. Write the Report

Default to roughly 5,000–10,000 words, expanding or contracting with the topic. Favor coverage and explanatory value over hitting a word count.

Draft directly into the output file rather than composing the whole report in one pass: write the title, metadata, and section headings first, then fill the sections in order, saving as you go. This keeps long reports from degrading or truncating near the end and makes the audit a genuine second pass over a complete file.

Use this framework, adapting the topic-specific body rather than forcing every subject into identical headings:

```markdown
# [Descriptive Report Title]
**Author:** [the AI system that produced the report]

**Prepared:** [Month Day, Year]

**Research current through:** [Month Day, Year]

## Executive Summary
[The central ideas, state of evidence, major debates, and why the topic matters.]

## Learning Objectives
[What an intermediate reader should understand after reading.]

## Key Concepts and Terminology
[A compact Markdown table or definition list.]

## The Big Picture
[The organizing model and boundaries of the topic.]

## [Topic-specific sections]
[Foundations, mechanisms, methods, subfields, applications, and connections in a logical sequence.]

## Evidence, Debates, and Limitations
[What is well supported, what is disputed, methodological limits, and common misconceptions.]

## The Current Frontier
[Recent developments, open questions, and promising directions.]

## Practical Implications
[Consequences for practice, policy, design, or further study where relevant.]

## References
[Complete linked references for every source cited, built from the source log.]
```

### Adapting the framework

For a **literature review**, reorganize the body around the literature itself:

- Replace Learning Objectives with a short scope note: what was searched, what kinds of sources were included, and the boundaries of the review.
- Organize the topic-specific sections around themes, schools of thought, and debates in the literature, comparing methods and findings across studies rather than only reporting conclusions.
- Make Evidence, Debates, and Limitations the center of gravity, and end with identified gaps and directions for future research.

For a **technology explainer**, keep the orienting sections but adjust the body:

- Explain the architecture: the pieces, how they fit together, and why the design is shaped the way it is.
- Include short illustrative examples in fenced code blocks where a few lines show more than a paragraph — configuration, queries, message formats — drawn from official documentation and checked against the current version. Do not run them; attribute them to their source.
- State the software version or specification revision the report describes alongside the research-current-through date.
- Replace Evidence, Debates, and Limitations with tradeoffs, known limitations, and when not to use the technology, comparing honest alternatives.
- Replace Practical Implications with getting-started guidance pointing at official documentation and tutorials.

### Depth and teaching style

- Assume basic familiarity; briefly refresh foundations, then reach the level where methods, mechanisms, tradeoffs, and evidence can be examined precisely.
- Explain how and why, not merely what. Include concrete examples, boundary cases, and quantitative findings where they matter.
- Use analogies and metaphors as bridges into difficult ideas. Make their limits clear so the bridge is not mistaken for the terrain.
- Keep the voice casual, direct, and intellectually serious. Vary sentence length and avoid hype, canned transitions, and textbook stiffness.
- Define specialist terms on first use even when they also appear in the terminology section.
- Use tables only when comparison is genuinely easier in rows and columns. Keep them narrow enough for an e-reader, preferably five columns or fewer.

### Citations and formatting

Cite substantive factual claims where they appear, using readable Markdown links. For papers, use `[Author et al., 2025](https://doi.org/...)` with DOI or stable publisher links. For technical sources, link the specific documentation page, specification section, or release note with descriptive link text, and name the version or revision in the prose when the claim is version-dependent. Add a complete References section built from the source log with title, author or organization, year, venue or site, and link.

Do not rely on Markdown footnote syntax, HTML, YAML front matter, embedded scripts, or layout-dependent diagrams. These convert poorly to EPUB. Use headings, paragraphs, lists, blockquotes, fenced code, and simple tables only. Write descriptive link text; do not use bare URLs throughout the body.

Write mathematics in plain text or Unicode (or a fenced code block for longer derivations); LaTeX delimiters such as `$...$` do not render in the EPUB pipeline. Describe important figures and diagrams in prose — the pipeline is text-only.

## 5. Audit and Save

Audit the finished file as a separate pass over the complete draft:

- Verify the report answers the central question and covers the important subtopics; note explicitly anything within scope that was left out.
- Check every citation against the source log. Each must correspond to a source actually read during research; remove or replace any that do not.
- Re-fetch a sample of linked sources — all of them when feasible, and always the ones carrying the most important claims — and confirm the title, author, year, and version where relevant match the citation, and that the source supports the nearby statement.
- Scan for quantitative claims, quotations, and named findings that lack a citation; support or delete them.
- Confirm current claims rely on current sources and foundational claims retain landmark sources.
- Confirm uncertainty, source limitations, and scholarly or practitioner disagreement are visible.
- Confirm analogies clarify rather than replace technical explanation.
- Confirm headings form a useful EPUB table of contents, no section depends on color or page layout, and no LaTeX, HTML, or footnote syntax remains.

Save the result as `research_<snake_case_topic>.md` in the user's current working directory unless another path is requested. Keep the filename under about 60 characters and strip diacritics and special characters.

Report the absolute path. If the user also asks for an e-book or reader delivery, pass this Markdown file to `convert-to-epub` or `send-to-reader` rather than duplicating their conversion or upload workflows.
