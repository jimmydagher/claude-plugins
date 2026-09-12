# Shared Context — Code Reviewer

Read by every skill in this plugin before it does anything else. Don't copy
this content into an individual skill's own SKILL.md — if something here
needs to change, it should only need to change once.

## Principles

- **The catalog is the single source of truth.** Every change made in
  `/execute` traces back to a specific catalog entry. If a change doesn't
  map to one, either add the entry first or don't make the change yet.
- **One stage is one reviewable unit.** If a stage would produce more
  change than a person can meaningfully review in one sitting, it's not
  one stage — split it.
- **Never advance out of sequence.** A later stage may depend on an
  earlier stage's new code. Skipping ahead means building on something not
  yet validated.
- **Old code stays until new code is proven.** Don't delete the old
  implementation in the same stage that introduces its replacement — that's
  what `/validate` is for.
- **Never guess on direction — ask.** Anything genuinely ambiguous about
  scope, priority, risk tolerance, or target stack goes through the
  `AskUserQuestion` tool, not an assumption. Reserve it for real forks in
  the road — don't ask about things the codebase or the catalog already
  answers.
- **Fail loud, same as the code itself.** If a review lens can't run, a
  stage can't be tested, or a validation is ambiguous, say so explicitly
  rather than quietly proceeding.

## Working files

Everything this plugin produces is written under `_scaffolding/` at the
root of the **target** project (not this plugin's own folder), so progress
survives across sessions — this is a multi-sitting process for any codebase
worth the trouble:

```
<target-project>/_scaffolding/
├── 00-guidance/
│   └── PROJECT-GUIDANCE.md      # captured by /strategy; the north star
├── 01-review/
│   ├── security.md   standards.md   efficiency.md   infrastructure.md
│   └── intake-verdict.md
├── 02-catalog/
│   └── FINDINGS-CATALOG.md      # the single source of truth (see above)
├── 03-strategy/
│   └── SEQUENCING-PLAN.md
├── 04-execution/
│   └── stage-<N>-<slug>/
│       └── summary.md
└── 05-validation/
    └── stage-<N>-<slug>.md
```

Whether `_scaffolding/` gets committed to git is the user's call — say so
explicitly rather than assuming. Committing it lets a team see progress the
way `ariel-docs/` documents ariel; gitignoring it keeps it as pure scratch
space. Either way, don't skip writing these files — they're what let this
process resume cleanly in a new session instead of re-deriving everything.

## Dependencies

- **SDSI** (Software Development Standard Instructions) — the standard
  `/intake` hands to its standards lens explicitly as *the* standard to
  check against, not generic best practices. Tried in this order:
  1. **The `sdsi` plugin, invoked by name** — `sdsi:sdsi` — if it's
     installed in this environment. Preferred: a by-name skill invocation
     resolves correctly regardless of where either plugin is installed,
     unlike a path reaching into another plugin's own files.
  2. **A project-local `SDSI.md`**, or one found in a shared location, if
     the `sdsi` plugin isn't installed.
  3. If neither exists anywhere reachable, say so and proceed on general
     good-practice grounds instead of blocking.

  Once loaded, `execute`, `strategy`, and `validate` cite it by section
  number (e.g. "SDSI §6") without reloading it themselves — the same
  standard, whichever of the two sources actually answered.

- **No dependency on the `council` plugin.** Source code review is this
  plugin's own job: `/intake` runs its own four lenses (security,
  standards, efficiency, infrastructure) directly and inline, every time —
  it never delegates to an external council. `council` reviews
  documentation and business plans, not code, so the two plugins are
  deliberately independent of each other.
