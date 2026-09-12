# Council

A council of contractor-style reviewer lenses for **documentation, designs,
plans, and business proposals**. Each lens is named for what it does, not
who it is — nothing to memorize to invoke the right one. For **source
code**, use the separate `code-reviewer` plugin instead; that's a
different job with its own process (intake → catalog → strategy → execute
→ validate), and this plugin deliberately doesn't overlap with it.

This plugin supersedes the earlier `council-of-claude` plugin, which named
each lens after a person (Tom, Mike, Pedro, Hector, Emma, John, Natalie).

## Structure

```
council
├── council:all         — all eight, one company-wide verdict
├── council:it          — Security, Standards, Efficiency, Infrastructure
│   ├── council:it-security
│   ├── council:it-standards
│   ├── council:it-efficiency
│   └── council:it-infra
└── council:bu          — Operations, Finance, Strategy, Legal
    ├── council:bu-ops
    ├── council:bu-finance
    ├── council:bu-strategy
    └── council:bu-legal
```

## IT lenses

For reviewing documentation, designs, or architecture proposals.

| Skill | Focus | Invoke with |
|-------|-------|--------------|
| `it-security` | Security gaps, auditability, logging | `council:it-security`, "security review" |
| `it-standards` | Standards, naming, structure, readability | `council:it-standards`, "standards review" |
| `it-efficiency` | Performance, resource use, KISS/simplicity | `council:it-efficiency`, "efficiency review" |
| `it-infra` | Tech/infra fit, cost, uptime, performance balance | `council:it-infra`, "infrastructure review" |
| `it` | All four together, one reconciled IT verdict | `council:it`, "have IT review this" |

## BU lenses

For reviewing business proposals, plans, budgets, or initiatives.

| Skill | Focus | Invoke with |
|-------|-------|--------------|
| `bu-ops` | Operational efficiency, ownership, process discipline | `council:bu-ops`, "operations review" |
| `bu-finance` | Cost trajectory, bottom-line soundness, savings quality | `council:bu-finance`, "finance review" |
| `bu-strategy` | Long-term fit, systems maturity, scalability, dependency risk | `council:bu-strategy`, "strategy review" |
| `bu-legal` | Contract, regulatory, IP, and data-privacy exposure | `council:bu-legal`, "legal review" |
| `bu` | All four together, one reconciled BU verdict | `council:bu`, "have leadership review this" |

## Full council

| Skill | Members | Invoke with |
|-------|---------|--------------|
| `all` | All eight — IT + BU | `council:all`, "convene the full council" |

## Setup

No configuration, environment variables, or external connectors required —
every skill runs on its own using only the document you give it.

## Usage

1. Attach or paste the document (or point Claude at a file) in your
   message.
2. Ask for a specific lens (`council:it-security`, or "review this from a
   security angle") for one point of view, a side (`council:it` or
   `council:bu`) for that side's reconciled take, or `council:all` for
   every lens and one company-wide verdict.
3. Plain language works too — each skill's description lists the phrases
   it responds to.

## Legal disclaimer

`bu-legal`'s output is a risk-flagging pass, not legal advice — it's meant
to tell you what to send to an actual attorney, not to replace one.

## Sharing with your team

Packaged as a single `.plugin` file — send it directly, or publish it to
your org's plugin marketplace if you run one.

## Customization

Want another lens, or a different split between IT and BU? Just ask — a
new lens slots in the same way (name, focus, checklist, output format) and
joins an existing side or a new one.
