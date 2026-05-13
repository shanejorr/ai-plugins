---
name: create-lesson
description: Generate a full numbered English lesson for the tutoring project at /Users/shaneorr/Documents/English — creates the instructor lesson plan (Lesson_NN_teacher.pdf) in Teacher Materials/, a shared grammar/topic notes reference sheet, and per-kid practice materials for Camillo and Luciana in Student Materials/Lesson_NN/. Use whenever Shane says "create lesson N", "build lesson N", "make lesson N", "generate lesson N", "prep lesson N", or any similar phrasing that references a specific lesson number. Trigger even if he only names the lesson number without enumerating the four artifacts — producing the complete set is the whole point of the skill.
---

# Create Lesson

End-to-end builder for one full lesson. Given a lesson number, produce exactly four PDFs in the correct local folders:

1. `Lesson_NN_teacher.pdf` — instructor lesson plan (what Shane teaches from) → `Teacher Materials/`
2. `Notes_<TOPIC>_SHARED.pdf` — shared reference sheet on the grammar/topic → `Student Materials/Lesson_NN/`
3. `Materials_Camillo.pdf` — Camillo's personalized reading + practice + homework → `Student Materials/Lesson_NN/`
4. `Materials_Luciana.pdf` — Luciana's personalized reading + practice + homework → `Student Materials/Lesson_NN/`

`CLAUDE.md` at the project root is authoritative for student profiles, tone, CEFR targeting, and constraints. Don't restate that brief here — just follow it.

## Before you draft anything

Read these first. The project evolves; skipping this step is how you re-teach grammar, reuse character names, and drift off-level.

- `CLAUDE.md` — authoritative brief.
- `Progress/Lesson_Schedule.md` — find the entry for lesson N. The topic and description there is the default unless Shane says otherwise.
- `Progress/coverage_tracker.md` — what's been taught, what stuck, review queue, and the interest-rotation tally.
- `Progress/vocabulary_log.md` — words already glossed, so you don't re-gloss.
- The last two or three existing `Lesson_NN/` folders — so you don't reuse character names or scenarios.

## Confirm scope before drafting

Use `AskUserQuestion` only where there is real ambiguity. Typical questions worth asking:

- If prior lessons shifted and the schedule's topic for N may no longer fit, confirm the topic.
- If the interest-rotation tally in `coverage_tracker.md` is lopsided, confirm which kid's interests lead the shared material.
- If `Lesson_NN/` already exists with files, confirm before overwriting.

If the schedule entry is clean and the rotation is balanced, skip the question. Just say briefly what you're proceeding with (topic, featured interest for shared content) and start drafting.

## What each artifact contains

Pitch everything to CEFR A1 unless the schedule says otherwise. When in doubt, aim at Luciana's level — she is the slower learner on paper and anxious about English. Camillo's IQ-report accommodations (chunking, visual aids, short dictations, varied evaluation formats) are good defaults for both.

### Lesson_NN_teacher.pdf — instructor lesson plan

One shared document. Shane holds this while teaching. Include:

- Header: lesson number, topic, date blank, estimated total time
- 2–4 measurable learning objectives
- Materials list
- Five sections, each with minute estimate and language-of-instruction label (Spanish / English / mixed): **Warm-up**, **Teaching**, **Guided Practice**, **Independent Practice**, **Wrap-up**
- Concrete board-work examples the teacher should write out
- Differentiation notes: where to lean on Camillo's accommodations, where to buffer Luciana's anxiety (low-stakes openers, no cold-call public reading)
- Anticipated A1 Spanish-speaker error patterns for this grammar point, with a one-line fix each
- Homework line that points to the per-kid materials PDFs

Default language routing: Spanish when introducing a new rule, English for drilling and production. Label it explicitly.

### Notes_<TOPIC>_SHARED.pdf — shared reference sheet

One shared document both kids keep. It is the "cheat sheet" for the grammar point:

- Brief Spanish explanation of the rule (a few sentences, not a lecture)
- Form tables — conjugation, subject-pronoun chart, spelling-rule table, whatever fits
- A handful of clear English example sentences with Spanish translation alongside
- Common Spanish → English pitfalls for this structure
- A small glossary only if this topic brings in new high-frequency words

File name uses the grammar/topic in upper snake case: `Notes_TO_BE_SHARED.pdf`, `Notes_PRESENT_SIMPLE_SHARED.pdf`, `Notes_ARTICLES_AND_PLURALS_SHARED.pdf`.

### Materials_Camillo.pdf and Materials_Luciana.pdf

Per-kid independent practice and homework. Tailor to each kid's interests per CLAUDE.md. Each should include:

- A short reading passage (A1: 100–180 words; A2: 180–300) that uses the target grammar naturally and introduces no structure not yet taught
- 4–6 comprehension questions (mix true/false, short answer, multiple choice)
- A vocabulary box with Latin American Spanish translations for any word above A1
- A targeted practice worksheet (fill-in, matching, transform, build-a-sentence) drilling the target grammar
- A short dictation section — especially for Camillo (per his IQ-report recommendation). Luciana benefits from one too.
- A brief homework prompt asking for 3–5 sentences using the target grammar about the kid's own life

Interest cues (from CLAUDE.md): Camillo leans soccer (Real Madrid, Ronaldo), anime, drawing, Bible stories, video games. Luciana leans volleyball, fashion, reggaeton, Catholic faith, friendship, *Lilo & Stitch*, real US-school situations (ordering food, asking a teacher for help, meeting classmates).

