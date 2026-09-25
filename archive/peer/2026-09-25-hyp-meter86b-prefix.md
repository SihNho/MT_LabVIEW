# hyp-meter86b-prefix

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.4261  in 28 / out 12902 / cache-create 108699 / cache-read 1383197  (153s, 20 turn(s))
- **date:** 2026-09-25 22:47:11
- **outcome:** ANSWERED (157s)
- **verdict-card:** NO-VERDICT: $.violations[0].loss_min: expected number/null, got str
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id hyp-meter86b-prefix, role hypothesis) ---
CLAIM: meter_l2a1_86b.py run 1 failed B1 by OUR SCRIPT BUG: the prefix was act 1 only, but #6007 turns source only at step_22 (sr2_L0), so after act 1 it is correctly a SINK face; the fix is prefix = ops 1-22 via Executor.run on ex.ops[:22].
PREDICTED: after act 1 (mv_5540) alone: #6007 source, bare, sole outer face of SelectorTunnel #5680; #5082 bare sink on SubVI #5058
OBSERVED: meter_l2a1_86b.log:58-59: B0 diff 0 vs step_01, but #6007 is_source False (wire 0, owner #5680, frame 23166); #5082 as predicted. step_01_move_in.json also has #6007 is_source False; step_22_wire.json first has True
ALREADY RULED OUT: LabVIEW state: B0 compare vs the simulated step_01 was diff 0 (the sim predicts the same sink face)
ALREADY RULED OUT: memory: private 559-579 MB, no error, meter lines 37-57
ATTACHMENT: tools/bench/meter_l2a1_86b.log (md5 None)
ATTACHMENT: tools/bench/meter_l2a1_86b.py (md5 None)
ATTACHMENT: tools/bench/sim/l2a1/plan_l2a1.json (md5 None)
ATTACHMENT: tools/stagexec.py (md5 None)
--- END REVIEW CARD ---

FAILED PREDICTION, card 86-1 (b): tools/bench/meter_l2a1_86b.py, log tools/bench/meter_l2a1_86b.log (run 1).

