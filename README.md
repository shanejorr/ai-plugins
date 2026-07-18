# Claude and Codex Plugins

A personal plugin marketplace for Claude Code. The `reading-pipeline` and
`job-search` plugins are also compatible with ChatGPT Work and Codex.

## Install for Claude Code

```
/plugin marketplace add shanejorr/ai-plugins
```

Then install any Claude plugin from the marketplace:

```
/plugin install <plugin-name>@shanejorr-plugins
```

## Install compatible plugins for ChatGPT Work and Codex

Register the GitHub marketplace and install the plugin:

```bash
codex plugin marketplace add shanejorr/ai-plugins
codex plugin add reading-pipeline@shanejorr-plugins
codex plugin add job-search@shanejorr-plugins
```

Restart ChatGPT or Codex and begin a new task so the installed skills are loaded. In the ChatGPT desktop app, the plugin can also be installed from **Plugins** in Work or Codex after the marketplace is registered.

The Codex marketplace currently publishes `reading-pipeline` and `job-search`.
The other plugins remain Claude-only.

## Plugins

| Name | Platforms | Description |
|------|-----------|-------------|
| reading-pipeline | Claude, ChatGPT Work, Codex | Research topics, summarize papers, convert to EPUB/KEPUB, and sync to Kobo or reMarkable via Google Drive |
| english-survival-lessons | Claude | Generate a 20-day functional survival English course (master itinerary + daily teacher plans, kid-facing readings/notes, audio script, three video scripts) |
| job-search | Claude, ChatGPT Work, Codex | Job-search toolkit: find roles matching your preferences, capture postings to markdown, scrape LinkedIn profiles, and get resume-tailoring recommendations |
