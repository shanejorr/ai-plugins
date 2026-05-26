---
name: curriculum-itinerary
description: "Generate the master 20-day functional-English course itinerary for Shane's at-home survival English course for his two newly adopted Colombian teens (Luciana 16, Camilo 13). Organized day-by-day (Day 01 → Day 20), NOT by week. Produces a single markdown file at ./curriculum/20-day-itinerary.md that maps Days 01–20 to a theme, target vocabulary (10–15 items per day), phrase frames, one optional grammar point, end-of-lesson communicative task, and which earlier vocabulary recycles. Includes a cumulative can-do checklist of 15–20 survival tasks. The course skips greetings/introductions/numbers/time — the kids already know that material. Run this skill ONCE at the start of the course; the daily-lesson skill reads its output. Trigger phrases include 'generate the curriculum', 'build the 20-day itinerary', 'create the english course plan', 'make the survival english curriculum', 'plan the 20-day course', 'build the master itinerary'."
user-invocable: true
disable-model-invocation: true
---

# Curriculum Itinerary

Produces the spine of the 20-day functional-English course. Run **once** at the start.
The `daily-lesson` skill reads the output of this skill, so any later regeneration
invalidates every lesson already produced.

## Step 1: Read the references first

Read both reference files in this plugin and let them shape every choice you make.
Do not paraphrase them back into the itinerary.

- `<plugin-root>/references/learners.md` — Luciana's and Camilo's profiles, interests,
  group dynamic, differentiation rules.
- `<plugin-root>/references/pedagogy.md` — comprehensible input first, task-based,
  light grammar, spaced repetition; cognate use; false-friend list; content constraints.

## Step 2: Check whether the itinerary already exists

If `./curriculum/20-day-itinerary.md` exists, use `AskUserQuestion` to confirm
overwrite vs. abort. Regenerating after lessons have been built will desync the
day-by-day plan from the lessons that already reference it.

If Shane confirms overwrite, proceed. Otherwise stop.

## Step 3: Compose the 20 days

### Hard rules

- **Skip greetings, introductions, numbers, and time.** The kids already know that
  material. Do not spend any day on it. Mention it only in passing if a later theme
  reuses it (e.g., telling a doctor your age).
- **Organize day-by-day.** The output is a flat sequence Day 01 → Day 20. Do **not**
  insert "Week 1", "Week 2", or any week-level grouping.
- 10–15 new vocabulary items per day.
- Each day picks **one** optional just-in-time grammar point (or none if the day's
  task doesn't need one).
- Each day ends with **one** communicative task (role-play: order food, ask a teacher,
  call 911, fill out a form).
- Total course budget across all 20 days: ~300–500 vocabulary words and ~100–200
  phrase frames.
- Personalize themes to the kids' interests. Rotate features so neither child
  dominates.

### Topical progression

Cover all four areas in this order. The exact day-by-day mapping can flex within
each block:

1. **Days ~01–05** — Asking for help, the school day & routines, self-advocacy
   phrases. ("I don't understand", "Can you repeat?", "How do you say …?",
   "May I go to the bathroom?", "I'm new here.")
2. **Days ~06–10** — Directions & getting around (school building, hallways, bus,
   walking), food & cafeteria, ordering and paying.
3. **Days ~11–15** — Health and feeling sick (nurse, doctor, body parts, pain),
   shopping & money, small talk with peers and adults.
4. **Days ~16–20** — Additional survival material the kids will hit in their first
   weeks: phone / voicemail / text basics, filling out forms (school, medical,
   address), emergency language (911, asking for help in public, feeling unsafe),
   peer / social English (parties, sports tryouts / PE / locker room — soccer for
   Camilo, volleyball for Luciana — talking about music and shows). Day 20 is a
   cumulative review.

### Spaced repetition (what to write into each day's "recycles" field)

For each day after Day 01, list 4–10 earlier-day vocabulary items that should
naturally recur on that day. Prefer:

- Items from the immediately previous day (still fresh, needs reinforcement).
- Items from the oldest earlier day with un-recycled material (they've gone longest
  without exposure).
- Items thematically connected to the new day's topic.

The `daily-lesson` skill will top this list up to a minimum of 8 if needed, but a
strong itinerary recycle list reduces the topping-up the daily skill has to do.

### Cumulative can-do checklist

Build a running list of 15–20 survival-English tasks the course adds up to.
Examples:

- I can ask the teacher to repeat.
- I can ask where the bathroom is.
- I can order lunch in the cafeteria.
- I can tell the school nurse where it hurts.
- I can call 911 and say my address.
- I can fill out a form with my name, date of birth, and parent's phone.

Each day should advance at least one item on the list. Show the list once at the top
of the itinerary, then annotate each Day section with which checklist items that day
advances.

## Step 4: Write the file

Write to `./curriculum/20-day-itinerary.md`. Create the `curriculum/` directory if it
doesn't exist.

Use this flat structure exactly:

```
# 20-Day Functional Survival English — Master Itinerary

## Course intent
<one paragraph: goal, audience, what's skipped, pedagogy in one line>

## Cumulative can-do checklist (course goal)
1. <item>
2. <item>
...

## Day 01 — <Theme>

**Theme:** <short phrase>
**Can-do targets advanced today:** <list of checklist item numbers>
**New vocabulary (NN items):**
- english item — Spanish gloss
- ...
**Phrase frames:**
- "<frame>" — "<Spanish gloss>"
- ...
**Grammar point:** <one line, or "none">
**Communicative task:** <one-line task description>
**Recycles from earlier days:** <none on Day 01; list on later days>

## Day 02 — <Theme>
...

## Day 20 — Cumulative review
...
```

No `## Week N` headings. Just twenty `## Day NN` sections in order.

## Step 5: End

Print a one-line summary naming the file path and the can-do count, e.g.:

> Wrote ./curriculum/20-day-itinerary.md — 20 days, 17 can-do targets.
