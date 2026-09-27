ATTACK this claim (card 113-1 P0, failed prediction in tools/bench/diag_c113a_b2agraph.log, script tools/bench/diag_c113a_b2agraph.py).

CLAIM: gate N failed because MY PREDICTION was wrong, not because the saved B2a file is wrong. The gate predicted that
L2-B2a (7 wire rows) added no non-Wire object to D1_l2_b2a_20260928_001426.vi relative to the B1 graph
(tools/bench/graph_l2b1_20260927.json). The read found 4 new Terminal objects: uids 25829, 25862 (owner IndexArray #8741) and
25854, 25961 (owner IndexArray #30331), all named 'disabled index (col)', bare (diag_c113a_b2agraph.log FACT DIFF lines). These
are exactly the terms that the B2a launch's E1 gate accepted under rule D4 (toward S1) in card 112-4:
tools/bench/stage_d1_l2b2a_r2.log:119-125 ("D4-ACCEPT ... 'disabled index (col)' #8741 x2, #30331 x2, in-S1 yes"), and
tools/bench/cards/result_112-4.json fact 2. LabVIEW grew them by type propagation once SRB1/SRB2 were typed
(review archive/peer/2026-09-27-c112c-b2a-e1.md). All other differences (32 diff rows) are the 7 planned B2a wires, the
renames element->subarray / index->index (row) on #8741/#30331 and their consumers, and #8634/#29625 'index (row)' ->
'disabled index (row)' (the PB closures of 112-4). No object was removed. The graph file itself
(tools/bench/graph_l2b2a_20260928.json md5 42fb5993) is a correct read of the saved B2a file (K1/K2/O/H gates PASS).

Uid check already made: launch 2's step diff after op 7 lists only_real_terms [25829, 25854, 25862, 25961]
(tools/bench/stage_d1_l2b2a_r2.log:118), the same 4 uids.

My fix: the gate now expects exactly those 4 terminals and nothing else; it re-runs OFFLINE on the saved read (no LabVIEW).

Question: is there any reading under which these 4 terminals are NOT the D4-accepted ones (e.g. different uids than launch 2
saw, or extra terminals elsewhere hidden by the diff method), which would make the graph unfit as the B2b planning base?
Cheapest discriminating test you would run.
