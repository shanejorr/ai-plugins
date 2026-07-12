# ai-plugins

A personal Claude Code plugin marketplace hosted on GitHub. Plugins here are built for Shane's own productivity and automation needs, but the marketplace is public so others can install them too. `reading-pipeline` is additionally packaged for ChatGPT Work and Codex.

`AGENTS.md` is a symlink to this file so Claude Code and Codex share the same repository instructions. Edit `CLAUDE.md`; do not replace the symlink with a separate copy.

## Repo layout

- `.claude-plugin/marketplace.json` — marketplace manifest. Every published plugin must have an entry here (`name`, `source`, `description`, `version`).
- `.agents/plugins/marketplace.json` — ChatGPT/Codex marketplace manifest. It currently publishes only `reading-pipeline`.
- `plugins/<plugin-name>/` — one directory per plugin.
  - `.claude-plugin/plugin.json` — plugin manifest.
  - `.codex-plugin/plugin.json` — Codex manifest, present only for plugins explicitly supporting ChatGPT/Codex.
  - `skills/<skill-name>/SKILL.md` — skill definitions (optional).
  - Plugins may also contain commands, hooks, agents, or MCP servers per the Claude Code plugin spec.
- `plugins/example-plugin/` — **placeholder only**. Delete it once real plugins exist; do not treat it as a canonical template.

## Working in this repo

- When adding a new plugin: create `plugins/<name>/`, add a `.claude-plugin/plugin.json`, and register it in `.claude-plugin/marketplace.json`. Update the plugin table in `README.md`.
- Do not add a plugin to `.agents/plugins/marketplace.json` or create `.codex-plugin/plugin.json` unless it is intentionally being made compatible with ChatGPT Work and Codex.
- For a dual-platform skill, keep instructions platform-neutral and validate the Codex plugin manifest and all bundled skills. Codex requires `disable-model-invocation: false` when that Claude frontmatter field is present.
- When removing a plugin: delete its directory, remove its entry from `marketplace.json`, and update `README.md`.
- No strict conventions on naming, structure, or versioning beyond what the Claude Code plugin spec requires — match whatever style fits the plugin.
- Bumping a plugin's `version` in its `plugin.json` should also update the version in `marketplace.json`.

## Install (for users)

### Claude Code

```
/plugin marketplace add shanejorr/ai-plugins
/plugin install <plugin-name>@shanejorr-plugins
```

### ChatGPT Work and Codex (`reading-pipeline` only)

```bash
codex plugin marketplace add shanejorr/ai-plugins
codex plugin add reading-pipeline@shanejorr-plugins
```

Restart ChatGPT or Codex and start a new task after installation so the plugin skills are loaded.
