# english-survival-lessons

Personal Claude Code plugin for Shane's at-home survival-English course for his two
newly adopted Colombian teens — Luciana (16) and Camilo (13) — across the ~20 school-day
window before they start US public school in Cobb County, GA. Goal is **functional
survival English** (navigate a school day, ask for help, order food, call 911), not
fluency. The kids already know greetings, intros, numbers, and time, so the course
skips those.

Both children get the same lesson and the same media each day; differentiation lives in
teacher notes. Pedagogy is comprehensible-input-first, task-based, light just-in-time
grammar, with spaced repetition explicitly threaded through every media file.

## Install

```
/plugin install english-survival-lessons@shanejorr-plugins
```

## Usage

1. Run `curriculum-itinerary` **once** to build the 20-day master plan
   (`./curriculum/20-day-itinerary.md`).
2. Run `daily-lesson` per day to generate that day's lesson package
   (`./lessons/day-NN/`).
3. Paste each of the three `video-script-N.md` files into HeyGen one at a time and
   record/render each video.
4. Paste `audio-script.md` into your AI TTS tool of choice to produce the audio.
5. Print `reading.pdf` and `notes.md` for the kids to follow along.

All file output is relative to the current working directory.

## Skills

### curriculum-itinerary

Produces the master 20-day itinerary as a single markdown file. Each day lists theme,
target vocabulary, phrase frames, optional grammar point, communicative task, and which
earlier vocabulary recycles that day. Includes a cumulative can-do checklist of 15–20
survival tasks. Run once at the start of the course.

Trigger phrases: "generate the curriculum", "build the 20-day itinerary",
"create the english course plan", "plan the 20-day course", "build the master itinerary".

### daily-lesson

Generates one day's complete lesson package into `./lessons/day-NN/`:

- `teacher-plan.md` — timed lesson flow, per-media discussion questions, peer
  (student↔student) activities, teacher-led activities, and Camilo/Luciana/Group
  differentiation notes. Topped by a spaced-repetition coverage table.
- `reading.md` + `reading.pdf` — controlled-vocabulary text, vocabulary preview,
  comprehension questions, cognate spotlight, false-friend warnings.
- `notes.md` — kid-facing study handout with vocab, phrases, grammar, cognates, and
  "try it" prompts with answer key.
- `audio-script.md` — AI-TTS-ready script with speaker labels and `[PAUSE]` markers.
- `video-script-1.md` — vocabulary preview video (HeyGen-ready segments).
- `video-script-2.md` — dialogue model video.
- `video-script-3.md` — task walkthrough video.

Trigger phrases: "create day N lesson", "generate day NN", "build day 7 lesson",
"make the lesson for day 03", "day NN lesson".

## Outputs

```
./curriculum/20-day-itinerary.md
./lessons/day-01/
    teacher-plan.md
    reading.md
    reading.pdf
    notes.md
    audio-script.md
    video-script-1.md
    video-script-2.md
    video-script-3.md
./lessons/day-02/
    ...
```

## PDF rendering

`reading.pdf` is rendered by `skills/daily-lesson/scripts/md_to_pdf.py`. Margins are
0.2 inch on all sides; body is 14pt serif (Shane's house PDF default). Dependencies:

```
pip install markdown weasyprint --break-system-packages
# macOS may also need: brew install pango cairo gdk-pixbuf libffi
```

If weasyprint is unavailable, the script falls back to pandoc.

## Personalization

The learner profiles and pedagogy rules live in `references/`:

- `references/learners.md` — Luciana and Camilo profiles, interests, group dynamic.
- `references/pedagogy.md` — CI-first priority, grammar policy, spaced-repetition
  rules, cognate list, false-friend list, content constraints.

Both skills read these files at the start of every run. Editing them changes future
generations without touching SKILL.md.
