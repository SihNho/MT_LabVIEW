ATTACK this claim (card 101-5, log tools/bench/diag_c101c_resim.log, script tools/bench/diag_c101c_resim.py):

CLAIM UNDER TEST (the card's pre-decided rule, task_101-5.json pass[1]): "in stagesim's move_in model, a CUT wire whose ONLY
source sat on the moved node and whose one other terminal is an outside sink is DELETED when the moved node is a PRIMITIVE
node, and KEPT as a sourceless half-wire when it is a SubVI" - i.e. the fate is decided by the SOURCE node's class.

WHAT THE OFFLINE REPLAY MEASURED (tools/bench/diag_c101c_resim.log:21-60, against the REAL reads of run r5,
tools/bench/stage_d1_disp_r5.log, record tools/bench/stage_d1_disp.json, real reads at k 2,3,4,5,12,24,25):
- With the source-class rule, the simulation diverges from the REAL reads at k24 and k25: the sim drops the half-wire on
  ControlTerminal #8323 ('Force (pN) vs Extension (nm) ', owner Diagram #639) after BuildArray #11261 moved, but LabVIEW KEPT
  it (r5 k24/k25 real == the OLD 'keep' model, diff 0; stage_d1_disp_r5.log:440,448).
- At k12 the source-class rule also removed edge [11369 -> 11270] (LoopTunnel #11363 OUTER -> BuildArray #11261 'array') and
  dangled 11270/11369, which the real read did NOT show (real diff at k12 was ONLY dangling_sim_only [11365]).
- The ONE case where LabVIEW did delete the half-wire: Bundler #11310 (primitive) moved; its 'output cluster' 11316 was the only
  source of w11374 whose other terminal was LoopTunnel #11363 INNER 11365 (InnerTerminal, sink). Real: 11365 read wire 0
  (stage_d1_disp_r5.log:249).
- Cases where LabVIEW KEPT the half-wire on the outside sink after a primitive/SubVI moved (all sinks are NODE or panel
  terminals, none a tunnel): Function #8764 'x' 8790 (ParameterTerminal), PolymorphicSubVI #28233 'X' 28291, SubVI #29009 'X'
  29049, Function #27716 'array' 27827, Bundler 'element' 11323, ControlTerminal 8323 - real reads k24/k25 kept 8323 dangling;
  k6-k11 had no real read (checkpoints only), the OLD keep-model's k12 real read showed no diff on them.
- Earlier measured keep case: SubVI #376 move left 1931 on w5274 and 5044 on w5056 (tools/bench/diag_c71_l7_1a_tunnels.log:60,64,70).
- Earlier measured delete case: DigitalNumericConstant #8775 -> sink 8753 of #8741 (stage_d1_disp_r4.log:89-90).

MY (NEW, UNMEASURED) EXPLANATION TO ATTACK: the fate is decided by the outside SINK's terminal class, not the source's class -
a LoopTunnel InnerTerminal left sourceless loses its half-wire (LabVIEW removes a wire that would leave a tunnel with a
one-ended wire inside the loop), while a node / panel terminal keeps it. The constant case would then be a separate rule
(constant source -> delete) that already replays correctly.

Give: (1) the strongest reason this sink-class explanation is wrong; (2) an alternative that ALSO fits all six facts
above (e.g. wire crossing a structure border at the moment of the cut; the move's destination diagram being the tunnel's
own loop; the junk-purge deleting the wire); (3) what would falsify each; (4) the cheapest discriminating test that
needs at most ONE LabVIEW read of the existing r5 scratch behaviour or none (offline over the r5 record / step files:
tools/bench/sim/disp/step_NN_*.json terminals; the graph tools/bench/par1359_95_graph.json).
Do not propose modifying any original .vi. Read-only.
