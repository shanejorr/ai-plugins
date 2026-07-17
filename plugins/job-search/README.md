# job-search

A Claude Code plugin for running a job search out of a project folder: find
open roles matching your preferences, capture postings as markdown, keep a
LinkedIn snapshot fresh, and get resume-tailoring recommendations.

## Install

```
/plugin marketplace add shanejorr/ai-plugins
/plugin install job-search@shanejorr-plugins
```

## Skills

| Skill | What it does |
|-------|--------------|
| `job-search` | Searches job boards and company career pages for roles matching your preferences; writes a ranked report to `job-search-{date}.md` |
| `capture-job-description` | Fetches a job posting URL and saves a clean structured copy to `job_descriptions/<slug>.md`, with a fit assessment |
| `update-resume` | Compares your resume against a captured job description and prints concrete tailoring recommendations (never edits the resume) |
| `scrape-linkedin` | Scrapes a LinkedIn profile by username and saves a structured snapshot to `linkedin_summary.md` |

A typical loop: `/job-search` → `/capture-job-description <url>` for the
interesting ones → `/update-resume job_descriptions/<slug>.md resume.md`.

## Customize it to your search

The skills read **your** preferences from your project, not from the plugin.
Set up a project folder for your search:

1. Copy `templates/job_preferences.md` (in this plugin) to the root of your
   project as `job_preferences.md` and fill it in — hard requirements,
   preferences, a short profile, and search keywords. A job-preferences
   section in the project's `CLAUDE.md` / `AGENTS.md` works too.
2. Optionally add career context files the skills will pick up:
   `career_info.md`, `linkedin.md` / `linkedin_summary.md`, and your resume
   as markdown.

Everything the skills produce (search reports, captured postings, LinkedIn
snapshots) is written into that project folder.

If you want to change *behavior* — different job boards, a different report
format, another output layout — fork the repo and edit the `SKILL.md` files
directly; they're plain markdown instructions.

## Requirements

- Web search + fetch tools (Tavily MCP preferred; built-in WebSearch/WebFetch
  work too).
- Optional: the Claude in Chrome extension makes `scrape-linkedin` far more
  reliable (it uses your logged-in browser to get past LinkedIn's authwall)
  and helps `capture-job-description` with JavaScript-heavy postings.
- Optional: Playwright (`npm install playwright && npx playwright install
  chromium`) enables the headless fallback for `scrape-linkedin`.
