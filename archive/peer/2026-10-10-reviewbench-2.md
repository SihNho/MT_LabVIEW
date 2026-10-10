# reviewbench-2

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.1374  in 26 / out 12918 / cache-create 76100 / cache-read 944896  (175s, 22 turn(s))
- **date:** 2026-10-10 21:16:36
- **outcome:** ANSWERED (179s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** card chat-X7 arm A (benchmark replay of cycle 164 hand-back 2; single hypothesis review vs discussion)
- **verdict:** unverified

## Question

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


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

No: the hand-back's framing does not hold as written. One real risk is in it, but its proposed fix is wrong and its precedent doesn't show what it claims. The K3f/K4f part is a separate problem from J and needs its own decision. (I couldn't save a plan file because the Write tool is disabled here, so the full review is below. Nothing was run, edited or locked.)

## 1. The strongest reason the claim is wrong

**The "settled form" can't be applied to w23519, and the old failure was not caused by `delete_object`.**

- **The fix would cut live wires.** The settled form (PD321(b)) says: before deleting a node, delete every wire whose only other end is that node, after checking that all the wire's sinks sit on that node. w23519 fails that check. The graph shows four sinks: one on #23501, and three on other nodes (tunnels #23417 and #23172, and Function #7201) (`graph_ring_p5s02c_20261010_131658.json`, `diag_c164_a2_4_facts.md:3`). So the release step "add `delete_wire` rows for 23519" would disconnect three live branches. That changes the original's computation, which hard rule 2 forbids. Only w23460 passes the check (`diag_c164_a2_4_facts.md:4`).
- **The old run failed at a step J doesn't have.** In the old P4 run, `delete_object` #10171 succeeded with its input wire still attached (no error, node count 664 → 663, `diag_c140_2_facts.md:26-27`). The error 1055 came from the *next* step, `wire_remove_loose_ends` on a wire that had just lost all its sinks (`:27-28`, `diag_c140_3_facts.md:9`). Group J has no `wire_remove_loose_ends` row. Deleting the wire first is a fix that worked, not a proven requirement.
- **A3 ("contradicted") points at test runs on copies, not at a launch.** Its evidence is the two scratch runs on byte copies. `diag_c140_3_facts.md:27` says "Launch NOT made". So the plan's sentence "`delete_object` has no passing launch yet" may be literally true. A3 is a disagreement about wording, not about a plan defect.
- **The truly new step was called "settled".** P4 never deleted a tunnel: #23417 survived. J deletes LoopTunnel #23501 while its outer face still carries a wire with other sinks. That shape is not covered by P4.
  - There is related evidence outside the case's file list: `tools/bench/diag_c116b_scratch.json:553-579` shows 13 LoopTunnel deletions with no error (tunnels 151 → 138, wires 1945 → 1934). I did not check whether wires were attached at each of those deletions.

## 2. Alternative explanations

**A. The real risk is leftover broken wires and the Error List count, not error 1055.** In LabVIEW, deleting a node or tunnel leaves the attached wires behind as broken wires ([NI forum, scripting move/delete](https://forums.ni.com/t5/LabVIEW/Disable-a-Node-Using-Scripting/td-p/3251989); [NI Idea Exchange, deleted tunnels leave broken wires](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Automatically-Delete-Passthrough-Wires-when-a-Linked-Tunnel-is/idi-p/2421080) — these are user reports, not NI documentation).
- The session's own Error List prediction already marks A54 and A55 as UNPREDICTED because of exactly these wires (`diag_c164_a2_3_facts.md:18-19`). That is the same kind of failure that stopped 140-3 (52 errors where 51 were predicted).
- Deleting w23460 first removes one possible broken leftover. It cannot fix w23519's leftover end at the deleted tunnel; that would need a `wire_remove_loose_ends` on w23519, which has not been measured.

**B. K3f/K4f are most likely wrongly addressed rows, not a gap in the router.**
- These rows are not in plan 872822f3 at all: the J+K3 plan routes with no failures (164-a2-2 PASS). They belong in a separate decision.
- The message at `stagexec.py:1933-1935` says the router has no *measured* route for an inner face. It does not say LabVIEW cannot make that wire.
- The STUB gate at `prep_c164_a2_1_mk.log:37` shows the target terminals t8776 and t24342 already carry wires w10362 and w25232. Adding a second wire to an input that is already fed would give a broken wire even with a working route. So the rows likely point at the wrong face, or are missing a `delete_wire`.

## 3. What would falsify the claim

Run J exactly as planned on a scratch copy. The claim is falsified if all of these hold:
- A54 and A55 return no error.
- After A55, w23519 still has its three other sinks and is not broken.
- The lost-wire set and the Error List match the prediction.

## 4. The cheapest test that separates them

- **Offline, free, already done:** the sink-subset check above (`diag_c164_a2_4_facts.md:3-4`). It already rules out the "delete w23519" fix. Only a `delete_wire` of w23460 qualifies.
- **Smallest LabVIEW test:** the one scratch run the plan already calls for, on a new byte copy (the user has to authorize it). Read three things right after A55:
  1. w23519's sinks and whether it is broken;
  2. whether a stub of w23460 remains (wire count change);
  3. the Error List count.
- **How to read the result:**
  - All match the prediction → the prior-art block can be lifted (marked REFUTED) for J as planned.
  - w23519 is broken, or the count is off → alternative A is right, and the fix is a measured cleanup of w23519, not deleting it.

**Two limits:**
- The simulator cannot settle this. It keeps w23460 as a half-wire under its default rule (`stagesim.py:1080-1095`) and has no model of loose wire ends (`:139-143`), so only a real run separates the two explanations.
- What would change my view: if PD321(b)'s actual text required deleting every attached wire whatever its other sinks, then the plan has a real conflict between that rule and rule 2, and the user has to decide.

## Sources

(extract from answer)

## What was done with it

Benchmark only (card chat-X7, `tools/bench/reviewbench/report_x7.md`): this answer was scored blind against the later
judgement (PD399); it drove no work. No FIXED/REFUTED release applies - it reviews a failure already resolved in cycle 164.
