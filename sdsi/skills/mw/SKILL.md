---
name: mw
description: >
  SDSI's companion for middleware and integration services — processes that
  move and reconcile data between several external systems (an ETL/sync
  job, a connector layer feeding a system of record, a data pipeline).
  Covers project layout for a connector/business-rules/task split,
  multi-system configuration, secrets for many systems at once, the
  extract-then-business-rules data flow, how a run reports its outcome, and
  deploying one image as several run shapes. Use whenever building or
  working on a middleware, integration, sync, or data-pipeline service.
  Depends on SDSI's base standard — read `../../references/shared-context.md`
  first, always; this skill only states what's additionally true for a
  middleware/integration codebase and assumes that standard already applies
  in full. Also triggers on "/sdsi:mw" or "sdsi middleware".
---

Before anything else, read `../../references/shared-context.md` — the base
SDSI standard, shared by every skill in this plugin. It's a hard
prerequisite, not an optional read. Everything there applies here in full;
what follows below only adds what's specific to a middleware/integration
codebase on top of it: project layout for a connector/business-rules/task
split, the systems-block configuration pattern, secrets and identity for
many systems at once, the extract → business rules → destination data flow
and where the mechanical/business boundary actually sits, the response
contract a run reports back through (exit codes, a machine-readable
outcome, callback vs. console reporting), deploying one image as several
run shapes, and documentation/change discipline on an established, ongoing
codebase.

## Don't repeat the base standard

If something below looks like it's only restating a general SDSI rule
rather than adding a middleware-specific one, that's a defect in this
document — flag it rather than leaving it duplicated.

---

# SDSI Companion: Middleware & Integration Services

A companion to `SDSI.md`, not a replacement for it — this project follows
`SDSI.md` in full, and this document adds what's specific to a middleware or
integration service: a process whose whole job is moving and reconciling
data between several external systems (a sync job, a connector layer
feeding a system of record, a batch data pipeline). Learned in practice
building `ariel`, an integration service moving job, workforce, and spend
data from several source systems into a financial system of record and,
from there, into a data warehouse.

Living document, same as `SDSI.md`: extend it whenever a middleware project
teaches us something worth generalizing — from an actual second project,
not from more speculation on this one (SDSI §1).

---

## 1. Project Layout for a Middleware Service

SDSI §3 gives the shape and the dependency direction (`helpers` ←
`integrations` ← `tasks` ← entry point); a middleware service earns one more
layer in the middle, because "download a system's data" and "decide what
that data means" are genuinely different kinds of work with different
change rates:

```
src/
  main.py            entry point — no logic (SDSI §12)
  helpers/           infrastructure that knows nothing about any vendor —
                      SDSI's shared-code home, unchanged
  connectors/        one module per external system, plus the pipeline that
                      joins them. This *is* SDSI §3's `integrations/`, just
                      named for what it is here: a connector's output is a
                      flat, cached file — call, page, retry, flatten, cache,
                      and it stops there. No business rule lives here.
  business/          the rules that decide something, reading from a cached
                      extract and writing another. This is new relative to
                      generic SDSI — see §4 below for why it earns its own
                      layer rather than living inside a connector or a task.
  tasks/             one callable per operation, plus the registry mapping
                      a name to its handler (SDSI §3, §13)
```

- **The mechanical/business boundary is a file, not a convention.** A
  connector never applies a rule; `business/` never calls a vendor. Putting
  a real file between the two — rather than trusting that a future change
  "just won't" add a rule inside a connector — is what keeps the boundary
  honest under time pressure. See §4 for the data-flow rationale.
- **Config, scripts, pipelines, and docs stay as SDSI §3 already lays them
  out.** A middleware service rarely gains a middleware-specific reason to
  deviate from those; if one shows up, deviate deliberately, name it, and
  write it into the project's own `CLAUDE.md` (SDSI §22) the moment it
  happens, not after it's caused confusion.
