> Read by every skill in this plugin before it does anything else — `sdsi`
> itself, plus `web`, `mw`, and `cli`, all point here rather than holding
> their own copy. A skill in *this* plugin reads this file directly by its
> relative path (`../../references/shared-context.md`), the same way
> `code-reviewer`'s own skills all read its `shared-context.md`. A skill in
> a **different** plugin (`council-of-claude`, `code-reviewer`) that wants
> this content should invoke the `sdsi` skill (`sdsi:sdsi`) by name instead
> of reading this file by a relative path — a plugin's own install location
> isn't something another plugin can assume, so a cross-plugin path is the
> one thing here that's genuinely fragile; a by-name skill invocation isn't.
> If something here needs to change, it only needs to change once.

# Software Development Standard Instructions (SDSI)

Generic foundation for every Python project. One document, no forks by project
type — project-specific scaffolding (new build vs. enhancement) is layered on
top of this later, as separate, shorter guidance, not as a second SDSI.

Living document: extend it whenever a project teaches us something worth
generalizing.

---

## 1. Guiding Principles

- **Consistency over cleverness.** Predictable code is what makes a handoff, a
  debug session, or AI-assisted work fast.
- **No setting or secret ever falls back to a value baked into the code.**
  A missing value should stop the run and say so, not silently substitute a
  guess.
- **Config and secrets are never code.** Nothing environment-specific or
  sensitive is hardcoded.
- **Observable by default.** Logging, error reporting and traceability are
  designed in from the start, not bolted on after something breaks in
  production.
- **Fail loud, fail early, fail once.** A problem should stop the run at the
  earliest possible point and report *everything* wrong in one pass, not one
  frustrating discovery at a time.
- **Resumable over restart-from-scratch.** Anything that moves data in batches
  should be able to pick up cleanly rather than reprocess everything.
- **One front door per capability.** One logger, one API client, one secrets
  accessor, one error handler. Extend it for everyone rather than working
  around it in one place.

### Non-negotiable working principles

These four hold regardless of project, language, or how small the change
looks — for a human working through this document or an AI agent following
it. Adopted from
[github.com/SpiritTrapper/simple-claude-skills](https://github.com/SpiritTrapper/simple-claude-skills).

- **No over-engineering.** Solve the problem actually in front of you, not
  the one you imagine might show up later. A pattern, an abstraction layer,
  or a config option earns its place by having a second real caller today —
  not by being "more flexible." *Example: a single hardcoded currency
  conversion doesn't need a pluggable exchange-rate-provider interface; a
  constant and a comment does the job until a second currency actually
  shows up.*
- **No assumptions.** A requirement, a config value, or an intended behavior
  that isn't stated doesn't get silently decided — it gets surfaced. Write
  it down as an open question (§22's `INTENT.md`/`SPEC.md` pattern is where
  this belongs on a new project) or ask, rather than picking an
  interpretation and moving on. *Example: the spec doesn't say whether a
  cancelled order refunds shipping — that's a question for whoever owns the
  spec, not a coin flip buried in the diff.*
- **No random or pointless changes.** Every line in a change traces back to
  a stated reason — a bug, a spec line, a catalog entry (see the
  `existing-code-reviewer` skill), a plan step. Reformatting, renaming, or
  "while I'm in here" edits that aren't part of the stated change get their
  own change, not a free ride in this one. *Example: noticing a typo in an
  unrelated docstring while fixing a bug is worth a separate, tiny commit —
  not a diff that makes the actual fix harder to review.*
- **Double-check your work.** Nothing is "done" on the strength of its own
  judgment alone — it's done once it's been verified against something
  outside that judgment: a test, a build, a screenshot, a second read. See
  §22's feedback-loop practice for how this gets operationalized day to
  day. *Example: run the test suite and paste the output before calling a
  task complete; "it looks right" is not a verification step.*

---

## 2. Naming & Casing

- **Functions, methods, arguments, local variables:** `snake_case`, spelled in
  full (`response`, not `r`; `error`, not `e`).
- **Classes:** `PascalCase`, and as **short as stays unambiguous** — prefer one
  clear word over a compound phrase. Drop a qualifier only when keeping it
  would collide with, or genuinely clarify against, something else already in
  the codebase:

  | Kept | Why |
  |---|---|
  | `LogFile` | `Log` is already the logger |
  | `HttpStatus` | `Status` is already the run outcome |
  | `ApiClient`, `ApiAuth` | one family; `Auth` alone is ambiguous |
  | `ErrorHandler` | "handler" already means something else nearby |

- **Constants:** `UPPER_SNAKE_CASE` — but reserved for **module-level
  constants and class-level configuration attributes.** Nothing else is
  written in uppercase.
- **Sub-folders:** `kebab-case`.
- **Modules (`.py` files):** `lowercase`, named for the **capability or
  domain concept they own** (`logs.py`, `secrets.py`, `config.py`), not
  forced to mirror a single class name — a module often holds one primary
  class plus its closely related exception types or helpers.
- **Markdown files:** root-level project documents — `README.md`,
  `CHANGELOG.md`, an AI-agent instructions file — are `UPPERCASE`.
  Everything else, including anything inside a `docs/` folder, is
  `lowercase-kebab-case.md`.
- **Configuration files:** `.yaml`.
- A **leading underscore** means internal to the module or class — not part
  of its public surface.

---

## 3. Project Structure & Dependency Direction

```
project-root/
├── src/
│   └── package_name/
│       ├── main.py            # entry point — holds no logic (§12)
│       ├── helpers/           # the one destination for shared/support
│       │                      #   code — shared functions, core utilities,
│       │                      #   any class used by more than one caller.
│       │                      #   No sibling core/, common/, shared/, or
│       │                      #   utils/ folder — see below.
│       ├── integrations/      # one module per external system/domain
│       │                      #   concept, plus a shared base class
│       └── tasks/              # one callable per operation, plus a
│                               #   registry that maps a name to its handler
├── tests/                      # every test, fixture, and test-tool
│                               #   config — see §14
├── config/
│   ├── default.yaml           # every setting, with comments — see §6
│   └── override/
│       ├── dev.yaml           # per-environment differences only
│       └── prod.yaml
├── docs/                       # operational documentation — see §20
├── scripts/                    # deploy/setup/maintenance tooling, not
│   ├── ps1/                    #   shipped application code — see below
│   └── python/
├── docker/
├── .vscode/                   # local run/debug configuration — see §18
├── .gitignore                  # see §16
├── requirements.txt           # or pyproject.toml
├── VERSION                    # see §17 — starts at 0.1.0 (§24)
├── CHANGELOG.md                # see §17
├── TODO.md                     # see §23
├── CLAUDE.md                   # project-specific conventions — see §22
└── README.md
```

**The project root holds no code and nothing loose.** Only the files and
top-level folders shown above — no `.py` file, no script, nothing runnable
sitting directly at this level. Application code lives under `src/`;
operational tooling lives under `scripts/`; nothing else earns a place here.

**Dependencies point one way: `helpers` ← `integrations` ← `tasks` ← entry
point.** A helper never imports from `integrations` or `tasks`. This same
one-directional-layering principle applies beyond this exact folder shape —
e.g. in a web app: infrastructure ← services ← routes/handlers ← app entry.

**`helpers/` is the one destination for shared or support code** — shared
functions, core utilities, and any class more than one caller uses. Don't
open a second home for it alongside `helpers/` (a `core/`, `common/`,
`shared/`, or `utils/` folder) — that's the exact fragmentation §11's "one
source of truth" warns against; extend `helpers/` instead.

Where a `Registry` maps a name (a task, a route, a command) to its handler,
have it **assert completeness at import time** — every declared name has a
handler — so a missed wiring step fails at startup, not three weeks later at
first use.

**`scripts/`** holds operational tooling — deployment, environment setup,
config publishing, one-off maintenance — organized by language
(`scripts/ps1/`, `scripts/python/`, and so on as needed). It's support
tooling for running and operating the project, not part of the shipped
application: `src/` doesn't import from it, and it doesn't import from
`src/`.

**The top-level source folder's name isn't fixed to `src/`.** Renaming it
to whatever fits the project's own domain (`site/` for a website, and
equally reasonable renames for other project shapes) is fine, as long as
the structural pattern underneath — `helpers/`, one-capability-per-module,
the dependency direction — stays the same. The name is a label; the shape
is the standard.

