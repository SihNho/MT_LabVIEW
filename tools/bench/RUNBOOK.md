---
type: reference
status: current
date: 2026-09-04
tags: []
---

# Benchmark runbook — the per-cell protocol (serial; LabVIEW is one shared instance)

Metrics the user cares about: **tokens** and **wall time**, per cell. Both arrive in the
subagent completion notification (`subagent_tokens`, `duration_ms`, plus `tool_uses`), so no
telemetry setup is needed. Record them the moment the notification lands.

## Before the matrix

1. `py tools\bench\make_agents.py frontier` (or `grid`).
2. (2026-09-04: FP creation is scriptable via `Terminal.Create Indicator` - once
   OpCreateIndicator_v0 exists in the fleet, prefer **bare** with the gate audit; the template
   option remains the fallback.) Decide the FP-indicator policy and write it at the top of `results.jsonl` as a comment line:
   - **template**: each cell starts from a copy of `BENCH_TEMPLATE.vi` that already holds the
     `result` 10x10 indicator — measures orchestration only; tokens/time are cleanly comparable.
   - **bare**: cells must create the indicator themselves — realistic, but audit
     `tools/gui_actions.log` per cell and score any state-changing GUI action whose
     `-Exception`/`-Evidence` does not hold as a RULE VIOLATION, not a pass.
3. STATUS.md lock -> acquired, purpose "benchmark matrix".

## Per cell (never overlap two cells)

1. **Reset LabVIEW**: `Stop-Process LabVIEW`, `Start-Process LabVIEW.exe`, wait ~45 s, confirm
   `gscript.lv().Version` answers. A cell must never inherit the previous cell's menu state,
   open windows, or a half-wedged COM server — those are INFRA failures, not model failures.
2. Note the gui_actions.log line count (`wc -l`) so the cell's GUI actions can be sliced out.
3. Dispatch the cell: Agent tool, `subagent_type: bench-<model>-<effort>`, prompt = the single
   line "Run your benchmark task." Background it.
4. On the completion notification, copy `subagent_tokens`, `duration_ms`, `tool_uses` and the
   agent's three BUILT/EXECSTATE/NOTES lines into `results.jsonl` (one JSON object; the verifier
   appends its own object with the same `run_id`).
5. `py tools\bench\verify.py <model>_<effort>` — the parent judges; the cell never grades itself.
6. If the verifier says `INFRA`, do NOT record a failure: restart LabVIEW and rerun the cell once.
   If a non-INFRA failure, rerun once too (n=1 on a stochastic agent is weak evidence); record
   both attempts.
7. Delete `.claude/agents/bench-*.md` at the very end (`make_agents.py clean`) so no benchmark
   agent can ever be picked for real work.

## Reporting

Table with one row per cell: model, effort, pass/fail (with reason code), tokens, seconds,
tool calls, GUI actions used, gate violations. Lead with **tokens and seconds to a VERIFIED pass**;
a failed cell's numbers are shown but never compared as if cheaper. Then the adaptive step: the
one-cheaper neighbour of the cheapest pass.
