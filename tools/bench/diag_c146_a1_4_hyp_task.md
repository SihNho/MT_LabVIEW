ATTACK this claim about a failed prediction (card 146-a1-4, Error List read of the P4 session-5 scratch work copy).

Runs: scratch tools/recipes/stage_d1_ring_p4_s05v18_scratch.py (plan tools/bench/plan_ring_p4_s05v18.json, 21 actions / 17 ops) ->
log tools/bench/diag_c145_p4s05v18_scratch.log, BGRUN END rc=0, RESULT 22/0: E1 every checkpoint real == sim (:284), D new wires 11 == sim 11,
lost 1 == 1 (:287), TD PASS (:292), PB cdiff == pred 16 rows / 11 open pairs (:294), PRIM PASS on the 3 Index Arrays (:158,:219,:280).
Saved work copy claudeDev\D1_ring_p4s05_20261008_002621.vi md5 3f9ac26b (ExecState 0 by design).
Then tools/errorlist_check.py --role final against tools/bench/errorlist_expected_D1_ring_p4s04_20261007_215031.json (s04's file, 58)
-> log tools/bench/diag_c146_a1_4_el.log rc=1; read file tools/bench/errorlist_D1_ring_p4s05_20261008_002621_20261008_003324.json.

Prediction: Error List 57 (tools/bench/plan_ring_p4_s05v18_pred.json `errorlist`, lines 78-140, by tools/elrule.py): base 58 + new
[input -32 (p4_ia_frameidx), local -30 (p4_lr_frameidx)] - closed [local 30001, sr 29403, sr 29648].
Observation: 55 items == window N 55, every item double-clicked, extra 0, missing 3 vs the s04 file (tools/bench/diag_c146_a1_4_elfacts.log):
  - s04 entry 0 "SubVI 'Track N beads four-fold over-kernel-v3.vi': required input 'Image In' is not wired" (count 1): matched 0
  - s04 entry 11 "Shift Register: unwired from inside the loop" #29403/#29648 (count 2): matched 0  (predicted closed)
  - Index Array 'Contains unwired or bad terminal': 3 read (s04 had 3; the pred adds input -32 -> 4 expected)
  - Local variable rows: 2 read (pred: 30001 closed, -30 new, 30016 open -> 2)  == prediction
So the read differs from the prediction by 2: the 'Image In' item is gone (s05 contains connect row `p4_w_img_trk`), and one Index Array
item fewer than predicted.

CLAIM (to attack): the build is right and the PREDICTION is wrong. Because every structural gate passed (real graph == simulated end at all
9 checkpoints), the 55 is the true Error List of the planned end, and the 2-item gap comes from tools/elrule.py's derivation:
(1) it does not count the subVI required-input item ('Image In' on #5058, an open row of the s04 base, wired by `p4_w_img_trk`) as closed,
and (2) its Index Array 'input' class count for this session is off by one (either -32 does not raise an item, or an s04 Index Array
#29843 / #29879 / #30002 stopped raising one because an s05 row wired it). No stage tool and no plan row is wrong.

Already ruled out: OCR loss (items 55 == window N 55, all double-clicked); a different file (bed md5 unchanged, scratch identical=True);
memory (peak 607.7 MB vs stop 680).

Give: the strongest reason the claim is wrong; an alternative explanation (e.g. the Error List hides a subVI's required-input error
behind another error on the same node; an item class merged by LabVIEW when two errors sit on one node; the s04 expected file's
entry 0 was itself mis-attributed); what would falsify the claim; the cheapest discriminating test, offline if possible (e.g. read
tools/elrule.py's closure rule for subVI inputs, the plan rows whose dst is #5058 or an s04 Index Array, and the simulated end step file
tools/bench/sim/ring_p4_s05v18/ for the unwired inputs of the six Index Arrays #29843 #29879 #30002 and the three s05 ones).
