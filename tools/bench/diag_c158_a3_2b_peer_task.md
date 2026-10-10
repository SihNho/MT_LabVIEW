ATTACK this claim (failed prediction, card 158-a3-2b; log tools/bench/diag_c158_a3_2b_el.log, script tools/bench/diag_c149_a1_2_elrun.py).

FACTS
- The P5-2 step-1 scratch (tools/bench/diag_c158_p5s02a_scratch.log) PASSED 23/0: E1 diff 0 at checkpoints 0,1,3,6,8,9,12,15,16,17; D pairs 21 == sim 21;
  CEN2 measured == declared; PB PASS with 2 RECORDED tag-only rows. Adopted claudeDev\D1_ring_p5s02a_20261010_023239.vi md5 94ffff94 (ExecState 0 by design,
  an in-between file: plan_ring_p5s02r_in.json actions 24..80 are owed by later steps).
- Final Error List read of that file: 56 items (tools/bench/errorlist_D1_ring_p5s02a_20261010_023239_20261010_024108.json); compared against the P5-1 expected
  (errorlist_expected_D1_ring_p5s01_20261009_124542.json, 45): extra 11, missing 0, verdict MISMATCH, rc 1. The step-1 pred (plan_ring_p5s02a_pred.json)
  predicted 47 (per class input 3, not-connected 22, loose-ends 21, two-types 1).
- Reason counts P5-1 (45) -> P5-2a (56): 'connects data sinks but has no source' 0 -> 5; 'not connected to anything' 22 -> 23; loose ends 21 -> 23;
  'Loop Tunnel: wire connected to an undirected tunnel' 0 -> 2; 'connected an input of While Loop to an input of SubVI' 0 -> 1; unwired input 1 -> 1; two types 1 -> 1.
- The brief (tools/bench/cards/brief_156-a2-1.md:41-44) says the Error List is NON-GATING (PD354, PD370(a)): another count is reported and the expected file
  is written from what was read.

CLAIM
The 11 extra items are the in-between file's by-design open rows - the inputs of #376 moved into the new Case #31308 (frame f0) whose sources still sit outside
the case (in-tunnels t_in3 / t_gi / t_hi and out-tunnels t_go / t_ho, plan_ring_p5s02r_in.json actions 24-40, plus frame index A48) - not a defect of the
step-1 build; the pred's 47 under-counted because elrule has no tunnel class and does not model a move_in that leaves sink-only wires (docs/d1/ring-p5.md:163).

Discriminating test to propose: which file / rows would show an extra item that is NOT explained by an owed step-2 action?
