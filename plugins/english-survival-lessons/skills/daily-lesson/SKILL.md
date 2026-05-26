---
name: daily-lesson
description: "Generate the complete lesson package for a single day (Day 01–20) of Shane's at-home survival English course for his two newly adopted Colombian teens (Luciana 16, Camilo 13). Takes a day number as input, reads ./curriculum/20-day-itinerary.md, and writes into ./lessons/day-NN/: teacher-plan.md (timed lesson flow with discussion questions/emphasis points for each media segment, student-to-student and teacher-to-student activities, differentiation notes for Camilo and Luciana, spaced-repetition coverage table), reading.md plus a rendered reading.pdf (vocabulary preview, controlled-vocabulary text, comprehension questions, cognate spotlight), notes.md (a kid-facing study handout covering vocab, phrases, and any grammar), audio-script.md (AI-TTS-ready script with speaker labels and [PAUSE] markers), and three video scripts (video-script-1.md vocabulary preview, video-script-2.md dialogue model, video-script-3.md task walkthrough — each HeyGen-ready with numbered segments giving avatar/spoken text/on-screen text/visual notes). Spaced repetition is threaded through every media file. Trigger phrases include 'create day N lesson', 'generate day NN', 'build day 7 lesson', 'make the lesson for day 03', 'day NN lesson', 'lesson day NN'."
user-invocable: true
disable-model-invocation: true
---

# Daily Lesson

Generates one full day's lesson package. Given a day number Shane provides, the skill
produces eight files inside `./lessons/day-NN/`.

## Step 1: Resolve the day number

Accept any of: "day 7", "Day 03", "07", or a bare numeric arg. Zero-pad to two digits
everywhere it appears in paths and filenames (`day-07`, not `day-7`).

If the day is outside 1–20, stop and tell Shane.

The lesson directory is `./lessons/day-NN/` — there is no week-level subdirectory.

## Step 2: Read references and the itinerary

Read all three before drafting anything:

- `<plugin-root>/references/learners.md` — profiles and differentiation rules.
- `<plugin-root>/references/pedagogy.md` — CI-first, spaced-repetition policy, false
  friends, content constraints.
- `./curriculum/20-day-itinerary.md` — the master plan.

If the itinerary file is missing, tell Shane to run the `curriculum-itinerary` skill
first and stop.

## Step 3: Extract the day's row

From the itinerary, pull this day's:

- Theme
- 10–15 new vocabulary items (English + Spanish gloss)
- Phrase frames
- Grammar point (or "none")
- Communicative task
- Recycled-vocabulary list

Cross-check the recycled list against earlier days' vocabulary so recycling is real,
not invented.

## Step 4: Build the spaced-repetition coverage set

This is the heart of the skill. The coverage set drives every media file produced in
step 6.

1. **Start with the itinerary's recycled-vocabulary list** for this day.
2. **Top up if needed.** If the list has fewer than 8 items, sample additional items
   from Days 01 through Day NN−1 to reach **at least 8 recycled items**. Prefer the
   oldest items first (smaller source-day numbers first — they've gone longest
   without exposure). Tie-break alphabetically within the same source day. (Day 01
   has no earlier material to recycle, so its coverage set is empty; later days
   build it up steadily.)
3. **Build the coverage table.** Rows are the recycled items; columns are the five
   media files: `reading.md`, `audio-script.md`, `video-script-1.md`,
   `video-script-2.md`, `video-script-3.md`. Assign each item to at least **two**
   files (more contexts beats single repetition). Distribute the load evenly across
   files so no single file is carrying every recycled item.
4. Write this table into `teacher-plan.md` at the top under a **Spaced repetition
   coverage** heading so Shane can see at a glance which items are revisited and
   where.

## Step 5: Idempotency check

If `./lessons/day-NN/` already exists with files, use `AskUserQuestion` to confirm
overwrite vs. abort. Do NOT silently overwrite.

## Step 6: Generate the output files

Write all files into `./lessons/day-NN/`. Every media file (`reading.md`,
`audio-script.md`, all three `video-script-N.md`) MUST naturally incorporate the
recycled items it was assigned in the coverage table. Recycling is not decoration —
it is how the kids retain vocabulary.

### `teacher-plan.md`

- **Header**: day number, theme, date blank, estimated total time ~60–75 min.
  (No "week" field.)
- 2–3 measurable **can-do objectives** sourced from the itinerary's cumulative
  checklist.
- **Materials list**: printed `reading.pdf`, printed `notes.md`, device for AI TTS
  playback, device for HeyGen video playback.
- **Spaced repetition coverage** table (from step 4) immediately under the header.
  Markdown table — rows are recycled items, columns are the five media files, cells
  marked ✓.
