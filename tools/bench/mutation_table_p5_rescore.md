---
type: facts
status: current
date: 2026-10-10
card: 158-a3-1 (re-score of 158-a2-4)
---
RE-SCORE (card 158-a3-1, PD386(d)) by prep_c158_a3_1_rescore.py: TD/D = stagekit.term_identity_pairs, PB = stagekit.pb_check_bound; RECORD = passes only by recording. Original table: mutation_table_p5.md (unchanged).
# Gate mutation table on graph 6716c499 (steer debate:plan-overall-02, PD384(d)) - made by `diag_c158_a2_4_mut.py`, every row in the json
Class rule: INVARIANT = removes or re-points a wire end, or changes a value (M1, M2, M3c, M6); REPRESENTATION = only names, uids, diagram membership or relay objects change, every computation input keeps its source through relays (M3r, M3t, M4, M5). Real end = mutated copy; base = sim end = the unmutated graph. RECORD = E1 warn/log class (not a block).
Gates: CD/CDF vigraph.computation_diff default / frame-keyed; TD, D stagekit.term_identity_gates; PB stagekit.pb_check (S1 vs real, pred = cdiff(S1, G0) 21 rows); E1 stagexec.compare; INV n.a.: invcheck.run_inv pins file md5s / snapshots (tools/invcheck.py:7-12, :97); it takes no graph pair.

| id | mutation | target | class | CD | CDF | TD | D | PB | E1 | INV | net |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M0.0 | identity copy | no change | ctl | PASS | PASS | PASS | PASS | PASS | PASS | n.a. | PASS |
| M1.0 | wire dropped | wire 40 (384 -> 5987) deleted | inv | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | n.a. | BLOCK |
| M1.1 | wire dropped | wire 23850 (23792 -> 30398) deleted | inv | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | n.a. | BLOCK |
| M1.2 | wire dropped | wire 44244 (44178 -> 44196) deleted | inv | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | n.a. | BLOCK |
| M2.0 | wire re-sourced | sink t6042 on #5987 moved from wire 40 (src #384) to wire 46 (src #442 | inv | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | n.a. | BLOCK |
| M2.1 | wire re-sourced | sink t30433 on #30398 moved from wire 23850 (src #23792) to wire 23898 | inv | BLOCK | BLOCK | PASS | BLOCK | PASS | BLOCK | n.a. | BLOCK |
| M2.2 | wire re-sourced | sink t44229 on #44196 moved from wire 44244 (src #44178) to wire 40 (s | inv | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | n.a. | BLOCK |
| M3c.0 | node moved, wires broken | #16 Function diagram 113 -> 124; its 2 wires deleted | inv | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | n.a. | BLOCK |
| M3c.1 | node moved, wires broken | #21699 Function diagram 21658 -> 113; its 3 wires deleted | inv | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | n.a. | BLOCK |
| M3c.2 | node moved, wires broken | #44196 SubVI diagram 44169 -> 113; its 4 wires deleted | inv | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | n.a. | BLOCK |
| M3r.0 | node moved, wires kept | #16 Function diagram 113 -> 124; wires untouched | rep | PASS | PASS | PASS | PASS | PASS | PASS | n.a. | PASS |
| M3r.1 | node moved, wires kept | #21699 Function diagram 21658 -> 113; wires untouched | rep | PASS | PASS | PASS | PASS | PASS | PASS | n.a. | PASS |
| M3r.2 | node moved, wires kept | #44196 SubVI diagram 44169 -> 113; wires untouched | rep | PASS | PASS | PASS | PASS | PASS | PASS | n.a. | PASS |
| M3t.0 | node moved, relayed by new tunnels | #16 Function diagram 113 -> 124; its 2 wires relayed through 2 new Tun | rep | PASS | PASS | PASS | BLOCK | PASS | BLOCK | n.a. | BLOCK |
| M3t.1 | node moved, relayed by new tunnels | #21699 Function diagram 21658 -> 113; its 3 wires relayed through 3 ne | rep | PASS | PASS | PASS | BLOCK | PASS | BLOCK | n.a. | BLOCK |
| M3t.2 | node moved, relayed by new tunnels | #44196 SubVI diagram 44169 -> 113; its 4 wires relayed through 4 new T | rep | PASS | PASS | PASS | BLOCK | PASS | BLOCK | n.a. | BLOCK |
| M4.0 | tunnel renamed | LoopTunnel #23501: 2 term names + ' ~renamed' | rep | PASS | PASS | PASS | PASS | PASS | PASS | n.a. | PASS |
| M4.1 | tunnel renamed | Tunnel #21730: 6 term names + ' ~renamed' | rep | PASS | PASS | PASS | PASS | PASS | PASS | n.a. | PASS |
| M4.2 | tunnel renamed | SelectorTunnel #20556: 3 term names + ' ~renamed' | rep | PASS | PASS | PASS | PASS | PASS | PASS | n.a. | PASS |
| M4.3 | tunnel renamed | FlatSequenceInnerTunnel #14794: 4 term names + ' ~renamed' | rep | PASS | PASS | PASS | PASS | PASS | PASS | n.a. | PASS |
| M4.4 | tunnel renamed | FlatSequenceOuterTunnel #28028: 2 term names + ' ~renamed' | rep | PASS | PASS | PASS | PASS | PASS | PASS | n.a. | PASS |
| M5n.0 | node uids renumbered | #16 Function: owner uid and its 2 term uids + 9000000 | rep | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | n.a. | BLOCK |
| M5n.1 | node uids renumbered | #21699 Function: owner uid and its 3 term uids + 9000000 | rep | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | n.a. | BLOCK |
| M5n.2 | node uids renumbered | #44196 SubVI: owner uid and its 12 term uids + 9000000 | rep | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | n.a. | BLOCK |
| M5w.0 | wire uid renumbered | wire uid 40 -> 9000040 | rep | PASS | PASS | PASS | PASS | PASS | PASS | n.a. | PASS |
| M5w.1 | wire uid renumbered | wire uid 23850 -> 9023850 | rep | PASS | PASS | PASS | PASS | PASS | PASS | n.a. | PASS |
| M5w.2 | wire uid renumbered | wire uid 44244 -> 9044244 | rep | PASS | PASS | PASS | PASS | PASS | PASS | n.a. | PASS |
| M5a.0 | all uids renumbered | every uid (terms, owners, wires, diagrams, objs, loops, fs pairs) + 90 | rep | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | BLOCK | n.a. | BLOCK |
| M6.0 | constant value changed | ControlReferenceConstant #37: value -> 'MUTATED' (new `value` key; the | inv | PASS | PASS | PASS | PASS | PASS | PASS | n.a. | PASS |
| M6.1 | constant value changed | RingConstant #20327: value -> 'MUTATED' (new `value` key; the graph ha | inv | PASS | PASS | PASS | PASS | PASS | PASS | n.a. | PASS |
| M6.2 | constant value changed | DigitalNumericConstant #50442: value -> 'MUTATED' (new `value` key; th | inv | PASS | PASS | PASS | PASS | PASS | PASS | n.a. | PASS |

(1) INVARIANT rows passing every gate (gaps): M6.0, M6.1, M6.2
(2) REPRESENTATION rows that block (false blocks): M3t.0, M3t.1, M3t.2, M5n.0, M5n.1, M5n.2, M5a.0
Blocks per gate (inv / rep): CD 9/4; CDF 9/4; TD 8/4; D 9/7; PB 8/4; E1 9/7; INV 0/0

Re-score vs 158-a2-4: invariant rows that blocked and no longer block: none; rows whose net moved: none; of those not representation: none.
