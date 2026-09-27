ATTACK this claim (card 113-2 P5, failed prediction in tools/bench/stage_d1_l2b2b.log, script tools/recipes/stage_d1_l2b2b.py).

PREDICTION that failed: the ONE launch of the 9-row L2-B2b plan (tools/bench/plan_l2b2b.json, base tools/bench/graph_l2b2a_20260928.json =
the saved B2a bed claudeDev\D1_l2_b2a_20260928_001426.vi) ends with cdiff(S1, real end) == the plan's 15 open_rows up to rule D4 (gate PB,
tools/recipes/stage_d1_l2b2b.py:88-91; D4 = tools/stagekit.py:1298 d4_pb, scope tools/bench/plan_l2b2b_d4.json). The simulation said row b2_03
(#11363 LoopTunnel outer face t11369 -> BuildArray #11261 sink t11270 'array', route 'nested') CLOSES the pair (11261, 'array').

OBSERVED (stage_d1_l2b2b.log):
 - all 9 ops ran, err '' each; E1 PASS: checkpoints 4, 8, 9 real graph == simulated step (terminal/edge compare, diff 0) (log STEPX 04/08/09);
 - b2_03's op readback at wiring time: {'UID': 11261, 'Name': 'array', 'UID 2': 0, 'Is Broken?': False} (log:83);
 - CT, D (6 new wires, 0 base wires lost) and FU gates PASS;
 - PB FAIL: bad = [('new-pair', (11261, 'array'))]; CDIFF ROWS (log:187-189):
     #11261 'array'      S1 ['11310|Terminal|output cluster|0']   real end None   (no terminal of that name)
     #11261 'element'    S1 ['11608|Terminal|output cluster|0']   real end ['11310|Terminal|output cluster|0']
     #11261 'element'[1] S1 None                                   real end []
 - nothing saved (PB is fatal before save), input md5 unchanged, LabVIEW gone.

CLAIM (my explanation): LabVIEW RENAMED BuildArray #11261's input t11270 from 'array' to 'element' after the wire landed, because the value
arriving through LoopTunnel #11363's outer face is a single cluster (the S1 path from #11310 reaches #11261 through an auto-indexing tunnel,
giving an array of clusters; in the bed #11363 is not indexing the same way, or its inner side is not yet fed as in S1), i.e. a type-propagation
effect the simulator does not model, and the real end therefore differs from S1 in DATA TYPE at #11261 - a rule-1a question, not a tool bug.
The cdiff's 'element' / 'element'[1] rows are the k-th-name keying shifting after the rename.

Question: is the claim wrong? Alternatives to weigh: (a) the wire landed on the wrong BuildArray input (t11270 vs the other input); (b) cdiff
keying artefact only (terminal names in the real read vs the graph dump's names) with no real type change; (c) #11363's tunnel mode matches S1
and the rename comes from something else upstream (an open row from B2a feeding the tunnel's inner side). Use the files: the bed graph
tools/bench/graph_l2b2a_20260928.json, S1 docs/wiki/subvi/D1_s1_copy.json, the plan, the log. What is the cheapest discriminating test (offline
first; a live read only on a byte copy of the bed)? Do NOT propose the design; I only report.
