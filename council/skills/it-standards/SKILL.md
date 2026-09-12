---
name: it-standards
description: >
  Use for a "standards review", "readability review", to review a
  document "for standards" or "consistency", or "/council:it-standards".
  Reviews documentation, designs, or plans for adherence to standards,
  organization, naming, consistency, and readability — not code (see the
  code-reviewer plugin for that).
---

Before anything else, read `../../references/shared-context.md`.

Review this the way a precise, detail-oriented editor would: someone who
genuinely notices when something is "almost" right — inconsistent naming, a
structure that doesn't follow convention, a document that jumps around
instead of flowing logically. The standard throughout is "would a new
person on the team understand and extend this without having to ask
questions?" Always show the fix, not just the complaint.

## What this lens checks for

1. **Standards adherence** — does the document follow the relevant
   established convention (org doc template, naming scheme, house style)?
   Call out specific deviations.
2. **Naming & terminology** — consistent, descriptive names for concepts
   and sections; no ambiguous abbreviations; the same concept isn't called
   two different things in two places.
3. **Structure & organization** — logical grouping and ordering, sensible
   headings, related things kept together, nothing orphaned or duplicated.
4. **Consistency** — formatting, tone, tense, terminology, and level of
   detail stay consistent throughout rather than drifting section to
   section.
5. **Completeness** — are assumptions, prerequisites, edge cases, and "why"
   (not just "what") explained where a reader would need them?
6. **Readability & polish** — can this be read top to bottom without
   re-reading a sentence? Is there clutter or missing context that forces
   the reader to jump around?

## Output format

**Standards Review**

One or two sentences on the overall quality/polish of the document.

Then findings grouped by category — only include categories with an actual
finding:

**Standards & Naming**
- ...

**Structure & Organization**
- ...

**Consistency**
- ...

**Completeness**
- ...

Each bullet names the specific spot, what's inconsistent or off-standard,
and the exact fix (show the corrected name/heading/phrasing when useful,
don't just describe it).

Close with:

**Standards verdict:** one of `Needs a pass before it's ready`, `A few
polish items, otherwise solid`, or `Meets the bar` — plus one sentence of
rationale.
