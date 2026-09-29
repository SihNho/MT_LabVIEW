**No, the saved VI isn't defective. The card's L4 check was the wrong test for this stage.** The handle growth comes from each tool function's first call, not from a leak.

**The check didn't apply to this stage**
- L4 asks for "handles +-100" (`tools/bench/cards/task_119-4.json:32`). That rule is meant for 20 repeated calls of one function (`CLAUDE.md:224-225`).
- Pre-decided 176(a) says this rule "does not apply to an editing stage". There, handles are "RECORDED, not gated", and a leak is judged only by the 20-call test (`docs/d1-loop12-17-split-plan.md:458-462`).
- The recipe only recorded the handle numbers (`stage_d1_qrt_pool.log:233`) and passed 21/0 (`:260`).
- R2's flat handle count (`stage_d1_l2r2.log:298-299`) came from a stage that only deleted objects (`:34`). It is not a fair comparison.

**The growth only happens on first calls**
- Repeat calls add about 0 handles:
  - create_primitive_nested: +79 / +0 / +0 (`stage_d1_qrt_pool.log:78,87,96`)
  - queue_node obtain: +27 / +2 (`:115,134`)
  - wire_const: +33 / +1 / +0 (`:160,168,197`)
- The +322 is almost all first calls after k1: +35 (`:68`), +79, +27, +29 (`:152`), +33, +58 (`:189`) and +75 (`:217`), which sum to 336. Hygiene tests skip call 0 because it includes loading the VI (`tools/bench/s0_hygiene_probe.py:62`).
- The size is normal:
  - Earlier editing stages that passed recorded +597 (`stage_d1_disp_c104B3.log:316`) and +482 (`stage_d1_l7_r_r2.log:458`).
  - After the panel closed (`tools/stagekit.py:1129-1139`), this run read 34139 (`stage_d1_qrt_pool.log:247`). Passing stages read 34128 and 34146 at the same point (`stage_d1_k_r2.log:556`, `stage_d1_l7_1b_r3.log:364`).
- The saved VI is never run (`stage_d1_qrt_pool.log:237`).

**The most plausible alternative: a leak inside a tool function, on every call**
- The 9/9 reference count can't rule this out: that counter "CANNOT see refnum-class exhaustion inside an op VI" (`tools/gscript.py:326-331`).
- The read functions are already cleared by 2,000-call records with a flat handle count (`tools/bench/op_hygiene/OpConstValueArr_v0.json:7-11`, `OpConstValueRing_v0.json:7-11`).
- The two connect functions ran only once here, but an earlier log repeats both:
  - connect_from_wire: +91, then +2 / −1 / 0 / −1 / +1 / 0 (`stage_d1_l2a1_86-5.log:332,373,414,447,467,487,506`)
  - connect_nested_v1: +27, then +4 / −4 / +1 / 0 (`:533,553,573,614,634`)
- Three calls still have no repeat data: drop_subvi (+35), enqueue (+29) and loop_in (+85, `stage_d1_qrt_pool.log:50`).

ROOT CAUSE: Card L4 applied the ±100 repeated-call rule, which Pre-decided 176(a) retired for editing stages, to a stage that creates objects using seven tool functions mostly called once, so the +322/+648 is one-time load and new-object growth in the LabVIEW editing process, not a leak in the saved VI, which is never run.
TEST: Without launching LabVIEW, list the handle change for each tool function by call number from this log and `stage_d1_l2a1_86-5.log` (a leak shows the same increase on every repeat call, load cost only on the first, which five functions already show), and only for drop_subvi, enqueue and loop_in run 176(a)'s 20-call test on a scratch copy, counting from call 1.