---
type: rules
status: current
date: 2026-10-10
tags: [rules, docs, lint]
---

# Rules - documentation

Restated briefly from `docs/rules/CLAUDE-full-2026-10-10.md` (cited ranges = full wording and quotes).

- **Rule 4 - documentation is layered: short top index, topic files below, archive unread.** Active docs state what is
  true now in as little text as a cold start needs; `STATUS.md` stays under one screen and only points; verified facts
  go to topic files (`docs/`, `docs/labview/`); narrative goes to `archive/` - nothing is deleted, only moved. Do not
  read `archive/` in normal work (open a specific file only when the active docs are ambiguous, and say why). When a
  doc needs scrolling to find the current state, push content down a layer now. Scratch artefacts are created and
  deleted in the same operation. **Long docs are frozen in place and indexed** (2026-10-02): `status: frozen` on the
  same line, a footer appended, a short INDEX of decisions in force; new decisions go to short per-topic files;
  `doc_lint` caps active docs at 400 lines. **STATUS.md over ~100 lines** = narrative crept back: move it verbatim to
  `archive/<date>-status-<topic>.md`, keep lock, hardware permission, current state, OPEN, NEXT.
  `docs/rules/CLAUDE-full-2026-10-10.md:614-634`
- **Documents are LINTED by code and INGESTED by a model every cycle** (2026-09-16), per cycle / per run, never weekly.
  Lint: `tools/doc_lint.py` (frontmatter, cited paths and `file:line` exist, STATUS length, one current plan,
  `supersedes:` targets, review dispositions, unmarked decisions) - every cycle close via `audit_cycle`. Ingest of
  changed docs: `tools/doc_ingest.py --cycle N` (Sonnet, `peer.ps1 -Role ingest`, archived to `archive/ingest/`) -
  contradictions only. Full ingest: `--full --model opus` every 5 cycles. Which side of a contradiction is right is a
  judgement-session call. "Ingest" means a model reads and refreshes state, not an index. `docs/rules/CLAUDE-full-2026-10-10.md:635-648`
- **Where to look:** `STATUS.md` first (lock, state, next); `docs/NAMES.md` (verified terminal strings - check before
  every wiring call); LabVIEW technique `docs/labview/SKILL.md` (skill `labview-automation` points there);
  `ARCHITECTURE.md` (the rig); `Requests.md` (the user's ground rules verbatim); `docs/peer-brief.md` (the peers'
  brief); `archive/` (history, rule 4). Start procedure for any session: `docs/START.md`. `docs/rules/CLAUDE-full-2026-10-10.md:849-858`

Related decisions: `docs/decisions/archive_history_dont_read_it_by_default.md`,
`docs/decisions/docs_are_linted_and_ingested_every_cycle.md`, `docs/decisions/claude_writes_every_document_here.md`.