- **Timed lesson flow** in this fixed order, with per-segment minute estimates:
  1. **Warm-up** — drill every recycled item from the coverage table (at least one
     quick prompt per item). This is the primary spaced-repetition moment.
  2. **Video 1: vocabulary preview** — play `video-script-1.md`'s video.
  3. **Vocabulary drill** — the day's 10–15 new items, anchored by `notes.md`.
  4. **Reading** — work through `reading.md` / `reading.pdf`.
  5. **Video 2: dialogue model** — play `video-script-2.md`'s video.
  6. **Audio listen-and-repeat** — play `audio-script.md`'s audio.
  7. **Video 3: task walkthrough** — play `video-script-3.md`'s video.
  8. **Task / Role-play** — the day's communicative task.
  9. **Wrap-up / quick review** — close the loop by calling back to 2–3 recycled
     items so the kids notice they used old vocab successfully today.
- Under **each video** segment in the timed flow: 2–3 **discussion questions** in
  English (Spanish gloss only when comprehension would otherwise fail) plus a
  one-line "emphasize this" note.
- Under the **reading** segment: 1–2 higher-level "talk about it" prompts (opinion
  or personalization) on top of the comprehension questions that live in
  `reading.md`.
- Under the **audio** segment: 1–2 discussion questions and a note on which phrases
  to drill in the listen-and-repeat block.
- **Peer activities (student ↔ student)**: at least one activity where Camilo and
  Luciana practice with each other (mini role-play, paired Q&A, information-gap
  task). Spell out exactly what each side says.
- **Teacher-led interactive activities (Shane ↔ students)**: at least two non-media
  activities where Shane interacts with them live — flashcard quick-fire (Spanish
  gloss only on miss), Total Physical Response commands tied to the day's verbs, a
  "Shane plays a role" sketch where each kid asks him something using the day's
  phrase frames. Make these vary across the course; do not use the same two every
  day.
- **Just-in-time grammar block** (if the day has one): ≤5 minutes, with one
  Spanish-glossed framing line and 3–5 English drill prompts.
- **Communicative task setup**: props, who plays whom, what success looks like.
- **Answer keys** for `reading.md` comprehension questions and for the per-media
  discussion questions you added above.
- **Differentiation notes** with three labeled blocks:
  - **Camilo** — minimize correction (recasts, not direct correction); save explicit
    correction for a brief private post-task moment; give instructions once,
    visually; gamify (points, soccer framing); short segments; prompt him to answer
    first.
  - **Luciana** — explicit grammar OK; give visible goals.
  - **Group dynamic** — do not let Luciana correct Camilo; if she starts to, redirect
    gently.

### `reading.md`

- **Vocabulary preview table** with columns: `English | Spanish gloss | example
  sentence`. Cover the day's new vocabulary.
- **Short controlled-vocabulary text** (≤200 words) on a topic tied to one of the
  kids' interests. Rotate so both kids see themselves over the course of the week.
  Short, simple sentences. Natural American English.
- **Spaced repetition**: the text MUST naturally use the recycled items assigned to
  `reading.md` in the coverage table. Make them appear in the prose as if they
  belong, not bolted on. After the text, include a short **"Words we've seen
  before"** callout listing the recycled items that showed up so the kids notice
  the recycling.
- **5–8 comprehension questions** in English (mix of literal and one-step
  inference). At least one question must target a recycled item, not just new vocab.
- **Cognate spotlight**: 2–4 Spanish–English cognates that appear in the text, with
  the shared meaning called out.
- **False-friend warning** when any cognate-looking word in the text could mislead
  (see the false-friend list in `pedagogy.md`). Skip if not relevant.

### `reading.pdf`

Render from `reading.md` by shelling out to the bundled script:

```
python <plugin-root>/skills/daily-lesson/scripts/md_to_pdf.py \
    ./lessons/day-NN/reading.md \
    ./lessons/day-NN/reading.pdf
```

