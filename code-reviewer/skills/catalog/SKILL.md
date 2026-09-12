---
name: catalog
description: >
  Used when the user asks to "/catalog", "classify these findings",
  "build the findings catalog", "deduplicate the review results", or as
  the second step the `code-reviewer` orchestrator invokes after
  `/intake`. Turns the raw intake review into one deduplicated, classified,
  prioritized catalog.
---

Before anything else, read `../../references/shared-context.md` for this
plugin's principles, working-file layout, and dependencies — don't
duplicate that content here or assume it from memory.

## Prerequisite

`_scaffolding/01-review/` must exist and have content. If it doesn't, stop
and tell the user `/intake` needs to run first, and offer to run it now
rather than guessing at findings that don't exist yet.

## Process

1. **Deduplicate.** The same underlying issue flagged by more than one
   lens (a hardcoded secret Tom flags as a security gap and Mike flags as
   an SDSI violation) becomes one catalog entry, cross-referenced to both.
2. **Classify** each entry:

   | Field | Values |
   |---|---|
   | Category | Security · Standards-Compliance · Optimization-Simplicity · Infrastructure-Dependencies · Architecture |
   | Subsystem | Which part of the codebase it lives in |
   | Severity | Critical · High · Medium · Low (keep Tom's scale for consistency) |
   | Blast radius | High · Medium · Low — how much else depends on this being fixed first; this is what drives `/strategy`'s sequencing |
   | Effort | S · M · L · XL |
   | Found by | Which lens(es) flagged it |
   | Status | Open · In Progress · Resolved · Deferred |

3. **Write** `_scaffolding/02-catalog/FINDINGS-CATALOG.md`:

   ```markdown
   # Findings Catalog — <project>

   | ID | Category | Subsystem | Severity | Blast Radius | Effort | Found By | Description | Status |
   |----|----------|-----------|----------|---------------|--------|----------|--------------|--------|
   | C-001 | Security | auth/ | Critical | High | M | Tom | Hardcoded API key in auth/client.py | Open |
   ```

This is a general classification pass, not a dedicated persona, unless the
user asks for one.

## Output format

Present the full catalog table, plus a short count by severity and
category. Close with: *"Catalog complete — N entries. Ready for
`/strategy`."* — and explicitly invite the user to flag anything the
reviewers got wrong or missed before it's baked into a sequencing plan.
