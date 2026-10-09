---
type: facts
status: current
date: 2026-10-09
card: 157-a1-4
---
# Card 157-a1-4 facts: planned X10 at cuts 20 / 23 / 26 with the current checkpoint rule; fp-76 closed; LabVIEW 0
## Method: `prep_c157_a1_4_cut.py` cd460ccc, log `prep_c157_a1_4_cut.log` RESULT 7/0 (:21), BGRUN END rc=0 after 12 s (:22)
- Calls stagexec.compile_plan (stagexec.py:803), stagexec.checkpoint_ops (stagexec.py:2028 = RingSession.CHECKPOINTS, stagekit.py:1929),
  stage_prerun.x10_model_peak (stage_prerun.py:2096, Executor-only) and stage_prerun.x10_gate (stage_prerun.py:2548, MAIN = Executor + 2 recipe source reads, :2608-2611).
- Cut = the all-plan's action list 1..k, every other key copied. Start 603.4 = 597.5 + op-0 read 5.9 (:5). Group ends read from prep_c156_a1_1_session.json (:4).
- Control: the stored plan_ring_p5s02a.json gives MAIN 679.7 R 14 / Executor 674.6 R 12 (:5-6) = diag_c157_a1_2_prerun.log:99-100; its cut copy cut23 compiles to the same 17 ops and meter (:10).
## Per cut (log lines)
| cut | group | ops | checkpoints | Executor-only MB (R) | MAIN MB (R) | last group: ops in it | group split |
|---|---|---|---|---|---|---|---|
| 20 | F1 (18..20) | 16 | 0,1,3,6,8,9,10,11,12,15,16 | 670.7 (11) | 675.8 (13) | op 16 tunnel acts 18-20 | no (:11-13) |
| 23 | F2 (21..23) | 17 | 0,1,3,6,8,9,10,11,12,15,16,17 | 674.6 (12) | 679.7 (14) | op 17 tunnel acts 21-23 | no (:7-9) |
| 26 | F3 (24..26) | 18 | 0,1,3,6,8,9,10,11,12,15,16,17,18 | 678.5 (13) | 683.6 (15) | op 18 tunnel acts 24-26 | no (:14-16) |
- Op kinds 1..18: add_sr, connect, create, wire_sr, wire_sr, create, connect, create, create, move_in x3 (ops 10-12), connect x2, tunnel x4 (ops 15-18) (:15).
  Ops 15, 16, 17 are all `tunnel` (one per group E / F1 / F2); cut 20 holds ops 15-16, not op 17. The compiled ops carry no cfw kind.
- Model limit fail_above 680.0 (:13, :16); card limit 675 (PD379(c)). Cut 26 MAIN 683.6 is above 680; cut 20 MAIN 675.8 is above 675 by 0.8.
## 23-action plan without move_in checkpoints (log :17-20; one whole-VI read = read_mb 2.53 MB, diag_c129_6_mem.log:55)
- without {12}: MAIN 677.2 R 13 (-2.5); without {11,12}: MAIN 674.7 R 12 (-5.0); without {10,11,12}: MAIN 672.1 R 11 (-7.6) = the old 672.1.
## Files written (only under tools/bench/sim/ring_p5s02a_c157/)
- cut20/plan_ring_p5s02a_cut20.json 296bac9a; cut23/plan_ring_p5s02a_cut23.json 29e73449; cut26/plan_ring_p5s02a_cut26.json a4c19ccb (input action lists, not simulated/finalized).
## fp-76 closed (tools/bench/gate_fp_queue.jsonl:76)
- status "closed", closed_iso 2026-10-09 19:50:34, close_reason: "Not a false positive: the launch gate was correct. Scratch card 156-a2-1 named no
  DRY-UNVERIFIED-OK string although the dry's PB gate is PASS-UNVERIFIED (tools/bench/diag_c156_a2_1_facts.md:19-22); the refusal is the designed one
  (tools/stage_prerun.py:4888-4895). Card omission, not a gate fault (card 157-a1-4)."
- No gate refused the work; no JEV-LADDER row (no failing gate); no stored plan/pred/licence/recipe/stage tool/hook edited; LabVIEW not started.
OPEN: no cut at a group end gives MAIN <= 675 with the current checkpoint rule (20: 675.8, 23: 679.7, 26: 683.6); dropping move_in checkpoint 12 from cut 20 would give 673.3 by the model (675.8 - 2.53) - judgement (PD379(c)/PD381(d)).
OPEN: the brief's "ops 15..17 = tunnel + two cfw of #24360/#24367" does not match the compiled kinds (ops 15-17 are three tunnels) - which ops hold those wires is not read here.
OPEN: the cut plans are action lists only; a step plan at cut 20 still needs the maker's pass A / REALSIM / pred / licence (prep_c156_a1_1_mk.py:443-500 is module-level, no shared cutter).
