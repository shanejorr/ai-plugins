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

Find open roles that fit the user and write them to a dated markdown file. Cast
a **wide net of ~20–30 roles** per run, ranked by fit — but every role in the
report must be **verified open against the employer's own job board or ATS
during this run** (Step 2). Verified count beats padded count.

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

Use an available web search tool for queries and a page-fetching or extraction
tool to open promising listings. If a board is JavaScript-heavy and a fetch
returns an empty shell, use an available browser-control tool to read the
rendered page. Run several queries per source type; don't rely on one search.
Adapt the board list to the user's sector — the mission-driven boards below
only apply when the user targets that sector.

This step is **discovery only**. Everything found here is a candidate, not an
open role, until it clears the verification gate in Step 2.

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
3. **Verified open?** See the verification gate below. This is mandatory.

### The verification gate (mandatory)

> **A role may only be included if its posting was verified open during this
> run against the employer's live job board or ATS. Never rely on a web-search
> result title, a cached page, or a previous run as evidence a job is open.**

A search hit proves the posting *existed*, not that it's *open* — search engines
keep job postings indexed for weeks or months after the req closes. Every role
needs its own live check, in this run, against an authoritative source.

**Greenhouse** — use the JSON API, not the HTML page:
- All live jobs on a board:
  `https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs`
- A single job:
  `https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs/{job_id}` —
  a **404 means closed**.
- A role counts as open **only if its `job_id` appears in the board's live
  list**.
- **Trap:** when a Greenhouse posting closes, its job URL *redirects to the
  board index page*. Fetching a closed job URL therefore returns board-listing
  HTML that looks like "a page loaded with job content." That is **not** proof
  the job exists. Treat any redirect of a job URL to the board root — or a
  404 — as definitive proof the job is **closed**.

**Lever** — `https://api.lever.co/v0/postings/{company}?mode=json` returns the
live postings. The job must appear there.

**Ashby** — `https://api.ashbyhq.com/posting-api/job-board/{org}` (or the org's
`jobs.ashbyhq.com/{org}` board). The job must appear in the current list.

**Workday / iCIMS / other JS-rendered boards** — confirm the exact posting is
present on the employer's own current careers listing, using a browser-control
tool if a plain fetch returns an empty shell. If the page can't be read, or
only returns metadata, mark the role **unverified** and exclude it (or move it
to a clearly-labeled "could not verify" section) — never list it as open.

**Aggregators (LinkedIn, Indeed, Idealist, ZipRecruiter, Glassdoor, etc.)** —
never sufficient on their own. Always resolve to the employer's own board/ATS
and verify there before including.

**Fallback rule:** if a posting cannot be verified against an authoritative
live source, do not present it as an open role. It may be omitted, or listed in
a separate "unverified — confirm before applying" section, but it must never
appear in the ranked matches.

Record, for each surviving role, **what source verified it** (e.g. "Greenhouse
board API") — Step 3 requires it in the report.

Score remaining roles by preference fit (sector, industry, org size, schedule)
and sort best-first. Include some reasonable stretch/adjacent roles, but mark
them clearly. The ~20–30 target is a stretch goal and is **subordinate to every
listed role being confirmed live** — never relax the verification gate to hit a
count.

Prefer a **direct company-website application link** — and that link must be the
one you verified. If you only have an aggregator link (LinkedIn/Indeed), find
the role on the company's own careers page or ATS, verify it there, and use that
link.

De-duplicate the same role appearing on multiple boards.

## Step 3 — Write the report

Compute today's date with `date +%Y-%m-%d` — use it both for the filename and
for the per-role verification notes — and save to the **project root**:
`job-search-{YYYY-MM-DD}.md` (e.g., `job-search-2026-06-21.md`).

Before writing, re-check the list: **every role in "Strong matches" and
"Stretch / adjacent roles" must have passed the Step 2 verification gate in this
run.** Any role without an authoritative live check goes in the "Unverified"
section or gets dropped — it does not go in the ranked matches.

Use this structure:

```markdown
# Job Search — {Month DD, YYYY}

_{N} verified-open roles found. Sorted by fit. Hard filters applied: {the user's
hard requirements, e.g. remote, ~5+ years, data/analytics/AI function}. Every
role below was confirmed open against the employer's ATS/job board on
{YYYY-MM-DD}._

## Strong matches

### {Job Title} — {Company}
- **Link:** {verified direct company/ATS application URL}
- **Verified:** open on {source, e.g. Greenhouse board API · Lever API · company careers page} as of {YYYY-MM-DD}
- **Location:** {Remote / Remote-US / city} · **Type:** {Full-time / Part-time} · **Seniority:** {e.g., 5+ yrs}
- **Sector/Industry:** {nonprofit · education, etc.} · **Org size:** {if known}
- **Overview:** {One short paragraph: what the role does, key responsibilities,
  required skills, and a sentence on why it fits the user.}

### {next role...}

## Stretch / adjacent roles

### {Job Title} — {Company}
- {same fields, including the **Verified:** line; note why it's a stretch}

## Unverified — confirm before applying

_Roles that looked promising but could not be confirmed open against an
authoritative source. Treat as leads, not openings._

### {Job Title} — {Company}
- **Link:** {best available URL}
- **Why unverified:** {e.g. Workday board would not render; only found on LinkedIn}
```

Rules for the report:
- One paragraph overview per job (2–5 sentences), not a wall of text.
- Always include a working link; never invent URLs — only list roles you
  actually found, opened, and verified.
- Every role under "Strong matches" or "Stretch / adjacent roles" carries a
  **Verified:** line naming the authoritative source and the date. No
  verification line means the role does not belong in those sections.
- Omit the "Unverified" section entirely if it's empty.
- If a field is unknown, write "Not specified" rather than guessing.
- Group into "Strong matches," "Stretch / adjacent roles," and "Unverified."

## Step 4 — Wrap up

After saving, present the file to the user and give a one-line summary (e.g.,
"Found 24 verified-open roles; 15 strong matches, top one is X at Y"). If the
verification gate cut the list well below the target, say so plainly rather than
padding. Offer to tailor their
resume or write a cover letter for any of them, and offer to schedule the
search to run on a regular cadence.

## Notes

- Job boards change; if a listed board is dead, skip it and lean on web search.
  Web search is fine for *discovery* — it is never sufficient for *verification*.
- Don't fabricate listings to reach the target count — fewer real roles beats
  padded results. **It is better to report 5 verified-open roles than 25
  unverified ones.**
- Stale postings are the main failure mode of this skill. Search indexes,
  aggregators, and caches all outlive the reqs they describe. When in doubt,
  leave the role out.
