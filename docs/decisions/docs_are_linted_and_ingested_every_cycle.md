---
name: docs-are-linted-and-ingested-every-cycle
description: "The user's 2026-09-16 direction — the project's .md files get a mechanical lint (a .py, no model) and a model \"ingest\" (read → find contradictions → refresh state) on a CYCLE / run cadence, never weekly; ingest means reading and refreshing, NOT building an index"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 97b1695e-68c2-4985-8cac-1ca3097b3b15
  modified: 2026-09-16T11:45:17.494Z
type: decision
status: in-force
date: 2026-09-16
source: memory/docs_are_linted_and_ingested_every_cycle.md
---

# Every cycle, the documents are linted by code and ingested by a model

On 2026-09-16, after a day in which STATUS.md grew to 526 lines, CLAUDE.md carried a stale slug list, and two
documents described the same wire in contradictory ways, the user said:

> *"특정 주기마다 .md 파일들 ingest 및 lint 하는 규약 필요해보임. 어떤 모델로 적용할지도 정해야"*

and, on the follow-ups: the mechanical lint is a **`.py` script**; the cadence is **per cycle or per actual run,
not weekly** (*"주 단위보다는 싸이클 단위 혹은 실제 실행 단위가 적절해보임"*); and "ingest" means **(a) a model reads
the documents and refreshes summary/state**, not (b) building an index — (b) was measured and rejected on
2026-09-15/16 (an index made the prior-art reviewer stop searching `archive/`, recall 6.5 → 5.0 of 8).

## The agreed shape

| layer | what | model | when |
|---|---|---|---|
| **lint** | `tools/doc_lint.py`: frontmatter present/valid; every cited path and `file:line` exists; STATUS ≤ ~100 lines; at most one `status: current` plan; `supersedes:` targets not still current; review dispositions not placeholders; decision sentences without `DECIDED:`/`MEASURED:` marks (warn) | none | every cycle close, with `audit_cycle`; refuses nothing by itself except what the existing gates already refuse |
| **ingest (changed docs)** | the claude peer as rule/consistency auditor reads the documents changed in the cycle window (the C7 list) and reports contradictions between them and with the active docs | **Sonnet** | every cycle close |
| **ingest (all active docs)** | the same audit over all of `docs/` + STATUS + CLAUDE.md | **Opus** | not weekly — triggered by a run count (every N cycles) the user sets; default proposal 5 cycles, same rhythm as the outcome review |
| **resolving a contradiction** | deciding which document is right | judgement session | when the ingest reports one |

## Why this shape

Code catches what needs no judgement, for free, every time. A model is spent only on what code cannot see — two
sentences that disagree — and only on the files that changed, so the cost tracks the work rather than the size of
the archive. The user's cadence choice ties the audit to the thing that produces drift (a cycle, a run), not to
the calendar.
