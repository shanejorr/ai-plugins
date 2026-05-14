---
name: send-chat-to-kobo
description: "Send a Claude chat response — or a user-selected section of one — to Shane's Kobo Color as a KEPUB e-book. Use this skill whenever the user wants to read part of the current conversation on their Kobo. Trigger phrases include 'send [X] to my Kobo', 'send your last response to my Kobo', 'send the section about [X] to my Kobo', 'put this on my Kobo', 'I want to read this on my Kobo'. Orchestrates convert-to-epub and send-to-reader; do not invoke those manually when this skill applies."
user-invocable: true
disable-model-invocation: true
---

# Send Chat to Kobo Skill

## Purpose

Turn a selected piece of the current Claude conversation — a full response, a specific section, or a multi-turn span — into a `.kepub.epub` e-book and upload it to the user's Kobo Color via the existing reading-pipeline skills. The end result: the content appears on the Kobo on its next sync, formatted as a proper book with Kobo reading stats and typography.

This skill is pure orchestration. It delegates conversion to `convert-to-epub` and upload to `send-to-reader`. Do not duplicate their logic here.

## Step 1: Identify What to Send

Locate the content the user referenced in the prior conversation. Common patterns:

- **"send your last response"** → the entirety of the immediately prior assistant turn.
- **"send the section about X"** → a named subsection of a prior response. Find it by heading or topic.
- **"send the summary you wrote"** → a summary the assistant produced earlier in the chat.
- **"send everything we discussed about X"** → multiple turns concatenated, preserving order.

Only confirm boundaries with the user if the request is genuinely ambiguous (e.g., two responses both discuss the topic). Otherwise, proceed without interrupting — they want this on their device, not another round of dialogue.

## Step 2: Write a Temporary Markdown File

Save to `/tmp/<snake_case_title>.md`:

- **Filename:** snake_case, under ~60 characters, derived from the content's topic. Examples: `/tmp/transformer_attention_explained.md`, `/tmp/kobo_workflow_summary.md`.
- **First line:** `# <Title>` — the `convert-to-epub` script auto-picks this up as the EPUB title. Infer a reasonable title from the content; ask only if nothing sensible can be inferred.
- **Blank line, then body.**
- **Preserve formatting** already present in the response: headings (`##`, `###`), lists, code blocks, tables, blockquotes. Do not rewrite or summarize — the user picked this content because they want to read it as-is.

Use the `Write` tool for this step.

## Step 3: Convert to KEPUB

Invoke the `convert-to-epub` skill on the temp `.md`. The output path must end in `.kepub.epub` — this is what tells the converter (and the Kobo) to produce a KEPUB:

```
/tmp/<snake_case_title>.kepub.epub
```

The `.kepub.epub` extension unlocks Kobo reading stats, annotations, and improved typography. A plain `.epub` would work but loses these features.

## Step 4: Upload to Kobo

Invoke the `send-to-reader` skill with:

- The `.kepub.epub` file path from Step 3
- `--device kobo`

That skill handles OAuth, folder lookup from its `config/folders.json`, and the Drive upload. If it surfaces a setup error (missing credentials, missing folder ID), relay the exact remediation to the user — don't retry blindly.

## Step 5: Confirm

Report briefly:

- The filename uploaded.
- That it will appear on the Kobo on its next sync.

**Do NOT dump the file contents back into chat.** The user is sending it precisely so they can read it on the Kobo instead of in the terminal.

## When NOT to Use This Skill

- **Sending an existing file (PDF, EPUB, KEPUB) to the Kobo:** use `send-to-reader` directly.
- **Sending to the reMarkable:** use `send-to-reader` directly with `--device remarkable`.
- **Converting a paper or document to EPUB without uploading:** use `convert-to-epub` directly.
- **Summarizing a research paper first:** use `summarize-research`, then this skill (or the two skills directly) on its output.