**An entry-point/runner script doesn't have to sit at the repo root just
because a framework's own scaffolding defaults to that.** It's legitimate
to nest it elsewhere if that fits a project's layout better — the cost is
that **every invocation has to be updated and kept updated** (build
files, docs, scripts, CI), and the non-default location has to be written
down in the project's own `CLAUDE.md` (§22), because a future session's
default assumption will otherwise be the framework's own convention,
silently regressing the project back toward it.

**A raw/source asset that gets built into a different, served/deployed
form belongs colocated with the code that consumes it, clearly
distinguished from its processed output copy.** A served copy silently
drifting from its source (edited in place, never regenerated) is a real
trap — name the two differently enough that which is which is obvious at
a glance.

---

## 4. No Magic Strings — Constants & Enums

Any string used for a comparison, a dispatch, a lookup key, or a config/env
variable name must be a named member of an enum or constants module, never a
bare literal repeated at each call site. A typo in a member name fails loudly
as an `AttributeError`; a typo in a bare string silently takes the wrong
branch or disables a check with no error at all.

- Use `StrEnum` for closed sets of values that get compared or dispatched on
  (statuses, task names, environment names, response types).
- Use a plain class of `UPPER_SNAKE_CASE` attributes for formats, templates
  and defaults that are never compared against — only ever read.
- **The one sanctioned exception:** a literal that is genuinely specific to
  one integration/vendor and used nowhere else (an endpoint path, a header
  name) can live as an `UPPERCASE` class attribute on that integration's own
  class. Centralizing something that belongs to exactly one place only makes
  it harder to find.
- Avoid resolving a variable by string key from a dynamic namespace
  (`locals()`/`globals()` lookups and similar); bind it directly so a typo
  cannot silently change which branch runs.

---

## 5. Comments & Docstrings

- Every module opens with a short docstring: what it's for, and why it's
  separate from neighboring modules.
- Every public function/method gets a docstring in this shape — a one-line
  summary, then `Input:` and `Output:`, naming each parameter's type and
  meaning and what comes back:

  ```python
  def retry(operation, attempts, delay, retry_on=Exception):
      """Call operation() until it succeeds, then return its result.

      Re-raises the last exception once attempts are exhausted, so a caller
      that cannot proceed still fails loudly.

      Input:
          operation (callable): takes no arguments.
          attempts (int): total tries, including the first.
          delay (float): seconds between attempts.
          retry_on (type|tuple): only these exception types are retried.
      Output:
          object: whatever operation() returned.
      """
  ```

- **Comments explain *why*, not *what*.** The code already says what it does;
  a comment earns its place by recording a decision, a constraint, or a trap
  that isn't otherwise visible.
- Every project has a root `README.md`: what it does, local setup, how to
  run/debug/test locally, how to deploy, and every environment variable or
  config key it depends on.

---

## 6. Configuration Management

- All tuneables live in a `default.yaml`, with per-environment differences
  only in `override/<env>.yaml`, deep-merged over the default at load time.
  State only what differs in an override — everything else is inherited.
- **No default values live in code.** A setting has exactly one source of
  truth — the YAML — and reading a missing key is an error, not a silent
  fallback.
- The **merged, per-environment configuration is validated against a schema
  before any work starts** — every key's type, allowed values and range
  declared up front. A missing, null, mistyped or out-of-range value stops
  the run and reports **every** problem at once, not one at a time.
- Add a `--validate-config` (or equivalently named) task/command that checks
  configuration and credential access without doing any real work — safe to
  run as a deploy pre-flight.
- **Distinguish *derived* values from *configured* ones.** A handful of
  values are computed from the run's own context rather than authored in the
  YAML — which environment's override was actually applied, how the caller
  invoked this run, what version of the code is running. Derive these and let
  them override anything the YAML happens to say; never let there be two
  places that could disagree about one of them.
- **Two independently-toggleable settings should never have one silently
  derived from the other, even when they usually change together.** An
  override that states one but not the other must not silently inherit a
  default that was fine for the setting stated but wrong for the one left
  unstated. State each explicitly in every override, even where they'd
  naturally seem to travel together — the failure mode (a default that's
  safe in one deployment topology and actively breaks another) is exactly
  the kind of thing that surfaces late, in whichever environment the
  default happened to be wrong for.
- Environment variables are reserved for **deployment wiring that has to
  exist before configuration can load** — config directory location, which
  environment this is, mount paths the deployment platform controls. Don't
  add a module-level tunable or read `os.environ` for an ordinary setting;
  put it in the YAML.
- **Never read a setting straight from `os.environ` inside business
  logic, as a substitute for the YAML.** A config class or module built
  around environment variables for ordinary settings is exactly the
  anti-pattern this section rules out — every setting has exactly one path
  from file to code (the schema below), and an environment variable that
  bypasses it is a second, silently-competing source of truth for the same
  value.
- **Placeholder convention:** a key that must be supplied by an override
  before it's usable is written as `<not configured>` in `default.yaml`,
  not a plausible-looking fake value — schema validation catches it before
  a run starts, and a real-looking value sitting in the default file hides
  which keys still need a real answer per environment. A key that's
  computed at load time rather than authored anywhere uses `<set at
  runtime>` instead, so a reader can tell "must override" and "this is
  derived" apart at a glance.
- Config files hold **non-secret settings only.** A secret's *name* can live
  in config; its *value* never does (§7).

**Adding a setting is three steps, always in this order:** add the YAML key →
add its named constant/enum member → add its schema entry. Skipping the
schema entry leaves it unvalidated.

---

## 7. Secrets & Credentials

- **No credential, API key, connection string or token appears anywhere in
  source control, config files, deployment templates, or the built
  artifact/image** — not even in commit history.
