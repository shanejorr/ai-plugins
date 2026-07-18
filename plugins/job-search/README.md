# job-search

A Claude Code, ChatGPT Work, and Codex plugin for running a job search out of a
project folder: find open roles matching your preferences, capture postings as
Markdown, keep a LinkedIn snapshot fresh, and get resume-tailoring
recommendations.

## Install for Claude Code

```
/plugin marketplace add shanejorr/ai-plugins
/plugin install job-search@shanejorr-plugins
```

## Install for ChatGPT Work and Codex

```bash
codex plugin marketplace add shanejorr/ai-plugins
codex plugin add job-search@shanejorr-plugins
```

Restart ChatGPT or Codex and begin a new task so the installed skills are
loaded. In ChatGPT desktop, the plugin can also be installed from **Plugins**
in Work or Codex after the marketplace is registered.

## Skills

| Skill | What it does |
|-------|--------------|
| `job-search` | Searches job boards and company career pages for roles matching your preferences; writes a ranked report to `job-search-{date}.md` |
| `capture-job-description` | Fetches a job posting URL and saves a clean structured copy to `job_descriptions/<slug>.md`, with a fit assessment |
| `update-resume` | Compares your resume against a captured job description and prints concrete tailoring recommendations (never edits the resume) |
| `scrape-linkedin` | Scrapes a LinkedIn profile by username and saves a structured snapshot to `linkedin_summary.md` |

A typical loop is to ask the assistant to find matching jobs, capture the most
interesting posting from its URL, and then recommend resume changes for that
captured role. In Claude Code, the corresponding slash commands are
`/job-search`, `/capture-job-description`, and `/update-resume`.

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

- Web search and page-fetching tools.
- Optional: a browser connector that can use your logged-in Chrome session
  makes `scrape-linkedin` far more reliable (it can get past LinkedIn's
  authwall) and helps `capture-job-description` with JavaScript-heavy postings.
- Optional: Playwright (`npm install playwright && npx playwright install
  chromium`) enables the headless fallback for `scrape-linkedin`.
