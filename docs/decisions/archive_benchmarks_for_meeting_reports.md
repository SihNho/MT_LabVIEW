---
name: archive-benchmarks-for-meeting-reports
description: "Every benchmark is archived at report quality — what the test WAS, environment, criteria, raw data, scripts, screenshots, results — in one dated folder plus a catalog, because the user presents them in lab meetings and wants them reusable in other environments"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 7b982769-ee4e-45be-8846-85edbec23e37
  modified: 2026-09-04T13:38:11.516Z
type: decision
status: in-force
date: 2026-09-04
source: memory/archive_benchmarks_for_meeting_reports.md
---

# Archive every benchmark: describe the test, keep the evidence, make it portable

Two statements from the user on 2026-09-04:

1. *"추후 미팅에서 리포트할 생각이니 기준과 결과 구체적으로 알 수 있도록 아카이빙 할 것"* — results will
   be reported in a lab meeting; criteria and results must be concrete.
2. *"벤치 테스트들은 전부 아카이빙 할 가치가 있겠어. 나중에 다른 환경에서 사용하더라도 참고하기 좋으니.
   연구실에 공유하기도 유의미하고. (어떤 테스트였는지도 같이 남겨야 더 의미 깊을듯)"* — ALL benchmark
   tests are worth archiving, for reuse in other environments and for sharing with the lab, and
   each archive must say **what the test was**.

So a benchmark is not finished until its archive has:

- **What the test was** — the question it answers, in one paragraph a lab member can read cold;
  what was held fixed and what was varied (model / method / effort — name which); why it was
  run at that moment.
- **Environment** — GPU and VRAM, driver, Ollama/llama.cpp version, LabVIEW version, OS, the
  exact model names/quantizations and Claude model IDs, CLI versions — so a different machine
  knows what changed.
- **Criteria written before the numbers** — target set and ground-truth source, the exact
  prompt/task given to every cell, pass rules and tolerances, metrics.
- **Raw evidence in one dated folder** (`archive/bench-YYYY-MM-DD/`): results JSONL, ground
  truth, per-cell answers, the scripts, and copies of referenced screenshots (the session
  scratchpad is not preserved).
- **Tables generated from the data** plus the caveats that change the reading (cold vs warm,
  calibrated vs raw, fixed spawn cost, n per cell, invalid cells and why).
- **How to rerun elsewhere** — prerequisites and the commands, so the same table can be
  produced on another rig.
- **A catalog entry** in `archive/benchmarks/INDEX.md` (one row per benchmark: date, question,
  varied/fixed, headline result, folder) and a copy of the report in `docs/` for the active
  layer, pointed to from STATUS.md.

Non-results are results: record failed attempts (what was tried, what happened, time lost)
and cells that turned out invalid, next to the valid ones.