Never use adoption, foster, or biological-family history as topic material. Vary character names across lessons — grep the last few lesson folders if unsure.

## Workflow

1. **Read.** `CLAUDE.md`, the schedule entry for N, `coverage_tracker.md`, `vocabulary_log.md`, and the last two or three `Lesson_NN/` folders.
2. **Confirm scope.** Ask only about real ambiguities; otherwise state briefly what you're proceeding with.
3. **Draft in markdown first.** Create four `.md` drafts in your outputs directory. Markdown is faster to iterate and the `pdf` skill renders it cleanly.
4. **Self-check each draft against CLAUDE.md:**
   - Vocabulary at or below A1 except glossed items
   - Spanish glosses use Latin American Spanish
   - Only grammar already taught (per `coverage_tracker.md`) plus the current target
   - Fresh character names; scenarios not reused from recent lessons
   - Right kid's interests in the right file; shared content reflects the rotation you chose
   - No forbidden topics
   - Length within A1 reading targets
5. **Render to PDF.** Invoke the `pdf` skill to convert each markdown draft. Output paths:
   - `/Users/shaneorr/Documents/English/Teacher Materials/Lesson_NN_teacher.pdf`
   - `/Users/shaneorr/Documents/English/Student Materials/Lesson_NN/Notes_<TOPIC>_SHARED.pdf`
   - `/Users/shaneorr/Documents/English/Student Materials/Lesson_NN/Materials_Camillo.pdf`
   - `/Users/shaneorr/Documents/English/Student Materials/Lesson_NN/Materials_Luciana.pdf`
   Create `Student Materials/Lesson_NN/` if it does not exist. `Teacher Materials/` is always flat — no subfolders. If files already exist, confirm before overwriting.
6. **Upload PDFs to Google Drive.** Two separate Drive destinations — run the bundled script via Bash:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/create-lesson/scripts/upload_to_drive.py" \
     --lesson <N> \
     --student-pdf "/Users/shaneorr/Documents/English/Student Materials/Lesson_NN/Notes_<TOPIC>_SHARED.pdf" \
     --student-pdf "/Users/shaneorr/Documents/English/Student Materials/Lesson_NN/Materials_Camillo.pdf" \
     --student-pdf "/Users/shaneorr/Documents/English/Student Materials/Lesson_NN/Materials_Luciana.pdf" \
     --teacher-pdf "/Users/shaneorr/Documents/English/Teacher Materials/Lesson_NN_teacher.pdf"
   ```

   - **Student PDFs** (`--student-pdf`) → Drive folder `1yO_leuifYFIMZItGECZ1BaqJ1nI2CJ1F`, inside a `Lesson_NN` subfolder (created if absent).
   - **Teacher PDF** (`--teacher-pdf`) → Drive folder `1eIHmpZ7PQIKBLsi2WPhOcE4ItFOLXr_q`, uploaded flat (no subfolder).

   The script prints a JSON summary with `student_subfolder_url` and `teacher_file_url`. If a file with the same name already exists, it is updated in place so Drive share links stay stable.

   **Auth.** Non-interactive service account. The script reads a JSON key from `~/.config/create-lesson/service_account.json`. No browser, no consent flow, no token expiry. If the key is missing, the script exits cleanly and points at the setup walkthrough in its docstring. One-time setup: create a Google Cloud project, enable the Drive API, create a service account, download its JSON key, place it at the path above, and share the target Drive parent folder with the service account's email (as Editor). Full steps are in the script's docstring.

   **Expected ownership quirk.** Files uploaded by the service account are *owned* by the service account, not by Shane. They appear in his Drive via the shared parent folder, but the Owner column shows the SA email. For regenerable lesson PDFs this is fine; flag it only if Shane asks why ownership looks odd.

   **Dependencies.** The script needs `google-api-python-client` and `google-auth-httplib2`. If the script bails on `ImportError`, install them with `pip install --break-system-packages google-api-python-client google-auth-httplib2` and retry.

   **Common first-run error.** A `403`/`404` from the Drive API almost always means the parent folder has not been shared with the service account. The script's error message will print the SA's email — share the folder with that address as Editor, then retry.

   Parse the script's JSON output to get `subfolder_url` and include it in the final share message.
7. **Share the files.** Return all four local paths (as `computer://` links if available), the Drive student subfolder URL, and the Drive teacher file URL. Note for Shane that the teacher plan goes to a separate Drive folder from the student materials. Do **not** update `coverage_tracker.md` or `vocabulary_log.md` — per CLAUDE.md those only get updated after Shane confirms the lesson was taught.

## CEFR self-check (do this before rendering)

Re-read each reading passage as if you are a true Spanish-speaking beginner. Red flags:

- Subordinate clauses where a simple sentence works
- Intermediate vocabulary with no gloss
- Tenses or structures the schedule says haven't been introduced yet
- Idioms or cultural references that need unpacking

If you catch any of these, revise the markdown before rendering.

## What not to do

- Don't write anything the kids will submit as their own work. These materials are for practice, not for them to turn in.
- Don't update `coverage_tracker.md` or `vocabulary_log.md` preemptively.
- Don't scatter files at the project root — student materials go in `Student Materials/Lesson_NN/`, teacher plan goes in `Teacher Materials/` (flat).
- Don't delete or silently overwrite an existing lesson folder.
- Don't put helper scripts in the lesson folder. If you need one, it goes in `Progress/scripts/`.
