---
name: code-reviewer
description: >
  Use this skill whenever the user wants to review, clean up, fix,
  upgrade, refactor, port, or modernize an existing/legacy codebase — not
  for building something new from scratch. Triggers include mentions of
  old or outdated code, outdated or vulnerable dependencies, security
  debt, tech debt, code smells, inconsistent style, poor performance, a
  candidate for a language or framework migration, or phrases like "this
  code is a mess," "let's modernize this," "upgrade our libraries,"
  "should we rewrite/port this in [language]," "audit this codebase," or
  types "/code-reviewer". Runs the full workflow end to end:
  `/intake`, `/catalog`, `/strategy`, then `/execute` and `/validate`
  looped per stage, stopping at a checkpoint after every phase and every
  stage. To resume mid-process, or to run just one phase on its own,
  invoke that phase's skill directly instead — `/intake`, `/catalog`,
  `/strategy`, `/execute`, or `/validate`.
---

Do not narrate the mechanics of "invoking a skill" — just run the phases
below in order and produce their output.

Before anything else, read `../../references/shared-context.md` for this
plugin's principles, working-file layout, and dependencies.

## Process

1. **Check for a resume.** Look for an existing `_scaffolding/` folder in
   the target project. If one exists, read `PROJECT-GUIDANCE.md` and
   `FINDINGS-CATALOG.md` (if present) and start from whichever phase its
   contents indicate comes next, rather than restarting at `/intake`.
2. **`/intake`** — scope the work, run the four-lens code review, save
   findings. Stop and present its output.
3. **`/catalog`** — deduplicate and classify into one catalog. Stop and
   present it for correction.
4. **`/strategy`** — gather direction via `AskUserQuestion`, build the
   sequencing plan. Stop and get explicit approval before continuing.
5. **For each stage in the approved plan, in order:**
   a. **`/execute`** that stage.
   b. **`/validate`** that stage. Only continue to the next stage once
      validation approves this one — on request-changes or reject, loop
      back to `/execute` for the same stage instead of advancing.
6. **Closing the loop.** Once every stage is validated, run the same
   four-lens review `/intake` performs once more against the finished
   result and diff its findings against the original
   `FINDINGS-CATALOG.md`: confirm the original findings are actually
   resolved (not just marked so), and flag anything new the changes
   introduced. New findings become new catalog entries — decide with the
   user, depending on severity, whether that's a new stage or a follow-up
   pass.

## Output

Each step's output is exactly that step's own skill's output format — this
orchestrator doesn't reformat or summarize it away, and it doesn't produce
a separate report of its own. Its job is sequencing and checkpointing, not
narration.

## Future: non-linear execution

The user has flagged that running every stage strictly in order is a
deliberate starting point, not a permanent constraint. A future version may
parallelize independent stages (ones with no shared blast radius) instead
of running the full sequence end-to-end. Don't build that now — revisit
once the linear version has been used on a real codebase and proven out.
