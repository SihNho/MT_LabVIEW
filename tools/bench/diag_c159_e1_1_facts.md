---
type: facts
status: current
date: 2026-10-10
card: 159-e1-1
---
# CEN2 judges Wire by (source, sink, frame) end pairs (PD389(b)) - built, self-test 8/0
## Changed (tools/stagekit.py only; md5 9cd8822e -> ac3a8f57)
- `Stage.census_gate` :307-349 - new `judged={class: (ok, detail)}`; judged classes leave the uid diff, their ok joins the verdict. judged=None = old code path.
- `term_identity_pairs` :2071 - its inline stub block is now the call `stub_sides` (same output; regression selftest_c158_gates386 16/0, log in %TEMP%).
- NEW `stub_sides` :2084-2093, `wire_end_pairs` :2096-2127, `cen2_wire_ends` :2130-2145 (docstrings name the self-test). The end key is
  diag_c159_b1_1.py:309-319's end key, moved into stagekit: base term uid if base has it with the SAME owner CLASS, else ('new', owner class); frame = base frame uid or 'new'.
- `RingSession.__init__` :2383 (`self.real`), `gates_ng_fr_d` :2457 (keeps the real rows), `gate_cen2` :2481-2512 (`real=None` arg; Wire judged
  by ends, `UID-REUSE` fact, `RECORD CEN2` stub facts; no real rows or no Wire class -> uid census as before).
- Owner UID is NOT in the key: moved control terminal 3453 has owner 31506 in real and 23405 in the sim (diag_c159_e1_1_probe.log:25-27); the first draft keyed by owner uid and failed C1 on it (selftest_c159_cen2_ends.log:7).
## Self-test `tools/bench/selftest_c159_cen2_ends.py` (labview none, 119 lines) -> `selftest_c159_cen2_ends_final.log` last segment: 8 pass / 0 fail
- C1: end-pair CEN2 PASS, new pairs sim 23 == real 23; old uid CEN2 Wire sim 11 / real 12; UID-REUSE "12 new uid(s), declared 12, sim end 11".
- C2: wire 31587's sink row removed -> FAIL, only_sim == [(24367, ('new','SelectorTunnel'), 23405)] exactly.
- C3: stub 24091 (sources [25235]) RECORDED sim-only, one FACT line, CEN2 still PASS.
- C4: non-Wire diff == the pre-edit gate's (bytes 9cd8822e kept as selftest_c159_cen2_ends_stagekit_9cd8822e.txt): pred {} / {} PASS both; SelectorTunnel+1 {(3,4)} FAIL both.
- V0/V1: 94ffff94, s09 eb1d0f31, P5-1a 2482fe7b, P5-1 7f2582ae unchanged (bytes read, no VI opened; no LabVIEW process).
- Sim end located: plan_ring_p5s02a.json finalized.step_files[-1] = sim/ring_p5s02a/step_23_wire.json b1892ad9; plan md5 4284c22a pinned by prerun_records.jsonl:1073.
## Unchanged
- stagesim eb99c6ba, stagexec 7a712ccb, stage_prerun 7605116f. No tools/hooks edit by this card (material_marker.log is written by bgrun --material itself).
- selftest_stagekit / selftest_c134_1_dry not run; no self-test re-pinned; no dry/prerun re-run.
## OPEN
- The real pred ed84b5fd declares Wire 12 (MEASURED-SCRATCH); the old real-run CEN2 on 94ffff94 PASSED (selftest log C1 FACT "pre-edit gate ok True"), so the 11-vs-12 was only the dry/sim side - PD389(b) is right, but the p5s02b pred's Wire count no longer decides anything.
- A recycled frame uid that equals a base frame uid would key as base (stagekit.py:2096 docstring); not seen in this data.
