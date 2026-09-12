---
name: strategy
description: >
  Used when the user asks to "/strategy", "plan the sequencing", "what
  direction should we take", "build the migration plan", or as the third
  step the `code-reviewer` orchestrator invokes after `/catalog`.
  Gathers the user's direction via AskUserQuestion and turns the catalog
  into an approved, foundation-first sequencing plan.
---

Before anything else, read `../../references/shared-context.md` for this
plugin's principles, working-file layout, and dependencies — don't
duplicate that content here or assume it from memory.

## Prerequisite

`_scaffolding/02-catalog/FINDINGS-CATALOG.md` must exist. If it doesn't,
stop and tell the user `/catalog` needs to run first.

## Process

### 1. Gather guidance

This phase cannot be completed by inference alone. Use `AskUserQuestion` to
resolve the topics that genuinely change the plan:

| Topic | Why it matters | Typical options |
|---|---|---|
| Primary goal | Changes everything downstream | Security/bug fixes only · Full modernization · Language or framework migration |
| Constraints | Determines how aggressive changes can be | Must stay live in production throughout · Can freeze this branch during the work · Hard deadline |
| Risk tolerance | Determines whether `/execute`'s parallel old/new pattern is required or optional | Minimal, reversible changes only · Bigger swings with safety nets are fine · Speed over caution |
| Target stack (if migrating) | Determines `/execute`'s whole approach | Same language, updated libraries · Same language, different framework · Different language entirely |
| Off-limits areas | Some subsystems may be untouchable (compliance, scheduled for deprecation, owned by another team) | None · specific list |

Write the answers to `_scaffolding/00-guidance/PROJECT-GUIDANCE.md` — the
north star every later phase (and every future session) reads instead of
re-asking.

### 2. Build the sequence

Order the catalog **foundation-first**, mirroring SDSI §3's own
dependency direction (`helpers ← integrations ← tasks`):

1. **Shared/core infrastructure** — secrets handling, logging, error
   handling, configuration. Everything else depends on these being sound.
2. **Shared functions & common dependencies** — the helpers/integrations
   layer, and any library upgrades that ripple across the codebase.
3. **Integration/boundary code** — external API calls, database access.
   Usually where outdated libraries bite hardest.
4. **Business logic** — last. Least reused, most numerous, benefits most
   from a stable foundation underneath it.

Group catalog entries into **stages** sized for one human review sitting
(see Principles in shared-context.md) — not one stage per entry, not "the
whole layer" either. High-severity, high-blast-radius items pull earlier
within their layer; cheap wins can pull forward if they don't reorder the
dependency chain.

3. **Write** `_scaffolding/03-strategy/SEQUENCING-PLAN.md` as an ordered
   list of stages, each naming its catalog entries.

## Output format

Present `PROJECT-GUIDANCE.md`'s captured answers, then the staged sequence.
**Explicitly ask the user to approve the plan before `/execute` starts** —
don't treat silence or moving on as approval.
