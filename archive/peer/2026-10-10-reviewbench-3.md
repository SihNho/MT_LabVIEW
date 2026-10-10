# reviewbench-3

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $0.8749  in 22 / out 12656 / cache-create 58245 / cache-read 657750  (154s, 16 turn(s))
- **date:** 2026-10-10 21:16:18
- **outcome:** ANSWERED (159s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** card chat-X7 arm A (benchmark replay of cycle 165 hand-back 2; single hypothesis review vs discussion)
- **verdict:** unverified

## Question

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


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**The claim is right about what happened but wrong about where the fix goes.** The face being wired by the stub at base is only why the check reached that face at all. The real defect is in the executor's base address check (the "PRIME" pass, `stagexec_case3.py.txt:2604-2643`). It checks each plan action's ends against the base graph without regard to plan order. So it tries to prove t8776/t24342 even though an earlier checkpointed `delete_wire` in the same plan removes their stubs before the connect runs. Changing `_triple` at line 1934, which is where the hand-back's OPEN line points, would be the wrong repair.

## 1. Strongest reason the claim is wrong (as a diagnosis that leads to a fix)

- **The refusal ignores wiring.** `_triple` refuses every inner face of a `LoopTunnel`, `Tunnel` or `SelectorTunnel`, wired or not (`stagexec_case3.py.txt:1932-1935`; `FACE_ROUTED` is defined at `:1366`). Deleting the stub would not make that refusal pass. It would only stop the base pass from calling it, through the `r["wire_uid"]` filter at `:2628`.
- **The design already says these acts need no index proof.** `loop_inner_face_sink` sends A73/A84 down `connect_term_uid`, which addresses the face by its terminal uid (`:1534-1537`, `:3608-3610`, `:4087-4089`). There is no position in the loop's terminal list to prove. The base pass already exempts acts of this kind, but only Flat Sequence ones: `kind == "connect_term_uid"` and a variant starting with `fs_` (`:2603-2606`).
- **The new variant is never exempted.** It is named `loop_inner_face_sink` (`:6341`), so it never matches the `fs_` test. In this plan the ops are also `connect` and `branch` kinds (log line 38; "ROUTE 2 connect", "ROUTE 9 branch"). So the kind test fails too, and adding the new variant name to that line alone would not be enough.
- **So the gap is in the base pass, not in `_triple`.** If someone loosened `_triple` instead, the Nodes[] index route would start accepting loop inner faces. That route is explicitly unmeasured ("only the outer face's owner route is measured", `:1934`).
- **Why the earlier self-test missed this.** The PD400(b)/PD401 self-test only checked that the plan compiles and that stored plans compile byte-equal. That is a structural check; it never ran this base pass with a stub-delete-then-connect order. This is the gap that let the prediction fail.

## 2. Alternative explanations of the same evidence

- **A (the main competitor): the base pass refuses these faces no matter how they are wired.** The code copy is broken exactly at the deciding line. At `:2628-2630` the `if` is indented 16 spaces, the `continue` 24, and the `try:` 20. That cannot be parsed (IndentationError), so this copy is not the code that ran. Removing the later change seems to have left a stray `continue`. My reading that "only wired, uncached ends get proved" is a reconstruction, not something I read off working code. If the code at failure time also proved unwired ends, then the stub is irrelevant and the claim's causal step fails.
- **B: fixing this check may only reveal the next failure.** Several later gates were never reached: C-OUT, IDS, X8, X17 and the Part 5 end-graph check (`diag_c165_a2_1_facts.md:33`). On the real backend this check stops the run before op 1 (`:2641`). "Tool fix owed before step 5" assumes this is the only blocker, and nothing shows that.

## 3. What would falsify the claim

The claim is falsified if t8776 is still refused when it is unwired at base. To see that, run the base pass with w10362 removed from t8776's row in memory. If t8776 still appears in the "not addressable at base" list, the stub is not the cause; the cause is that this pass checks all loop inner-face ends of non-Flat-Sequence acts.

Separately, the prediction about the outcome after the fix rests on nothing measured. The census values in [{}, {'Wire': 1}] and "Is Broken? False" are marked "UNMEASURED - no recorded connect_term_uid sample onto a LoopTunnel inner face" (`:6342`). The c127 precedent covers a Flat Sequence inner face as the source, not an unwired LoopTunnel inner face as the sink (`diag_c165_a2_1_facts.md:12`). Outside sources don't settle this either. NI forum threads confirm that the "Connect Wire" scripting method creates tunnels automatically. They also show that reaching inner tunnel terminals by script is fiddly. None of them measures a wire connected onto an existing loop tunnel's inner face.

## 4. Cheapest test that tells the claim and alternative A apart

This test is offline, needs no LabVIEW, and edits no files. Load graph 2a5fa0c4 and plan 0b895983 in memory and set t8776's `wire_uid` to 0. Then run only the dry (collecting) executor up to the base-pass report line (`:2637`).

- **If the claim is right:** ROUTE 2's refusal disappears and ROUTE 9's (t24342, still wired) stays.
- **If alternative A is right:** both refusals stay.

Do it before anyone edits the pinned file. The result decides whether the fix is "exempt connect acts using the loop-sink variant in the base pass" or something wider. An even cheaper first step: find the stagexec version that actually ran (md5 6ea6637f) and read its lines 2628-2630, since the review copy cannot be parsed there.

**Where I stand:** I still think the claim's mechanism is likely right (about 70%, given the broken lines). The conclusion that line 1934 needs a fix is probably wrong. A test showing the refusal persists with the stub removed would change my mind on the first point.

Sources:
- [NI forum: Programmatically creating a tunnel with LV scripting](https://forums.ni.com/t5/LabVIEW/Programmatically-creating-a-tunnel-with-LV-scripting/td-p/1830745)
- [NI forum: wiring a pass-through tunnel inside a case structure](https://forums.ni.com/t5/LabVIEW/LabvVIEW-Scripting-wiring-a-pass-through-tunnel-inside-a-case/td-p/3945608)
- [NI forum: Script connect existing loose wires to case tunnels](https://forums.ni.com/t5/LabVIEW/Script-connect-existing-loose-wires-to-case-tunnels/m-p/4196003)

## Sources

(extract from answer)

## What was done with it

Benchmark only (card chat-X7, `tools/bench/reviewbench/report_x7.md`): this answer was scored blind against the later
judgement (PD402); it drove no work. No FIXED/REFUTED release applies - it reviews a failure already resolved in cycle 165.
