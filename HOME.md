---
type: reference
status: current
date: 2026-09-15
tags: [hand-off, index]
---

# V6 Parallelisation — vault home

Open this first in Obsidian; a session opens [STATUS.md](STATUS.md) first. Both point at the same places.

## Right now

- [STATUS.md](STATUS.md) — the lock, what stands, the OPEN questions, and the NEXT action. One screen, always current.
- [CLAUDE.md](CLAUDE.md) — the standing rules. Read before doing anything; they bind every session.
- [docs/stage2-assembly-step-e.md](docs/stage2-assembly-step-e.md) — the cycle in progress (the reseed case).

## The three layers

| layer | where | read it when |
|---|---|---|
| **state** | [STATUS.md](STATUS.md) | every session start |
| **verified facts** | `docs/` — [docs/NAMES.md](docs/NAMES.md) (LabVIEW-scripting names and standing facts), [docs/toolkit-capabilities.md](docs/toolkit-capabilities.md) (what the op fleet can do), [docs/GLOSSARY.md](docs/GLOSSARY.md) | before wiring, before assuming a capability |
| **narrative & evidence** | `archive/` — 216 peer exchanges, cycle histories, [archive/benchmarks/INDEX.md](archive/benchmarks/INDEX.md) | only when the active docs are ambiguous, and say why |

## Process devices (they refuse, they do not remind)

| device | refuses / reports |
|---|---|
| `tools/hooks/guard_bash.py` | a LabVIEW command run in the foreground without a short timeout |
| `tools/hooks/guard_peer.py` | the next build while a failed prediction has no archived review |
| `tools/hooks/guard_cycle.py` | the next build while the previous cycle has no retrospective, or a violation slug is at threshold |
| `tools/audit_cycle.py` | mechanical compliance of a window + its cost lines |
| `tools/retrospective.py` | the end-of-cycle review of HOW the cycle ran |
| `tools/violations.py` | the tally that decides when a device becomes mandatory |

## Tags worth clicking

`#stage2` the rebuild · `#vi-scripting` how LabVIEW is driven by script · `#main-vi` the original's anatomy ·
`#measured` numbers with evidence · `#open-question` waiting on the user · `#process` how the work is run ·
`#peer-review` the adversarial record

## Conventions

- `status: superseded` in a document's frontmatter means **its content is known to be wrong or replaced** — the
  graph and search still show it, so the reason it was wrong stays readable.
- Archive notes never wikilink into the active set (the graph would fill with peer exchanges); active notes may cite
  archive evidence deliberately. `tools/audit_cycle.py` check A7 enforces it.
- Nothing is deleted, only moved down a layer.
