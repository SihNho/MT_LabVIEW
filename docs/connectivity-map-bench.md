---
type: reference
status: current
date: 2026-09-23
tags: [connectivity-map, jev, bench, step-5b]
---

# Connectivity-map bench (plan step 5b): current results

The full report, raw logs and scripts are in `tools/bench/bench_map_20260923/README.md`. Everything ran on dated scratch copies of `claudeDev\D1_s1_copy.vi` (S1). No VI was run or saved, and the original and all stage pins held throughout.

| test | criterion | result | verdict |
|---|---|---|---|
| A1 mutation: 8 deletes + 1 add through `stagekit.from_decision` | diff lists exactly 9 rows | precision 1.000, recall 1.000; control diff (fresh read vs wiki) ∅ | **PASS** 12/0 |
| A2 200 random wires vs `OpWireSource_v5` | 200/200 | source owner 200/200; full endpoint multiset 200/200; 0.085 s/wire | **PASS** |
| A3 58 FSOT, fresh `read_tunnel` vs wiki `fs_tunnel_pairs` | 58/58 | 58/58; also 58/58 against the OpAllTerms_v1 rows each tunnel owns; FSIT 518/518 repeatable | **PASS** |
| A4 functional units of `docs/frame-loop-wire-graph.md` via `path()` | every unit | 150/151. The miss is `#23175`, whose unit link went through the 2026-09-01 TIFF fixture, which is not in S1. R1/R2 sequence crossings pass (2/2). | PASS (1 miss explained) |
| A5 Jev menus on a held-out half | PAIR ≥ 0.85 accuracy and 0 dangerous errors | PAIR 0.92 accuracy, **1 dangerous** (t 0.65 from half 1). CHAIN 0.931/0; RISK 1.0/0; OP argmax 0.5 | **FAIL: PAIR does not act** |
| A5b 1000 seeds + leave-one-intent-out (the review's own test) | – | 503/1000 splits are dangerous, from 6 intents. With a name filter it is still 513/1000. | confirms A5 |
| B end to end, 0 LLM turns | 11/11 restored, ExecState 1, computation_diff ∅ | arm 1: nothing executed (PAIR not acting). Oracle-verdict arm: **8/9** restored with exact S1 keys (2 of the 11 wires are not in S1), ExecState 0, computation_diff 1 row (`#9243 'x'`), diff 2 rows. 367 s, 260 Jev calls ≈ $0.021 | **FAIL** |

Per-layer outcome in B (9 rows that exist in S1):
- **Candidate:** 9/9 contain the true pair (2 of them only through `map_key`, because the terminals were renamed).
- **Verdict:** 0/9 act. The truth is ranked first on 7/9. On 9635 and 11232 a wrong "flipped" inner terminal is ranked first.
- **Op:** the Python rule covers 8/9. w9635 (a LoopTunnel inner source) has no rule entry, and Jev's OP menu does not act.
- **Execution:** 8/8 rows executed correctly.

Facts the bench measured that no earlier document states:
1. Cutting the wire that feeds an input tunnel makes its inner terminals read as SINKS. Their wires then have 0 sources and no edge. `jev_candidates` lists those inner terminals as legal sinks, and Jev scores them about as high as the true outer terminal.
2. Cutting both wires of the VISA shift-register carrier renames its terminals `'VISA out'` → `'Outgoing Handle'`. Re-wiring them renames the terminals back.
3. `jev_candidates.load()` built the heuristic fs edges until this bench. It now passes the wiki's exact `fs_tunnel_pairs`.

Reviews: `archive/peer/2026-09-23-bench-map-a5-pair-heldout.md` and `archive/peer/2026-09-23-bench-map-b-endtoend.md`.
