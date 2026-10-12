# p6_buildarray - BuildArray census before/after RBW and the #11261 'appended array' path (card 168-a1-1)

Source: `tools/bench/diag_c168_a1_1_ba.py` (offline, vigraph over the stored graphs). Data: `tools/bench/p6_buildarray.json`.
Graphs: before = tools/bench/graph_ring_p5s02e_20261012_173009.json (7815af09), after = tools/bench/graph_ring_p6rbw_20261012_191349.json (c5531708). Type column: the graph stores no terminal type -> `unread`.

## 1. Census (every BuildArray node)

| uid | container (before) | before: unwired inputs | after: unwired inputs | out sinks b/a |
|---|---|---|---|---|
| #2626 | #23166 Diagram < #10170 WhileLoop < #686 Diagram | all wired | all wired | 1/1 |
| #4117 | #3886 Diagram < #3826 CaseStructure < #3667 Diagram < #3593 Sequence | all wired | all wired | 1/1 |
| #5123 | #20774 Diagram < #20548 CaseStructure < #20530 Diagram < #20474 CaseStructure | all wired | all wired | 1/1 |
| #5368 | #5038 Diagram < #3593 Sequence < #3628 Diagram | all wired | all wired | 1/1 |
| #8566 | #7911 Diagram < #1359 ForLoop < #23166 Diagram < #10170 WhileLoop | all wired | all wired | 1/1 |
| #11261 | #23166 Diagram < #10170 WhileLoop < #686 Diagram | t11270 'array', t11273 'element' | t11270 'array', t11273 'element' | 1/0 |
| #14259 | #14037 Diagram | all wired | all wired | 1/1 |
| #15744 | #15683 Diagram < #15649 Sequence < #15622 Diagram < #15544 EventStructure | all wired | all wired | 1/1 |
| #15756 | #15683 Diagram < #15649 Sequence < #15622 Diagram < #15544 EventStructure | all wired | all wired | 1/1 |
| #15874 | #15795 Diagram < #15649 Sequence < #15622 Diagram < #15544 EventStructure | all wired | all wired | 1/1 |
| #17227 | #17020 Diagram | all wired | all wired | 1/1 |
| #21109 | #20774 Diagram < #20548 CaseStructure < #20530 Diagram < #20474 CaseStructure | all wired | all wired | 1/1 |
| #23365 | #22847 Diagram < #22786 ForLoop < #22780 Diagram < #22541 Sequence | all wired | all wired | 1/1 |
| #23899 | #23729 Diagram < #23619 CaseStructure < #22780 Diagram < #22541 Sequence | all wired | all wired | 1/1 |
| #24257 | #24013 Diagram < #23619 CaseStructure < #22780 Diagram < #22541 Sequence | all wired | all wired | 1/1 |
| #24902 | #24449 Diagram < #23619 CaseStructure < #22780 Diagram < #22541 Sequence | all wired | all wired | 1/1 |
| #25992 | #25890 Diagram < #25850 ForLoop < #25769 Diagram | all wired | all wired | 1/1 |
| #27844 | #81548 Diagram | all wired | all wired | 1/1 |
| #29973 | #29894 Diagram < #29874 ForLoop < #23166 Diagram < #10170 WhileLoop | all wired | all wired | 1/1 |

**before**: with an unwired input [11261]; all inputs wired [2626, 4117, 5123, 5368, 8566, 14259, 15744, 15756, 15874, 17227, 21109, 23365, 23899, 24257, 24902, 25992, 27844, 29973].

**after**: with an unwired input [11261]; all inputs wired [2626, 4117, 5123, 5368, 8566, 14259, 15744, 15756, 15874, 17227, 21109, 23365, 23899, 24257, 24902, 25992, 27844, 29973].

### Inputs, per node (after = c5531708)

