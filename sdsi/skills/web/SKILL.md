---
name: web
description: >
  SDSI's companion for Django and general website development — project
  layout, the Django settings.py config bridge, secrets via a cloud key
  vault, deploying the same app to both a cloud PaaS and a self-hosted box,
  automating SDSI's versioning policy with git hooks, and AI-agent working
  notes specific to this stack. Use whenever building or working on a
  Django site, or a website project more generally. Depends on SDSI's base
  standard — read `../../references/shared-context.md` first, always; this
  skill only states what's additionally true for a Django/website project
  and assumes that standard already applies in full. Also triggers on
  "/sdsi:web" or "sdsi web".
---

Before anything else, read `../../references/shared-context.md` — the base
SDSI standard, shared by every skill in this plugin. It's a hard
prerequisite, not an optional read. Everything there applies here in full;
what follows below only adds what's specific to a Django/website project on top
of it: project layout (`site/` in place of `src/`, where `manage.py` and
Django app naming legitimately deviate from framework defaults), the
`settings.py` config bridge (`force_https`, `ALLOWED_HOSTS`/
`CSRF_TRUSTED_ORIGINS`), secrets via a cloud key vault, deploying the same
app to both a managed cloud PaaS and a self-hosted box, automating SDSI
§17's versioning policy with git hooks, documentation judgment calls, and
working with an AI coding agent on this stack.

## Don't repeat the base standard

If something below looks like it's only restating a general SDSI rule
rather than adding a Django/website-specific one, that's a defect in this
document — flag it rather than leaving it duplicated.

---

# SDSI Companion: Django & Website Development

A companion to `SDSI.md`, not a replacement for it — this project follows
`SDSI.md` in full, and this document adds what's specific to a Django
website, learned in practice building `flammeau`. `SDSI.md` stays generic
across every project (a data-sync tool, a personal dashboard, a website);
this document is where the web/Django-specific instinct lives instead of
diluting that generality.

Living document, same as `SDSI.md`: extend it whenever a Django/website
project teaches us something worth generalizing.

---

## 1. Project Layout for a Django Site

SDSI §3's `src/` becomes `site/` for a website (the folder itself renamed,
same structural pattern) — a more accurate name for what it holds when the
"package" in question is a whole website rather than a generic library.
Everything else about §3 (dependency direction, `helpers/` as the one
shared-code home, no loose files at the repo root) applies unchanged.

- **`manage.py` doesn't have to sit at the repo root.** Django's own
  scaffolding assumes it does, but nothing about Django actually requires
  it — it's a thin runner script whose only real dependency is that the
  project package is importable when it runs (via `PYTHONPATH`, not via
  its own file location). It's legitimate to nest it elsewhere (e.g.
  `site/admin/manage.py`) if that fits a project's layout better. The
  cost: **every invocation has to be updated and kept updated** —
  Dockerfile, docker-compose files, docs, scripts — and the non-default
  location needs to be written down in the project's own `CLAUDE.md`
  (SDSI §22), because a future session's default assumption will
  otherwise be Django's own convention, silently regressing the project
  back toward it.
- **`core` is a bad name for the shared-code app in a Django project** —
  it collides conceptually with Django's own "core" framework internals
  and reads as ambiguous. Rename it to `helpers`, matching SDSI §3's
  shared-code convention directly, and treat it as the same rename
  discipline SDSI §11 already asks for (one destination, not a second
  home for the same kind of code).
- **Django app naming**: set `AppConfig.name` to the dotted package path
  (`mysite.accounts`), but never set an explicit `app_label` — Django's
  own default derivation (the last segment of `name`) is what every
  already-applied migration's app label and DB table prefix assume.
  Setting it explicitly is an easy way to silently diverge from
  migrations already run against the database.
- **Raw design-source assets** (unprocessed logo files, brand source
  material not meant to be served) belong colocated with the code that
  consumes them — under `site/`, not the repo root — clearly distinguished
  from the *served*, processed copies that live under the app's own
  `static/` folder. Document which is which; a served copy silently
  drifting from its unprocessed source is a real trap.

---

## 2. Configuration: the Django `settings.py` Bridge

SDSI §6 covers the config system generically; here's what actually bites
in a Django settings module built on top of it.

- **`django.force_https` must be its own explicit key, never derived from
  `debug`.** An environment override that turns off `debug` without also
  stating `force_https` silently inherits the default file's
  `force_https: true` — which turns on `SECURE_SSL_REDIRECT` and
  secure-only cookies. Behind real TLS termination that's correct;
  anywhere without it (local dev, a plain-HTTP LAN deployment) it breaks
  every request with a redirect to a `https://` nothing serves, and
  cookies the browser silently refuses to set. **Every new environment
  override states `force_https` explicitly** — never assume it follows
  `debug`.
- **`ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` need both the bare domain and
  its `www.` subdomain**, for every environment that's reachable by
  either. It's an easy, common miss to add only `example.com` and forget
  `www.example.com` (or vice versa) — the symptom is a clean 400 or a
  silent CSRF failure on whichever variant was left out, often not
  noticed until a real user hits it.
