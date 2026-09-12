---
name: intake
description: >
  Used when the user asks to "/intake", "start intake on X", "run the
  review phase", "kick off the code review", or as the first step the
  `code-reviewer` orchestrator invokes. Scopes the target codebase, loads
  the SDSI standard if reachable (the `sdsi` plugin if installed, else a
  local `SDSI.md`), runs its own four-lens code review against it, and
  saves the raw findings for `/catalog` to work from.
---

Before anything else, read `../../references/shared-context.md` for this
plugin's principles, working-file layout, and dependencies — don't
duplicate that content here or assume it from memory.

## Process

1. **Confirm scope.** Whole repository, or a specific module/subsystem?
   If the user hasn't said, ask — legacy modernization is rarely "the
   whole thing at once."
2. **Check for a resume.** Look for `_scaffolding/01-review/` in the
   target project. If it already has content, tell the user intake has
   already run for this scope and ask whether to re-run it or move on to
   `/catalog`.
3. **Load the SDSI standard.** If the `sdsi` plugin is installed, invoke
   `sdsi:sdsi` by name — that's the preferred source (see
   `shared-context.md`'s Dependencies section for why a by-name invocation
   beats reaching into another plugin's files directly). Otherwise, look
   for a project-local `SDSI.md`, or one in a shared location, if
   reachable. If neither exists anywhere, say so plainly and proceed on
   general good-practice grounds instead of blocking.
4. **Run the four-lens review** against the in-scope code, directly and
   inline — this plugin doesn't delegate code review to an external
   council; explicitly pass the loaded standard along as what the
   Standards lens should check against, in addition to its usual
   general-standards checklist:

   | Lens | Focus |
   |---|---|
   | Security | Attack surface, secrets handling, authn/authz, input handling, error leakage |
   | Standards | Naming, structure, readability, and specifically SDSI compliance if available |
   | Efficiency | Performance, resource use, unnecessary complexity |
   | Infrastructure | Dependency health, deployment/runtime fit, cost, migration friction |

5. **Reconcile into an Intake Verdict.** After all four lens reviews,
   write a short verdict that reconciles them:
   - **Where they agree** — findings two or more lenses independently
     flagged, or issues that reinforce each other.
   - **Where they conflict** — name the tensions explicitly (commonly
     Security/robustness vs. Efficiency's simplicity, or Standards'
     polish vs. Infrastructure's lean-cost preference).
   - **Resolution** — make an actual call per conflict. Default:
     unresolved *Critical* or *High* Security findings always outrank the
     others regardless of what the other lenses say.
   - **Single verdict** — one of `Not ready — blocking issues to resolve
     first`, `Ready with required changes`, `Ready with optional
     follow-ups`, or `Ready to ship`, plus a short prioritized list of
     what's required. This verdict is informational for `/catalog`, which
     does its own classification next — keep it tight.
6. **Save the raw reviews.** Write the four lens reviews and the Intake
   Verdict to `_scaffolding/01-review/`.
7. **Don't lose the migration-relevant findings.** Outdated or vulnerable
   dependencies, deprecated language/framework features, and anything
   that would make a future language/framework migration harder (tight
   coupling to a runtime-specific API, for instance) tend to surface in
   the Infrastructure lens and the Efficiency lens — make sure they're
   clearly called out, since `/catalog` needs them intact.

## Output format

Present the four lens reviews (Security Review, Standards Review,
Efficiency Review, Infrastructure Review), each in its own lens's exact
format, followed by the Intake Verdict — don't reformat or summarize it
away. Close with a one-line status: *"Intake complete — N findings saved to
`_scaffolding/01-review/`. Ready for `/catalog`."*
