# Stage K (cycle 79, card 79-3) - plan for the prior-art review

Design: `docs/d1-loop12-17-split-plan.md` Pre-decided 177 (decided by the cycle-79 judgement session). This page is
the EXECUTION route only; it re-decides nothing.

## What it does
Input `claudeDev\D1_s4_loop17.vi` md5 `4b621946...` (the S4 bed). Output `claudeDev\D1_k_<ts>.vi`.
- (a) move the CPU kernel `#5058` into body `#23166` of the 1.2 loop `#10170`;
- (b) ONE new shift-register pair on `#10170` for the kernel's S1 chain (`pos in cal image out` -> R, L -> `pos in
  cal image in`, L initialised from FSIT `#6239`, the old `#2972`'s source); old `#119/#2972` NOT deleted (L2-R);
- (c) six NEW input tunnels on `#10170` (t2, t9, t11, t12, t14, t15), each fed by the same FSIT source term as its
  `#637` original, IndexMode = original's (all 0, measured live);
- (d) the two indicators `#3173 'Pos within cal image'` and `#9519 'Pos: Diffraction Pattern'` (measured: ControlTerminal,
  indicator, only source = `#5058` t8) move into `#23166` and are re-wired from t8;
- (e) every other kernel row stays OPEN (t0, t1, t3, t4, t7, t8's `#10969/#10757`) - no queue is built.

## Route (the simulator route of `docs/stage-simulator-plan.md`, first use on a SAVED stage)
1. `tools/bench/k_contract_79.py` (DONE, 11/0, read-only LabVIEW): live terminal table + loop table of the bed
   (`tools/bench/graph_k_s4_20260925.json`, `graph_loops_k_s4_20260925.json`), 177(d) class check, 177(c) IndexModes.
2. `tools/bench/sim_k_split.py` (pure Python): the stageplan/1 file from `k_facts_79.json` + the contract by 177's rules
   (RULE-CHAIN-S1 for (b) via `jev_candidates.s1_chains`, never Jev), simulated with `tools/stagesim.py` on the measured
   op models, finalized with `open_rows` = the end cdiff rows after a gate that every row is explained by an (e) row or
   by the two carried L7 rows (w4517, w3268); `stagexec` dry run PASS; writes `plan_k_split.json` + `plan_k_rows.json`.
3. `tools/recipes/stage_d1_k.py` (110 lines, stagekit + stagexec): the stagexec Executor with LVBackend on the dated
   WORK copy (not discarded, unlike `stagexec.py run`), per-op real-vs-simulated graph compare, then the 177(g) gates:
   IndexMode, ordered second pass Is Broken? on node-terminal sinks (verify_term_uid, 174), PB cdiff == open_rows FATAL
   before save, ES recorded, handles recorded, save (scripted if ES 1, else rule-6 GUI save), pins.
4. dry + pre-run through `tools/stage_prerun.py`, then ONE LabVIEW run under the retry cap.

## What already exists and is reused (checked)
`tools/stagesim.py`, `tools/stagexec.py` (Executor/LVBackend/compile/bind; L7 bench `tools/bench/stagexec_l7_bench_r2.log`
14/0), `tools/bench/sim_l7_split.py` (plan-building shape), `tools/recipes/stage_d1_l7_r.py` (second pass, IndexMode,
save), `tools/stagekit.py`, `tools/bench/opmodels/*.json`. New files are only the three above. No new op VI.

## Since card 79-3 (card 79-4, Pre-decided 178)
- 178(b): the simulator's A0 is an OWNERSHIP check (#23166 owned by #10170, read from the dump's structure->diagram order,
  the same reader returning L7's #23041->#23405; #5058 on #23166 at the end); P3 credits t3 only by end-graph evidence
  (unwired; #5796's inner 5810 sourceless) and a negative control (fake t3 -> #2626 'array') must fail it.
  Run 4 of `tools/bench/sim_k_split.py` (log `tools/bench/sim_k_split.log`, last block) is the finalizing run.
- 178(c): PB = the 10 end rows `#376`x2, `#2626 'array'`, `#5696`/`#6085 'x,y,z array'`, `#10757`/`#10969 'array'`,
  `#5058` t0/t1/t7; t3 has no row of its own.
- 178(d): 177(b)'s "Jev argmax check" is WITHDRAWN; the chain rows are RULE-CHAIN-S1 (not a deviation any more).
- 178(e): the Case-frame merge of `computation_diff` is carried to L2-A1; K does not touch #5796/#5805.

## Known deviations to attack
- The second pass cannot address register faces or front-panel terminals (not in `Diagram.Nodes[]`); those 4 rows
  rely on the per-op graph compare only (L7-R likewise skipped its indicator row, `stage_d1_l7_r.py:93`).
- Remove Bad Wires is NOT run in K: the (e) rows' half-wires stay for the next stages (177 names no RBW).
