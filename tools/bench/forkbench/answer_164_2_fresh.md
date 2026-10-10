I've judged hand-back 2 and am writing the round-3 purpose. As instructed, no files were written.

**What I accept from hand-back 2** (`tools/bench/cards/handback_164_2.json`):
- The prior-art review was right on both counts.
  - **Group J does not follow the settled delete form** (PD321(b)/PD323(a), `docs/d1/ring-p4b.md:22-27`). The graph read `diag_c164_a2_4_facts.md:3-6` shows:
    - w23460 has all its ends on the two nodes being deleted (#23501 to #23042), so it must be deleted as a wire first.
    - w23519 keeps 3 live sinks (t23450, t23241, t7606), so it must not be deleted. It gets `wire_remove_loose_ends` after the tunnel is removed, as in the P4 form.
  - **My PD397(d) premise was false.** `delete_object` did pass in P4 (`diag_c140_3_facts.md:14,22`). The review is owed only for deleting the TUNNEL. This is a correction to `docs/d1/ring-p5c.md:57`.
- **K3f/K4f (A70/A80) are a real block, not a dry-run artefact.** They connect to the inner faces t8776/t24342 of the kept loop tunnels. No tool route reaches those faces (`stagexec.py:1930`), and each face also holds a stub wire (w10362/w25232).

**What I decide (PD399):**
- Step 4 = J in the P4 form, plus K3. That is about 19 rows; J+K3 measured MAIN 642.5 before the one extra checkpoint read.
- K3f, K4 and K4f become step 5, planned on step 4's real graph.
- I am not choosing between rewriting K3f/K4f onto the outer face or measuring an inner-face route here. The outer-face rewrite may change the computation (a rule-1a question), and the tunnel's indexing mode has not been measured. An offline facts card collects what is needed, and the next cycle decides.
- This is the last of the cycle's 3 rounds, so the PB tightening, fp-86, re-pins and the fn batch move to cycle 165.
- Hook gate-fps go to the chat. The cycle-163 retrospective disposition is already written (PD398(e)).

**Two things I could not fill in:**
- The plan md5 is a placeholder. PD399 is not written in this bench and I have no shell to hash the file.
- The A-number labels below for the two new rows are my own. The hand-back numbers only A54/A55 (`diag_c164_a2_4_facts.md:21`).

```json
{
  "schema": "next/1",
  "cycle": 164,
  "act": "Round 3/3 (PD399): re-form group J in the PD321(b)/PD323(a) delete form (NEW delete_wire w23460 before the two delete_object rows, NEW wire_remove_loose_ends w23519 after delete_object #23501), re-make plan_ring_p5s02d.json = J+K3 on graph 3d5196ab, gates + prior-art release by FIXED: lines, ONE scratch on a new byte copy of 564d8cbe, adopt claudeDev D1_ring_p5s02d_<ts>.vi. Offline beside it: K3f/K4f inner-face FACTS card (no decision). K3f/K4/K4f = step 5.",
  "task_kind": "build",
  "plan": {"path": "docs/d1/ring-p5c.md", "md5": "<md5 of ring-p5c.md after the judgement writes PD399 and corrects :57 - not computed in this bench>"},
  "pass": [
    "Accepted from round 2, cite only: hashes 26/0 (prep_c164_a2_1_hash.log), dst-only pass wire compiles (prep_c164_a2_1_mk.log:42-53, prep_c164_a2_2_mk.log:34,134-135), X10 per prefix (diag_c164_a2_1_facts.md:18-26), J/w23519/w23460 facts (diag_c164_a2_4_facts.md:3-6)",
    "Re-hash before any edit: VI 564d8cbe, graph 3d5196ab, EL 26d45c71, memory_model 8fb432e4, r_in 4d93c82d, plan_ring_p5s02d.json 872822f3, stagekit dd57c1ca, stagexec a4df7e15, stagesim 95a162ba, stage_prerun 7605116f; any drift = hand back",
    "Wire gates quoted on 3d5196ab BEFORE the row edit: w23460 ends all on #23042/#23501 (delete_wire allowed); w23519 has >= 1 sink outside #23042/#23501 (keeps t23450/t23241/t7606; RLE allowed, delete_wire refused); a different result = hand back",
    "plan_ring_p5s02r_in.json (4d93c82d): exactly 2 rows added in group J, delete_wire w23460 between A53 and the delete_object of #23042, and wire_remove_loose_ends w23519 right after the delete_object of #23501; JSON compare shows only those 2 additions; new md5",
    "plan_ring_p5s02d.json re-made on 3d5196ab = J (10 rows) + K3 (A61..A69), K3f/K4/K4f NOT included; every delete_wire a checkpoint; X10 MAIN <= 675 quoted (limit and memory model unchanged); SB REALSIM final True, route PASS, 0 UNROUTABLE",
    "stagesim end graph quoted: #23042, #23501, w23460, w23489 absent; w23519 present with exactly the sinks t23450/t23241/t7606; K3 tunnel group and w_k3pass present",
    "Recipe pair stage_d1_ring_p5s02d{,_scratch}.py = the step-3 recipe inputs on the shared stagekit gates (RingSession), re-made on the new plan; dry both PASS or PASS-UNVERIFIED with CEN2 the only unverified gate; PB rows quoted; a PB block = hand back, no class added",
    "prerun PASS (X10/X14/X17/X8); --check-launch PASS with 'DRY-UNVERIFIED-OK: CEN2 new-object census' named on the launch card (stage_prerun.py:3432-3456); --scratch-required exit quoted",
    "Predicted step-4-end Error List from 26d45c71: each cleared/raised item cited to an action (the delete_object rows predicted in the P4 form where the P4 facts allow, else named UNPREDICTED); file + md5",
    "Prior-art STOP RECORDs on both re-made recipes released by FIXED: lines: settled-already -> the plan rows (file:line) in the PD321(b)/PD323(a) form; contradicted -> docs/d1/ring-p5c.md:57 corrected by the judgement (PD399); flags.peers include priorart; any new non-novel verdict = hand back",
    "ONE scratch on a NEW byte copy of 564d8cbe: peak <= 675 and every BLOCK gate PASS, quoted (SCRATCH- peak line, GATE MEM line); per J delete row: wire/node gone after the op, w23519 still has its 3 sinks, no error 1055; else RETURN, no second run",
    "On PASS adopt claudeDev D1_ring_p5s02d_<ts>.vi (in-between, not counted); md5; graph read + md5; full Error List vs the prediction item by item",
    "tools/bench/memory_model.json: ONLY one load_by_vi entry for the adopted md5 (MB line cited); every other key equal by JSON compare, fail_above_mb 680",
    "Measured census written into the step-4 pred by a script citing the graph reads; census keys only; md5s",
    "Offline facts card, labview none, beside or after the LabVIEW card (facts only, no route decision): for t8776 (#5204) and t24342 (#10404) quote the tunnel class and direction, IndexMode if in the graph else UNMEASURED, the stub wires w10362/w25232 (source, sinks), the PD379(b)/plan_ring_p5s02r_in.json design rows A70/A80, the measured face routes (stagexec loop_inner_face_route, l2a1_faces_81.log), and whether any stored measurement wires an inner face as a SINK; file diag_c164_k3f_facts.md + md5",
    "Originals not opened; eb1d0f31, 7f2582ae, 94ffff94, f9ae7751, 564d8cbe unchanged by hash; LabVIEW closed and verified gone"
  ],
  "blocked_by": null,
  "stop_requested": false,
  "advances": ["M3", "M8", "R1"],
  "note": "Hand-back 2 judged (PD399). Round 3 of 3: a failed gate or a returned scratch closes the cycle on this purpose. Moved to cycle 165: PD397(e) PB tightening + fp-86, re-pins, fn batch, make_step_plan routability (prep_plan_flow_lib.py:171). Hook gate-fps (fp-75/80/...) go to the chat."
}
```

In real mode I would also rewrite STATUS.md's `## NEXT` to say the same first act: re-hash, quote the two wire gates on 3d5196ab, add the 2 rows to r_in, and re-make the J+K3 plan. I did not write it here because of the bench instruction.