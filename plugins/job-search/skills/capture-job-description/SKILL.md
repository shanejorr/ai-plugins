---
name: capture-job-description
description: Capture a job posting from a URL into a structured markdown file in job_descriptions/. Use when given a job posting web address and asked to save, capture, or record the job description. Takes one argument: the job posting URL.
---

# Capture job description

Fetch a job posting from a URL and save it as a clean, structured markdown file in `job_descriptions/` (created in the project root if it doesn't exist).

## Input

A single job posting URL (passed as the argument). If no URL was provided, ask the user for it before proceeding.

## Steps

1. **Fetch the page.** Use a web fetch tool on the URL (e.g. Tavily `tavily_extract` or `WebFetch`).
   - If the fetch fails or is blocked, tell the user and stop — do not try to retrieve the content another way.
   - If the fetch succeeds but returns only a page shell, a loading spinner, an "enable JavaScript" message, or otherwise no real job content, the page is client-rendered. Switch to browser tools (e.g. Claude in Chrome: `navigate` then `get_page_text`) to read the rendered page.

2. **Pick a filename.** Derive a short, lowercase, hyphenated slug from the organization and/or role (e.g. `project-evident.md`, `acme-data-analyst.md`). Save to `job_descriptions/<slug>.md`. If a file with that name already exists, ask the user before overwriting.

3. **Write the markdown file** using the structure below. Only include sections that the posting actually contains — omit empty ones rather than inventing content. Use prose and bullets that mirror the source; do not editorialize inside the main sections.

```
# <Job Title> — <Organization>

**Source:** <URL>
**Captured:** <today's date, YYYY-MM-DD>

## Quick facts
- Organization, job title, reports to, role type (full/part time + hours),
  salary, location, seniority, hours, travel — whatever the posting states.

## About <Organization>
Short org description from the posting.

## Position summary
The posting's summary of the role.

## Essential duties
The responsibilities, preserving any percentage breakdowns or groupings.

## Education and/or experience
Minimum requirements.

## Knowledge, skills, and abilities
Required and preferred skills.

## Work environment / Physical demands
If present.

## Benefits
If present.

## Notes / fit assessment
A brief assessment against the user's job preferences: strong-fit signals
and watch-outs (e.g. required tools, salary, location, on-site/hours
constraints).
```

4. **Present the file.** Show the user the path to the new file, then give a one- or two-sentence summary highlighting the strongest fit signals and any watch-outs relative to the user's job preferences.

## Job preferences

For the fit assessment, read the user's preferences from (in order): `job_preferences.md` in the project root, or a job-preferences section in the project's `CLAUDE.md` / `AGENTS.md`. If neither exists, skip the fit assessment and note that adding a `job_preferences.md` (template in this plugin's `templates/` directory) enables it.

## Notes

- Keep the markdown faithful to the source. The "Notes / fit assessment" section is the only place for your own judgment.
