---
name: cli
description: >
  SDSI's companion for command-line tools — command/subcommand design,
  configuration precedence for flags vs. files, exit codes and
  machine-readable output modes, packaging/versioning, and testing a CLI.
  Use whenever building or working on a command-line tool or script meant
  to be run and reused, not a one-off. Depends on SDSI's base standard —
  read `../../references/shared-context.md` first, always; this skill only
  states what's additionally true for a CLI project and assumes that
  standard already applies in full. This companion is a generic starting
  draft (unlike
  sdsi:web and sdsi:mw, it isn't yet distilled from a real project) — treat
  it as a base to extend, not a finished standard. Also triggers on
  "/sdsi:cli" or "sdsi cli".
---

Before anything else, read `../../references/shared-context.md` — the base
SDSI standard, shared by every skill in this plugin. It's a hard
prerequisite, not an optional read. Everything there applies here in full;
what follows below only adds what's specific to a CLI project on top of it:
command and subcommand structure, config precedence (flags/env/file/
defaults, and where that legitimately deviates from SDSI §6), stdout/stderr
conventions, exit codes and a `--json`-style machine-readable mode,
interactive vs. non-interactive/CI behavior, packaging and versioning, and
testing a command-line interface.

## This one is a draft — say so, and grow it deliberately

What follows was written generically, not distilled from a real CLI
project the way the `web` and `mw` companions were. Apply it, but don't
treat it as settled: when a real CLI project teaches it something
concrete, extend it from that lesson (SDSI §1's "no over-engineering" —
generalize from an actual second case, not from more speculation up
front), the same way its two siblings grew.

## Don't repeat the base standard

If something below looks like it's only restating a general SDSI rule
rather than adding a CLI-specific one, that's a defect in this document —
flag it rather than leaving it duplicated.

---

# SDSI Companion: Command-Line Tools

A companion to `SDSI.md`, not a replacement for it — this project follows
`SDSI.md` in full, and this document adds what's specific to a command-line
tool meant to be run and reused, not a one-off script.

**This one is a draft, and says so on purpose.** `SDSI-DJANGO-WEB.md` and
`SDSI-MIDDLEWARE.md` were both distilled from a real project's actual
lessons; this document was written generically, ahead of one. Apply it, but
treat every section as a starting position to be corrected by the first real
CLI project that disagrees with it — that's a more honest way to grow a
standard than guessing further ahead of any evidence (SDSI §1's
no-over-engineering principle, applied to writing standards documents
themselves).

---

## 1. Command & Subcommand Design

- **A subcommand is a middleware-style task by another name** (SDSI §13):
  one callable per subcommand, dispatched from a registry that asserts
  completeness at import/startup time, not discovered by trial and error
  the first time someone runs an unwired command.
- **Group subcommands by the noun they act on when the tool grows past a
  handful** (`tool user add`, `tool user list`) rather than a flat,
  ever-growing list of top-level verbs — but don't introduce the grouping
  before there's a second subcommand that actually needs it (SDSI §1).
- **A CLI's help text is documentation, and drifts exactly like any other
  documentation if it isn't updated in the same change as the flag it
  describes** (SDSI §20's golden rule, applied to `--help` output
  specifically).
- **Flags are the CLI's public interface — treat a renamed or removed flag
  as a breaking change**, versioned accordingly (SDSI §17's MAJOR/MINOR/
  PATCH table: a removed or renamed flag breaks a deployed caller until
  someone updates their invocation, which is a MAJOR-shaped change by
  SDSI's own operational-impact definition, not just a semver technicality).

---

## 2. Configuration Precedence — a Sanctioned Deviation from SDSI §6

SDSI §6 says a setting has exactly one source of truth: the YAML. A CLI
tool is the one sanctioned exception to that, because a flag *is* the
mechanism by which a user overrides a default for one invocation — that's
what a CLI is for. State the precedence explicitly, and keep it to a short,
predictable chain:

```
explicit flag  >  environment variable  >  config file  >  built-in default
```

- **Say which layer won, when it matters.** A `--verbose` or `--debug` run
  (or a dedicated `--show-config` subcommand) should be able to report
  where each effective value actually came from — a config value silently
  overridden by a stale environment variable is a common, confusing class
  of bug that's cheap to make diagnosable.
- **A config file, if the tool has one, still follows SDSI §6 for
  everything *not* meant to be overridden per-invocation** — secrets above
  all (SDSI §7 still applies in full: a CLI is not an exception to "no
  credential in a flag visible in shell history or `ps`").
- **Never read a setting from the environment as a silent substitute for an
  explicit flag the user could have passed** — an environment variable is
  for what should persist across invocations (an API endpoint, a default
  profile); a flag is for what the user is deciding right now. Blurring the
  two makes "why did this run behave differently" hard to answer.

---

## 3. Output: Streams, Exit Codes, and Machine-Readable Modes

- **stdout is the tool's actual output; stderr is everything else** —
  progress, warnings, diagnostics. A caller piping stdout into another
  program should never have to filter out anything but the data it asked
  for.
- **Decide color/styling once, at startup, based on whether stdout is an
  interactive terminal** (SDSI §8 already says this generically — a CLI is
  the clearest case of it). Piped or redirected output gets plain text,
  always; never per-line, never guessed from a flag alone unless the user
  explicitly forced it with something like `--color=always`.
- **Every exit path returns a meaningful, documented exit code** (SDSI §9):
  `0` for success, a small set of small positive integers for specific,
  named failure classes (bad arguments, a runtime failure, a
  couldn't-even-start failure) — documented once, in the help text or the
  README, and kept stable across releases the same way a flag's name is.
- **Offer a machine-readable output mode (`--json`, `--format=json`) for any
  command a script might reasonably wrap**, distinct from the
  human-readable default. Never make a script parse the human-readable
  text — that format is allowed to change for readability; the
  machine-readable one is a contract and versioned like one.
- **A destructive or hard-to-reverse action needs an explicit,
  non-interactive-safe confirmation path** — a `--yes`/`--force` flag for
  scripted use, and an actual interactive prompt only when stdin is a
  real terminal (never a prompt that silently blocks a CI pipeline waiting
  for input that will never arrive).

---

## 4. Packaging, Versioning & Distribution

- **`--version` prints the same `VERSION` file SDSI §17 already establishes
  as the single source of truth** — never a second, hand-maintained
  version string baked in elsewhere that can drift from it.
- **Pin dependencies the same way any other project does** (SDSI §15); a
  CLI tool that gets installed into other people's environments has an
  extra reason to keep its dependency tree small, since every dependency is
  something that now has to coexist with whatever else is already
  installed there.
- **Decide the distribution shape deliberately and write it down**: a
  pip/npm-installable package with an entry point, a single self-contained
  binary, or a container image are genuinely different operational
  commitments (install-time dependency resolution vs. a large but
  self-contained artifact vs. requiring a container runtime) — pick the one
  that matches how the tool is actually meant to be run, rather than
  defaulting to whichever is easiest to scaffold today.

---

## 5. Testing a CLI

- **Test the command's underlying callable directly, not by shelling out to
  the installed binary**, wherever that's possible — it's faster, and
  failures point at the actual function rather than at a subprocess
  boundary. Reserve a real subprocess invocation for a smaller set of true
  end-to-end tests that specifically verify the packaged entry point itself
  works.
- **Treat `--help` output and any machine-readable mode's shape as
  something a test can catch a regression in** — a snapshot/golden-file
  test that fails loudly when help text or JSON output shape changes
  unexpectedly is cheap insurance against silently breaking a script that
  depends on either.
- **A test that only proves argparse (or equivalent) is wired up correctly
  is a real, if thin, regression test** — the SDSI §14 standard still
  applies: name the regression it would catch (a flag silently stops being
  read, a subcommand stops being registered) rather than asserting nothing
  meaningful.

---

## 6. Working With an AI Agent on This Stack

- **A flag's behavior is the contract; changing it needs the same
  "stop and flag the scope change" discipline as any other breaking
  change** (SDSI §22) — don't quietly widen or narrow what a flag does
  while fixing something adjacent to it.
- **When extending this document from a real project's lessons**, follow
  the same discipline `SDSI-DJANGO-WEB.md` and `SDSI-MIDDLEWARE.md` were
  built with: read the project's actual code before generalizing from it,
  and note explicitly what's project-specific versus what's worth carrying
  forward here.
