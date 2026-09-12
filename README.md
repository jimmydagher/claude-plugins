# claude-plugins

Jimmy Dagher's Claude Code plugins, and the marketplace catalog for all of
them, in one repo.

```
claude-plugins/
├── .claude-plugin/
│   └── marketplace.json   # lists every plugin below by folder
├── sdsi/                  # SDSI — base coding standard + sdsi:web/mw/cli
├── code-reviewer/         # staged legacy-codebase review/modernization workflow
└── council/               # doc/plan review lenses — council:it, council:bu, council:all
```

## Install

```
/plugin marketplace add jimmydagher/claude-plugins
/plugin install sdsi@jimmy-plugins
/plugin install code-reviewer@jimmy-plugins
/plugin install council@jimmy-plugins
```

Already added the marketplace and just want the latest plugin versions?
`/plugin marketplace update jimmy-plugins`, then re-run `/plugin install`
for anything that changed (or wait for auto-update, if enabled for this
marketplace).

## Adding a new plugin later

1. Drop the new plugin's folder in here, next to `sdsi/`, `code-reviewer/`,
   and `council/` — it needs its own `.claude-plugin/plugin.json` and
   `skills/` the same as the others.
2. Add one entry to `.claude-plugin/marketplace.json`:
   ```json
   {
     "name": "<plugin-name>",
     "source": "./<plugin-folder>",
     "description": "..."
   }
   ```
3. Commit and push. `/plugin marketplace update jimmy-plugins` then
   `/plugin install <plugin-name>@jimmy-plugins` picks it up — no new repo,
   no new marketplace, nothing else to wire up.

## Each plugin's own docs

See `sdsi/README.md`, `code-reviewer/README.md`, and `council/README.md`
for what each one does and how it's organized internally.
