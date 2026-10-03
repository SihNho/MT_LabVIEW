---
type: brief
status: current
date: 2026-10-03
---
# Brief 143-2 — identify the 2 extra Error List items of the session-2 scratch file (MEASUREMENT, read-only)

Context: 143-1 scratch PASSED every build gate (21/0, peak 620.3) and saved `claudeDev\D1_ring_p4s02_20261003_110001.vi`
(md5 84cac48781c7c915c8f0d7e8fb079341, NOT adopted). Its Error List = 53 vs predicted 51/52: extra
"Local Variable ... not connected to anything" + "While Loop: Conditional terminal is not wired" (`errorlist_D1_ring_p4s02_20261003_110001_20261003_110836.json`
:5638-5642), no uids on either. Judgement's hypothesis H: both are the plan's by-design session-boundary state — the
Local read created by s02's last action `p4_lr_stop12` (#6902) has its output wired only by s03's first action
`p4_w_stop12`, and loop 1.2's conditional terminal is empty because s02 removed the scaffold stop (PD295(b)). Alternative
H': a delete in s02 cut a wire the plan did not mean to cut (and/or #23166 term '').

## Steps (read-only on the s02 file; nothing is edited or saved)
1. Fresh LabVIEW instance: load `D1_ring_p4s02_20261003_110001.vi` (load MB measured) + whole graph read with the prepared
   `tools/bench/diag_c143_1_graph.py` / `diag_c143_1_graph_plan.json` → `tools/bench/graph_ring_p4s02_20261003_110001.json` + md5.
   LabVIEW closed and verified gone.
2. OFFLINE from that graph: list (a) every While loop whose conditional terminal has no wire (uid, owner loop uid, which
   loop — is it 1.2?), (b) every Local node whose terminal(s) have no wire (uid, which control, read/write),
   (c) #23166's '' terminal wired or not, (d) every terminal unwired in the s02 real graph that was wired in
   `graph_ring_p4s01_20261002_234419.json` (key (uid, owner, name)).
3. Compare with the s02v18 simulated END graph (`tools/bench/sim/ring_p4_s03v18_s02end/base_provisional.json`, or the s02v18
   sim end step it was copied from): are (a)/(b) open in the simulated end too? Does `plan_ring_p4_s03v18.json`'s first
   action wire exactly them?
4. Then the failed-prediction review: write a `review/1` card (`py tools/protocol.py new review --id c143-2-el53`) with the
   measured facts of steps 2–3, dispatch `peer.ps1 -Agent claude -Role hypothesis -ReviewCard ...` (asks to REFUTE H), record
   its verdict. Do not write a disposition that adopts the file — that is judgement's.

## Return
`result/1`: load MB, graph file + md5, the step-2 lists (uids), step-3 yes/no per item with file:line, review verdict file.
Facts → `tools/bench/diag_c143_2_facts.md`. Return at the first unexpected result.
