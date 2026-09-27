# Card 111-2: object-level attribution of B1's 14 UNATTRIBUTED Error List items

B1 = `claudeDev\D1_l2_b1_20260927_193100.vi`, md5 `b705728a...` (unchanged, never run, never saved). Sources:
graph `tools/bench/graph_l2b1_20260927.json` (byte-copy read, `diag_c111b_b1graph.log` 5/0 + `_offline.log` 2/0);
diff vs L2-A3 `tools/bench/graph_l2b1_diff_20260927.json` (59 rows); A4 scratch `tools/bench/diag_c111b_tunnelitems.log` 13/0;
captures `tools/bench/errorlist_shots/c111b_item*_sel.png` (`diag_c111b_shots.log`). Row ids = `facts_c111b_l2b_rows.json`.

## A4 - what one cut raises (scratch copy of the L2-A3 bed, 29 known items; log :121-132)
Mutations: (a) delete w9097 (LSR #9025 -> tunnel #9087 outer; inner w9076 keeps 1 sink), (b) delete w29787 (#29240 -> tunnel
#29777 outer; inner w29766 keeps 2 sinks), (c) one unwired `add_shift_reg` on #10170. Result 29 -> 41 items:
undirected tunnel +2, tunnel-to-input +1 (Replace Array Subset), no-source +1, node "unwired or bad terminal" +2
(Build Array / Replace Array Subset), different types +2, different dims +2, SR unwired-inside +1, SR type-undefined +1.
=> each cut tunnel raises its OWN "undirected tunnel" item in addition to its wire's item (one wire, >= 2 items), and the
cut propagates type errors downstream (types/dims/node items on wires that were never cut). One unwired new SR = exactly 2 items.

## The 14 items
| # | class | object (uid, owner) | how identified | row / verdict |
|---|---|---|---|---|
| 1 | undirected tunnel | LoopTunnel #9087 (For #1359, 1.2) | B1 RBW sink-only w9076 | double-item (A4); B2-11 |
| 2 | undirected tunnel | LoopTunnel #10004 (For #1359) | w9993 | double-item; B2-01 |
| 3 | undirected tunnel | LoopTunnel #10177 (For #1359) | w10166 | double-item; Q-01 (never) |
| 4 | undirected tunnel | LoopTunnel #28370 (For #1359) | w28365 | double-item; B3-02 |
| 5 | undirected tunnel | LoopTunnel #9503 (For #1359) | w28684 | double-item; Q-02 (never) |
| 6 | undirected tunnel | LoopTunnel #29777 (For #29874, 1.2) | w29766 | double-item; Q-06 (never) |
| 7 | undirected tunnel | LoopTunnel #29911 (For #29874) | w29853 | double-item; B2-14 |
| 8-9 | SR unwired inside x2 | NEW RSR #9603 / #25545 (SRB1/SRB2, WhileLoop #10170 = 1.2), every terminal wire 0 | graph_l2b1 owners + SR terms; A4 (c) | B2-10 / B2-13 (R.inner); also B2-09/-11, -12/-14 |
| 10-11 | SR type undefined x2 | same new pairs #9603/#10544, #25545/#25582 | A4 (c): 1 new SR -> 1 + 1 | B2-09..B2-14 |
| 12 | Index Array | IndexArray #30331 (For #29874 body 29894, 1.2); 'array' <- #29625 'output array', whose 'array' is sink-only w29853; lost 2 'disabled index (col)' terminals (29265, 33430) vs L2-A3 | capture match (item 16: selection outline on the IndexArray in the lower For loop with the Median icon) + graph diff | cascade of B2-14 (no row of its own) |
| 13 | unwired selector | case selector Tunnel #2276 (loop 1.2 after B1; was 1.1): t2282 wired from 'Z/dZ' in L2-A3, wire 0 in B1 | graph diff | B2-15 |
| 14 | different dims | NOT resolved to a uid (captures 9/28 too coarse); candidate w28443 #8741 'element' -> FIR #28233 'X' (#8741 also lost 2 'disabled index (col)' terminals) | A4: 2 cuts alone gave +2 dims | cascade (A4); no row of its own |

Old SR pairs #9018/#9025 and #29505/#29512 (WhileLoop #637 = 1.1): RSR inner t9028 on sink-only w9215, t29516 on w29591;
S1 inner sources #9227 t9234 / #29616 t29624 (plan_l2b1.json:229,238). No row re-makes them (SRB1/SRB2 replace them), so they
stay in B1's pool as no-source wires, not SR items.

LabVIEW: absent after every run (b1graph H, tunnelitems H). B1 md5 unchanged (b1graph K1 x2).
