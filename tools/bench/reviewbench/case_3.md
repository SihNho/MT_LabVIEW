# Review case 3 - cycle 165 hand-back 2: route check refuses connects onto inner faces t8776/t24342

**Question:** What is the most likely cause of this failure, what is the strongest alternative, and what is the
cheapest test that tells them apart?

**Repository root:** `G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop` - every path
below is relative to it (read the files there, not in any other checkout).

**Reading rules (same for every reviewer):** answer from this file and from the code / data / log files it cites. For
the executor code use ONLY `tools/bench/reviewbench/src/stagexec_case3.py.txt` (the code as it stood at the failure:
today's `tools/stagexec.py` minus the change made AFTER this failure; md5 ec4f38e5 - the pinned 6ea6637f was never
committed, so line numbers may differ from the log's by ~1). Do NOT open `tools/stagexec.py`, `docs/**`, `archive/**`,
`STATUS.md`, `tools/bench/cards/**`, `tools/bench/reviewbench/**` (other than this file and the code copy), or any
cycle-165 file not cited here: the case is a replay of the moment of failure, and the later record would give the answer
away.

## Background (decisions in force at the time, quoted from the plan, cycle 165 judgement)

> PD400(a) K3f/K4f route = the designed form, not the outer-face rewrite. t8776 and t24342 each hold a one-end sink-only
> stub (w10362, w25232) with no source; OK3/OK4 sit on the same diagram 23405 as the inner faces. [...] Design form: plan
> rows `delete_wire` w10362 before A70 and `delete_wire` w25232 before A80 (each a checkpoint, PD393(a)); then A70/A80
> unchanged.
> PD400(b) The tool gap, closed narrowly (compile refuses A70 at `stagexec.py:1930`). A dst that is the INNER face of a
> While/For LoopTunnel with wire 0 (seen after the stub-delete checkpoint) routes by `gscript.connect_term_uid` (face uid <-
> source terminal uid). That is the sink-side twin of `loop_inner_face_route`, with the same owner checks. Every other
> inner face (wired, Case / Flat Sequence tunnel, owner not one While/For loop) still stops. stagesim models the same.
> Self-test on graph 2a5fa0c4: A70/A80 compile to `connect_term_uid`; the four stop cases still stop; the stored plans
> compile byte-equal.
> PD401 (hand-back round 1): `stagexec.loop_inner_face_sink` (stagexec.py:6345, md5 6ea6637f) self-test 25/0, the six
> stored plans compile and dry byte-equal; r_in 9dadb0c1 -> 0b895983 = exactly the 2 added `delete_wire` rows. KEPT.
> (b) What the step-5 plan predicts, per stub-delete + connect pair: after `delete_wire` w10362 / w25232 the face has wire
> 0; after A70 / A80 the census is in [{}, {'Wire': 1}], t8776 / t24342 sit on OK3's / OK4.outer's net.

## Machine record

Hand-back `tools/bench/cards/handback_165_2.json` (verbatim):

```json
{"schema": "handback/1", "cycle": 165, "round": 2, "trigger": "session",
 "detail": "165-2-1 FAIL: route check refuses connects onto inner faces t8776/t24342 (UNROUTABLE 2, mk.log:68,75). Face still wired by stub at base, so stagexec.py:1934 refuses; fix edits pinned stagexec 6ea6637f.",
 "cards": [{"id": "165-2-1", "status": "FAIL", "first_fail": "SB REALSIM FINAL: route check FAIL, UNROUTABLE 2 (w_k3f #8776, w_k4f #24342: 'INNER face of LoopTunnel ... only the outer face's owner route is measured')"}],
 "cost_usd": 5.98, "minutes": 12.0}
```

Failing log `tools/bench/prep_c165_a2_1_mk.log`:

```
33: FACT DW dw_10362 w10362 in base graph: rows [(5204, 'file progress', False)]; sourceless True
34: FACT DW dw_25232 w25232 in base graph: rows [(10404, 'file number to append out', False)]; sourceless True
36: GATE PASS | STUB no base sink end carries a wire that no plan delete_wire removes (no stub delete needed) | []
38: FACT C K3f A72..A73: 2 ops [('delete_wire', None, [1]), ('connect', None, [2])]; checkpoints [0, 1, 2]; delete_wire ops [1]
45: GATE PASS | C K3f+K4+K4f compiles; every delete_wire op [1, 8] is a checkpoint | [0, 1, 3, 4, 6, 7, 8, 9]
68:   ROUTE 2 connect ['w_k3f']: connect_term_uid  UNROUTABLE ADDRESS: 1 wired end(s) not addressable at base: ADDRESS: #8776 is an INNER face of LoopTunnel #5204: only the outer face's owner route is measured (l2a1_faces_81.log)
75:   ROUTE 9 branch ['w_k4f']: connect_term_uid  UNROUTABLE ADDRESS: 1 wired end(s) not addressable at base: ADDRESS: #24342 is an INNER face of LoopTunnel #10404: ...
100: FACT REALSIM plan tools/bench/plan_ring_p5s02e.json md5 20bde81a...: final False; failed null; steps 13; provisional []; route check FAIL; UNROUTABLE 2
101: GATE FAIL | SB REALSIM FINAL on the base graph: failed None, 13/13 replayed, 0 PROVISIONAL, route ... {'final': False, 'route': 'FAIL'}
```

Card 165-2-1 facts (from its result): "C compile PASS all 3 prefixes, every delete_wire a checkpoint: full = 9 ops, cps
[0,1,3,4,6,7,8,9], delete_wire ops [1,8]"; "SB FAIL: REALSIM 13/13 ok, 0 provisional, but route check UNROUTABLE 2: w_k3f
t8776 / w_k4f t24342 'ADDRESS ... INNER face of LoopTunnel'"; "Refusal text is tools/stagexec.py:1934 (_triple:
FACE_ROUTED owner with term_class != OuterTerminal), raised by the route check's base ADDRESS step"; "c127 precedent:
diag_c127_1_fsinner.log:81-102 three connect_term_uid <- #32868 each returned wire 32859, census {}". Its OPEN:
"loop_inner_face_sink (stagexec 6ea6637f) compiles A73/A84 but the route check's base ADDRESS check
(stagexec.py:1929-1935) still refuses the inner face: tool fix owed before step 5?"

## Files

- code `tools/bench/reviewbench/src/stagexec_case3.py.txt` (`Addr._triple`, `loop_inner_face_sink`, the Executor's
  base pass and the route check), `tools/stagesim.py`
- `tools/bench/diag_c165_a2_1_facts.md`, `tools/bench/diag_c165_a1_1_facts.md`, `tools/bench/diag_c164_a3_2_facts.md`
- graph `tools/bench/graph_ring_p5s02d_20261010_154830.json` (2a5fa0c4); plan input `tools/bench/plan_ring_p5s02r_in.json`
  at the time = 0b895983 (later versions may exist on disk); `tools/bench/diag_c127_1_fsinner.log:81-102`