- #2626 t2813 'appended array' output w31017 type unread: sinks t31012 '' #31000 SelectorTunnel [graph_ring_p6rbw_20261012_191349.json:terminals[1391]]
- #2626 t2832 'element' input w30418 type unread: source t30354 'element' #30300 IndexArray [graph_ring_p6rbw_20261012_191349.json:terminals[1392]]
- #2626 t4160 'element' input w30270 type unread: source t30159 'element' #30119 IndexArray [graph_ring_p6rbw_20261012_191349.json:terminals[1393]]
- #2626 t4165 'element' input w30274 type unread: source t30228 'element' #30216 IndexArray [graph_ring_p6rbw_20261012_191349.json:terminals[1394]]
- #2626 t4168 'array' input w30522 type unread: source t30473 's? t:f' #4594 Function [graph_ring_p6rbw_20261012_191349.json:terminals[1395]]
- #4117 t4123 'appended array' output w32086 type unread: sinks t31433 'Position values' #30804 SubVI [graph_ring_p6rbw_20261012_191349.json:terminals[81]]
- #4117 t4132 'element' input w4381 type unread: source t3860 'If no: current pos z?' #3858 SelectorTunnel [graph_ring_p6rbw_20261012_191349.json:terminals[82]]
- #5123 t25764 'appended array' output w7141 type unread: sinks t21058 'Velocity values' #21046 SubVI [graph_ring_p6rbw_20261012_191349.json:terminals[3019]]
- #5123 t25788 'element' input w60 type unread: source t27209 'element' #7962 IndexArray [graph_ring_p6rbw_20261012_191349.json:terminals[3020]]
- #5368 t5370 'appended array' output w5873 type unread: sinks t5421 'Velocity values' #5403 SubVI [graph_ring_p6rbw_20261012_191349.json:terminals[144]]
- #5368 t5374 'element' input w29859 type unread: source t29467 'Value' #29447 Property [graph_ring_p6rbw_20261012_191349.json:terminals[145]]
- #8566 t8572 'appended array' output w10043 type unread: sinks t8647 'new element/subarray' #8634 GrowableFunction [graph_ring_p6rbw_20261012_191349.json:terminals[1514]]
- #8566 t8575 'element' input w9993 type unread: source t10006 '' #10004 LoopTunnel [graph_ring_p6rbw_20261012_191349.json:terminals[1515]]
- #8566 t8578 'element' input w28732 type unread: source t28092 'Force' #28083 SubVI [graph_ring_p6rbw_20261012_191349.json:terminals[1516]]
- #11261 t11267 'appended array' output w0 type unread: sinks none [graph_ring_p6rbw_20261012_191349.json:terminals[1445]]
- #11261 t11270 'array' input w0 type unread: source none [graph_ring_p6rbw_20261012_191349.json:terminals[1446]]
- #11261 t11273 'element' input w0 type unread: source none [graph_ring_p6rbw_20261012_191349.json:terminals[1447]]
- #14259 t14261 'appended array' output w14424 type unread: sinks t14208 'Velocity values' #14196 SubVI [graph_ring_p6rbw_20261012_191349.json:terminals[3660]]
- #14259 t14264 'element' input w14421 type unread: source t7516 'Trans Speed (mm/s)' #14037 Diagram [graph_ring_p6rbw_20261012_191349.json:terminals[3661]]
- #15744 t15746 'appended array' output w15771 type unread: sinks t15764 'element' #15756 BuildArray [graph_ring_p6rbw_20261012_191349.json:terminals[4679]]
- #15744 t15749 'element' input w15780 type unread: source t15737 'X' #15732 Unbundler [graph_ring_p6rbw_20261012_191349.json:terminals[4680]]
- #15744 t15752 'element' input w15777 type unread: source t15740 'Y' #15732 Unbundler [graph_ring_p6rbw_20261012_191349.json:terminals[4681]]
- #15756 t15758 'appended array' output w15774 type unread: sinks t15664 '' #15662 Tunnel [graph_ring_p6rbw_20261012_191349.json:terminals[4676]]
- #15756 t15761 'array' input w15768 type unread: source t15669 'Array of bead\nx/y pos' #15667 Tunnel [graph_ring_p6rbw_20261012_191349.json:terminals[4677]]
- #15756 t15764 'element' input w15771 type unread: source t15746 'appended array' #15744 BuildArray [graph_ring_p6rbw_20261012_191349.json:terminals[4678]]
- #15874 t15876 'appended array' output w15886 type unread: sinks t15680 '' #15677 Tunnel [graph_ring_p6rbw_20261012_191349.json:terminals[4722]]
- #15874 t15879 'array' input w15889 type unread: source t15675 'exp/ref array' #15672 Tunnel [graph_ring_p6rbw_20261012_191349.json:terminals[4723]]
- #15874 t15882 'element' input w15895 type unread: source t15868 '32bit integer' #15866 Function [graph_ring_p6rbw_20261012_191349.json:terminals[4724]]
- #17227 t17229 'appended array' output w17248 type unread: sinks t17176 'Velocity values' #17164 SubVI [graph_ring_p6rbw_20261012_191349.json:terminals[4395]]
- #17227 t17232 'element' input w17251 type unread: source t28954 'Value' #7462 Property [graph_ring_p6rbw_20261012_191349.json:terminals[4396]]
- #21109 t21111 'appended array' output w558 type unread: sinks t9277 'Position values' #1779 SubVI [graph_ring_p6rbw_20261012_191349.json:terminals[3028]]
- #21109 t21114 'element' input w6492 type unread: source t26811 'element' #2536 IndexArray [graph_ring_p6rbw_20261012_191349.json:terminals[3029]]
- #23365 t23367 'appended array' output w23587 type unread: sinks t22833 '' #22831 RightShiftRegister [graph_ring_p6rbw_20261012_191349.json:terminals[5779]]
- #23365 t23370 'array' input w23584 type unread: source t22837 '' #22835 LeftShiftRegister [graph_ring_p6rbw_20261012_191349.json:terminals[5780]]
- #23365 t23373 'element' input w23593 type unread: source t23188 'radial intensity profile 1' #23119 SubVI [graph_ring_p6rbw_20261012_191349.json:terminals[5781]]
- #23365 t23376 'element' input w23590 type unread: source t23200 'radial intensity profile 2' #23119 SubVI [graph_ring_p6rbw_20261012_191349.json:terminals[5782]]
- #23365 t23379 'element' input w23464 type unread: source t23347 'radial intensity profile 1' #23278 SubVI [graph_ring_p6rbw_20261012_191349.json:terminals[5783]]
- #23365 t23382 'element' input w23461 type unread: source t23359 'radial intensity profile 2' #23278 SubVI [graph_ring_p6rbw_20261012_191349.json:terminals[5784]]
- #23899 t23901 'appended array' output w23998 type unread: sinks t23653 '' #23650 SelectorTunnel [graph_ring_p6rbw_20261012_191349.json:terminals[5399]]
- #23899 t23904 'array' input w24004 type unread: source t23646 '' #23643 SelectorTunnel [graph_ring_p6rbw_20261012_191349.json:terminals[5400]]
- #23899 t23907 'element' input w24001 type unread: source t23881 'radial intensity profile 1' #23812 SubVI [graph_ring_p6rbw_20261012_191349.json:terminals[5401]]
- #24257 t24259 'appended array' output w24434 type unread: sinks t23654 '' #23650 SelectorTunnel [graph_ring_p6rbw_20261012_191349.json:terminals[5487]]
- #24257 t24262 'array' input w24440 type unread: source t23647 '' #23643 SelectorTunnel [graph_ring_p6rbw_20261012_191349.json:terminals[5488]]
- #24257 t24265 'element' input w24437 type unread: source t24239 'radial intensity profile 1' #24170 SubVI [graph_ring_p6rbw_20261012_191349.json:terminals[5489]]
- #24257 t24269 'element' input w24356 type unread: source t24251 'radial intensity profile 2' #24170 SubVI [graph_ring_p6rbw_20261012_191349.json:terminals[5490]]
- #24902 t24904 'appended array' output w25076 type unread: sinks t23655 '' #23650 SelectorTunnel [graph_ring_p6rbw_20261012_191349.json:terminals[5626]]
- #24902 t24907 'array' input w25082 type unread: source t23648 '' #23643 SelectorTunnel [graph_ring_p6rbw_20261012_191349.json:terminals[5627]]
- #24902 t24910 'element' input w25079 type unread: source t24725 'radial intensity profile 1' #24656 SubVI [graph_ring_p6rbw_20261012_191349.json:terminals[5628]]
- #24902 t24913 'element' input w25019 type unread: source t24737 'radial intensity profile 2' #24656 SubVI [graph_ring_p6rbw_20261012_191349.json:terminals[5629]]
- #24902 t24916 'element' input w24959 type unread: source t24884 'radial intensity profile 1' #24815 SubVI [graph_ring_p6rbw_20261012_191349.json:terminals[5630]]
- #25992 t25994 'appended array' output w26007 type unread: sinks t25885 '' #25883 LoopTunnel [graph_ring_p6rbw_20261012_191349.json:terminals[6085]]
- #25992 t25997 'element' input w26016 type unread: source t25977 'Low bandpass' #25968 SubVI [graph_ring_p6rbw_20261012_191349.json:terminals[6086]]
- #25992 t26000 'element' input w26013 type unread: source t25974 'High bandpass' #25968 SubVI [graph_ring_p6rbw_20261012_191349.json:terminals[6087]]
- #25992 t26003 'element' input w26010 type unread: source t25971 'forget radius' #25968 SubVI [graph_ring_p6rbw_20261012_191349.json:terminals[6088]]
- #27844 t27846 'appended array' output w28276 type unread: sinks t27877 '2D array' #27872 Function [graph_ring_p6rbw_20261012_191349.json:terminals[256]]
- #27844 t27849 'array' input w28282 type unread: source t27866 'transposed array' #27864 Function [graph_ring_p6rbw_20261012_191349.json:terminals[257]]
- #27844 t27852 'element' input w28273 type unread: source t27825 'initialized array' #27820 GrowableFunction [graph_ring_p6rbw_20261012_191349.json:terminals[258]]
- #29973 t29693 'element' input w30636 type unread: source t30140 '' #30135 LoopTunnel [graph_ring_p6rbw_20261012_191349.json:terminals[1424]]
- #29973 t29980 'appended array' output w30241 type unread: sinks t29637 'new element/subarray' #29625 GrowableFunction [graph_ring_p6rbw_20261012_191349.json:terminals[1422]]
- #29973 t29989 'element' input w29766 type unread: source t29779 '' #29777 LoopTunnel [graph_ring_p6rbw_20261012_191349.json:terminals[1423]]