- **Split deploy tooling from the pipeline that produces the artifact, and
  name each folder for what runs it, not what it does.** A useful split
  when a service has more than one deployable shape (§6 below):
  `scripts/ps1/` (or your platform's shell) for everything a human or a
  deploy step runs by hand, `scripts/python/` for tooling scripts, and a
  separate `pipelines/` folder for CI/CD definitions. Keep `pipelines/`
  strictly upstream of `scripts/` — a pipeline builds and pushes an
  artifact; a script is what actually runs or deploys it. The two must
  never converge into one file that both builds and deploys, because that's
  the shape that makes "which environment does this pipeline run affect"
  an unanswerable question under a deadline.

---

## 2. Configuration: the Systems Block Pattern

SDSI §6 covers the config system generically; a middleware service typically
configures several external systems that differ in the details but need
identical *shape*, so the connector base class needs no per-system special
cases:

```yaml
systems:
  <system-name>:
    enabled: true
    base_url: <not configured>
    auth: oauth2          # or api_key / bearer / basic / database
    secret_name: <not configured>
    username: <not configured>   # only when auth needs one
    timeout: 30
    retries: 3
    page_size: 100
```

- **Every system gets the same keys**, even the ones a particular system
  doesn't use — a system that doesn't need `page_size` still declares it as
  `<set at runtime>`'s sibling for "not applicable here," so a reader can
  tell "unused" apart from "someone forgot to configure it."
- **Reserve environment variables for what has to exist before config can
  load at all** (SDSI §6) — for a middleware service that's typically
  little more than: which config directory to read, which environment this
  is, where logs/cache/metrics land, and whatever a cloud platform injects
  for managed-identity auth. Enumerate that list explicitly somewhere near
  the config loader, and treat any addition to it as worth a second look —
  it's the one part of config that bypasses schema validation.
- **Distinguish derived values from configured ones, explicitly** (SDSI
  §6). Three are common to nearly every middleware service and worth
  naming the same way every time:

  | Value | Derived from | Why not YAML |
  |---|---|---|
  | `environment` | which override file was applied | Names itself; a YAML key here would be a second, competing source of truth |
  | how the run reports back | whether an invoker-supplied callback address was given | Depends on *how this run was invoked*, not on which environment it's in — see §5 |
  | running version | a `VERSION` file baked into the image | Config lives on its own schedule (a mounted share, a config-publish step); the version that actually matters is the one shipped in the image, not the one last uploaded to config |

  All three still belong in the validated schema, so a `--validate-config`
  (SDSI §6) run reports what a given invocation actually resolved to.
- **A pre-flight task that validates config and credential access without
  doing real work earns its place on every middleware service** (SDSI §6
  already asks for this generically) — it's what a deploy step runs before
  trusting a new container, and it's the fastest way to answer "which
  credential would this run actually use" without waiting for a real failure
  three steps into a sync.

---

## 3. Secrets & Identity for Many Systems at Once

SDSI §7 covers secrets generically; a middleware service multiplies the
naming problem across every external system it touches, so the naming
convention has to scale without drifting:

- **Secret name = `<system>-<purpose>-<kind>`**, derived mechanically from
  the system's `auth:` value so a name can't drift from the block it
  belongs to:

  | `auth:` | Name shape | Example |
  |---|---|---|
  | `api_key` | `<system>-api-key` | `crm-api-key` |
  | `oauth2` | `<system>-client-secret` | `payroll-client-secret` |
  | `bearer` | `<system>-bearer-token` | `banking-bearer-token` |
  | `basic` | `<system>-basic-pwd` | `ledger-basic-pwd` |
  | a database | `<system>-database-pwd` | `warehouse-database-pwd` |
  | a paired credential | `<system>-<purpose>-pair` | `payroll-client-pair` |
  | the platform's own | `container-<purpose>-<kind>` | `container-validation-key` |

  Three parts, always, the platform's own secrets included — a two-part
  name is where a set of names starts to drift once there are a dozen
  systems instead of two.
- **One vault per environment** (SDSI §7), not one shared vault with the
  environment folded into every secret's name. A short, consistent
  per-environment suffix on the vault's own name (not the secret's) keeps
  the mapping from a secret name to its local override legible without
  repeating the environment inside every single name.
