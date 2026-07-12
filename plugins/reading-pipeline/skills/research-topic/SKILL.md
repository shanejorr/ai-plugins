---
name: research-topic
description: "Research a topic in depth and create a current, citation-rich Markdown report for an intermediate reader at upper-level undergraduate depth. Use this skill when the user asks for deep research, a comprehensive research report, a literature-grounded topic overview, a course-level treatment, or broad and deep coverage of a subject rather than a summary of one supplied paper. Prioritize current academic and technical literature, explain specifics with casual analogies and metaphors, and produce output compatible with convert-to-epub and send-to-reader. Do NOT use when the primary task is to summarize a particular research paper; use summarize-research instead."
user-invocable: true
disable-model-invocation: false
---

# Research Topic

## Purpose

Create a standalone research report that gives an intermediate reader both a wide map of a topic and a close view of its machinery. Aim for the breadth and depth of an upper-level undergraduate course unit, but write like an informed guide rather than a textbook committee.

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
2. The concepts and prerequisite ideas the reader needs.
3. The topic's foundations, mechanisms, methods, major subfields, applications, debates, limitations, and active frontier.
4. Cross-disciplinary connections that materially improve understanding.
5. The evidence needed for each major section and the likely primary sources.
6. The report structure, expected depth, and source cutoff date.

Treat the topic as a landscape: map the mountain ranges before inspecting individual rocks. Do not let the first plausible search result dictate the outline.

## 3. Conduct Deep Research

Use the strongest research capability exposed by the current platform:

- **ChatGPT:** Use native Deep Research when it is available. Supply it with the complete research brief, including audience, scope, evidence rules, structure, and output requirements. Cooperate with its clarification step without dropping constraints from the user's request.
- **Claude:** Use the available research, web-search, page-fetching, browser, and document tools to execute the same brief. Search iteratively, follow citations to primary sources, and synthesize only after the evidence base is broad enough.
- **Other OpenAI surfaces:** Use an exposed Deep Research tool or model when available. Otherwise perform a tool-driven multi-source research pass and state the limitation briefly; never claim that native Deep Research ran when it did not.

Search in rounds: establish terminology and landmark work, investigate each major subtopic, then run targeted searches for recent developments, disagreements, replications, and missing perspectives. Revise the outline when the literature reveals that the initial map was wrong or incomplete.

### Evidence priorities

Prefer sources in this order, while adapting to the field:

1. Peer-reviewed original research, systematic reviews, meta-analyses, and scholarly books from reputable academic presses.
2. Current conference proceedings and preprints in fast-moving fields; label preprints and distinguish them from peer-reviewed findings.
3. Standards, specifications, official technical documentation, government data, and reports from authoritative research institutions.
4. High-quality secondary analysis for context or explanation.

Use tertiary summaries, vendor marketing, SEO pages, and unsourced commentary only to discover better sources, not as the backbone of the report. Prefer the original paper or official publication over a page describing it.

Prioritize recent literature for the current state of the field, but retain older sources that established a theory, method, or result. Record publication dates and search through the present date. For fast-moving claims, verify that a newer source has not superseded an older one.

Triangulate important or contested claims. Represent meaningful disagreements instead of flattening them into false consensus. Separate established findings, reasonable interpretations, emerging evidence, and speculation. Never invent a citation, DOI, quotation, statistic, or access date.

## 4. Write the Report

Default to roughly 5,000–10,000 words, expanding or contracting with the topic. Favor coverage and explanatory value over hitting a word count.

Use this framework, adapting the topic-specific body rather than forcing every subject into identical headings:

```markdown
# [Descriptive Report Title]
**Author:** [OpenAI Deep Research, Claude, or the actual research system used]

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

## Further Study
[A short, prioritized reading path with a sentence explaining why each source matters.]

## References
[Complete linked references for every source cited.]
```

### Depth and teaching style

- Assume basic familiarity; briefly refresh foundations, then reach the level where methods, mechanisms, tradeoffs, and evidence can be examined precisely.
- Explain how and why, not merely what. Include concrete examples, boundary cases, and quantitative findings where they matter.
- Use analogies and metaphors as bridges into difficult ideas. Make their limits clear so the bridge is not mistaken for the terrain.
- Keep the voice casual, direct, and intellectually serious. Vary sentence length and avoid hype, canned transitions, and textbook stiffness.
- Define specialist terms on first use even when they also appear in the terminology section.
- Use tables only when comparison is genuinely easier in rows and columns. Keep them narrow enough for an e-reader, preferably five columns or fewer.

### Citations

Cite substantive factual claims where they appear, using readable Markdown links such as `[Author et al., 2025](https://doi.org/...)`. Prefer DOI or stable publisher links for papers and official canonical URLs for technical sources. Add a complete References section with title, author or organization, year, venue, and link.

Do not rely on Markdown footnote syntax, HTML, YAML front matter, embedded scripts, or layout-dependent diagrams. These convert poorly to EPUB. Use headings, paragraphs, lists, blockquotes, fenced code, and simple tables only. Write descriptive link text; do not use bare URLs throughout the body.

## 5. Audit and Save

Before saving, verify that:

- the report answers the central question and covers the important subtopics;
- current claims rely on current sources and foundational claims retain landmark sources;
- every citation resolves to the claimed work and actually supports the nearby statement;
- uncertainty, source limitations, and scholarly disagreement are visible;
- analogies clarify rather than replace technical explanation;
- headings form a useful EPUB table of contents and no section depends on color or page layout;
- the report contains no unsupported quotations, statistics, or fabricated references.

Save the result as `research_<snake_case_topic>.md` in the user's current working directory unless another path is requested. Keep the filename under about 60 characters and strip diacritics and special characters.

Report the absolute path. If the user also asks for an e-book or reader delivery, pass this Markdown file to `convert-to-epub` or `send-to-reader` rather than duplicating their conversion or upload workflows.
