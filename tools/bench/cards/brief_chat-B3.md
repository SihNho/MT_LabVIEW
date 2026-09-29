# brief chat-B3 — ULTRACODE bench on LARGE tasks: build tasks + harness, probe, smoke (user 2026-09-29: "이걸 벤치해보자. 사실 이게 핵심이거든")

Rig 실험중: NO LabVIEW / GUI / hardware; never touch the user's LabVIEW process. Offline only.

## Question
Where does ultracode (= the Workflow tool: one request split across many sub-agents — fan-out, pipeline, adversarial
verify, completeness critic) improve on a single session? decbench v1 (`tools/bench/decbench/report_v1.md`) tested
only a 4-cell approximation on single-answer questions; ultracode itself was never measured. Its claimed strength is
LARGE, decomposable work that does not fit one context. So this bench uses large tasks with a known answer set.

## Arms (pin ids)
| arm | how |
|---|---|
| S-MX | one `claude-opus-5-5` / max session, same prompt, same tools, same time cap |
| S-H  | one `claude-opus-5-5` / high session (cheap baseline) |
| UC   | ultracode: a `claude-opus-5-5` session whose prompt carries the keyword that opts into multi-agent orchestration, so it authors and runs a Workflow (fan-out + verify). Record agent count, sub-agent tokens, wall time, usd |

**PROBE FIRST (the main unknown):** does the Workflow tool work inside a `claude -p` cell in a replay worktree, with
the cell guard hooks active, and do its sub-agents inherit the guard (labview none, git history forbidden, write only
in the worktree/%TEMP%)? Try the cheapest probe (a 2-agent workflow that lists 3 files). If `claude -p` cannot run
Workflow, report the exact error and the fallback you propose (e.g. the chat runs the UC arm with the Workflow tool
itself, pointed at the worktree path) — do NOT implement a fallback that lets UC agents see the current repo (the
answers are on disk at HEAD).

## Tasks (3), each at a BASE commit where the answer was not yet on disk; leak-check as decbench does
Each task must be large (many files / many items), decomposable, and have a known answer SET so recall and precision
can be scored. Candidates — choose the three strongest, replace any that leak or have a soft answer key:
- **L1 whole-doc contradiction audit.** Base = a commit just before a `doc_ingest.py --full` (Opus) run or a
  judgement session that recorded a set of contradictions between active docs (STATUS / CLAUDE.md / docs/*). Answer
  key = the contradictions that were later CONFIRMED and fixed (resolution notes in the docs, e.g. "Resolved
  2026-09-18 by the cycle-18 judgement session after doc_ingest reported…"). Task: "find every contradiction between
  the active documents; cite both sides".
- **L2 original-VI fact census from saved graph dumps** (no LabVIEW): base with a saved graph JSON of the original
  copy (tools/bench/graph_*.json or similar) and a later verified census as key — e.g. every motor/VISA/serial call
  site and the loop it sits in (motor-limit-checker results, the rotor's nine call sites, Pre-decided 133), or every
  display indicator write. Task: "list every X in this VI with its node uid and containing loop".
- **L3 cross-cycle process audit.** Base with N ≥ 10 cycles of logs/cards/retrospectives; key = the repeated failure
  classes / violations that `tools/violations.py` or later retrospectives counted (e.g. repeated-failure-class,
  device-failed, judgement-in-material with their cycle numbers). Task: "find every failure class that repeated
  across these cycles, with the cycles and evidence".
Fix per task BEFORE any run: the answer set (items with ids), matching rules for recall, and how a claimed item NOT in
the key is judged (blind Opus 5.5 high scorer with the base-commit files: real / not real) → precision.

## Scoring per run
recall (key items found), precision (claims that are real), false claims count, usd, wall minutes, sub-agent count,
tokens. Blind scorer: answers shuffled, arm hidden (strip "agents/workflow" wording from UC answers before scoring).

## Scale
2 repeats × 3 tasks × 3 arms = 18 runs; per-run cap 60 min (UC may need it); `--par` as high as the 5-hour limit
allows (runs are independent). Estimate the cost in the smoke; usage-limit rule applies (record resume point,
return BLOCKED with the renewal time).

## This card (B3) = build + probe + smoke, NOT the full run
Reuse decbench/matbench worktree + guard code by import. Smoke = 1 run per arm on the smallest task. Return result/1:
probe outcome, the 3 tasks (base, key size, leak check), smoke per arm (recall/precision/usd/min/agents), projected
full cost/time, `open:` for the chat.
