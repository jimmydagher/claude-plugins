> Read by every skill in this plugin before it does anything else. Don't copy
> this content into an individual skill's own SKILL.md — if something here
> needs to change, it should only need to change once.

## What this council reviews — and what it doesn't

This plugin reviews **documentation, designs, plans, and business
proposals** — not code. Each lens is a contractor brought in for one
specific specialty; you invoke it by that specialty (`council:it-security`,
`council:bu-finance`, ...), not by a personal name, and its output is
titled the same way ("Security Review", "Finance Review", ...). None of
them adopt a named persona or a distinct voice for its own sake — the
value here is the specific lens applied carefully, not a character.

**Source code review is a different job with a different process**,
handled by the separate `code-reviewer` plugin (`/code-reviewer`,
`/intake`, `/catalog`, `/strategy`, `/execute`, `/validate`). If someone
asks this plugin to review code, say so and point them at `code-reviewer`
instead of reviewing it here — the two plugins are deliberately not
overlapping.

## Shared process, every lens

1. **Identify what's under review** — an attached file, pasted text, or a
   file/section the user points to. If it's genuinely unclear, ask before
   proceeding rather than guessing.
2. **Write the review directly.** Don't narrate "adopting a persona" or
   "running a skill" — just produce the lens's own output format.
3. **Don't manufacture findings.** If a lens has nothing of concern, say so
   plainly and briefly, while still noting what it specifically checked so
   the reader knows the review was thorough, not skipped.
4. **Every finding needs a concrete fix**, not a generic instruction — "add
   a named owner for the migration rollout" beats "improve accountability."

## Structure

```
council
├── council:it          — Security, Standards, Efficiency, Infrastructure
│   ├── council:it-security
│   ├── council:it-standards
│   ├── council:it-efficiency
│   └── council:it-infra
├── council:bu          — Operations, Finance, Strategy, Legal
│   ├── council:bu-ops
│   ├── council:bu-finance
│   ├── council:bu-strategy
│   └── council:bu-legal
└── council:all         — all eight, one company-wide verdict
```

## Bucket skills (`council:it`, `council:bu`, `council:all`)

Each bucket runs its members' reviews in full, each under its own heading,
using that lens's exact output format — then closes with a **Verdict**
section that reconciles them (see each bucket skill for its own
reconciliation rules). The verdict is the most important part of a
bucket's output; never let it collapse into a shallow restatement of the
findings tables above it.

## Individual lens skills

Each defines its own checklist and output table — that's what's specific
to it and belongs only in that skill's own file, not here.