Test: on a fresh LabVIEW and a D1_k scratch, run plan_l2a1 act 45 (rw_6007_5082: SelectorTunnel #5680 outer face #6007 ->
SubVI #5058 terminal #5082, route 'tunouter') ALONE after a prefix, then read the new wire's sink back by uid.

Prediction: after the prefix act 1 only (mv_5540: case #5540 into loop body 23166), #6007 is a SOURCE, bare, the only
OuterTerminal of #5680, and #5082 is a bare sink on #5058 (the state 85-3's P1 saw after acts 1-44,
unroutable_l2a1_85.log:555-556).
Observed (meter_l2a1_86b.log:58-59): B0 = live graph after act 1 vs simulated step_01 diff 0; B1 FAILED: #6007 is_source
False (wire 0, owner #5680, frame 23166, OuterTerminal); #5082 as predicted.

My explanation: our own script's bug. The prefix assumption "acts 2-44 touch neither #6007 nor #5082" was wrong. The
simulated step files themselves record #6007 as a sink face at step_01 and a source only from step_22_wire.json
(sr2_L0 wires new:SR2L.inner to #5702 terminal 6038 inside case #5540, so the case tunnel flips to output); #6026 flips
at step_18. Fix already on disk: meter_l2a1_86b.py now runs the executor's own diff-checked run over ex.ops[:22]
(acts 1-22), then executes op 41 (act 45) with prev = step_44 state / after = step_45 state, then reads back.

Questions: (1) is the flip really caused by sr1_L0/sr2_L0 wiring into the case (and not something LabVIEW-side the
sim merely copied)? (2) is prefix ops 1-22 sufficient, or does act 45's addressing (tunouter: face_twins via owners map,
Addr.tun needs #5680 to own exactly one OuterTerminal; destination triple on #5058 by unique (name, dir, wire) match)
depend on acts 23-44 (tunnels T1/T2, rewires on #5058 terminals 5171 etc.)? (3) is passing prev=step_44 state to
Executor.execute valid when acts 23-44 did not run (real_term resolves base uids 6007/5082 through the binding only)?
Files: tools/bench/meter_l2a1_86b.py, tools/stagexec.py (Executor.run ~line 810, execute ~925, connect_route ~455,
Addr.tun ~690), tools/bench/sim/l2a1/plan_l2a1.json and step_*.json.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"hyp-meter86b-prefix","verdict":"<one of: refuted | supported | unverified>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

**Verdict: supported, with one gap.** Run 1 failed because the test's own prediction was wrong. LabVIEW did nothing unexpected. The fix (run acts 1–22 first) is enough to get act 45 addressed and routed. It is not enough to show that act 45 behaves the same way it would after acts 1–44.

**1. Strongest reason the claim could be wrong.** LabVIEW never measured `sr2_L0` flipping #6007 on its own. The only LabVIEW reading of #6007 turning from sink to source is `l2a1_unflip_81_run2.log:217,261,272`, and that run wired 6038 (on #5702) and 5741 (on #5725) together before reading. Pinning the flip on `sr2_L0` alone comes from the wiring layout plus the simulator's unflip model (`tools/stagesim.py:374-399`). The model was fitted to that same run, so the sim agreeing with it proves nothing new.

**2. Alternative explanation of the same evidence.**
- **Different cause:** the flip back to source could have come from the 5741 wire in run 2, and not from 6038.
- **Weak on wiring layout:** 5741's inner (5733) feeds #6016, not #5680 (`l2a1_unflip_81.py:27-28`).
- **Weak on how LabVIEW works:** NI's documentation says a tunnel's direction follows where its source is, and a tunnel with no source has no direction ([NI: wire connected to undirected tunnel](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/wire-connected-to-undirected-tunnel.html), [NI forum](https://forums.ni.com/t5/LabVIEW/wiring-inputs-n-outputs-for-case-structure/td-p/584388)). That matches the chain the claim describes:
  - the move cuts wire 5637 (`step_01_move_in.json`, flip record);
  - #5702's inner 5705 loses its source;
  - wire 5710 into #5680's inner 5999 has no source;
  - so #5680 has no direction and its outer face 6007 reads as a sink;
  - wiring 6038 restores the chain.

**3. What would falsify the claim.** In the fixed run, op 21 (step_21: 6007 still a sink) or op 22 (step_22: 6007 a source) ends with a STEP-DIFF on 6007. `Executor.run` checks every op against its step file (`tools/stagexec.py:902-913`). Also, if B1 still fails after op 22, the claim is wrong.

**Your three questions:**

- **(1) Cause of the flip.** It is a LabVIEW behaviour the sim copied, not something the sim made up: #6007 read as a sink after the move and as a source after the wire in `run2.log:217/261`. The step files agree: 6007 is a sink at steps 01, 17, 18 and 21 and a source from step 22; 6026 is a source from step 18. Only the `sr2_L0`-alone attribution is unmeasured, and the fixed run measures it for free.
- **(2) Is ops 1–22 enough?** Yes. The claim missed one dependency that happens to be inside the prefix:
  - **Hidden dependency:** the `tunouter` route needs `face_twins(...) > 1` (`stagexec.py:515`). That means #6026 must also be a *source* outer face on #5540, because twins must match direction (`:544`). #6026 becomes a source only at step 18.
  - **`Addr.tun` needs #5680 to have exactly one outer face** (`:701-703`). Acts 23–44 add no outer face to #5680.
  - **#5082 is found by a unique name/direction/wire match** (`:770`). Acts 23–44 wire only *sources* on #5058 (5124/5111 in the prefix, 5171 in acts 35–36), so the "Bead is good? array in" sink match does not change.
- **(3) Is `prev=step_44` valid?** Yes for this op. `real_term` resolves `{uid, term_uid}` for base uids 6007/5082 through a binding that returns the same uid (`:799-809`). No symbolic `new:` end is involved. The script never compares the live graph against step_45, so the missing acts 23–44 cannot cause a false diff.

**The gap in scope.** After acts 1–22 the graph is not the one run 85 failed on:
- Wire 6011 into #5680's other inner (6003) still has no source, because #5967 is only restored by `tun2_in` (act 30).
- SR3, T1 and T2 do not exist.
- Terminal 5171 is unwired.

So a PASS on B2/B4 says act 45 works on this smaller graph. It does not clear act 45 inside the full sequence. That matters most if run 85's error 2 came from memory built up over acts 23–44: "act 45 alone passes" would then be expected and would settle nothing.

**Process fault.** The step file was on disk before the run and already said 6007 is a sink at step_01. The prediction was taken from run 85's state after act 44 (`meter_l2a1_86b.py` first-run docstring, log lines 5–6) and was not checked against step_01 offline.

**4. Cheapest discriminating test.** It is already on disk: run the fixed `meter_l2a1_86b.py` and read STEPX lines 21 and 22. The diff should be 0 at both, which means 6007 is still a sink after op 21 and a source after op 22. Then B1 should pass.

To check the scope gap cheaply, extend the prefix to `ops[:40]` (acts 1–44, still one LabVIEW launch) and meter act 45 on both graphs. If act 45 passes after 22 and fails after 44, the fault is accumulated state, not the op itself.

VERDICT {"schema":"verdict/1","id":"hyp-meter86b-prefix","verdict":"supported","alternative":"The source-flip of #6007 was only measured in LabVIEW with 6038 AND 5741 wired together (unflip_81_run2.log:261); sr2_L0-alone attribution is sim/topology. Also: prefix 1-22 omits acts 23-44 (6011 still unsourced, no T1/T2/SR3), so an act-45 PASS does not clear act 45 in the full sequence.","discriminating_test":"Run fixed meter_l2a1_86b.py: STEPX 21 and 22 diff 0 (6007 sink after op21, source after op22) then B1 PASS. For scope: meter act 45 after ops[:40] too; pass@22 + fail@44 => accumulated-state cause.","violations":[{"slug":"inference-over-measurement","loss_min":"?","loss_usd":"?","evidence":"tools/bench/sim/l2a1/step_01_move_in.json (6007 is_source false) vs meter_l2a1_86b.log:5-6"}],"sources":["tools/bench/l2a1_unflip_81_run2.log:217","tools/bench/l2a1_unflip_81_run2.log:261","tools/bench/sim/l2a1/step_21_wire.json","tools/bench/sim/l2a1/step_22_wire.json","tools/stagexec.py:515","tools/stagexec.py:701","tools/stagesim.py:374","https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/wire-connected-to-undirected-tunnel.html","https://forums.ni.com/t5/LabVIEW/wiring-inputs-n-outputs-for-case-structure/td-p/584388"],"note":"tunouter also needs #6026 source (step_18) for face_twins>1 - inside the 22-op prefix, unstated in the claim."}

## Sources

(extract from answer)

## What was done with it

Card 86-1 (material), 2026-09-25 ~22:5x. Verdict `supported` ACCEPTED: run 1's B1 fail was our script's prediction, not
LabVIEW. The fix (prefix = `ex.ops[:22]` through `Executor.run`, per-op diff-checked) is on disk in
`tools/bench/meter_l2a1_86b.py` and was NOT run: the card's rule "review owed -> hypothesis review then stop" was applied.
- Scope gap ACCEPTED as a fact for judgement: a PASS after ops 1-22 would clear act 45's addressing on a smaller graph only;
  the review's ops[:40] variant (act 45 metered after acts 1-44) is the discriminating one for accumulated state. Which
  variant runs is handed to judgement (card OPEN), not chosen here.
- `inference-over-measurement` ACCEPTED: the step_01 file was on disk and already said #6007 is a sink; it was not read
  before run 1.