## 2. #11261 terminals

- before: t11267 'appended array' w25618 -> ["t8323 'Force (pN) vs Extension (nm) ' #23166 Diagram/ControlTerminal"] [graph_ring_p5s02e_20261012_173009.json:terminals[1445]]
- before: t11270 'array' w0 -> nothing [graph_ring_p5s02e_20261012_173009.json:terminals[1446]]
- before: t11273 'element' w0 -> nothing [graph_ring_p5s02e_20261012_173009.json:terminals[1447]]
- after: t11267 'appended array' w0 -> nothing [graph_ring_p6rbw_20261012_191349.json:terminals[1445]]
- after: t11270 'array' w0 -> nothing [graph_ring_p6rbw_20261012_191349.json:terminals[1446]]
- after: t11273 'element' w0 -> nothing [graph_ring_p6rbw_20261012_191349.json:terminals[1447]]

## 3. t11267 downstream (vigraph.build4 + reach4/path)

- **before**: reached 1 terminal(s); overall class **display-only**.
  - leaf class display-only; chain: t11267 #11261 BuildArray 'appended array' [graph_ring_p5s02e_20261012_173009.json:terminals[1445]] -> t8323 #23166 ControlTerminal 'Force (pN) vs Extension (nm) ' [graph_ring_p5s02e_20261012_173009.json:terminals[1700]]; edges ['wire']
  - rows with the leaf's label: ['t8323 #23166 Diagram/ControlTerminal src=False w25618']
- **after**: reached 0 terminal(s); overall class **none-reached**.
  - rows with the leaf's label: []

## 4. Delete prediction (c5531708)

Wires attached to #11261: none. Wire objects now 2066; expected after deleting #11261: **2066** (objs class Wire count of graph_ring_p6rbw_20261012_191349.json minus distinct wire uids on #11261 terminal rows).
