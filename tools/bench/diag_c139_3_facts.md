---
type: facts
status: current
date: 2026-10-02
tags: [card-139-3, loop_in, for-loop, donor, boolean-constant, scratch-verify]
---
# Card 139-3 facts (LabVIEW, scratch only; bed never opened, a byte copy used as Greater?/AMM donor as in 139-1)
Run `tools/bench/diag_c139_3_run.py` -> `tools/bench/diag_c139_3_run.log` (BGRUN END rc=0 after 84 s, 38 pass / 0 fail).
Out JSON `tools/bench/diag_c139_3_out.json`; record `tools/bench/scratch_verify/for_group_c139_3_190704.json` (status PASS).
LabVIEW gone, 2 scratch files deleted, bed md5 unchanged (log, last gates).
## 1. DonorBoolF_v0.vi (claudeDev, md5 2346e9d83a1caf8f29a9cc594178b247)
- EMPTY_v0 copy + While #43 + `create_const_loop_term("while_cond", 0, value=False)`: exactly one new constant **#126**,
  `read_const_value` -> cls BooleanConstant, value False, err '' (route OpConstValueB_v0); ExecState 1; saved by script.
- Use as `const_donor` with `{"donor": DonorBoolF_v0.vi, "uid": 126}`. The donor's While loops forever if run - never run it.
## 2. loop_in with a SubVI present (the 139-1 B blocker)
- One unwired DonorI32Max_v0 SubVI (#43) dropped on the top level (`gscript.drop_subvi`, diagram index 0).
- `g.loop_in("for", TGT, <While body index>, (250,150))` (stagexec.py:2653 form, all defaults) -> returned ForLoop #47,
  exactly one new Diagram #271, **zero LoopTunnels added** (Names=[] -> no tunnels from the SubVI; answers 139-1 facts :31-32).
- So 139-1's error 1055 is removed by a SubVI existing at Traverse SubVI[0]: the reviewer's "Arm A" discriminator
  (`archive/peer/2026-10-02-c139-3-hyp-c139-1.md:78`) succeeded; the Diagram-index alternative is not supported here.
- The SubVI shows 12 unwired, non-required terminal rows; it did not break ExecState.
## 3. For group inside the While body (as 139-1 pass 1)
- Nodes: GT #319 Greater? and AMM #338 in While body #238; SW #365 Select and KMX #499 (DonorI32Max uid 127) in FMN body #271.
- 6 wires by `connect_term_uid`, every one err '' and broken False; Num control (I32[20]) on GH.x, `y` control on GT.y,
  `min value` indicator on AMM.
- FMN tunnels: #427, #430 (in, I32[20] and Bool[20]) and #454 (out), IndexMode 1 each; While in-tunnel #386 IndexMode 0;
  generator For out-tunnel #628 IndexMode 1.
- Wire.Is Broken? False on all 14 wires; ExecState 1.
## 4. Runs (Num = [-1,5,3,9,0,1,2,-7,4,8,6,7,10..17]; `last` control is an ARRAY, set to [last]*20)
- last 2 -> min 3 (1.57 s); last 17 -> 2147483647 (1.60 s). Both as predicted.
- Each run takes ~1.6 s: UNMEASURED cause; DonorI32Max_v0 (the unwired SubVI) holds a For with N = 2147483647, a candidate.
## Peer
- Hypothesis review of the 139-1 failures, `archive/peer/2026-10-02-c139-3-hyp-c139-1.md` (ANSWERED): claim 2 confirmed by
  this run (Arm A); claim 1's gate fix must use `compare()` extra/missing or `norm_ocr`, not whitespace normalisation
  (an "anvthing"/"anything" OCR letter swap survives `norm()`). Its "What was done with it" section is NOT filled
  (outside this card's write flags).
OPEN: the review's "What was done with it" needs a writer with archive/peer write access; and should the bed route keep the
default SubVI source, or should loop_in be given src_cls of a node known to exist (the review's ForLoop-source variant, unrun)?
