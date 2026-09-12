---
name: validate
description: >
  Used when the user asks to "/validate", "review this stage", "approve
  this change", "check the last stage", or as the fifth step the
  `code-reviewer` orchestrator invokes — once per stage, right
  after `/execute`. Presents a completed stage for approval and, once
  approved, retires the old code path and advances the plan.
---

Before anything else, read `../../references/shared-context.md` for this
plugin's principles, working-file layout, and dependencies — don't
duplicate that content here or assume it from memory.

## Prerequisite

A stage summary must exist in `_scaffolding/04-execution/` without a
matching file yet in `_scaffolding/05-validation/`. If none does, stop and
tell the user `/execute` needs to run for the next stage first.

## Process

1. **Present** the stage summary: what changed (scoped to this stage, not
   the whole repo), which catalog entries it resolves, how to run and
   compare old vs. new side by side if applicable, and residual risk.
2. **Use `AskUserQuestion`** for an explicit **approve / request changes /
   reject** decision. Don't infer approval from silence or the
   conversation moving on.
3. **On approval:**
   - If a parallel old/new path was used, **retire the old path now**, as
     its own explicit cleanup step. Leftover parallel code after
     validation is standards debt in its own right (SDSI §11 — reuse
     over reimplementation applies here too: two live paths for one job is
     exactly the thing to avoid once one of them has won).
   - Update `FINDINGS-CATALOG.md`: mark this stage's entries `Resolved`.
   - Write `_scaffolding/05-validation/stage-<N>-<slug>.md` recording the
     decision.
   - Tell the user which stage is next per `SEQUENCING-PLAN.md` (or that
     the plan is complete).
4. **On request-changes or reject:** don't advance. Record what needs to
   change in the same validation file, so the next `/execute` attempt on
   this stage has the context, and hand back to `/execute`.

## Output format

The approve/request-changes/reject decision, plus (on approval) a short
confirmation of what was cleaned up and what's next; (on rejection) a
clear, specific list of what needs to change.