- Use a real secrets manager (Key Vault, Secrets Manager, etc.), read at
  runtime, held in memory only for the life of the process. Config holds only
  the secret's *name*.
- **Secret naming convention:** `<owner>-<purpose>-<kind>` — lowercase,
  hyphens, three parts, no exceptions (e.g. `payments-client-secret`,
  `reporting-database-pwd`). `<purpose>` and `<kind>` should be derivable
  from how the credential is used, so a name can't drift from the thing it
  belongs to.
- **One secrets store per environment**, rather than encoding the
  environment into the secret name. Repeating the environment in the name
  gives two places that can disagree, and risks a name written for one
  environment being copy-pasted into another.
- A **paired credential** (client id + secret, username + password) that must
  always rotate together is better stored as one delimited value
  (`username:secret`) than as two secrets that can drift apart — but only
  when they truly must move atomically; otherwise prefer two plain values,
  since a non-sensitive username in config can be read and changed without
  touching the vault at all.
- **Local-dev fallback (e.g. an environment variable) is for developers
  without vault access only, and must be explicitly disabled in every
  deployed environment**, so an unreachable vault fails loudly there instead
  of quietly reading a weaker source.
- **Rotation is a disable-old → change-at-the-source → set-new sequence,
  with no third step.** Disabling the current version is the one signal that
  can't be ignored — nothing can read a disabled value, so no code path can
  authenticate with something already wrong. Setting a new value creates a
  new, enabled version and every future read picks it up atomically; there is
  nothing to remember to turn back on.
- **A secret caught mid-rotation should be waited out, not failed on the
  spot.** Disabling the current version — the first step of the rotation
  sequence above — is a real state a reader can land on, not just a failure:
  a scheduled task or long-running process that happens to read the secret
  during that exact window would otherwise fail an entirely healthy run over
  a timing coincidence, and a vendor that locks an account after a few bad
  attempts turns that failure into an outage the moment the stale value gets
  retried against it. Tell "this version is disabled" apart from "this
  identity may not read it" using whatever the store's error response
  actually encodes (a vendor-specific inner error code, not just the outer
  HTTP status — both commonly answer with the same status alone), and only
  wait out the first: poll on a short interval up to a bounded ceiling, then
  fail loudly — naming the secret and the wait, never falling back to a
  stale in-memory copy — if the ceiling passes before a new version lands. A
  caller that must answer immediately rather than eventually (a deploy
  pre-flight, say) opts out of the wait explicitly rather than inheriting it.
- **A secret value is never logged, printed, cached to disk, or included in
  an error message.** Errors may name *which* secret and *which* store —
  never the value.
- Run **any text that could leave the process** — tracebacks, alert payloads,
  callback bodies — through a redaction step first. A traceback that quotes
  a failing URL can carry a signed token in its query string; redact by
  pattern (query-string credentials, `key = value` assignments whose name
  suggests a secret, bearer tokens) before it goes anywhere off-box. A local
  log file that never leaves the machine doesn't need this.

### Authenticating to the secrets manager

Above covers *storing* secrets in a real manager, name-only in config.
Separately: how does a running workload actually authenticate to that
manager? Tried in priority order, each gated by its own config flag:

1. **The platform's own workload identity** (a cloud provider's managed
   identity, or equivalent) — the only path in a real deployment. No
   credential exists anywhere in the image, the environment, or the repo;
   the platform itself vouches for the workload.
2. **The developer's own signed-in CLI/session credentials** — for local
   development *against the real store*, since a laptop has no workload
   identity of its own. What it can read is decided by the developer's
   own access grant, not by anything the app holds, and every use should
   log a visible warning — this is a debugging convenience, not the
   deployed path.
3. **A named environment variable** — the last-resort fallback for a
   developer with no access to the real store at all, and must be
   explicitly disabled in every real deployment (above), so an
   unreachable store fails loudly there instead of quietly reading
   something weaker.

**A workload outside the platform's own identity fabric is a real gap
this pattern doesn't solve for free.** A self-hosted box (on-prem, a home
server) has neither the platform's workload identity nor a practical
*persistent, unattended* session to borrow credentials from. Decide
explicitly, rather than picking silently: give it its own bootstrap
credential and accept that one secret now has to be held outside the
manager to reach everything else inside it, or leave that specific
deployment target out of the secrets-manager migration entirely and keep
it on a simpler mechanism — genuinely fine when that target is
low-stakes, rather than forcing a mismatched pattern onto it for
consistency's own sake.

---

## 8. Logging & Output

- Structured logging through **one central logger class**, never bare
  `print()` for anything that matters. One method is the actual producer of
  a log line; named shorthands (`.info`, `.warning`, …) all funnel through it,
  so there is a single answer to "was this written, and what did it look
  like."
- Standard levels, each with a clear job:

  | Level | Use for |
  |---|---|
  | `DEBUG` | Dev-only detail; hidden in deployed environments |
  | `INFO` | Normal progress — what the run is doing right now |
  | `WARNING` | Something's wrong; the run continues |
  | `ERROR` | One unit of work failed; the run may still complete others |
  | `CRITICAL` | The run cannot be trusted or cannot continue — what someone must act on tonight, not read about tomorrow |

  The filter is a **floor**: at `INFO`, everything INFO and above is written;
  DEBUG is dropped. Make the "would this even be written?" check public and
  cheap to call — a debug line that serializes a large object costs the same
  to build whether or not it's then discarded.
- If output has to reach more than one destination at once (console, a log
  file, a response payload back to a caller), write it once through a single
  fan-out point rather than duplicating calls per destination.
- **Decide whether output is colored/styled once, at startup, for the whole
  run** — never per line and never per stream. Base it on the destination
  (an interactive terminal, yes; a log file or anything structured, no).
  Deciding it once means every destination gets identical bytes and a log
  file can never end up with stray escape codes in it.
- If logging to a file, write on a **background thread** so a slow disk never
  blocks the actual work; bound how long shutdown waits for that queue to
  drain, and keep that bound comfortably under whatever grace period your
  deployment platform gives a process between "stop" and "kill."
- A message discovered *after* the log file has already closed can only
  reach the console — say so explicitly in code/comments rather than letting
  it silently vanish.

---

## 9. Error Handling

- Define a **typed exception hierarchy**, one root type for everything the
  app raises deliberately, with a specific subtype per layer or concern
  (an API-call failure, a cache failure, a database failure, a
  configuration failure, …). Never raise or catch a bare `RuntimeError`/
  `Exception` for an anticipated failure — a handler needs to be able to
  tell a downstream outage from a bad config from a bug.
- Centralize **fatal-error handling in one place** — call it once, from the
  outermost level, and build it *before* configuration or logging exist so a
  failure at any stage of startup is still handled. Two invariants govern
  that object:
  1. **Nothing inside it may raise.** An error handler that throws replaces
     the real failure with its own; a throw from a `finally` block also
     discards whatever exit behavior was intended. Guard every internal step
     and degrade to silence rather than propagate.
  2. **Nothing it hands off may leave the process unredacted** (§7).