- **A validation secret is the sanctioned exception to "never printed."**
  Reading a token from managed identity proves less than it looks like — a
  token is issued whether or not the identity was ever actually granted
  anything on the vault. A dedicated, non-credential secret (holding
  nothing but the environment's own name, say) that a pre-flight task reads
  and *prints* is what actually proves "this identity can read this vault,
  and the network path is open" — and it's safe to print only because it
  was chosen specifically to hold no real credential. Nothing under an
  ordinary `secret_name` key gets the same treatment.
- **Identity and grants are two different lists, for two different
  callers, and they fail differently:**

  | Who | Needs | Symptom without it |
  |---|---|---|
  | The container's own identity | Read access to the vault; pull access to the image registry | Missing vault access: starts, then fails on first secret read. Missing registry access: never starts at all, often with an unhelpfully generic error |
  | Whatever *invokes* the container (an orchestrator, a scheduler) | Its own, separate grant to create/manage the run | A failure here looks nothing like a container-identity failure — don't debug one as if it were the other |

  For anything that creates a fresh container instance per run rather than
  reusing one, give it a **user-assigned** identity provisioned once and
  attached to every instance — a system-assigned identity (and any grant
  made to it) would otherwise be new, and ungranted, on every single run.
- **Test the credential-rotation wait against a real vault**, not a mock
  (SDSI §7's disable → change → set sequence, and the wait for a version
  caught mid-rotation). A mock proves the code called the right method; it
  can't prove the vault's actual error shape is the one your code is
  branching on. Keep that one test outside the normal unit-test run (it
  needs real network and real vault access) and run it deliberately, on
  demand, rather than in CI on every commit.

---

## 4. Data Movement: Extract → Business Rules → Destination

SDSI §10 gives the generic sequence — `source → staging copy → transform →
destination`. A middleware service's specific version of it, and where it
deliberately sharpens SDSI's own wording:

```
extract    vendor API  → download → retry → flatten → cache
business   cache       → rules → transform → cache
load       cache       → the destination's own shape → write → destination
```

- **The cache holds what the *connector* returned, already flattened — not
  the vendor's raw nested payload.** This is a deliberate, named departure
  from SDSI §10's "exactly what the source returned": calling, paging,
  retrying, and flattening are one mechanical act with no business content
  in it, so treating the flattened, cached file as the replay point (rather
  than the vendor's raw response) keeps the boundary between mechanical and
  business work a physical file instead of a convention someone has to
  remember. What's given up is real and worth naming rather than glossing
  over: a value nested three levels deep in the vendor's payload is harder
  to re-model later than the object it came from, if it's ever needed. If a
  raw copy is genuinely wanted, add it as a second cache write behind its
  own setting — don't reorder the pipeline to get it, which puts a shaping
  step back between the cache and the destination, exactly where the next
  change reasonably reaches for a business rule instead.
- **A connector calls a vendor and never applies a rule; `business/` reads
  a cache file and never calls a vendor.** The two are enforced apart, not
  just documented apart — a business rule showing up inside a connector (or
  a vendor call showing up inside `business/`) is a correctness bug in the
  architecture, worth catching the same way any other misplaced-code review
  finding is caught.
- **A period/incremental filter is applied to the cached rows, after the
  extract, never before it** (SDSI §10 already says this generically —
  it's worth restating here because it's easy to get backwards under
  pressure to "just filter at the source"). Whatever field the filter keys
  on has to be named in its *cached, flattened* spelling, not the vendor's
  original field name — getting that wrong is a silent failure, not a
  loud one: the filter simply never matches anything, and every run reports
  a clean, empty, wrong success.
- **Every record written to a destination carries lineage columns** — which
  source system it came from, which scope/dataset, which run loaded it,
  when, and (where useful) a content hash — so a bad load can be identified
  and cleanly removed later without guessing which rows came from where.
- **The cache is scratch space, not storage.** Purge old entries at the
  start of a run rather than letting them accumulate; nothing about the
  cache should be relied on to survive between runs except as a
  replay/debug convenience.

---

## 5. The Response Contract: How a Run Reports Back

SDSI §9 already asks for a machine-readable outcome on every exit path,
distinct from any free-text reason. A middleware service usually has more
than one kind of caller, and *how* it reports depends on *who's asking*:

- **Decide the reporting mode from what the invoker actually supplied, not
  from a flag or a config key that says the same thing a second way.** A
  run invoked with a callback address reports there; a run invoked from a
  terminal or a plain scheduled job prints and exits with a code. The
  presence of that one piece of invocation data is the whole test — adding
  a second, independent way to express the same thing (an explicit
  `--mode` flag, say) creates two sources of truth that will eventually
  disagree about which mode a given run is actually in.
- **Every exit path reports something, including ones that fail before
  configuration finishes loading** (SDSI §9). A minimal, stable table, kept
  close to the code that produces it:

  | Outcome | Roughly means | Typical exit code |
  |---|---|---|
  | Succeeded | Ran fine | 0 |
  | Failed | Ran, and the work itself failed | 1 |
  | Invalid input | Bad/missing arguments — a usage error | non-zero, distinct from "Failed" |
  | Critical/startup failure | Couldn't even get configured — alert, don't retry | non-zero, distinct from both above |
  | Interrupted | Stopped by the platform mid-run — routine, not an incident | matches the platform's own signal-to-exit-code convention |

  Whatever calls this service should branch on the machine-readable code,
  never on the free-text reason — the reason may be redacted (SDSI §7) and
  is meant for a human, not a conditional.
- **A caller that blocks waiting for a callback needs to hear *something*,
  always** — including on a startup failure that happens before the
  callback mechanism itself is even wired up. A caller that times out
  uninformatively is a worse failure mode than a late, ugly answer.
- **The log file is written on a background thread**, so a slow disk never
  blocks the actual work (SDSI §8 already asks for this generically). For
  a middleware service specifically: bound the drain time on shutdown, and
  keep that bound comfortably under whatever grace period the deployment
  platform gives a process between "stop" and "kill" — a drain that's still
  running when the platform force-kills the process loses whatever hadn't
  flushed yet.
- **A warning discovered after the log file has already closed can only
  reach the console (and, if one exists, an incident/alert payload) — say
  so explicitly in code and comments, rather than letting it silently
  vanish.** This is a real, narrow gap worth naming rather than pretending
  it doesn't exist.
- **If the platform sends a graceful-stop signal, convert it into something
  the normal shutdown path handles**, so the log drains and any
  fatal-error handling still runs on a routine stop — not just on an
  unhandled exception. A forceful kill signal generally can't be caught at
  all; a grace-period expiry there loses whatever was still in flight, which
  is exactly why the bound above has to fit inside that grace period.

---

## 6. Deployment: One Image, Several Run Shapes

A middleware service commonly needs to run more than one way over its
life — a long-lived process, a scheduled batch job, a per-invocation
instance created by an orchestrator — without becoming several different
codebases:

- **Build one image; let *how it's invoked* decide the shape**, rather than
  building a different artifact per shape. `main.py` with a task/command
  selector (SDSI §13) already gives the hook: the same image, run with a
  different task and a different set of environment-supplied wiring, is a
  batch job in one deployment and a callback-driven one-off in another.
- **Keep the pipeline that builds the artifact separate from the
  scripts/templates that deploy it, and never let the two converge.** The
  pipeline's job stops at pushing a validated, tagged image (or, for
  config, at publishing a validated config bundle to wherever the running
  shapes read it from) — nothing in Azure, or whatever the target platform
  is, should be triggered to actually pick up a new image or a new config
  just because a build finished. A person (or an explicit, separate deploy
  step) decides when a shape actually restarts onto what the pipeline
  produced.
- **The build definition itself lives in the repository, not typed into
  the CI tool's own UI.** Whatever the CI platform holds should be limited
  to a *registration* pointing at a path in the repo, plus the genuinely
  environment-specific bits that aren't build logic (a service connection,
  branch policy, required approvals). A build definition edited only in the
  CI tool's UI is a second, silently-diverging source of truth for how the
  project builds — the exact failure mode SDSI §6's "no setting lives only
  in code" warns about, one layer up the stack.