- **Don't over-populate `CSRF_TRUSTED_ORIGINS` defensively.** Django only
  needs an explicit trusted origin when a request's `Origin` header
  wouldn't already self-match the request's own scheme+host. A plain-HTTP
  LAN deployment reached by its own IP or hostname (no TLS, no reverse
  proxy) typically needs **no** entries there at all — the browser's
  Origin header already matches `ALLOWED_HOSTS` by construction. Add an
  entry only when the access pattern genuinely differs from the host the
  request already thinks it's reaching (a TLS-terminating proxy in front
  changes the scheme the browser sees, for instance).
- **A secret's *name* is an ordinary config value, schema-validated like
  any other string** — the vault/environment resolution logic that turns
  the name into a real value (§4 below) is a separate concern layered on
  top. Don't let the schema itself grow any awareness of "this one's
  secret" beyond validating that a name string is present.

---

## 3. Secrets via a Cloud Key Vault

The pattern that replaces "read a credential straight from an environment
variable" once a project has (or gains access to) a real secrets manager
— ported in practice from a sibling project's existing Azure Key Vault
integration, adapted rather than copied verbatim.

- **Config holds only a name, never a value.** `database.secret_name:
  mysite-database-url`, not the URL itself. A small resolver module turns
  the name into a value at the moment it's needed, over HTTPS, and the
  value is held in memory for the life of the process only — never
  logged, printed, or written to disk.
- **Authentication, tried in priority order, each gated by its own config
  flag:**
  1. **Managed identity** — the only path in a real cloud deployment
     (Container Apps, App Service, a VM). No credential exists anywhere
     in the image, the environment, or the repo; the platform itself
     vouches for the workload.
  2. **The developer's own signed-in CLI session** (`az login` and
     equivalents) — for local development *against the real vault*,
     since a laptop has no managed identity. What it can read is decided
     by the developer's own role grant, not by anything the app holds,
     and every use should log a visible warning (this is a debugging
     convenience, not the deployed path, and a run authenticating as a
     person rather than as the workload is worth noticing).
  3. **A named environment variable** — the last-resort fallback for a
     developer with no vault access at all, and **must be explicitly
     disabled in every real deployment**, so an unreachable vault fails
     loudly there instead of quietly reading something weaker.
- **One vault per environment**, never one shared vault with the
  environment baked into each secret's name. A name that never carries an
  environment suffix can't be copy-pasted from a dev vault into a prod
  one by mistake, and the vault itself is already the scope.
- **A workload outside the cloud provider's own identity fabric is a real
  gap this pattern doesn't solve for free.** A self-hosted box (a home
  NAS, an on-prem server) has neither a managed identity nor a practical
  *persistent, unattended* CLI session to borrow a token from. Two honest
  options, and both are legitimate — don't silently pick one:
  - Give it its own bootstrap credential (a service-principal client
    secret) and accept that one secret now has to be held outside the
    vault to reach everything else inside it, or
  - Leave that specific deployment target out of the vault migration
    entirely and keep it on the older env-var-in-a-gitignored-file
    mechanism — genuinely fine when that target is low-stakes (LAN-only,
    single operator), rather than forcing a mismatched pattern onto it
    for consistency's own sake.
- **When mirroring a pattern from a reference project, read its actual
  implementation before designing — a description from memory of "how it
  probably works" isn't a substitute**, and the reference project may not
  have solved the exact problem in front of you (see the NAS gap above:
  the reference project this was ported from never runs outside a cloud
  environment or a developer's own machine, so it never had to answer
  this question either). Adapt naming and structure to the target
  project's *own* existing schema shape rather than importing a generic
  abstraction the target doesn't need (a whole "system registry"
  framework, when the target has a handful of named credentials, not an
  open-ended connector list).

---

## 4. Multi-Target Deployment: Cloud PaaS vs. a Self-Hosted Box

Real differences that bite when the same app deploys to both a managed
cloud container platform and a self-hosted LAN deployment.

- **A cloud PaaS's volume-mount primitive usually mounts a whole
  directory, not a single arbitrary file** — unlike a plain Docker
  bind-mount, which can target one file directly. Mounting a managed
  file-share volume straight over a directory that also holds files baked
  into the image (committed config, for instance) will clobber them.
  Mount it at a separate path instead, and point the app at that path
  with one small piece of wiring (a single environment variable
  supplying the path, defaulting to the ordinary in-image location so
  every *other* deployment target needs zero change).
- **Check whether the platform already has a native secrets mechanism
  before building a file-mount workaround to get secrets there.** A
  managed identity + a real secrets manager (§3) is very often simpler
  than provisioning a storage account and a volume mount purely to avoid
  environment-variable secrets — don't reach for the more complex
  mechanism out of habit when the platform's own answer is already
  sitting there.
