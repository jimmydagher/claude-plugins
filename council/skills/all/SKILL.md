---
name: all
description: >
  Use to "convene the full council", "get everyone's review", "have the
  whole company review this", "run IT and BU on this", or "/council:all".
  Runs all eight lenses — Security, Standards, Efficiency, Infrastructure
  (IT) and Operations, Finance, Strategy, Legal (BU) — and converges
  every review into a single company-wide verdict.
---

Before anything else, read `../../references/shared-context.md`.

## Process

1. Identify the document or proposal under review. If genuinely unclear,
   ask before proceeding.
2. Review it eight times, applying each lens's checklist and output format
   exactly as defined in the `it-security`, `it-standards`, `it-efficiency`,
   `it-infra`, `bu-ops`, `bu-finance`, `bu-strategy`, and `bu-legal` skills.
   Keep each review self-contained.
3. Close with a **Council Verdict** that reconciles all eight — the most
   important part of the output, not a shallow summary.

## Output structure

Present the eight reviews first, grouped under two headings in this order:

**IT**
- Security Review
- Standards Review
- Efficiency Review
- Infrastructure Review

**BU**
- Operations Review
- Finance Review
- Strategy Review
- Legal Review

Each review follows its own skill's format exactly.

Then close with:

---

## Council Verdict

**Where they agree:** findings two or more lenses — from either side, or
across both — independently flagged, or issues that reinforce each other
(e.g. a missing audit trail from Security and a diligence-risk flag from
Strategy on the same gap are related).

**Where they conflict:** name the specific tensions explicitly, both within
a side and across IT/BU. The recurring cross-side tension is engineering
rigor/cost (IT) vs. business urgency/return (BU) — e.g. Infrastructure
spend vs. Finance's cost-down mandate, or Security's hardening timeline vs.
a near-term savings target. State both sides of each tension in one
sentence each.

**Resolution:** for each conflict, make an actual call. Defaults when
nothing in the document says otherwise, in order: (1) unresolved *Critical*
or *High* findings from Security always outrank everything else; (2) a
Legal finding with "Needs counsel: Yes" on real exposure outranks a
near-term cost or efficiency win; (3) beyond those two, a diligence risk
from Strategy (undocumented systems, messy data, single-person dependency)
outranks a near-term cost/efficiency win from Operations or Finance, since
that risk compounds and is expensive to unwind later; (4) otherwise,
prioritize by concrete, quantified impact/likelihood, not by which lens
raised it.

**Single verdict:** one of `Not ready — blocking issues to resolve first`,
`Ready with required changes`, `Ready with optional follow-ups`, or `Ready
to move forward` — plus a short numbered list of the specific changes
required, ordered by priority. If nothing is required, say so.

Keep the Council Verdict tight — a company leadership summary after reading
all eight takes, not a repeat of the findings tables.
