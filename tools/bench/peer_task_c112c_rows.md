ATTACK this claim about the FAIL of the OFFLINE row scan tools/bench/diag_c112c_rows.py (log tools/bench/diag_c112c_rows.log,
card 112-3 W0, no LabVIEW involved).

Context: after review archive/peer/2026-09-27-c112c-fixture.md s2 (accepted), the T1/T2 scratch fixture is a scratch byte copy of the
bed claudeDev\D1_l2_b1_20260927_193100.vi, whose graph is tools/bench/graph_l2b1_20260927.json. The scan lists candidate rows:
T1 = an existing WhileLoop register whose R.inner is fed by ONE source and whose L.inner wire has ONE sink (delete + re-wire through
wire_sr RightIn/LeftIn); T2 = a wired ControlTerminal -> case-selector 'Tunnel' outer face (delete + re-wire through 'ctltun').
Result: 6 usable T2 rows (e.g. CT t11532 '1 L-Turn' -> Tunnel #18978 outer t18977 w19293, owner CaseStructure #18975), and NO
ROW-T1 line printed at all -> the script's own RESULT said FAIL "no usable T1 (0) or T2 (6) row".

CLAIM (mine): a key bug in my scan, not a property of the bed. The script iterated stagexec.base_registers(G)
(tools/stagexec.py:838-850) and skipped every entry lacking a "left" key; base_registers returns ONE entry PER REGISTER uid with keys
loop/right/cls/loop_class - a Right entry never carries its left uid, so every register was skipped before any row test. The
patched scan iterates the graph's loops table (loop_uid, left_of {right: [left]}) directly and classes the loop from objs.
Evidence the bed HAS WhileLoop registers with left_of: tools/stagexec.py:841 docstring (loop #10170 right 9603 -> left 10544) and
tools/bench/diag_c112b_addr.log:42-44 (SRB1/SRB2 = Shift Registers[4]/[5] of WhileLoop #10170, so [0..3] exist).
Already ruled out: the graph file (md5 8327f974 = the card's pin); LabVIEW (never started).
Attack: is there a reason a usable T1 row may still not exist on the bed (e.g. every pre-existing WhileLoop register's inner wire
branches to several sinks, or the old ring registers were retired), and is deleting then re-wiring a pre-existing register's wire
in a byte copy of the bed a faithful check of 'wire_sr on a register made in an EARLIER session' (B2a's SRB1/SRB2 are bare faces
on registers B1 created)?
