# SDSI

Software Development Standard Instructions — a single base standard for
every project (coding, structure, security, logging, error handling,
testing, versioning, the AI-native workflow), plus stack-specific
companions layered on top of it. Everything shared lives in one file,
once; the stack skills only state what's *additionally* true for their own
stack and never repeat what's already covered there.

## Structure

```
SDSI
├── references/
│   └── shared-context.md  — the base standard. Every skill in this plugin
│                             reads this file first, always.
└── skills/
    ├── sdsi/  — /sdsi:sdsi — thin pointer to shared-context.md; the name a
    │            skill in a DIFFERENT plugin invokes to get the standard
    ├── web/   — /sdsi:web  — Django & website development (from flammeau)
    ├── mw/    — /sdsi:mw   — middleware & integration services (from ariel)
    └── cli/   — /sdsi:cli  — command-line tools (generic draft — grow it
                              from a real project)
```

## Skills

| Skill | Covers | Invoke with |
|---|---|---|
| `sdsi` | Nothing of its own — points to `references/shared-context.md`, the base standard: naming, project structure, config, secrets, logging, error handling, data flow, reuse, entry points, testing, dependencies, version control & changelog discipline, local dev, containerization, documentation, SOLID & typing, the AI-native workflow, `TODO.md` | `/sdsi`, "our dev standards" — mainly meant to be invoked **from another plugin** |
| `web` | Django/website project layout, the `settings.py` config bridge, secrets via a cloud key vault, multi-target deployment, versioning automation, AI-agent notes for this stack | `/sdsi:web`, "build a Django site" |
| `mw` | Connector/business-rules/task project layout, multi-system config, secrets & identity for many systems, the extract → business-rules → destination flow, the response contract, one image as several run shapes, docs discipline on an established codebase | `/sdsi:mw`, "build an integration/middleware service" |
| `cli` | Command/subcommand design, config precedence, exit codes & machine-readable output, packaging/versioning, testing a CLI | `/sdsi:cli`, "build a command-line tool" |

## How the dependency works — and why there are two mechanisms

The base standard lives in exactly one place, `references/shared-context.md`,
and gets to every skill that needs it one of two ways, depending on where
that skill lives:

- **A skill in *this* plugin** (`web`, `mw`, `cli` — and `sdsi` itself)
  reads `../../references/shared-context.md` directly, by relative path,
  as the first thing it does. This is the same pattern `code-reviewer` uses
  for its own `shared-context.md`: cheap, and correct as long as the file
  is inside the same plugin folder as the skill reading it.
- **A skill in a *different* plugin** (`council-of-claude`,
  `code-reviewer`, or anything installed alongside `sdsi`) should invoke
  `sdsi:sdsi` **by name** instead of reading `sdsi`'s `shared-context.md`
  by a relative path. Two plugins' folders aren't guaranteed to sit at any
  particular position relative to each other — that assumption is exactly
  what a relative path across a plugin boundary would depend on, and it's
  the one thing here that's genuinely fragile. A by-name skill invocation
  isn't: it resolves correctly wherever `sdsi` happens to be installed.

That split is the whole reason `sdsi` is kept as an actual skill rather
than just being "the file other plugins should go read" — it's the stable,
addressable front door for anything outside this plugin.

## Setup

No other plugin or configuration required. Install it so the standard is
available in every session and every project without needing a local copy —
the stack skills (`web`, `mw`, `cli`) only add value on top of it once it's
there.

## Usage

- **Any development task, in any project:** just start working — `sdsi`
  is written to trigger broadly (new project, feature, bug fix, review,
  refactor), not only when something looks stack-specific.
- **Django or a website:** "/sdsi:web" or describe the task; it reads
  `shared-context.md` first, then applies the Django/website layer.
- **A middleware or integration service:** "/sdsi:mw" or describe the
  task; it reads `shared-context.md` first, then applies the middleware
  layer.
- **A command-line tool:** "/sdsi:cli" or describe the task — treat the
  result as a draft to correct from the first real project, not a
  finished standard.
- **From another plugin** (e.g. `code-reviewer`'s standards check, or a
  `council-of-claude` persona): invoke `sdsi:sdsi` by name to get the
  standard, rather than reaching into this plugin's files directly.
- **A project with its own `CLAUDE.md`:** read that too, if present — a
  project's stated, deliberate deviation wins for that project; SDSI
  governs everywhere else.

## Customization

Each companion is a living document, same as the base standard itself —
extend the content in `web/SKILL.md`, `mw/SKILL.md`, or `cli/SKILL.md` (or
add a new skill, e.g. `sdsi:mobile`) the moment a real project teaches it
something worth generalizing. Keep everything shared across stacks in
`references/shared-context.md` and out of the companions — that's the whole
point of splitting them apart.
