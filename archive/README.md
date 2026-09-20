---
type: narrative
status: historical
date: 2026-08-28
tags: [archive]
---

# Archive — history, kept but not routinely read

**Do not read this directory as part of normal work.** Per `CLAUDE.md` rule 4, ordinary sessions
consult only the active documents in the project root. Nothing here is deleted; it is kept because it
may be needed later, and moved out of the way because reading it every session is what made the
documentation expensive.

Open one specific file here only when an active doc is ambiguous or contradicted and you genuinely
need the original reasoning — and say why you opened it.

| file | what it is | why it moved here |
|---|---|---|
| `VI_SCRIPTING_GUIDE.md` | the project's original VI Scripting write-up, including the full library evaluation | **absorbed into the `labview-automation` skill**, which is now the single source of truth for LabVIEW technique. Kept for the long library survey and the decision trail behind it |
| `GUI_PLAYBOOK.md` | the project's original GUI-automation write-up | likewise absorbed into the skill. Note its "Wanted next" section is stale — `probe` and `hover` were built |
| `WORKLOG.md` | dated session narrative — what was tried, what failed, why | pure history; the conclusions live in `STATUS.md` and the `labview-automation` skill |
| `VERSION_HISTORY.md` | evidence-based changelog of the `.vi` files, 4.1 → 4.6 | reference for a question that is now settled (the base VI is 4.5) |
| `BENCHMARKS.md` | GUI-control model benchmark + the pipeline-configuration benchmark, merged | both concluded; the verdicts are in `STATUS.md` and the portable skill |
| `TEST_MATRIX.md` | capability tests that had to pass before V6 could start | capability testing is complete and passed |
| `OPTIONS_beyond_gui.md` | routes beyond GUI automation (DLL, text export, why not to extract NI DLLs) | superseded by `ARCHITECTURE.md` §10, which carries the decision |
| `ANALYSIS_METHOD.md` | how `.vi` binaries were mined for text without opening LabVIEW | a fallback technique now; also packaged as the `labview-vi-analysis` skill |
| `GEMINI_EXECUTOR.md` | the Claude-plans / **Gemini-executes-GUI** split | **superseded 2026-08-28.** GUI grounding is done locally by UI-TARS via Ollama, and Gemini's role changed entirely: it is now a **read-only research peer**, not an executor (`CLAUDE.md` rule 5, `AGENTS.md`). The user also chose CLI login over the API key this design was waiting on |

| `peer/` | **every exchange with a peer agent** (Codex, Gemini) — question, answer, sources, verdict | see its own README. This one directory has a standing exception to rule 4: it is **checked before asking a peer anything**, because re-asking burns finite quota |

If work resumes on something archived here, move the file back to the root rather than working out of
this directory, so that the active set always states what is actually live.
