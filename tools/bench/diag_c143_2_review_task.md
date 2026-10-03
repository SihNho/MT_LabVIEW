ATTACK this claim (card 143-2, failed prediction in tools/bench/diag_c143_1_scratch.log Error List 53 vs 51/52, and gate H-a of
tools/bench/diag_c143_2_offline.log run 1 from tools/bench/diag_c143_2_offline.py).

Claim H: the two extra Error List items of the P4 session-2 scratch file claudeDev\D1_ring_p4s02_20261003_110001.vi
("Local Variable ...: This variable is not connected to anything." and "While Loop 'While Loop': Conditional terminal is not
wired", tools/bench/errorlist_D1_ring_p4s02_20261003_110001_20261003_110836.json:5638-5642, no uids) are the plan's by-design
state at the session-2/session-3 boundary:
1. While #10170 (loop 1.2, body diagram #23166) has its conditional terminal #23246 unwired because session 2 deleted the
   scaffold stop wire w23310 on purpose (p4_dw_23310, tools/bench/plan_ring_p4_s02v18.json:325-327);
2. Local #6902 (StopAll READ, made by session 2's last action p4_lr_stop12, symbol -20) has its single terminal unwired
   because only session 3's FIRST action p4_w_stop12 (tools/bench/plan_ring_p4_s03v18.json:77-84) wires -20 -> #10170 cond.
Alternative H': a session-2 delete cut a wire the plan did not mean to cut.

Measured facts (all in tools/bench/diag_c143_2_facts.md; graph tools/bench/graph_ring_p4s02_20261003_112505.json read from a
fresh LabVIEW, session-2 edits verified present, file md5 unchanged):
- of the 6 While body diagrams only #23166's '' sink (#23246) has wire 0; of 25 Locals only #6902 has an unwired terminal;
- terminals unwired in s02 but wired in the s01 graph: exactly 2, #23246 (w23310) and LoopTunnel #23417 inner #23435
  (w23255), both explicit deletes of the s02 plan (:325-333);
- the s02 SIMULATED end graph (tools/bench/sim/ring_p4_s03v18_s02end/base_provisional.json) has the same three open;
- s03 action 1 names the Local's terminal 'value' while the measured name is 'StopAll' (not tested);
- offline run 1 gate H-a failed because the script expected the cond row under the WhileLoop owner; the graph stores a While's
  conditional terminal as the '' sink row of its body Diagram.

Answer: the strongest reason H is wrong, an alternative explanation that fits the same facts, what would falsify H, and the
cheapest discriminating test (offline from the attached files if possible). Also say whether the 'value' vs 'StopAll'
terminal name is a risk for s03 action 1.