- Use a **retry helper** for expected, transient failures inside a task
  (a flaky network call, a locked file) — it re-raises the last error once
  attempts are exhausted, so a real bug still fails loudly rather than being
  silently absorbed. Use the central fatal-error handler for failures that
  should end the run. Don't blur the two: retrying something non-transient
  just delays the same failure; treating something transient as fatal costs
  reliability for free.
- **A disabled/switched-off capability should fail its task, not silently
  return an empty success.** An empty result and a broken one look identical
  to whatever's watching the run; failing loudly is what keeps them
  distinguishable.
- **A run invoked with no clear instruction (no task/command given) should
  fail, not succeed as a silent no-op** — a scheduled job that does nothing
  and reports "fine" is the failure mode nobody notices until it's expensive.
- Give every exit path a machine-readable outcome, distinct from any
  free-text reason (which may be redacted and shouldn't be branched on):

  | Outcome | Roughly means |
  |---|---|
  | Succeeded | Ran fine |
  | Failed | Ran, and the work itself failed |
  | Invalid input | Bad/missing arguments — a usage error, not a runtime one |
  | Critical/startup failure | Couldn't even get configured — alert, don't retry |
  | Interrupted | Stopped by the platform mid-run (routine; don't treat as an incident) |

  Every exit path — including ones that fail before configuration finishes
  loading — should report *something* to whatever is waiting on the outcome.
  A caller blocked waiting for an answer that never comes just times out
  uninformatively.

---

## 10. Data & Process Flow

For any task that moves or transforms data in batches, use the same fixed
sequence every time, run by one shared piece of orchestration rather than
reimplemented per task:

```
source → staging copy → transform → destination
```

- The staging copy costs one file and buys a lot: a replayable snapshot of
  exactly what the source returned, so a broken transform can be fixed and
  re-run without going back to the source system a second time.
- Treat the staging area as **scratch space, not storage** — it should be
  safe to lose entirely between runs. Purge old entries at the start of a
  run rather than letting them accumulate.
- A period/time-window filter (e.g. "records changed since X") should be
  applied **after** the staging copy is written, never before — so the
  staging copy always holds the full, unfiltered response and a different
  window can be replayed from it later without re-hitting the source.
- Every record persisted to a destination should carry a small set of
  **lineage columns**: which source/system it came from, which run loaded
  it, when it was loaded, and (where useful) a content hash — enough that a
  bad load can be identified and cleanly removed later.
- When a data source can tell you "what changed since X" vs. cannot, make
  that distinction **explicit and declared per source/dataset**, not
  discovered by trial and error each time — and log loudly whenever a
  window is being emulated locally (full fetch, filtered after the fact)
  rather than genuinely pushed to the source, since the cost is easy to miss
  otherwise.

---

## 11. Reuse Over Reimplementation

Before writing something a task needs, check whether the shared layer already
provides it — an HTTP client, a secrets accessor, a cache, a logger, a way to
read/write files. If a shared helper doesn't quite fit a new need, **extend it
generically for everyone** rather than working around it in one place. A
capability implemented twice is a capability that will eventually disagree
with itself.

This is the DRY principle, applied at every level, not just functions: **one
source of truth for logic, constants, types, and validation rules.** Refactor
into a shared home the *second* time the same semantic rule appears — not
preemptively on the first occurrence, and not for code that merely *looks*
similar but means something different (two five-line blocks that happen to
resemble each other because the domain is genuinely separate are coincidental
duplication, not a DRY violation — leave them alone).

---

## 12. Entry Point & Composition Root

The entry point file (`main.py`/`app.py`) contains **no logic** — it wires
things together and exits with whatever the orchestration layer returns.
Startup order, dispatch to the right task/handler, and shutdown all live in
one composition-root module. Anything that would otherwise be a loose
function at the top of the entry-point file belongs in a helper, an
integration, or a task instead.

---

## 13. CLI / Task Design

For a project structured as a set of discrete, schedulable operations (batch
jobs, syncs, scheduled tasks), a single entry point with a task/command
selector keeps each operation small, testable, and independently retriable:

```
python main.py --task SOME-OPERATION
```

- Each named task does one job and can be run, scheduled, or retried on its
  own.
- Consider a control mechanism (a per-task or per-integration on/off toggle)
  when several tasks/integrations share one codebase, for operational
  flexibility without a redeploy.
- Prefer running the process as a **job that does one thing and exits**,
  rather than a long-running service, when the underlying workload is
  batch/triggered rather than request/response.

---

## 14. Testing

- **Every test, fixture, and test-tool config file lives under one
  `tests/` folder** (§3) — nothing scattered next to the source it tests,
  no per-module test subfolder inside `src/`. `pytest.ini` (or the
  `[tool.pytest.ini_options]` table in `pyproject.toml`), `conftest.py`,
  fixtures, and test data all live inside `tests/` too. Mirroring `src/`'s
  structure inside `tests/` is fine and often helps navigation
  (`tests/helpers/test_logs.py` for `src/package/helpers/logs.py`) — a
  second home for any of it outside `tests/` is not.
- `pytest` as the standard framework.
- Unit tests cover business logic; mock external systems (APIs, databases,
  cloud services) rather than calling them in unit test runs.
- Integration tests that hit real dev/sandbox endpoints are welcome, but
  should be separately marked/flagged so they can be run selectively.
- Prioritize meaningful coverage of core logic and edge cases over chasing a
  100% coverage figure.
- Tests run in CI and must pass before merge.
- Aim for the full pyramid — unit, integration, **and** end-to-end — not
  unit tests alone; which layers matter varies by project, but the gap
  shouldn't be silent.
- A coverage number is a signal, not a target. A test that only pads it — a
  snapshot dump with no real assertion, a tautological assert, a test that
  mocks the very thing it's supposed to be testing — counts as **zero**, not
  as coverage. If you can't name the regression a test would catch, delete
  it rather than keep it for the count.

---

## 15. Dependency Management

- **The standard library is preferred.** A third-party package is added only
  when it's genuinely necessary and has a long, trustworthy track record.
- Prefer a small number of well-understood dependencies over a large
  transitive tree — e.g. a couple of direct REST calls over pulling in a
  full vendor SDK, when that's all that's needed. Every dependency is
  something that has to be scanned, updated, and trusted.
- Pin versions (`requirements.txt` with pins, or `pyproject.toml` + lockfile).
  Always develop inside a virtual environment.
- Review and update dependencies on a regular cadence; scan for known
  vulnerabilities (`pip-audit`/`safety`) as part of CI, not as an
  afterthought.
- Import anything heavy or environment-specific **lazily, by name from
  config**, so a given deployment only pays for what it actually uses.
- **Resolve to the latest stable version at the time a dependency is
  added** — not an old pin copied out of habit from another project. Commit
  the lockfile so the resolution is reproducible.
- **No floating tags in anything deployed** — no `latest`, `main`, or `HEAD`
  for a dependency or a container base image; pin container images to a
  digest, not just a tag, so a retag upstream can't silently change what
  ships.
- A vulnerability scan that's merely scheduled to run *eventually* doesn't
  count as clean — it has to actually be clean (or explicitly, visibly
  waived) before merge.

---

## 16. Version Control & Commit Hygiene

- Feature branches off `main`/`develop`; PR review required before merge.
- Conventional Commits style messages: `feat:`, `fix:`, `chore:`, `docs:`,
  `refactor:`, `test:`.
- No secrets in commit history, ever — `.gitignore` local secret files, and
  use a pre-commit secret-scanning hook where possible.
- **`.gitignore` excludes everything that isn't essential, reviewable
  source** — generated or compiled artifacts (`__pycache__/`, `*.pyc`,
  `.pytest_cache/`, `.mypy_cache/`), local environment files (`.env`),
  anything under a scratch/cache/log directory (§10), editor backups
  (`*.bak`, `*.orig`), and any config file rendered with real values
  substituted in by a deploy script. Nothing that isn't needed to build,
  test, or run the project in production has any business being tracked.
- A pre-commit (or equivalent) hook is a good place to **enforce documentation
  discipline mechanically** — e.g. refuse a commit that touches shippable
  code without a corresponding `CHANGELOG.md` entry (§17). Keep an escape
  hatch (`--no-verify`) for the genuinely-not-a-release commit, and repeat
  the check server-side in CI where the escape hatch can't reach. See §17
  for a fuller automation of this — a hook pair that bumps the version and
  promotes the changelog for you.

---

## 17. Versioning & Changelog

- One `VERSION` file at the project root is the single source of truth for
  the current version — starting at `0.1.0` for a new project (§24); bump
  it in the **same change** as the code/config that earns the bump, and
  tag the build to match.
- Version semantics are tied to **operational impact on someone deploying
  it**, not just to API shape:

  | Bump | Means | What the operator has to do |
  |---|---|---|
  | **MAJOR** | A deployed environment breaks until someone acts (a renamed/removed config key, a new required secret, a new grant, a removed operation) | Plan the deploy; read the whole entry |
  | **MINOR** | New capability, existing behavior unchanged, but new required settings (settings have no code default — §6) | Update configuration, then deploy |
  | **PATCH** | Code only — no config or secret change | Drop-in replacement |

- **`CHANGELOG.md` is written for whoever deploys the release, not for
  whoever reviewed the diff.** A commit message describes a change; a
  changelog entry describes a release.
- **Structure: one heading per version, with four fixed subsections
  underneath, always in the same order** — a human scanning the file
  finds the same shape every time, whichever version they're reading:

  ```markdown
  # Changelog

  All notable changes to this project. Organized by version, newest at
  the top — the opposite growth direction from `TODO.md`'s **Done**
  section (§23), which appends at the bottom; a changelog is read most
  often right after a release, so the newest entry stays the one you see
  first. See `VERSION` for the current release and SDSI.md §17 for what a
  version bump means.

  ## 🚧 Unreleased

  ### Added or New Features
  (none)

  ### Removed
  (none)

  ### Changed
  (none)

  ### Bug/Issues/Fixes
  (none)

  ## 🆕VERSION 1.1.0 📅 2026-09-08

  ### Added or New Features
  - <what's new, in plain language>

  ### Removed
  - <what's gone, and what replaces it if anything>

  ### Changed
  - <what's different in existing behavior — call out anything an
    operator has to do (a new config key, a new secret, a new grant)
    right in the bullet, since that's exactly what a plain code deploy
    will miss>

  ### Bug/Issues/Fixes
  - <what was broken, now fixed>

  ## 🟥VERSION 1.0.0 📅 2026-08-15

  ### Added or New Features
  - Initial release.

  ### Removed
  (none)

  ### Changed
  (none)

  ### Bug/Issues/Fixes
  (none)
  ```

  Every heading carries two markers, in this order:
  - **🆕 / a color square** — exactly one entry in the file is 🆕 at any
    time: the newest, current version. Every other, already-shipped
    version gets a plain colored square instead, assigned **once, when
    that version ships, and never changed again** (same "written once"
    rule as the heading itself) — cycling through this order as each new
    version ships: 🟥 🟧 🟨 🟩 🟦 🟪 🟫, wrapping back to 🟥 after 🟫.
    When a new release is added: it becomes 🆕, and the entry that held
    🆕 just before it takes the next color in the rotation — nothing
    else already colored in the file ever changes.
  - **📅 date** — the day that version's changelog entry was finalized
    (the day of the version-bumping commit, per "update the changelog
    before committing" below), in unambiguous `YYYY-MM-DD` form.

  **`🚧 Unreleased`** sits permanently at the very top, above even the
  current 🆕 version — it's the one section expected to be edited
  repeatedly, unlike every `VERSION` heading below it (the "written once"
  rule above doesn't apply here, precisely because nothing under
  `Unreleased` is released yet). Log a change into it, under whichever of
  the four subsections it belongs to, as soon as it's made — not saved up
  for the end.

  **On commit, decide: did this change touch code?**
  - **Yes** — it bumps `VERSION`, **even if only a PATCH**, however small
    the change. `🚧 Unreleased` is renamed to `🆕VERSION x.x.x 📅 <today>`,
    becoming the new current entry; the entry that was 🆕 a moment ago
    takes the next color in the rotation (the same swap as any other new
    release, above); and a fresh, empty `🚧 Unreleased` goes back at the
    top for whatever comes next.
  - **No** (documentation, comments, anything with no code diff) — no
    version bump. Move `Unreleased`'s bullets into the matching
    subsections of the current 🆕 entry instead, then reset `Unreleased`
    back to empty. The change still gets recorded — it just rides along
    on the existing version rather than earning a new one.

  A new release is **inserted at the top**, just under the title/intro and
  above the previous newest entry — the most recent version is always the
  first thing a reader hits. An empty subsection stays in place, marked
  `(none)`, rather than being dropped: the fixed shape is the point, so a
  reader never has to wonder whether **Removed** was skipped or genuinely
  had nothing in it.
- Update the changelog **before** committing the change it describes, not
  afterward from the diff — a changelog written in arrears tends to
  describe what changed in the code, not what the operator has to do
  about it, which is the harder and more valuable half. Anything an
  operator needs to act on belongs directly in **Changed** (or
  **Removed**, if that's what's gone) — not a separate note that's easy
  to scan past.
- Promoting a build to another environment should be a **retag of an
  existing, already-tested artifact**, never a rebuild — a rebuild is a
  different artifact than the one that was tested, whatever the version
  number says.
- **Every commit names the version it belongs to in its own message —
  not just the commits that bump it.** A commit that bumps the version
  carries a plain `VERSION x.x.x` line (in the commit body, or as the
  subject itself: `VERSION x.x.x — <what changed>`); a docs-only commit
  that doesn't bump anything still names the version it landed in, tagged
  `VERSION x.x.x-updated` so it reads distinctly from an actual bump. This
  makes `git log` searchable by version without cross-referencing the
  changelog for which commit shipped what, and leaves no commit — bump or
  not — without an answer to "what version was this."
- Each `## VERSION x.x.x` heading is **written once and never silently
  rewritten** — a mistake in an already-shipped entry gets corrected by a
  new version and a new entry, not a rewrite of one already released.

### Automating the version bump and changelog promotion

The policy above is genuinely automatable as a git hook, for a project
with few enough committers that a merge race isn't a design concern:

- **Two hooks, not one.** `pre-commit` decides whether the commit touches
  code, bumps `VERSION`, and promotes `CHANGELOG.md`'s `Unreleased`
  section — all staged into the same commit. `commit-msg` appends the
  version to the commit message, because the message doesn't exist yet
  at `pre-commit` time (hook order: `pre-commit` → `prepare-commit-msg` →
  message finalized → `commit-msg` → `post-commit`) — it reads whether
  `pre-commit` staged a `VERSION` change this run to decide which of the
  two message-tag forms above to append: plain `VERSION x.x.x` if it did,
  `VERSION x.x.x-updated` (the version already in the file, unchanged) if
  it didn't.
- **Guard against double-appending the version line on `git commit
  --amend`** — check whether the exact line is already present in the
  message file before appending, in both hooks. Without that check,
  amending a commit re-runs `commit-msg` against a message that already
  has the line, stacking a second copy onto it.
- **A simple file-path heuristic decides "docs-only"** (everything staged
  falls under a docs folder or matches a doc-file extension) rather than
  trying to infer semantic intent from a diff.
- **Respect a bump already made by hand** — a MAJOR/MINOR-vs-PATCH
  distinction isn't inferable from a diff, so if `VERSION` is *already*
  staged with a change when the hook runs, treat that as the deliberate
  choice and only handle the changelog promotion.
- **Store hook scripts in a tracked repo folder** (`scripts/`, §3) and
  wire them via `git config core.hooksPath <folder>` — never rely on
  copying into the untracked, unversioned `.git/hooks/` directory by
  hand. Wire this into whatever script already bootstraps local dev, so
  a fresh clone gets it automatically.
- **Test a new hook against a real, throwaway commit before trusting
  it** — create a trivial staged change, commit for real, inspect the
  actual result; don't reason from the script's source alone (§22's
  "read the real thing" principle applies to your own tooling too).
- **Never use a hard reset to undo a test commit — or any commit — when
  the working tree might hold other, unrelated uncommitted changes.** A
  hard reset discards *every* uncommitted change to every tracked file,
  not just what was in the commit being undone. A soft reset (keeps
  everything staged) or a plain mixed reset (keeps everything, unstaged)
  is the safe default any time the working tree isn't known to be
  otherwise clean; reach for a hard reset only after confirming there's
  nothing else in the tree worth keeping.

---

## 18. Local Development Environment

- Local run/debug configuration (IDE launch configs, `docker-compose`
  files, etc.) is treated as **part of the application**, not a personal
  convenience — keep it in version control and keep it in sync with
  anything that changes how the app is invoked (a new task, a new required
  environment variable, a new environment to select).
- **No credential ever goes in a committed local-run file.** Local secrets
  come from the developer's own shell environment or a gitignored local env
  file, never from anything checked into git.
- Where possible, give a local run the same shape of wiring a deployed run
  gets (the same environment variables, the same config-loading path) so
  local behavior is a genuine preview of deployed behavior, not a separate
  code path.

---

## 19. Containerization & Deployment

- Keep configuration **out of the built image** — mount or inject it per
  environment at deploy/run time, so one build artifact is promotable across
  environments without rebuilding (see §17).
- Use a clear, consistent naming/tagging convention per environment so it's
  never ambiguous what's running where.
- Prefer your cloud platform's native scheduling/orchestration over standing
  up separate orchestration infrastructure, unless there's a concrete reason
  the native option doesn't fit.
- Document the **local** dev/run/debug workflow separately from the
  **deployment** workflow — they solve different problems and get confusing
  mixed into one document.
- Prefer a process that runs one job and exits over a long-running service,
  when the workload is inherently batch/triggered (§13).

**A cloud platform's managed volume-mount primitive commonly mounts a
whole directory, not a single arbitrary file** — unlike a plain
Docker-Compose bind-mount, which can target one file directly. Mounting a
managed volume straight over a directory that also holds files baked
into the image (committed config, for instance) will clobber them. Mount
it at a separate path instead, and point the app at that path with one
small piece of wiring (a config value or environment variable naming the
path, defaulting to the in-image location so every other deployment
target needs zero change).

**Check whether the platform already has a native secrets/identity
mechanism before building a file-mount (or other) workaround just to get
secrets out of environment variables.** The platform's own answer
(workload identity + a real secrets manager, §7) is very often simpler
than provisioning storage/volume infrastructure to avoid environment
variables — don't reach for the more complex mechanism out of habit when
a simpler, native one already exists.

**A deployment with a different trust boundary needs its
security-relevant settings configured for *its own* boundary,
explicitly** — never assume another environment's settings (a
cloud-hosted, TLS-terminated deployment's, say) are a safe default to
inherit for a self-hosted or differently-exposed one. The two can have
fundamentally different assumptions baked into what "safe" even means.

---

## 20. Documentation

- Update documentation **in the same change** as the code it describes, not
  afterward — a document that lags is worse than one that's simply missing,
  because it's still believed.
- **The golden rule: any change that affects one of the document types
  below updates that document, in the same change.** Not "eventually,"
  not "in a follow-up" — the same change.

### Document types

`docs/` (§3) holds *operational* documentation — separate from `README.md`
(what the project does), `CLAUDE.md` (how the code is written,
project-specific conventions, §22), and `CHANGELOG.md` (what changed and
what an operator has to do about it, §17):

| Document | Answers | Update it when… |
|---|---|---|
| A setup doc (one per deployable shape, if there's more than one) | How to stand up the environment from nothing | A new resource, credential, or one-time step is added to getting a fresh environment running |
| A deployment doc | How to ship a change | The deploy sequence, a required check, or a rollback step changes |
| A cheat sheet | The commands reached for when something's wrong — every operation, every flag, where things land | A task/operation is added, renamed, or removed |
| A documentation index | What every other document covers, and what it doesn't — points elsewhere for anything not operational | A document is added, renamed, or removed |
| A features doc (optional) | What's been built, in plain language, for a non-technical audience | A user-visible capability ships |

- **Every command block names where it runs** — a local shell, CI, inside
  a running container, a cloud console — never left ambiguous. A command
  that looks identical in two environments can still fail in one of them
  for a reason that has nothing to do with the command itself.
- Keep a short table, somewhere durable, mapping "what changed" to "what
  else has to be updated" — the table above is a starting point, not the
  full list for every project. Making the mapping explicit is what keeps
  documentation from silently drifting out of sync as a project grows.

---

## 21. Code Design Rigor: SOLID & Strict Typing

Complements §1's KISS instinct and §11's DRY practice with two more
disciplines, adopted from
[github.com/SpiritTrapper/simple-claude-skills](https://github.com/SpiritTrapper/simple-claude-skills).
Both apply at review time, not just at write time — a self-check before
calling anything done.

### SOLID, applied practically

- **Single responsibility.** A class or module has one reason to change. If
  describing what it does needs "and," it's probably two things — this is
  the same instinct behind §3's `helpers`/`integrations`/`tasks` layering,
  just applied one level down to a single class.
- **Open for extension, closed for modification.** Add a new case by adding
  a new implementation (a new class, a new registered handler — see §3's
  registry pattern), not by growing a chain of `if`/`elif`/`switch` keyed on
  type. A growing conditional chain is the tell that a new abstraction is
  overdue.
- **Liskov substitution.** A subtype has to honor the contract of what it
  replaces — same expectations on inputs, same category of outcome. A
  subtype that requires extra setup, or one whose failure modes look
  nothing like its parent's, is not a real substitute, however similar the
  interface looks.
- **Interface segregation.** Size an interface to what a caller actually
  needs, not everything a class could ever expose. A caller depending on
  one method shouldn't be handed — or forced to implement — nine others it
  never calls.
- **Dependency inversion.** Infrastructure — an HTTP client, a database
  connection, a secrets accessor — is passed in (constructor, parameter,
  config), never constructed inside business logic. This is the same
  instinct as §6/§7's config/secrets injection, generalized: business logic
  should describe *what* it needs, not *how* to get it.

### Strict typing

- Type hints are load-bearing, not decorative. Every public function/method
  signature is fully typed (§5 already requires this; this section is
  about what "typed" actually means in practice).
- No blanket type-suppression escapes (a bare `# type: ignore`, a cast to
  `Any` to make an error go away) as a substitute for fixing the actual
  mismatch. A suppression that's genuinely warranted names *why*, next to
  the line it covers.
- External or untrusted input (an API response, a file, a CLI argument, a
  webhook payload) enters as an unvalidated shape and gets validated at the
  boundary — once — before anything downstream treats it as trustworthy.
  This is the same discipline as §6's config-schema validation, applied to
  runtime data instead of configuration.
- A sensitive or easily-confused primitive (an ID, a monetary amount, a
  currency code) is worth its own small type rather than a bare `str`/`int`
  that a caller could accidentally pass in the wrong order. Cheap insurance
  against an entire class of mix-up bugs.

---

## 22. AI-Native Development Workflow

Applies with full force on **new projects** (per this document's
enhancement-vs-new-build split — the `existing-code-reviewer` skill covers
the enhancement side); adopt what fits when working on established code.
Adapted from Anthropic's AI-Native SDLC playbook
([claude.com/blog/the-ai-native-sdlc-playbook](https://claude.com/blog/the-ai-native-sdlc-playbook))
— read the source for the full depth behind each stage; this section
distills it into what SDSI expects.

The core shift: **every stage ends by committing a markdown artifact the
next stage reads.** The chain of artifacts is the audit trail — what was
asked for, what was decided, what was built, what was found — and it's what
makes "no assumptions" and "double-check your work" (§1) actually
enforceable rather than just aspirational.

### The artifact chain

| Stage | Artifact | Captures |
|---|---|---|
| Plan | `INTENT.md` | The problem, in the requester's own words — what's wanted, why, and under what constraints. Open questions stay open questions here, not silent assumptions. |
| Design | `SPEC.md` | Requirements and design in one pass, checked against this project's own standards (this document) as it's written, not discovered in review afterward. |
| Build | `PLAN.md` | Which files change, in what order, and what proves the change worked — written and reviewed *before* any code is written. |
| Build | the diff + its tests | The implementation itself, plus whatever verifies it (§14). |
| Deploy | the PR + review findings | What was checked, by whom (or what), and what was decided. |
| Maintain | a new `INTENT.md` | Anything production surfaces — an incident, a drift, a bug — re-enters at Plan, not as an ad hoc fix off to the side. |

Each artifact is a real, version-controlled file — not a conversation that
evaporates when the session ends. A file that isn't written down didn't
happen, for audit purposes.

**A historical planning/spec artifact — the `INTENT.md`/`SPEC.md`/`PLAN.md`
chain, or any dated record of what was decided at the time — is generally
left untouched when later, unrelated work changes what it describes.**
Rewriting it to match new reality misrepresents history, and the whole
point of the artifact chain is that it's a permanent audit trail, not a
living reference. **The exception:** when the historical content itself
is an active, ongoing source of confusion going forward — a superseded
decision or direction still described as if it were current, that a
future session (human or AI) could easily mistake for the present state.
There, updating it (or clearly marking it superseded) is worth the
"rewriting history" cost. This is a judgment call to make and flag
explicitly each time, not a blanket rule in either direction.

### Plan before code, always

Nothing gets implemented from an unstated plan. For anything beyond a
trivial fix: write `INTENT.md` (what's wanted and why), then `SPEC.md` (how
it fits this codebase and this standard), then `PLAN.md` (which files, what
order, what proves it) — and only then start changing files. Each of these
is a natural place to apply the "no assumptions" principle (§1): an open
question belongs in the artifact, not silently resolved.

This scales down. A one-line fix doesn't need three files — but it still
deserves a stated reason ("no random or pointless changes," §1) and, if the
fix isn't self-evidently safe, a plan of exactly one sentence before
touching code beats no plan at all.

### Reference an existing system by reading it, not recalling it

**"Do it the way project/system X already does it" means reading X's
actual implementation before designing — reasoning from a description or
a remembered impression of "how it's probably done" isn't a substitute.**
Reading the real thing in full can also surface that the reference case
never had to solve the exact problem now in front of you, which is itself
important information to bring back before designing, not something to
discover mid-implementation.

### Verify before calling anything done

Every task needs a way to check itself — tests, a build, a screenshot diff —
and the check runs *before* the work is reported done, not after someone
else notices it's broken ("double-check your work," §1, operationalized).
For a bug fix specifically: write the failing test first, confirm it fails
for the expected reason, commit it, *then* make it pass without touching the
test. A test that predates the fix and wasn't rewritten to accommodate it is
real proof the bug is gone.

### Institutional knowledge lives in files, not habit

A team's actual conventions, gotchas, and repeated corrections belong in a
project-level `CLAUDE.md` (or equivalent) — commands, architecture notes,
and the mistakes that keep recurring — kept under a page and updated the
moment a mistake happens twice. This document (SDSI.md) is the standard; a
project's own `CLAUDE.md` is where project-specific detail and reminders
particular to *this* codebase live, without repeating what SDSI already
covers.

Anything that has to be applied consistently and updated from one place — a
security checklist, an API convention — is a strong candidate for a skill (a
`SKILL.md` with a clear trigger), not a paragraph someone has to remember to
mention. This entire document works the same way: written once, referenced
everywhere, updated centrally when the standard changes.

**The same applies the moment a project deviates from one of SDSI's own
default assumptions** (§3's source-folder naming, a folder shape, anything
else this document otherwise takes as given) — write the deviation down in
`CLAUDE.md` immediately, precisely so a future session doesn't quietly
regress back toward SDSI's usual default by following the standard
instead of the deviation. Don't wait for the deviation to cause a visible
problem first.

### Review runs in both directions

A code change gets reviewed against this standard, the accepted `SPEC.md`,
and the accepted `PLAN.md` — not just against a reviewer's general
instincts. Findings get a severity, and only the ones that would actually
break behavior, leak data, or breach a stated policy block anything; style
nits don't. Whichever review layer catches a mistake, the same mistake
getting caught *twice* is the signal to add it to the project's `CLAUDE.md`
so a session catches it the first time going forward.

### Scope changes get flagged, not absorbed

When a request's scope grows mid-conversation past what was originally
understood — a small, contained fix that turns into something touching
production secret-handling, or a decision that starts affecting every
deployment target instead of the one originally in view — **stop and say
so explicitly**, rather than quietly absorbing the growth into the
original, smaller-scoped task. Reclassify and get a fresh, explicitly
scoped decision before designing further.

### Stage gates, not a free-for-all

Human judgment concentrates at the gate between stages — approving an
`INTENT.md`, accepting a `SPEC.md`, approving a `PLAN.md`, merging a PR —
rather than being spent re-litigating each line of implementation. Once a
plan is approved, staying inside it is the default; departing from it
mid-implementation means updating `PLAN.md` in the same change, not letting
the plan quietly go stale.

### Closing the loop

Production issues re-enter as a new `INTENT.md`, not as a special
off-process hotfix path — the same Plan → Design → Build → Test → Deploy
sequence applies, just triggered by a monitor or an incident instead of a
person's idea. Every incident that ships a fix earns a permanent regression
test (§14), so the same class of failure can't quietly recur.

---

## 23. TODO.md — Tracking Work Across Sessions

A running list of outstanding work, kept at the project root alongside
`CHANGELOG.md` and `VERSION`. Where those two are the permanent, versioned
record of what already shipped, `TODO.md` is the working, ever-changing
list of what hasn't — cheap to add to, reword, or drop, because nothing in
it is a historical record yet.

### What goes in it

Anything that comes out of a session and isn't done — a follow-up, a
deferred decision, a bug found but not yet fixed, an open question left
over from an `INTENT.md` or `SPEC.md` (§22) that's too small to deserve its
own artifact chain. For anything substantial, `TODO.md` is the entry point,
not the destination: promote it to a real `INTENT.md` (§22) once it's
bigger than a line item.

### Format

Keep it flat and plain — a human should be able to read and add to it
without learning a convention:

```markdown
# TODO

- [ ] <what needs doing, in plain language> — <why, if not obvious>

---

## Done

- [x] <what was done> — completed <date or VERSION x.x.x>
```

No priority tiers, no assignees, no due dates, unless a project genuinely
needs that structure — a todo list isn't the place to prove "no
over-engineering" (§1) wrong either way.

### Who updates it, and when

- **The AI updates it continuously.** A session that ends without a pass
  over `TODO.md` — adding what's newly outstanding, checking off what's
  newly done — leaves the file stale, which is worse than not having one.
- **The human can add directly, any time**, in the same plain-language
  format — no special tooling required to contribute an item.

### Completing an item

1. Check it off (`- [x]`) and move it to the **Done** section, appended
   after the last entry there — the section reads oldest-to-newest,
   top-to-bottom, so a new completion lands at the very bottom of the
   file.
2. If the completion is part of a commit that bumps the version (most real
   completions will be), tag it with that version instead of a bare date
   once the version is known — see §17 for the versioning mechanics
   themselves. A single commit can close several `TODO.md` items at once;
   all of them get the same version tag.
3. Use the closed items — plus the diff itself — as the raw material for
   `CHANGELOG.md`'s `🚧 Unreleased` section (§17): log them there as the
   work happens, not saved up for the end. At commit time, follow §17's
   promotion rule — a code change bumps `VERSION` and `Unreleased`
   becomes the new current entry; a non-code change folds into the
   existing current entry instead. Either way, commit with the version
   named in the message when one was bumped (§17).

If **Done** grows long enough to feel unwieldy, that's a signal to lean on
`CHANGELOG.md` and git history instead of pruning `TODO.md` by hand —
`CHANGELOG.md` is already the permanent record; `TODO.md`'s **Done**
section is a convenience, not the archive.

---

## 24. Starting a New Project

The kickoff sequence for a brand-new, empty project — as distinct from the
`existing-code-reviewer` skill, which covers one that already has code.

### Trigger

The user drops `SDSI.md` into an empty (or near-empty) project folder and
tells Claude they want to start a new project. That's the signal to run
this sequence rather than treating it as an ordinary feature request.

### Sequence

1. **Brainstorm before planning.** Turn whatever the user first said into
   something concrete with a brainstorming-style pass (see SETUP.md for a
   brainstorming skill option) — the same instinct as §22's Plan stage:
   ask the questions an analyst would ask (scope, users, constraints, what
   success looks like), rather than jumping straight to a plan from a
   one-line idea.
2. **Surface every real decision with `AskUserQuestion` — don't assume any
   of them** (§1). Nothing about this document's own defaults (a language,
   a framework, a hosting target, a testing approach) should be silently
   carried over into a new project without confirming it's actually the
   right fit here. Decisions typically worth surfacing:
   - Primary language/framework, if not already implied by the ask
   - What "done" looks like for a first version — the MVP scope
   - Deployment target (local script, container, cloud service — §19)
   - Real constraints (deadline, must integrate with an existing system,
     data sensitivity)
   - Anywhere this project should deviate from SDSI's defaults, and why
3. **Write `INTENT.md`.** Capture the brainstorm and the decisions from
   step 2 (§22's Plan artifact); let the user correct it before it's
   treated as settled.
4. **Write `SPEC.md`.** Requirements and design against `SDSI.md` and
   whatever project-specific constraints came out of step 2 (§22's Design
   stage).
5. **Scaffold the full skeleton before writing any real logic.** Be
   explicit about this rather than organic — this is exactly where gaps
   like a missing `CHANGELOG.md` or code left sitting at the project root
   come from:
   - Root: `README.md`, `CLAUDE.md`, `TODO.md` (empty), `CHANGELOG.md`
     (intro plus an empty `🚧 Unreleased`, §17), `VERSION` (containing
     `0.1.0`), `.gitignore` (§16) — and nothing else at this level (§3).
   - `src/<package>/` with `helpers/`, `integrations/`, `tasks/`, and
     `main.py` (§3), even if each starts nearly empty.
   - `tests/` (§14), `config/default.yaml` + `config/override/` (§6),
     `docs/` (§20), `scripts/` (§3), `docker/`, `.vscode/` (§18).
   - Commit this skeleton on its own, before any feature work — it's the
     thing every later session assumes already exists.
   - Once there's at least this skeleton in place — enough for the
     `claude-code-setup` plugin (SETUP.md) to have something to scan —
     run it to recommend the MCP servers, skills, hooks, and subagents
     actually suited to this stack, rather than guessing generically
     before anything exists to analyze.
6. **`PLAN.md`, then build.** Same as §22's Build stage from here.
