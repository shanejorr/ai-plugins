---
name: scrape-linkedin
description: Scrape a LinkedIn profile page by username and save a structured markdown summary to linkedin_summary.md in the project root. Use whenever the user asks to scrape, capture, pull, refresh, or summarize a LinkedIn profile or LinkedIn page — e.g. "/scrape-linkedin some-username", "scrape my linkedin", "update my linkedin summary". Takes one argument: the LinkedIn username (the slug after linkedin.com/in/).
---

# Scrape LinkedIn profile

Fetch a LinkedIn profile page and save its contents as a structured markdown file, `linkedin_summary.md`, in the project root.

## Input

One argument: the LinkedIn **username** — the slug in the profile URL after `linkedin.com/in/`. If the user pasted a full URL, extract the slug from it. If no username was provided, ask for it before proceeding.

Build the target URL: `https://www.linkedin.com/in/<username>/`

## Getting the page text

LinkedIn aggressively blocks anonymous scraping: unauthenticated requests usually get an "authwall" (a sign-in / join page) instead of the profile. So try the methods below **in order**, moving to the next one whenever a fetch fails or fails the validity check.

**Validity check (apply after every attempt):** the text counts as a real profile only if it contains actual profile content — the person's headline plus recognizable sections like Experience, Education, or Skills. If the text is dominated by "Sign in", "Join LinkedIn", "Join now", or is just a page shell / cookie notice, treat the attempt as failed and fall through to the next method.

### 1. Web fetch

Try a direct fetch of the URL first — it's nearly free and non-intrusive, though it usually hits the authwall:

- Prefer the Tavily tools if available (`tavily_extract` on the profile URL, with `extract_depth: "advanced"`).
- Otherwise use the built-in `WebFetch` tool.

Don't retry variations if this fails — one clean attempt, then move on.

### 2. Chrome MCP (user's real browser — most likely to succeed)

The user's own Chrome is typically **logged in to LinkedIn**, which bypasses the authwall entirely. Use the Claude in Chrome tools (`mcp__claude-in-chrome__*`; load them via ToolSearch if deferred):

1. `navigate` to the profile URL, wait a moment for it to render.
2. `get_page_text` to read the content.
3. Profile pages truncate long sections. If Experience/About entries end with "…see more", scroll down and expand them (or visit `https://www.linkedin.com/in/<username>/details/experience/` for the full experience list) and read again.

### 3. Other browser automation for the user's real browser

If the Claude in Chrome extension isn't connected but another tool can drive the user's logged-in browser (e.g. an AppleScript-based Chrome controller), use it the same way:

1. Open the profile URL, wait a few seconds for it to render.
2. Read the page text.
3. For truncated sections, open the details pages (e.g. `.../details/experience/`) and read those too.

### 4. Playwright (headless browser)

Only worth trying when no logged-in browser path is available: it is unauthenticated, so it faces the same authwall as web fetch, and headless Chromium is more likely to be bot-flagged. Run the bundled script **only if Playwright is already installed** — do not download Chromium (~150MB) just to attempt this tier:

```bash
node <skill-dir>/scripts/scrape_profile.mjs <username>
```

It prints the rendered page text to stdout. If it reports Playwright is missing, skip this tier (mention to the user that installing it — `npm install playwright && npx playwright install chromium` in the scripts dir — would enable it for future runs).

### 5. Other fallbacks

- Try any available in-app browser pane — it won't be logged in, but occasionally renders public profiles.
- **Save to PDF (manual, reliable):** ask the user to open the profile in their browser, click **More → Save to PDF** (LinkedIn's native profile export), and drop the downloaded PDF into the project root. Read the PDF and build the summary from it. This captures the full profile cleanly and beats copy-pasted page text.

If every method returns only an authwall, tell the user plainly which methods were tried and why they failed — do not fabricate profile content from memory or from search snippets.

## Writing linkedin_summary.md

Save to `linkedin_summary.md` in the **project root** (the directory containing `CLAUDE.md` / `AGENTS.md`). If the file already exists, overwrite it — it is a refreshable snapshot.

Use this structure:

```
# <Full Name>

**Headline:** <headline>

**Location:** <location>
**LinkedIn:** [www.linkedin.com/in/<username>](https://www.linkedin.com/in/<username>)
**Connections:** <count, if visible>

---

## Experience

### <Job Title>
**<Company> · <Employment type>**
*<Start> – <End> · <duration>*
<Location> · <Remote/Hybrid/On-site if shown>

<Role description paragraph, if present>

- <accomplishment bullets as written on the profile>

**Skills:** <skills tagged on that role, if shown>

---
(repeat one `###` block per role, separated by `---`)

## Education

### <School>
**<Degree>**
*<Years>*
<Activities/societies, if shown>

## Skills

- <one bullet per skill>

## Projects

### <Project name>
<Project description>

## Interests

<Companies, groups, etc., if visible>
```

Guidelines:

- Stay faithful to the profile text — preserve the person's own wording in descriptions and bullets. Don't editorialize, condense, or rewrite.
- Only include sections that actually appear on the page (About, Licenses & Certifications, Volunteering, Publications, etc. get their own `##` sections if present); omit empty ones.
- Separate major entries with `---` horizontal rules.

## Wrap up

Tell the user the file was written, which fetch method ultimately worked, and note anything that couldn't be captured (e.g. truncated sections, hidden connection count).
