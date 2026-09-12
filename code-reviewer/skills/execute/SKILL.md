---
name: execute
description: >
  Used when the user asks to "/execute", "start the next stage",
  "implement stage N", "make the changes for this stage", or as the fourth
  step the `code-reviewer` orchestrator invokes — once per stage,
  looped with `/validate` between each. Implements one stage of the
  sequencing plan, using a parallel old/new implementation when the change
  is risky enough to warrant one.
---

Before anything else, read `../../references/shared-context.md` for this
plugin's principles, working-file layout, and dependencies — don't
duplicate that content here or assume it from memory.

## Prerequisite

`_scaffolding/03-strategy/SEQUENCING-PLAN.md` must exist and be approved.
Determine the next stage to run: the first one in the plan without a
corresponding file in `_scaffolding/05-validation/`. If every stage already
has one, say so — the plan is done; that's the orchestrator's
closing-the-loop step, not this skill's.

## Process, for this stage only

1. **Confirm scope** — this stage's catalog entries only. Don't pull work
   forward from a later stage even if it's tempting.
2. **Baseline first, for anything under-tested.** If the subsystem this
   stage touches has thin or no test coverage, write characterization
   tests first — tests that pin down *current* behavior, bugs included —
   before changing anything. Otherwise there's no way to tell an
   intentional fix from an accidental regression.
3. **Decide: in place, or side by side?** Not every change needs a
   parallel path — a one-line security patch doesn't. Use one specifically
   when the change is large or risky enough that a side-by-side comparison
   adds real safety: a core-logic refactor, a library swap with a
   different API surface, or a module-level language port. Roughly in
   order of setup cost:
   - **A config toggle** (SDSI §6-compliant — the switch lives in
     config, never hardcoded) selecting old vs. new at a single call site.
   - **An adapter/routing layer** in front of both implementations
     (strangler-fig style) — needed when the two paths have different
     interfaces.
   - **Two functions/modules coexisting**, call sites migrated one at a
     time, for smaller-scoped changes where a full toggle is overkill.

   For a genuine language migration, expect the comparison to mean shadow
   traffic or an explicit parity test suite rather than a simple toggle.
4. **Implement the stage's changes.**
5. **Self-check** against the SDSI standard and the specific catalog entries
   this stage claims to resolve — this is the stage's own mini-review, not
   a substitute for `/validate`.
6. **Run tests** — the characterization tests from step 2, plus whatever
   else covers this code.
7. **Write** `_scaffolding/04-execution/stage-<N>-<slug>/summary.md`.

Then **stop.** Don't start the next stage — that's `/validate`'s call to
make, not this skill's.

## Output format

The stage summary: what changed, which catalog entries it addresses, how
old and new code can be compared if a parallel path was used, and any
residual risk or open question. Close with: *"Stage N implemented — ready
for `/validate`."*
