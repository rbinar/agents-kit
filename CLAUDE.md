# agents-kit — maintainer guide

This repo is a Claude Code plugin marketplace, not an application. It ships 48 English subagents in three plugins. Architecture, pipelines and the full agent list live in [README.md](README.md) — do not repeat them here or in agent files.

## Layout

| Path | Content |
|---|---|
| `.claude-plugin/marketplace.json` | Marketplace `agents-kit`; one entry per plugin (`name`, `source`, `description`) |
| `plugins/sdlc/` | `dev-*`, `product-*`, `meta-*` agents + the six lifecycle commands (`commands/`) |
| `plugins/marketing/` | `marketing-*` agents |
| `plugins/sales/` | `sales-*` agents |
| `plugins/<p>/.claude-plugin/plugin.json` | Plugin manifest — `name` must equal the marketplace entry; holds the `version` |
| `scripts/validate.py` | Repo validator, run by CI on every push |

Each plugin directory must be self-contained: Claude Code copies it to a cache and rejects paths with `..`.

## Agent file contract

- One file per agent: `plugins/<plugin>/agents/<name>.agent.md`; the file name must equal the frontmatter `name`.
- The name prefix decides the plugin: `dev-`/`product-`/`meta-` → `sdlc`, `marketing-` → `marketing`, `sales-` → `sales`.
- Allowed frontmatter keys: `name`, `description`, `model`, `disallowedTools`, `tools`, `color`. Plugin agents ignore `permissionMode`, `hooks` and `mcpServers`, so do not use them.
- Read-only agents carry `disallowedTools: Write, Edit, Bash`. Agents that write must name their allowed directories (under `.specs/` or `.docs/`) in the body and in the README's Artefact Storage Strategy table.
- Subagents have no `AskUserQuestion` (or other interactive tools). When an agent needs input it ends its report with a `## Questions for the user` section — 2-4 options per question, recommended first — and stops if it cannot continue. Never reference `AskUserQuestion` in an agent body.
- Agents hand off by bare name ("hand off to dev-coordinator"); the main session resolves the namespaced agent. Explicit references in commands and docs use the namespaced form: `sdlc:dev-coordinator`, `/sdlc:plan`.
- A new pipeline gets the facilitator + guardian + critic trio, like the existing ones.

## Commands

Plugin commands are only registered with their namespace (`/sdlc:spec`, never `/spec`). They run in the main session, so they may use `AskUserQuestion`; they delegate the actual work to agents.

## Releasing

Users only receive an update when the plugin's `version` changes. Bump `version` in `plugins/<p>/.claude-plugin/plugin.json` for every plugin whose runtime content (agents, commands) you change — not for icons or docs (patch: wording/fixes, minor: new agent or command, major: rename or removal). Do not set `version` in `marketplace.json`.

## Validation

```bash
python3 scripts/validate.py              # manifests, frontmatter, references, README coverage
claude plugin validate .                 # marketplace
claude plugin validate plugins/sdlc      # each plugin
claude --plugin-dir plugins/sdlc         # try a plugin locally without installing it
```

When adding an agent: put it in the right plugin, add it to the README pipeline table, bump the plugin version, and run the commands above.
