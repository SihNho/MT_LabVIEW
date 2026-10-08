---
card: 147-a1-7 (retry of 147-a1-6; resume of 147-a2-1)
date: 2026-10-08
status: PASS - prerun of the build recipe 16/0 (147-a1-6 below: FAIL 14/2)
---
# Facts - card 147-a1-7 (X6 + X10 fixed in the s06 build recipe; tools, plans, memory_model untouched)

## What changed (build recipe 7e0edcf8 -> 9150f15bb13c622031eee7086225037c; scratch recipe unchanged 31009bfc)
- X6: `stage_d1_ring_p4_s06v18.py:45-51` - SINK is DERIVED: SG_ROW "p4_rbA_re1" -> plan action's dst term_uid (3173) -> base terminal
  (owner_uid, term_name). No uid / terminal-name literal remains (prerun X6 "uids []; names []", diag_c147_a2_1_prerun3.log:109).
- X10: `:55-60` class SGBackend(SX.LVBackend) overrides only read() to KEEP the executor's whole-VI read (no extra read);
  `:72-73` sg_read uses EX["be"].last_terms and requires it to be the read after the LAST op (x.reads_real[-1] == len(x.ops); the
  last op is always a full read, stagexec.py:2385-2390, and run_deferred runs after it, stagexec.py:2491-2493). AT.read_terms no longer called.
- `:103` body: be = EX["be"] = DryPlanBE(dry) | SGBackend(real, same args as LVBackend before).
- check_sink_gates still length 1, sink [23166, 'Pos within cal image'] (diag_c147_a2_1_check3.log:4-5).
- `tools/bench/diag_c147_a2_1_check.py` (-> cfbf0872) stubs the new read source (be.last_terms; AT.read_terms stubbed to RAISE) and adds
  SGB (subclass overrides only read), T6 (read not after last op -> False), T7 (no kept read -> False).

## Runs on the FINAL bytes (each `py tools/bgrun.py --material --max-min N --log <log> -- py -u ...`)
- diag_c147_a2_1_check.py -> RESULT 10/0, rc 0 (diag_c147_a2_1_check3.log:16-17; py_compile both OK :2-3).
- stage_prerun --dry build -> PASS 1/0 rc 0 (diag_c147_a2_1_dry3.log:92-94); --dry scratch -> PASS 1/0 rc 0 (diag_c147_a2_1_scr_dry3.log:114-116).
- stage_prerun --prerun build -> PASS 16/0 rc 0 (diag_c147_a2_1_prerun3.log:118-120); X10 PASS peak 679.3 MB vs fail 680.0, R 8
  (source reads census_snapshot@38x2 + Executor 6) (:112-114).
- stage_prerun --prerun scratch -> PASS 16/0 rc 0 (diag_c147_a2_1_scr_prerun3.log:140-142).
- stage_prerun --scratch-required build -> rc 3 as expected (CENSUS-UNPREDICTED rows 1..25; diag_c147_a2_1_scrreq3.log).
- Untouched: stagexec 1bab9cf9, gscript 1a80236e, stage_prerun 61d6f590, plan cfbd9823, _in db72d8af, _pred c4a6a35a, _licence 7dce79aa,
  memory_model 88eeb037. No LabVIEW process (tasklist count 0).