- **When one shared config store serves every environment** (a single file
  share or bucket holding a `default.yaml` plus every environment's
  override, say), publishing the *default* is implicitly a production
  change no matter which environment's pipeline triggered it — scope a
  triggered/automatic publish to that one environment's own override file
  only, and require an explicit, deliberate action to publish anything
  wider.
- **Promoting a build to another environment is a retag of an
  already-tested artifact, never a rebuild** (SDSI §17) — a rebuild is a
  different artifact than the one that was actually tested, whatever the
  version number says.

---

## 7. Documentation & Change Discipline on an Established Codebase

SDSI §22's artifact chain (`INTENT.md` → `SPEC.md` → `PLAN.md` per change)
is written with a new project foremost in mind, and says explicitly to
"adopt what fits when working on established code." A middleware service is
almost always the latter by the time SDSI arrives — here's a concrete
adaptation that keeps every row of that artifact table landing somewhere
version-controlled, without a per-change folder that nobody returns to
afterward:

| §22 stage | What it captures | Where it lands instead |
|---|---|---|
| Plan (`INTENT.md`) | What's wanted and why; open questions stay open | The commit message body; `TODO.md` → *Open questions* for anything still unanswered |
| Design (`SPEC.md`) | How it fits this codebase and this standard | The project's own `CLAUDE.md` for a standing decision; `TODO.md` → *Decided*, dated, for a one-off worth keeping the reasoning for |
| Build (`PLAN.md`) | Which files, in what order, what proves it | The commit itself, plus whatever gate proves it (typing, tests) |
| Build (diff + tests) | The implementation and its proof | The test suite, with the regression it catches named in a docstring |
| Deploy (PR + findings) | What an operator has to do to take it | The release entry in `CHANGELOG.md` |
| Maintain (a new `INTENT.md`) | An incident re-enters at Plan | A new `TODO.md` entry, not an off-process hotfix |

