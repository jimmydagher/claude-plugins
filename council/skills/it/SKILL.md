---
name: it
description: >
  Use to "convene IT", "have engineering review this", "run all IT
  lenses on this document", or "/council:it". Runs the Security,
  Standards, Efficiency, and Infrastructure reviews of the same document
  and converges them into a single reconciled IT verdict.
---

Before anything else, read `../../references/shared-context.md`.

## Process

1. Identify the document under review. If genuinely unclear, ask before
   proceeding.
2. Review it four times, applying each lens's checklist and output format
   exactly as defined in the `it-security`, `it-standards`, `it-efficiency`,
   and `it-infra` skills. Keep each review self-contained.
3. Close with an **IT Verdict** that reconciles all four — the most
   important part of the output, not a shallow summary.

## Output structure

Present the four reviews first, each under its own heading (Security
Review, Standards Review, Efficiency Review, Infrastructure Review), in
that order, each following its own skill's format exactly.

Then close with:

---

## IT Verdict

**Where they agree:** findings two or more lenses independently flagged, or
issues that reinforce each other (e.g. a missing auth check from Security
and a missing audit-log retention plan from Infrastructure are related).

**Where they conflict:** name the specific tensions explicitly — usually
some version of security/robustness vs. simplicity, or polish/completeness
vs. cost/lean infrastructure. State both sides of each tension in one
sentence each.

**Resolution:** for each conflict, make an actual call rather than
presenting both sides and stopping. Default: unresolved *Critical* or
*High* findings from Security always outrank the others and must be
addressed regardless of what the other lenses say. Beyond that, prioritize
by concrete impact/likelihood, not by which lens raised it.

**Single verdict:** one of `Not ready — blocking issues to resolve first`,
`Ready with required changes`, `Ready with optional follow-ups`, or `Ready
to ship` — plus a short numbered list of the specific changes required,
ordered by priority. If nothing is required, say so.

Keep the IT Verdict tight — a lead reviewer's summary after reading all
four takes, not a repeat of the findings tables.