---
(card 147-a1-6's facts, kept verbatim)
# Facts - card 147-a1-6 (ONE recipe sink gate for s06, PD355(b))

## Recipe bytes (this card changed NOTHING; both files are as the killed card 147-a2-1 left them)
- No git baseline: both recipes are UNTRACKED (`git status`: `?? tools/recipes/stage_d1_ring_p4_s06v18*.py`), so "diff vs HEAD" is empty.
  Baseline used instead = brief items 1-6 + `tools/bench/diag_c147_a2_1_check.log` (the killed card's own md5 trail 27b96525 -> 26f486bf -> 7e0edcf8).
- Build recipe md5 7e0edcf8f2a8d50e73f35bc8d29eeb65 (was 41ad9d35 before 147-a2-1). Lines added by 147-a2-1: 16 (docstring), 17 (SG in PREDICTION),
  22/24 (imports copy, allterms AT), 38-72 (SINK, SG_GATE, SG_TERMS, SG_ACTS, SG_SRC_NAME, EX, sg_read, SINK_GATES, SINK_FNS), 82-85 (SG gate),
  86 (LVBackend gets sink_gates/gates), 87-88 (EX x/s). Kept by this card: all.
- Scratch recipe md5 31009bfce0c0487b0600359c3dac2bd0 (was 8554bdd6). Lines added: 31-32 (import-time check_sink_gates + assert), 79 (prints SG). Kept: all.

## Item 1-3, 5 - present and checked
- Build declares ONE sink gate: `stage_d1_ring_p4_s06v18.py:71` SINK_GATES=[{gate SG-p4_rbA_re1-pos-within-cal-image, sink [23166,'Pos within cal image']}], :72 SINK_FNS, :86 passed to LVBackend.
- Scratch asserts the same ONE at import: `stage_d1_ring_p4_s06v18_scratch.py:31-32` (len(SG)==1==len(R.SINK_GATES), sink == R.SINK); it runs R.body (:80) which hands R's pair to LVBackend.
- check_sink_gates (stagexec.py:2734) on the pair -> `[{"gate": "SG-p4_rbA_re1-pos-within-cal-image", "sink": [23166, "Pos within cal image"]}]` length 1 (diag_c147_a2_1_check2.log).
- Entry handed to the callable (read, not inferred): stagexec.py:2985-2987 {gate, sink=[rd owner_uid, rd term_name], tag, err, source=[rs owner_uid, rs term_name]};
  called once per deferred entry by run_deferred (stagexec.py:2782-2789) at the end of Executor.run (stagexec.py:2491-2493). Op 21 (acts [25]) is the LAST op, so "after op 21" == end of run.
- sg_read readbacks (`stage_d1_ring_p4_s06v18.py:49-68`, uids through x.bind term/obj): (a) indicator t3173 has exactly one row, wired, owner/name == entry sink;
  (b) source t5171 #5058 'pos in cal image out' one row on the SAME wire, entry source == [#5058 bound, name]; (c) sources on that wire == [t5171] only. Detail string carries all three.
- `py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c147_a2_1_check2.log -- py -u tools/bench/diag_c147_a2_1_check.py` -> RESULT 7/0, rc 0 (T1 good True; T2 unwired, T3 other net, T4 2nd source, T5 entry source differs -> False).

## Item 4 - offline runs on these FINAL bytes (each under `py tools/bgrun.py --material --max-min N --log <log> -- py -u ...`)
- py_compile both: OK (check2.log lines 3-4).
- `tools/stage_prerun.py --dry tools/recipes/stage_d1_ring_p4_s06v18.py` -> PASS 1/0, rc 0 (diag_c147_a2_1_dry.log).
- `tools/stage_prerun.py --dry tools/recipes/stage_d1_ring_p4_s06v18_scratch.py` -> PASS 1/0, rc 0 (diag_c147_a2_1_scr_dry.log).
- `tools/stage_prerun.py --prerun tools/recipes/stage_d1_ring_p4_s06v18.py` -> **FAIL 14/2, rc 1** (diag_c147_a2_1_prerun.log:108,113,117):
  - X6 ast lint: no re-typed uid / terminal name: uids [(23166, 41)]; names [('Pos within cal image', 41)] - the SINK literal at recipe line 41.
  - X10 UNMEASURED: "script whole-VI read count not bounded from the source (read_terms line 72: function sg_read used as a value (call count not offline))"; Executor-only peak 674.2 MB vs fail 680.0.
  - (147-a1-3's prerun of the pre-edit bytes was 16/0, prep_c147_a1_3_prerun.log:116 - both fails come from the sink-gate edit.)
- `tools/stage_prerun.py --prerun tools/recipes/stage_d1_ring_p4_s06v18_scratch.py` -> PASS 16/0, rc 0 (diag_c147_a2_1_scr_prerun.log).
- `tools/stage_prerun.py --scratch-required tools/recipes/stage_d1_ring_p4_s06v18.py` -> rc 3 as expected (CENSUS-UNPREDICTED rows 1..25; diag_c147_a2_1_scrreq.log).
- `--el-advisory-selftest` NOT run: returned at the first failed prediction (card chat-P2 rule).

## Untouched (md5 after == card inputs)
stagexec.py 1bab9cf9, gscript.py 1a80236e, plan_ring_p4_s06v18.json cfbd9823, _in.json db72d8af, _pred.json c4a6a35a, memory_model.json 88eeb037. No LabVIEW process (tasklist count 0).

OPEN: X6 vs brief item 2 ("not through typed numbers beyond the [23166,...] sink the plan names") - derive SINK from the plan row p4_rbA_re1 + base terminals, or release X6? 
OPEN: X10 - sg_read's one whole-VI read_terms is unbounded for the memory model (674.2 of 680 MB); reuse the executor's final read, declare a bound, or accept?
