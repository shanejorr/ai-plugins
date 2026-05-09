# claude-plugins

A personal Claude Code plugin marketplace hosted on GitHub. Plugins here are built for Shane's own productivity and automation needs, but the marketplace is public so others can install them too.

## Repo layout

- `.claude-plugin/marketplace.json` — marketplace manifest. Every published plugin must have an entry here (`name`, `source`, `description`, `version`).
- `plugins/<plugin-name>/` — one directory per plugin.
  - `.claude-plugin/plugin.json` — plugin manifest.
  - `skills/<skill-name>/SKILL.md` — skill definitions (optional).
  - Plugins may also contain commands, hooks, agents, or MCP servers per the Claude Code plugin spec.
- `plugins/example-plugin/` — **placeholder only**. Delete it once real plugins exist; do not treat it as a canonical template.

## Working in this repo

- When adding a new plugin: create `plugins/<name>/`, add a `.claude-plugin/plugin.json`, and register it in `.claude-plugin/marketplace.json`. Update the plugin table in `README.md`.
- When removing a plugin: delete its directory, remove its entry from `marketplace.json`, and update `README.md`.
- No strict conventions on naming, structure, or versioning beyond what the Claude Code plugin spec requires — match whatever style fits the plugin.
- Bumping a plugin's `version` in its `plugin.json` should also update the version in `marketplace.json`.

## Install (for users)

```
/plugin marketplace add shanejorr/claude-plugins
/plugin install <plugin-name>@claude-plugins
```