Margins 0.2in on all sides; body 14pt serif (Shane's house PDF default). If the
script errors (e.g., weasyprint not installed), surface the error to Shane verbatim
plus the install command from the script's docstring. Do not silently skip.

### `notes.md` — kid-facing study handout

The kids hold this during the lesson. Age-appropriate for teens — not childish.
Short lines, generous whitespace. No emojis. Markdown only — no PDF needed.

- **Header**: day number, theme (no "week"), one-sentence "Today you will learn
  to …" in English with Spanish gloss in parentheses.
- **Vocabulary** section: a two-column list (English | Spanish), with a one-line
  example sentence for each item.
- **Phrases** section: the day's phrase frames as a numbered list with Spanish gloss
  and a slot example, e.g. `"Can I ___?" — "¿Puedo ___?"`.
- **Grammar** section (only if the day has a grammar point): a kid-readable
  explanation in plain English with a Spanish-glossed framing line, 2–3 example
  sentences, and one common mistake to avoid. Skip this section entirely on no-
  grammar days.
- **Cognates and false friends** mini-section: the same cognate spotlight and false-
  friend warning as in `reading.md`, restated as a quick reference card.
- **Review from earlier days**: a "you already know these" bullet list of every
  recycled item in this day's coverage set (English + Spanish gloss). This makes
  the spaced-repetition load explicit to the kids.
- **Try it** prompts: 3–5 fill-in-the-blank or short-answer items the kids can
  attempt on their own using the day's vocab and phrases. **At least one prompt
  must reuse a recycled item** from the review list.
- **Answer key** at the very bottom in a clearly labeled section so they can self-
  check after attempting the prompts.

### `audio-script.md`

- Listening-comprehension focused. Slow beginner pacing. Fed directly into AI TTS.
- Use speaker labels (`NARRATOR:`, `STUDENT:`, `TEACHER:`, etc.) and explicit
  `[PAUSE]` markers (TTS-engine-agnostic — plain bracketed text the user can adapt
  to their engine's pause syntax).
- **Spaced repetition**: weave the recycled items assigned to `audio-script.md`
  into the dialogue or narration in natural contexts. Include at least one
  **"remember this from earlier?"** segment where the narrator says the recycled
  English word / phrase, pauses, says the Spanish gloss, pauses, then uses it in a
  new sentence.
- At least one **"Listen and repeat"** block — short phrases with `[PAUSE — repeat]`
  markers. Mix new and recycled items in this block.
- **Header note**: "For AI TTS playback. The `[PAUSE]` markers indicate where the
  engine should insert silence."
- Do NOT include recording-yourself instructions or stage directions for Shane.

### `video-script-1.md` — Vocabulary preview (~2–3 min)

- **HeyGen-ready, numbered segments** (4–6). Each segment block has these four
  fields exactly:
  - `Avatar/Speaker:` — which avatar speaks
  - `Spoken text:` — the exact words to say
  - `On-screen text:` — caption / supers
  - `Visual note:` — what the avatar / scene should show
- Introduces each new vocabulary item once with the English word on screen, Spanish
  gloss in a smaller caption, and an example sentence. Heavy repetition.
- **Spaced repetition**: open with a 20–30-second "from before" segment that
  flashes the recycled items assigned to this video. Each is said aloud once with
  the Spanish gloss on screen. This grounds the new vocab against known items.
- **Header note**: "Generated for HeyGen — paste segments in order."

### `video-script-2.md` — Dialogue model (~2–3 min)

- Same HeyGen segment format (4 fields per segment), 5–8 numbered segments.
- Models a realistic short dialogue using the day's vocabulary and phrase frames
  (student asks teacher for help, kid orders cafeteria lunch, etc.). Two on-screen
  speakers; switch avatars between turns. Replay / recap the key phrase at the end.
- **Spaced repetition**: the dialogue MUST naturally incorporate the recycled items
  assigned to this video — characters reuse old phrases the kids already know in
  the new context.
- **Header note**: "Generated for HeyGen — paste segments in order."

### `video-script-3.md` — Task walkthrough (~2–3 min)

- Same HeyGen segment format, 4–6 numbered segments.
- Walks through the day's end-of-lesson communicative task step by step — what the
  kids are about to do in role-play. Models success and one common mistake.
- **Spaced repetition**: chain together new + recycled phrase frames so the kids
  see how earlier-day language slots into today's task.
- **Header note**: "Generated for HeyGen — paste segments in order."

## Step 7: Render the reading PDF

After all five media files are written, render `reading.pdf`:

```
python <plugin-root>/skills/daily-lesson/scripts/md_to_pdf.py \
    ./lessons/day-NN/reading.md \
    ./lessons/day-NN/reading.pdf
```

If it fails, surface the exact error and the install command from the script's
docstring. Do not silently skip.

## Step 8: Verify spaced-repetition coverage

Walk the coverage table from step 4 against the generated files. For each recycled
item × assigned-file pair, do a substring match against the rendered file text. If
any item is missing from a file it was assigned to, regenerate that file rather than
ship an incomplete coverage table.

## Step 9: Summarize

Print a short summary naming the directory, listing files written, confirming
`reading.pdf` rendered, and reporting recycled-item coverage, e.g.:

> Wrote ./lessons/day-07/ — 8 files (teacher-plan.md, reading.md, reading.pdf,
> notes.md, audio-script.md, video-script-1.md, video-script-2.md,
> video-script-3.md). reading.pdf rendered via weasyprint. 9 recycled items, each
> appearing in ≥2 media files.
