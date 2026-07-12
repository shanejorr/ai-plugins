# Claude and Codex Plugins

A personal plugin marketplace for Claude Code. The `reading-pipeline` plugin is also compatible with ChatGPT Work and Codex.

## Install for Claude Code

```
/plugin marketplace add shanejorr/ai-plugins
```

Then install any Claude plugin from the marketplace:

```
/plugin install <plugin-name>@shanejorr-plugins
```

## Install reading-pipeline for ChatGPT Work and Codex

Register the GitHub marketplace and install the plugin:

```bash
codex plugin marketplace add shanejorr/ai-plugins
codex plugin add reading-pipeline@shanejorr-plugins
```

Restart ChatGPT or Codex and begin a new task so the installed skills are loaded. In the ChatGPT desktop app, the plugin can also be installed from **Plugins** in Work or Codex after the marketplace is registered.

Only `reading-pipeline` is currently published in the Codex marketplace. The other plugins remain Claude-only.

## Plugins

| Name | Platforms | Description |
|------|-----------|-------------|
| reading-pipeline | Claude, ChatGPT Work, Codex | Summarize research papers, convert to EPUB/KEPUB, and sync to Kobo or reMarkable via Google Drive |
| claude-prompt-best-practices | Claude | Reference guide for writing effective prompts for Claude (official Anthropic docs as a skill) |
| ui-style | Claude | Shane's house UI style guide: editorial civic-warm aesthetic for parent/civic-facing web products |
| english-survival-lessons | Claude | Generate a 20-day functional survival English course (master itinerary + daily teacher plans, kid-facing readings/notes, audio script, three video scripts) |
