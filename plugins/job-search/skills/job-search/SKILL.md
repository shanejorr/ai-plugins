---
name: job-search
description: >-
  Search the internet for open jobs that match the user's preferences and
  experience, then compile them into a dated markdown report. Use when the user
  says "find jobs", "search for jobs", "run a job search", "any new roles?",
  "look for openings", or otherwise asks to locate job opportunities. Searches
  nonprofit/mission boards, general remote boards, niche boards, and company
  career pages, then saves results to job-search-{date}.md.
---

# Job Search

Find open roles that fit the user and write them to a dated markdown file. Aim
for a **wide net of ~20–30 roles** per run, ranked by fit.

## Step 0 — Load the user's preferences

Before searching, gather the user's job preferences and background. Check these
sources in order and read every one that exists (all paths relative to the
project root):

1. `job_preferences.md` — the plugin's preference file (see the template at
   `<plugin-dir>/templates/job_preferences.md`)
2. A **job preferences** section in the project's `CLAUDE.md` or `AGENTS.md`
3. Career info files, if present: `career_info.md`, `linkedin.md`,
   `linkedin_summary.md`, a resume markdown file

From these, establish:

- **Hard requirements** — conditions a role must meet (location/remote,
  function, seniority). Roles failing these are dropped.
- **Strong preferences** — factors that rank a role higher but don't
  disqualify (sector, industry, org size, schedule, salary).
- **Keywords** — job titles and skills to seed searches, paired with sector
  terms.

If **no preference source exists**, ask the user for their hard requirements,
preferences, and a short professional profile before searching, and offer to
save the answers to `job_preferences.md` (using the plugin template) so future
runs are automatic.

## Step 1 — Search across all four source types

Use a web search tool for queries and a fetch/extract tool (e.g. Tavily
`tavily_extract` or `WebFetch`) to open promising listings. If a board is
JavaScript-heavy and a fetch returns an empty shell, use browser tools (e.g.
Claude-in-Chrome) instead. Run several queries per source type; don't rely on
one search. Adapt the board list to the user's sector — the mission-driven
boards below only apply when the user targets that sector.

**1. Nonprofit / mission boards** (when the user targets mission-driven work)
- Idealist (idealist.org)
- Work for Good (workforgood.org)
- The Chronicle of Philanthropy jobs (jobs.philanthropy.com)
- 80,000 Hours job board (jobs.80000hours.org) — good for high-impact/AI roles
- Tech Jobs for Good (techjobsforgood.com)
- Example query: `remote senior data analyst nonprofit education site:idealist.org`

**2. General + remote boards**
- LinkedIn Jobs, Indeed
- We Work Remotely (weworkremotely.com)
- RemoteOK (remoteok.com)
- Built In (builtin.com)
- Example query: `remote "<job title>" <sector term> <seniority> years`

**3. Niche boards for the user's field**
- Pick boards specific to the user's function (e.g. ai-jobs.net or Kaggle Jobs
  for data/AI roles; equivalent niche boards for other fields)
- Example query: `remote <job title> part time <industry term>`

**4. Company career pages (direct)**
Target organizations in the user's preferred industries and check their careers
pages directly (a direct company link is preferred for the report). Brainstorm
the *kinds* of org that fit the user's sector/industry preferences — then
confirm each is currently hiring.
- Example query: `"<industry term>" careers <job title> remote`

## Step 2 — Screen each candidate role

Open the listing and confirm before including it:

1. **Hard requirements met?** Check each hard requirement from Step 0 (e.g.
   remote, seniority level, function). Drop roles that fail any of them.
2. **Function fit?** Must match the user's target function, not adjacent
   (e.g., if they want data/analytics, not a pure software engineering or
   marketing role).
3. **Still open?** Skip listings that look closed/expired.

Score remaining roles by preference fit (sector, industry, org size, schedule)
and sort best-first. Include some reasonable stretch/adjacent roles to hit the
~20–30 target, but mark them clearly.

Prefer a **direct company-website application link**. If you only have an
aggregator link (LinkedIn/Indeed), do a quick search for the role on the
company's own careers page and use that link when found.

De-duplicate the same role appearing on multiple boards.

## Step 3 — Write the report

Compute today's date with `date +%Y-%m-%d` and save to the **project root**:
`job-search-{YYYY-MM-DD}.md` (e.g., `job-search-2026-06-21.md`).

Use this structure:

```markdown
# Job Search — {Month DD, YYYY}

_{N} roles found. Sorted by fit. Hard filters applied: {the user's hard
requirements, e.g. remote, ~5+ years, data/analytics/AI function}._

## Strong matches

### {Job Title} — {Company}
- **Link:** {direct company URL preferred, else board URL}
- **Location:** {Remote / Remote-US / city} · **Type:** {Full-time / Part-time} · **Seniority:** {e.g., 5+ yrs}
- **Sector/Industry:** {nonprofit · education, etc.} · **Org size:** {if known}
- **Overview:** {One short paragraph: what the role does, key responsibilities,
  required skills, and a sentence on why it fits the user.}

### {next role...}

## Stretch / adjacent roles

### {Job Title} — {Company}
- {same fields; note why it's a stretch}
```

Rules for the report:
- One paragraph overview per job (2–5 sentences), not a wall of text.
- Always include a working link; never invent URLs — only list roles you
  actually found and opened.
- If a field is unknown, write "Not specified" rather than guessing.
- Group into "Strong matches" and "Stretch / adjacent roles."

## Step 4 — Wrap up

After saving, present the file to the user and give a one-line summary (e.g.,
"Found 24 roles; 15 strong matches, top one is X at Y"). Offer to tailor their
resume or write a cover letter for any of them, and offer to schedule the
search to run on a regular cadence.

## Notes

- Job boards change; if a listed board is dead, skip it and lean on web search.
- Don't fabricate listings to reach the target count — fewer real roles beats
  padded results.
