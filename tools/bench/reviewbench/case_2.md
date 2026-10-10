# Review case 2 - cycle 164 hand-back 2: prior art says group J must use the P4 delete form; K3f/K4f unroutable

**Question:** What is the most likely cause of this failure, what is the strongest alternative, and what is the
cheapest test that tells them apart?

**Repository root:** `G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop` - every path
below is relative to it (read the files there, not in any other checkout).

**Reading rules (same for every reviewer):** answer from this file and from the code / data / log files it cites
(`tools/*.py`, `tools/bench/plan_*.json`, `tools/bench/graph_ring_p5s02c_20261010_131658.json`, the cited
`tools/bench/*.log` and `diag_*_facts.md` files). Do NOT open `docs/**`, `archive/**`, `STATUS.md`, `tools/bench/cards/**`,
`tools/bench/reviewbench/**` (other than this file), or any cycle-164/165 file not cited here: the case is a replay of the
moment of failure, and the later record would give the answer away. Line numbers in `tools/stagexec.py` may have moved
since the failure; search by function name.

## Background (decision in force at the time, quoted from the plan, PD397(c)-(d) and PD398, cycle 164 judgement)

> Step 4 = `plan_ring_p5s02d.json` on the real p5s02c graph 3d5196ab: the longest prefix of WHOLE groups J (A53..A60,
> `delete_object`), K3 (A61..A69), K3f (A70), K4 (A71..A79), K4f (A80) whose MAIN is <= 675, rows <= 40; a group is never
> split. [...] Prior-art review `novel` + disposition when owed (owed for the TUNNEL deletion; `delete_object` has no
> passing launch yet). Then ONE scratch on a NEW byte copy of 564d8cbe.
> PD398 (hand-back round 1): A69/A79 pass wires carry `frame: "True"` on the DST end only; compile must take it as the
> group out-wire or hand back.

Group J as planned (from `tools/bench/diag_c164_a2_4_facts.md`): A53 `delete_wire` w23489; A54 `delete_object` #23042
(Comparison `x = y?`); A55 `delete_object` #23501 (LoopTunnel); A56..A60 create a Local read LR7 + `Equal?` EQ7 and wire
them to the loop condition. No `delete_wire` of w23460 or w23519 in A53..A60.

## Machine record

Hand-back `tools/bench/cards/handback_164_2.json` (verbatim, trimmed to the failing / passing cards):

```json
{"schema": "handback/1", "cycle": 164, "round": 2, "trigger": "session",
 "detail": "Prior art on plan 872822f3 (J+K3) is settled-already+contradicted: J deletes #23042/#23501 with w23519/w23460 attached (PD321(b)). K3f/K4f sit on LoopTunnel inner faces, unroutable (stagexec.py:1930). Facts: diag_c164_a2_4_facts.md, diag_c164_a2_1_facts.md:27-34.",
 "cards": [
  {"id": "164-a2-1", "status": "FAIL", "first_fail": "SB REALSIM FINAL: plan_ring_p5s02d.json e3054ab6 final False, route FAIL, UNROUTABLE 2 (k14 w_k3f #8776, k20 w_k4f #24342 = INNER face of LoopTunnel) - prep_c164_a2_1_mk.log:161"},
  {"id": "164-a2-2", "status": "PASS", "retry_of_card": "164-a2-1"},
  {"id": "164-a2-3", "status": "FAIL", "first_fail": "pass item 4: prior-art verdict settled-already + contradicted, not novel (tools/bench/prep_c164_a2_3_priorart.log:48-49); STOP RECORDs armed on both recipes (:53-54)"},
  {"id": "164-a2-4", "status": "PASS"}],
 "cost_usd": 14.04, "minutes": 36.1}
```

164-a2-2 PASS: `plan_ring_p5s02d.json` 872822f3 = J+K3 (A53..A69), 17 rows, final True, route PASS, UNROUTABLE 0, MAIN 642.5.

`tools/bench/prep_c164_a2_1_mk.log` (164-a2-1, the all-5-group prefix):

