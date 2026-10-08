---
card: 147-a2-1
status: current
date: 2026-10-08
---
# Brief 147-a2-1 - ONE recipe sink gate for s06 (offline, PD355(b))

Offline only. No LabVIEW process, no camera, no motor. `tools/stagexec.py` and `tools/gscript.py` are NOT edited (md5 1bab9cf9 / 1a80236e before and after).

## Why
Round 1 (card 147-a1-4) stopped IN op 21 (`p4_rbA_re1` connect). Cause (`archive/peer/2026-10-08-c147-a1-4-re1.md`, `tools/bench/diag_c147_a1_4_facts.md`): `gscript.wire_indicators` raises "target BROKEN after wiring" whenever `exec_state(target) != 1` (`tools/gscript.py:2148-2155`); every P4 bed is ExecState 0 by design, and `tools/recipes/stage_d1_ring_p4_s06v18.py:46` declares `sink_gates=[], gates={}`. `stagexec.sink_gate_for` (`tools/stagexec.py:2751`, used at :2985) already turns a declared sink into a recipe-owned readback. PD355 (`docs/d1/ring-p4b.md:356-377`) orders ONE such gate: sink `[23166, 'Pos within cal image']`, the indicator that op 21 wires to the net of #5058 'pos in cal image out'.

## To produce
1. In `tools/recipes/stage_d1_ring_p4_s06v18.py`, declare ONE sink gate `{"gate": <label>, "sink": [23166, "Pos within cal image"]}` plus `gates = {<label>: callable(entry) -> (ok, detail)}` and pass both to the `LVBackend` call (line 46). Example of a recipe-owned reader on the same API: `tools/recipes/stage_d1_l2a2.py:34-50`. The `DryPlanBE` branch needs no change.
2. The gate callable must read back, on the real work VI after op 21: (a) the indicator `[23166, 'Pos within cal image']` exists and has exactly ONE wire, (b) that wire is the net of #5058 'pos in cal image out', (c) that net has exactly one source. Anything else returns `ok=False` (the executor then raises ExecStop). The detail string carries the three readbacks so the log shows them. The uid mapping between plan symbols and real uids goes through the executor's binding (`x.bind`), not through typed numbers beyond the `[23166, ...]` sink the plan names. Read how `sink_gate_for`/`check_sink_gates` hand the entry to the callable BEFORE writing it; do not infer.
3. `tools/recipes/stage_d1_ring_p4_s06v18_scratch.py` runs `R.body(s)` (line 78). It must declare, or visibly assert against, exactly ONE sink gate with the same sink as well (for example by asserting `R`'s declaration at import). Report in the facts file how each of the two files satisfies "declares exactly ONE sink gate" with `file:line`.
4. Re-run, on the NEW bytes of both recipes: py_compile; the dry run of the build recipe; the dry run of the scratch recipe; the offline pre-run (`tools/stage_prerun.py`, the form the 147-a1-3 / 146 cards used, records in `tools/bench/prerun_records.jsonl`); `--el-advisory-selftest` of the scratch recipe if it still exists. Per the launch gate a scratch recipe's dry form may need `--scratch-required` (rc 3 expected there). Quote each command and its rc. New md5s of the two recipes go in the facts file.
5. Count of sink gates by `stagexec.check_sink_gates(decl, gates)` run offline on the declared pair: print the returned object (must be length 1) and the declared sink.
6. A gate or checker false positive goes to `tools/bench/gate_fp_queue.jsonl` via `tools/gate_fp.py`, never an env bypass. Any tool defect in stagexec/gscript: RETURN with `file:line`, do not edit.

## Report (facts only, in `tools/bench/diag_c147_a2_1_facts.md`, <= 40 lines)
Two new md5s; diff summary by `file:line` for each recipe; the callable's three readbacks as designed; dry/prerun commands with rc and the first failing gate line if any; `check_sink_gates` output; md5 of `stagexec.py`, `gscript.py`, `plan_ring_p4_s06v18*.json`, `memory_model.json` after (must equal the inputs); `OPEN:` line for anything you could not settle.
