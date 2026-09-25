FAILED PREDICTION (card 81-7, stage L2-A1, first LabVIEW run): tools/bench/stage_d1_l2a1.log:302.

Prediction: stagexec E1. Each of the 42 real ops matches its simulated step, and every plan end is addressable. The dry run and stage_prerun X1-X7 PASSED on the same recipe (tools/bench/prerun_l2a1_81c.log).

Observed: ops 1-17 had diff 0 (log:35-301). Op 18 is `sr1_L0`: wire_sr LeftIn, sink `{"uid":5825,"term_uid":5883}` (tools/bench/sim/l2a1/plan_l2a1.json, action 18). It stopped with `ADDRESS: node #5825 not in Diagram[21] (#23166).Nodes[]`. #5825 is a SelectorTunnel on moved CaseStructure #5540. At base, PRIME could not prove #5825, #5702, #2886 or #5818 (log:36), and gave the same "not in Diagram.Nodes[]" reason for each.

Hypothesis H1: stagexec.Addr._triple (tools/stagexec.py:344-398) addresses a terminal by V.node_of(row) in Diagram.Nodes[]. For a SelectorTunnel (and a FlatSequenceInnerTunnel) that node is the tunnel, and the real LVReader.node_uids (gscript.node_labels, stagexec.py:583) does not list border tunnels. The DRY SimReader (stagexec.py:782-792) DOES list them, and that is why dry and pre-run passed. So this is a reader/addressing gap in our tool, not a plan or model error. Every stagexec sink that is a structure-border tunnel terminal will hit it: sr1_L0 (#5825), sr2_L0 (#5702), sr3_L0 (#10750), tun1_in (#5725) and tun2_in (#5967).

Already ruled out: the graph state is not the cause. Step 17's diff was 0, and the base read matched step_00 (log:35). The launch gate and the prior-art review passed on this sha. The bed D1_k is unchanged (H2 PASS).

Refute H1. Name an alternative explanation, say what would falsify H1, and give the cheapest discriminating test. The test must need no second LabVIEW run of the stage (retry cap). For example: does gscript/stagekit already address a tunnel terminal by its owner structure (e.g. the L7 stages that wired tunnel inner/outer faces, stage_d1_l7_1b.py / stage_d1_l7_r.py, build_opconnectfromwire_v0, OpFsInnerTunnelConnect_v1)?