"Plan before code" (SDSI §1, §22) still holds unchanged — a plan has to
exist and be agreed before files change. What moves is only *which file*
records it once the change has landed, not whether planning happened.

- **Keep a living "what changed → what else has to be updated" table**
  (SDSI §20 already asks every project to keep one) and make it
  concrete for this codebase's own moving parts — typically: adding a task
  touches the task registry *and* wherever a human picks a task to run by
  hand (a debugger launch config, an ops runbook); adding or renaming a
  secret touches the setup docs and the cheat sheet; adding an environment
  variable touches every place local dev mirrors deployed wiring (SDSI §18);
  a deploy script's parameters changing touches its own deployment doc.
  Extend the table the moment a new top-level folder or a new kind of
  moving part is added — that's the same moment SDSI §22 already asks a
  deviation to be written down, applied to documentation specifically.
- **A pre-commit (or equivalent) hook is worth enforcing this
  mechanically** (SDSI §16, §17): refuse a commit that touches shippable
  code without a `CHANGELOG.md` entry, and refuse a version bump that isn't
  matched by a changelog heading for that version. Keep an escape hatch for
  the genuinely-not-a-release commit, and repeat the check server-side
  where the escape hatch can't reach.

---

## 8. Working With an AI Agent on This Stack

- **"Do it the way system X's connector already does it" means reading
  that connector's actual implementation, not recalling how it probably
  works** (SDSI §22) — and reading it in full can surface that the
  reference connector never had to solve the exact problem now in front of
  you (a vendor with no paging, a secret that's a paired credential, a
  system with no reliable "changed since" filter), which is itself
  important information to bring back before designing the new one.
- **When mirroring a pattern from a sibling project** (a vault integration,
  a deploy shape) **read that project's actual code before adapting it** —
  a description from memory of "how it probably works" isn't a substitute,
  and the sibling project may not have had to answer the exact question
  now in front of you either.
- **When a request's scope grows mid-conversation** — a small connector
  tweak that turns into a change touching how every system authenticates,
  or a decision that starts affecting every deployment shape instead of
  the one originally in view — **stop and say so explicitly**, rather than
  quietly absorbing the growth into the original, smaller-scoped task.
- **A test that proves a rotation, a retry, or a paging walk works needs to
  run against the real thing it's protecting, at least once, deliberately**
  — a mock proves the code called the right method, not that the real
  system's actual error shape or pagination boundary is what the code
  assumed.
