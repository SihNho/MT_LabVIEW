ATTACK this claim about a failed prediction (card 147-a1-4, the ONE scratch run of RING P4 v18 session 6).

Runs: tools/recipes/stage_d1_ring_p4_s06v18_scratch.py (plan tools/bench/plan_ring_p4_s06v18.json, 25 actions / 21 ops, prerun 16/0,
X10 674.2) on a byte copy of claudeDev\D1_ring_p4s05_20261008_002621.vi (3f9ac26b) -> log tools/bench/diag_c147_p4s06v18_scratch.log,
BGRUN END rc=1, RESULT 12/2. Ops 1..20 ran (PRIM PASS on the created Index Array #30300, :245). Stopped IN op 21 (the LAST op).

Prediction: every op real == simulated; op 21 `p4_rbA_re1` (plan :377-388) wires #5058 SubVI 'pos in cal image out' (t5171) to indicator
'Pos within cal image' t3173, after op 19 `p4_rbA_dw` deleted w23807 (plan :357-362, the wire on t5171) and op 20 `p4_rbA_re0` (plan :363-375)
wired t5171 -> #10969 'array' t10975.
Observation (log lines):
  - :275-281 delete_wire w23807 -> err '' ; census 688 -> 688.
  - :283 op 20 STALE-ADDRESS: #10975 'array' on #10969 had 0 (name,dir,wire) matches in [('array', False, 0), ...] -> fresh read + one retry.
  - :286 op 20 readback {'UID': 10969, 'Name': 'array', 'UID 2': 0, 'Is Broken?': False}; :288 connect_nested_v1 err ''.
  - :294 op 21 STALE-ADDRESS: #5171 'pos in cal image out' on #5058: 0 (name,dir,wire) matches (list truncated in the log) -> retry.
  - :297-298 wire_indicators N[26] ['pos in cal image out'] -> ['Pos within cal image'] raised RuntimeError: "target BROKEN after wiring -
    a source terminal was probably unwired (WI then extends an unrelated wire; revert the target)".
  - :302-309 work copy saved (gui_save) claudeDev\D1_ring_p4s06_20261008_020717.vi md5 b58046e3, ExecState 0; resume record
    tools/bench/resume/resume_plan_ring_p4_s06v18_20261008_021435.json (from_step 20). Peak 618.7 MB; H2/H3/H5/H6 PASS; LabVIEW gone.

CLAIM (to attack): the plan and the simulator are right and op 21 failed because op 20 did NOT actually wire t5171 -> t10975: the readback
'UID 2': 0 at :286 shows the 'array' input still without a wire after connect_nested_v1 returned err '', so after delete_wire w23807 the
source t5171 had no wire at all and gscript.wire_indicators (which needs a wired source to extend) wired into nothing and broke the target.
I.e. a silent decline of connect_nested_v1 on a source whose only wire was just deleted (a tool fault in the connect route, not a plan fault).

Already ruled out: memory (peak 618.7 vs stop 680); input changed (3f9ac26b unchanged, H2); reference leak (opened 22 == closed 22).

Give: the strongest reason the claim is wrong; an alternative explanation (e.g. 'UID 2' in the readback is not a wire uid; delete_wire
removed more than w23807 or left t5171's terminal re-numbered so the address #5171 went stale; wire_indicators cannot take a source that
already feeds another sink; the simulator's route for re1 should have been connect, not wire_indicators); what would falsify the claim; the
cheapest discriminating test, offline if possible (the scratch json tools/bench/diag_c147_p4s06v18_scratch.json, the sim step files
tools/bench/sim/ring_p4_s06v18/step_23_delete_wire.json / step_24_wire.json / the step for re1, gscript.wire_indicators and the
connect_nested_v1 readback code in tools/gscript.py / tools/stagexec.py), else the smallest scratch-VI check.
