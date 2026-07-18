---
name: update-resume
description: >-
  Recommend how to tailor a resume to a specific job description. Use when the
  user asks to update, tailor, or adapt their resume for a job. Takes a job
  description Markdown file, a resume Markdown file, and optionally additional
  career-information files. Prints recommendations and does not edit the
  resume.
---

# Update resume

Compare a resume against a job description and print concrete recommendations for tailoring the resume to that job. This skill only produces recommendations — it does not modify the resume file.

## Input

- **Job description file** (required) — a markdown file, typically in `job_descriptions/` (e.g. captured with the capture-job-description skill).
- **Resume file** (required) — a markdown file (e.g. `resume.md` or a resume template file).
- **Career info files** (optional) — zero or more additional markdown files with supporting material, e.g. `linkedin.md`, `linkedin_summary.md`, `career_info.md`.

## Steps

1. **Validate inputs.** Check that both a job description file and a resume file were provided as arguments and that both files exist on disk.
   - If either argument is missing, or either file does not exist, tell the user exactly what is missing (e.g. "The job description file `job_descriptions/foo.md` does not exist") and stop. Do not guess at filenames or substitute other files.
   - If an optional career info file is listed but doesn't exist, note it and continue with the files that do exist.

2. **Read all files.** Read the job description, the resume, and any career info files provided.

3. **Analyze the match.** Compare the resume against the job description:
   - Which required and preferred qualifications the resume already demonstrates, and where.
   - Which requirements the resume addresses weakly or not at all.
   - Experience in the career info files that is relevant to the job but missing or underemphasized in the resume.
   - Keywords and terminology from the posting (tools, methods, domain language) that the resume should mirror for both human reviewers and applicant tracking systems.
   - Content in the resume that is irrelevant to this job and could be trimmed or de-emphasized to make room.

4. **Print recommendations.** Output the recommendations directly in the response (do not write a file unless the user asks) using this structure:

```
## Resume recommendations: <Job Title> — <Organization>

### Fit summary
2-4 sentences on overall alignment between the resume and the job.

### Summary / headline
Suggested rewording of the resume's professional summary to lead with
what this job values most.

### Experience section
Per role or bullet: what to reword, add, reorder, or cut — with
suggested replacement text where a specific change is recommended.

### Skills section
Skills to add, rename to match the posting's terminology, or remove.

### Content to pull from career info
Relevant experience found in the supplemental files but absent from the
resume, with a suggested bullet for where it should go. (Omit this
section if no career info files were provided.)

### Gaps you cannot close
Requirements the resume genuinely cannot demonstrate — flag them
honestly rather than suggesting embellishment.
```

## Notes

- Every recommendation must be grounded in the provided files — never invent experience, employers, dates, or accomplishments that don't appear in the resume or career info files.
- Keep suggested wording in the voice and format of the existing resume.
- If the project has job preferences (`job_preferences.md` in the project root, or a job-preferences section in `CLAUDE.md` / `AGENTS.md`), use them for context — but the job description file is the authority on what this specific job requires.