```
37:  GATE FAIL | STUB no base sink end carries a wire that no plan delete_wire removes (no stub delete needed) | [('w_k3f', 'dst', 8776, [10362]), ('w_k4f', 'dst', 24342, [25232])]
103:   ROUTE 14 branch ['w_k3f']: branch  UNROUTABLE ADDRESS: #8776 is an INNER face of LoopTunnel #5204: only the outer face's owner route is measured (l2a1_faces_81.log)
109:   ROUTE 20 branch ['w_k4f']: branch  UNROUTABLE ADDRESS: #24342 is an INNER face of LoopTunnel #10404: ...
161: GATE FAIL | SB REALSIM FINAL on the base graph: ... {'final': False, 'route': 'FAIL', 'first_fail': "UNROUTABLE 2 row(s) ..."}
```

`tools/bench/prep_c164_a2_3_priorart.log` (164-a2-3, the prior-art review of plan 872822f3), lines 12-26 and 48-54:

```
A1 SETTLED ALREADY: how to delete a scaffold stop. P4 session 1 removed loop 1.2's scaffold stop the same way: deleted the
stop-to-cond wire w23310, then the Comparison #10171, then routed a new stop onto the existing cond. That attempt failed
first with error 1055: deleting the node left its tunnel->Comparison input wire with no sink, and the follow-up
`wire_remove_loose_ends` then failed on that wire. The settled form, PD321(b) and PD323(a): first `delete_wire` every wire
whose only other end is the node; then `delete_object`; and gate on "that wire's sink set is a subset of the node's
terminals". This plan does not follow it: J deletes only w23489, then `delete_object`s #23042 and the in-tunnel #23501
while wires 23519 and 23460 are still attached. What LabVIEW does to 23519, and to the outer wire 23460, has not been
measured. To release: add `delete_wire` rows for 23519, and for 23460 if its sinks are only #23501, each with PD321(b)'s
sink-subset gate. Or show in writing why deleting the tunnel object is safe for these wires.
A3 CONTRADICTED: the plan says "`delete_object` has no passing launch yet"; diag_c140_2_facts.md:26 shows op 2
`delete_object` Comparison #10171 returned err '' with the node count 664->663.
48: PRIOR-ART: settled-already
49: PRIOR-ART: contradicted
discriminating_test (the reviewer's): "On graph 3d5196ab list sinks of w23519 and w23460: if 23460 has a sink outside
#23501, deleting the tunnel cuts a live branch; then compare predicted D-gate lost-wire set with the stagesim end graph."
53-54: STOP RECORD armed on tools/recipes/stage_d1_ring_p5s02d{,_scratch}.py (launch refused until FIXED:/REFUTED:)
```

`tools/bench/diag_c164_a2_4_facts.md` (164-a2-4, read-only, graph 3d5196ab), Wires section:

```
- w23519: source #8486 Function `x+1` t8494. Sinks: #23501 LoopTunnel t23514; #23417 LoopTunnel t23450; #23172 LoopTunnel t23241; #7201 Function `x` t7606. Only 1 of 4 sinks on #23501; none on #23042.
- w23460: source #23501 LoopTunnel inner t23505. Sinks: #23042 Comparison `x` t23481 and `y` t23477. All sinks on #23042.
- w23489: source #23042 Comparison `x = y?` t23472. Sink: t23456 owner #23405 (Diagram). Source on #23042.
- P4 #10171 / error 1055 (diag_c140_2_facts.md:26-28): op 1 delete_wire w23310, op 2 delete_object #10171 ran (err ''); op 3 wire_remove_loose_ends w23255 -> error 1055; w23255 = source LoopTunnel #23417 -> sinks only #10171.
```

## Files

- `tools/bench/diag_c164_a2_1_facts.md`, `tools/bench/diag_c164_a2_3_facts.md`, `tools/bench/diag_c164_a2_4_facts.md`
- `tools/bench/diag_c140_2_facts.md`, `tools/bench/diag_c140_3_facts.md` (the P4 precedent)
- graph `tools/bench/graph_ring_p5s02c_20261010_131658.json` (3d5196ab)
- code `tools/stagexec.py`, `tools/stagesim.py` (delete_wire / delete_object / wire_remove_loose_ends handling; the
  route ADDRESS check for an INNER face of a LoopTunnel)
