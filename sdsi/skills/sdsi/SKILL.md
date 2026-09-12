---
name: sdsi
description: >
  The Software Development Standard Instructions (SDSI) — the base coding,
  structure, security, and operational standard that applies to every
  software project, in any language or stack. This is the foundation every
  other skill in this plugin (sdsi:web, sdsi:mw, sdsi:cli) depends on, and
  it belongs in every development session, not only when something looks
  stack-specific. Use it whenever writing, reviewing, planning, or
  scaffolding code: starting a new project, adding a feature, fixing a bug,
  setting up project structure, configuration, secrets, logging, error
  handling, tests, versioning, or dependencies, or reviewing/refactoring
  existing code. Also the skill for a skill in a *different* plugin
  (`council-of-claude`, `code-reviewer`) to invoke by name — `sdsi:sdsi` —
  when it needs SDSI's general standard rather than reading this plugin's
  files directly. Also triggers on "/sdsi" or a mention of "SDSI" or "our
  dev standards".
---

Read `../../references/shared-context.md` — that file *is* the standard;
this skill's only job is making sure it's loaded. There's nothing else to
do here and nothing below to duplicate it.

## Contents, at a glance

The standard covers, in one document, for every project regardless of
language or stack: guiding principles (including the non-negotiable
no-over-engineering / no-assumptions / no-pointless-changes /
double-check-your-work set), naming & casing, project structure and
dependency direction, constants & enums, comments & docstrings,
configuration management, secrets & credentials, logging & output, error
handling, data & process flow, reuse over reimplementation, the entry
point/composition root, CLI/task design, testing, dependency management,
version control, versioning & changelog discipline, the local dev
environment, containerization & deployment, documentation, SOLID & strict
typing, the AI-native development workflow, `TODO.md` tracking across
sessions, and how to start a brand-new project.

## Two ways this gets loaded

- **From `sdsi:web`, `sdsi:mw`, or `sdsi:cli`** (same plugin): those skills
  read `../../references/shared-context.md` directly, by relative path,
  rather than invoking this skill — the same pattern `code-reviewer`'s own
  phase skills use for its `shared-context.md`. This skill isn't in that
  path at all; it exists for the case below.
- **From a skill in a different plugin** (`council-of-claude`,
  `code-reviewer`, or any future one): invoke `sdsi:sdsi` by name rather
  than reading this plugin's `references/shared-context.md` by a relative
  path. Where the two plugins happen to sit on disk relative to each other
  isn't something either can assume, so a cross-plugin relative path is
  fragile in a way a by-name skill invocation isn't. This skill is what
  makes that reliable: whatever calls `sdsi:sdsi` gets the same file,
  loaded the same way, regardless of install location.

## If the target project has its own CLAUDE.md

A project's own `CLAUDE.md` is where project-specific deviations and
particulars live (SDSI §22, §24) — it is not a substitute for the standard
and shouldn't repeat it either. Read the project's `CLAUDE.md` too, if it
has one: where the two genuinely disagree, a stated, deliberate deviation in
that file wins for that project; everywhere else, and for every project that
doesn't have one, the standard governs.