- **A LAN-only, no-TLS-termination deployment needs its security flags
  turned off explicitly** (§2's `force_https`) **and its own
  `ALLOWED_HOSTS` entry** (its LAN IP, or a hostname if one resolves to
  it) — never assume the cloud-prod deployment's settings are a safe
  default to inherit for a self-hosted box; the two have fundamentally
  different trust boundaries.

---

## 5. Automating SDSI §17's Versioning Policy

SDSI §17 already states the rule in full ("bump `VERSION` on any
code-touching commit, even PATCH-only; skip docs-only changes; promote
`CHANGELOG.md`'s Unreleased section to a new heading in the same
motion"). It's genuinely automatable with a git hook rather than left to
manual discipline, once a project has exactly one committer (no merge-race
concern to design around).

- **Two hooks, not one**: `pre-commit` decides whether the commit touches
  code, bumps `VERSION`, and promotes `CHANGELOG.md`'s Unreleased section
  — all staged into the same commit. `commit-msg` appends the
  `VERSION x.y.z` trailer to the message, because the message doesn't
  exist yet at `pre-commit` time (hook order is `pre-commit` →
  `prepare-commit-msg` → the message is finalized → `commit-msg` →
  `post-commit`).
- **A simple, file-path heuristic decides "docs-only"** (everything
  staged falls under `docs/` or matches `*.md` anywhere) rather than
  trying to infer semantic intent from a diff. Good enough in practice,
  and legible enough that a human can predict what will and won't trigger
  a bump.
- **Respect a bump already made by hand.** SDSI §17's MINOR/MAJOR
  distinction (a new required setting vs. a breaking change) isn't
  something a hook can infer from a diff — if `VERSION` is *already*
  staged with a change when the hook runs, treat that as the developer's
  deliberate choice and only handle the `CHANGELOG.md` promotion, never
  overwrite it with an auto-computed PATCH bump.
- **Store hook scripts in a tracked repo folder** (e.g. `scripts/git-hooks/`)
  and wire them with `git config core.hooksPath <folder>` — never rely on
  copying into the untracked `.git/hooks/` directory by hand. Add the
  `git config` line to whatever script already bootstraps local dev, so a
  fresh clone gets it wired automatically.
- **Test a new hook against a real, throwaway commit before trusting it**
  — create a trivial staged change, commit for real, and inspect the
  actual result (the bumped file, the promoted changelog, the message
  trailer) rather than reasoning about the script from its source alone.
- **Never use `git reset --hard` to undo a test commit (or any commit)
  when the working tree might hold other, unrelated uncommitted changes**
  — `--hard` discards *every* uncommitted change to every tracked file,
  not just what was in the commit being undone. This is exactly the
  mistake made while building and testing this hook: an unrelated,
  in-progress file move (with several supporting doc/script edits still
  unstaged) was silently wiped out by a `reset --hard` meant only to
  discard a one-file test commit. `git reset --soft` (keeps everything
  staged) or plain `git reset` (keeps everything, unstaged) is the safe
  default any time the working tree isn't known to be otherwise clean;
  reach for `--hard` only after confirming there's nothing else in the
  tree worth keeping.

---

## 6. Documentation Judgment Calls

- **A historical planning/spec document (a dated record of what was
  actually decided and built at the time) is generally left alone when
  later, unrelated work changes the code it describes** — rewriting it to
  match new reality misrepresents history, and SDSI's own artifact-chain
  philosophy (§22) treats these as a permanent audit trail, not a living
  reference.
- **The exception: when the historical content itself is an active
  source of confusion going forward** — an abandoned direction (a brand
  concept, a design approach) still described in an old spec as if it
  were current, that a future session (human or AI) could easily mistake
  for the present plan. There, updating it (or clearly marking it
  superseded) is worth the "rewriting history" cost, because the risk of
  it misleading someone later outweighs the value of an untouched record.
  This is a judgment call to make explicitly and ask about, not a
  blanket rule either way.
- **A living layout document (a project's `CLAUDE.md`) gets updated the
  moment a project deviates from a generic standard's default assumption**
  — precisely so a future session doesn't quietly regress toward that
  default. §1's `manage.py` location is the concrete example: the
  deviation is only safe long-term if it's written down where the next
  session will actually look.

---

## 7. Working With an AI Agent on This Stack

Process notes specific to building a Django website with an AI coding
agent, distinct from anything about Django itself.

- **Load a dedicated design skill before writing any new CSS/markup**,
  and explicitly ground new design tokens in what's *already* on the
  page — reuse the established palette, type, and spacing rather than
  introducing a parallel visual language for just the new section.
  Visual consistency across the whole site is a real, explicit
  expectation worth confirming, not an implicit nice-to-have a design
  skill will assume on its own.
- **When a request grows mid-conversation past its original scope**
  (a small script tweak that turns into a change touching production
  secret-handling, or a decision that starts affecting every deployment
  target instead of one), **stop and say so explicitly** rather than
  quietly absorbing the growth into the same task. Reclassify (a bounded
  fix becoming an architectural change, say) and get a fresh, scoped
  decision before designing further — the same instinct as
  `superpowers:brainstorming`'s "hidden complexity upgrades the path,"
  applied specifically to the moment scope actually grows, not just at
  the very start of a task.
- **"Mirror how project X does this" means reading project X's actual
  code, not reasoning from a description of it** — and reading it in
  full can surface that the reference project never had to solve the
  exact problem now in front of you, which is itself important
  information to bring back before designing.
