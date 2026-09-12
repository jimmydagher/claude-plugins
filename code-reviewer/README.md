# Code Reviewer

A staged workflow for modernizing, refactoring, or remediating an existing
codebase — outdated dependencies, security debt, style drift, poor
performance, or a candidate for a language/framework migration. This is the
*enhancement* arm of the project's scaffolding; a different, simpler scaffold
applies to brand-new projects (not yet built).

Code review is this plugin's own job — `intake` runs its own four-lens
review directly. The separate `council` plugin reviews documentation and
plans, not code, so the two deliberately don't call into each other.

## Structure

```
Code Reviewer
├── /code-reviewer  — orchestrator: runs every phase below, in order
├── /intake     — Phase 0+1: scope the work, run the four-lens code review
├── /catalog    — Phase 2: dedupe & classify findings into one catalog
├── /strategy   — Phase 3: sequencing plan, built with your input
├── /execute    — Phase 4: implement one stage at a time
└── /validate   — Phase 5: approve or reject each stage before the next
```

## Skills

| Skill | Phase | Does | Invoke with |
|---|---|---|---|
| `code-reviewer` | All | Runs every phase in order, stopping at each checkpoint | `/code-reviewer`, "review and modernize this project", "help me upgrade our dependencies" |
| `intake` | 0 + 1 | Scopes the work, runs its own four-lens review (security, standards, efficiency, infrastructure) against the code, with the SDSI standard | `/intake`, "start intake on X", "run the review phase" |
| `catalog` | 2 | Deduplicates and classifies findings into one catalog | `/catalog`, "classify these findings", "build the findings catalog" |
| `strategy` | 3 | Gathers direction via AskUserQuestion, builds a foundation-first sequencing plan | `/strategy`, "plan the sequencing", "what direction should we take" |
| `execute` | 4 | Implements the next stage; runs old/new code side by side when risky | `/execute`, "start the next stage", "implement stage N" |
| `validate` | 5 | Presents a stage for approval; retires old code once approved | `/validate`, "review this stage", "approve this change" |

## Setup

No other plugin is required for `intake` — it runs its own four-lens code
review directly. For the standard it checks against, `intake` prefers the
`sdsi` plugin (invoked by name, `sdsi:sdsi`) if it's installed; otherwise it
reads a project-local `SDSI.md`, or one in a shared location, if present —
no other configuration required either way.

## Usage

- **First pass on a whole codebase:** "review and modernize this project"
  (or `/code-reviewer`) runs the full sequence, stopping for your
  input at `/strategy` and for your approval after every `/execute` stage.
- **Resuming mid-process in a new session:** point Claude at the target
  project and invoke whichever phase comes next — e.g. `/strategy` if a
  catalog already exists but no sequencing plan does yet. Each skill checks
  its own prerequisite and will say so if something upstream hasn't run.
- Plain language works as well as slash syntax — each skill's description
  lists the phrases it responds to.

## Working files

Every phase writes to `_scaffolding/` at the root of the **target**
project (not this plugin's folder) — see
[`references/shared-context.md`](references/shared-context.md) for the
exact layout and the principles every skill follows. This is what lets the
process resume cleanly across sessions instead of re-deriving everything
each time.

## Sharing with your team

Packaged as a single `.plugin` file — send it directly, or publish it to
your org's plugin marketplace if you run one.

## Customization

Want a dedicated reviewer voice for one of `intake`'s four lenses, or a
distinct persona for `/catalog`'s classification pass instead of a general
prompt? Just ask.
