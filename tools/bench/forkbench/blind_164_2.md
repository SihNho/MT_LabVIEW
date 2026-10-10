# Blind case 164_2

## GROUND TRUTH 1 - what the real judge decided (its final message)
I accepted the round-2 hand-back as correct and wrote a revised purpose for the last hand-back round (3 of 3). No LabVIEW was touched in round 2, and none was touched in this session.

**What was decided** (PD399, `docs/d1/ring-p5c.md:105`):
- **The prior-art review was right on both points.**
  - Group J deleted nodes #23042 and #23501 with wires still attached. That breaks the delete order settled in P4.
  - My earlier note "`delete_object` has no passing launch yet" was false. It is corrected at `docs/d1/ring-p5c.md:57`.
- **Group J now follows the P4 order:**
  - **First, delete wire w23460.** Both of its ends are on the nodes being deleted.
  - **Then, delete the two nodes.**
  - **Last, run `wire_remove_loose_ends` on w23519.** This wire still feeds 3 other nodes, so it must not be deleted outright.
  - The checks for both wires are quoted from the graph before the edit. The simulated end graph must show w23519 left with exactly its 3 other sinks; any other result means a hand-back.
- **Step 4 is now J + K3 only, with the memory limit unchanged at 675 MB.** K3f lands on the inside face of a loop tunnel, and no current tool can wire there. So K3f, K4 and K4f become step 5. An offline card collects the facts on K3f/K4f; it does not pick a route. Moving the wire to the outside face may change what it computes, so that is not assumed to be safe.
- **Moved to cycle 165:** tightening the PB gate, clearing the fp-86 entry in the gate false-positive queue, re-pinning the self-tests, and the function-description batch. This is the last hand-back round, so the LabVIEW deliverable goes first.

`tools/bench/next.json` is rewritten and passes validation. The `## NEXT` section in `STATUS.md` and two lines in `docs/d1/INDEX.md` are updated. The runner will now start round 3 of the assignment session.

**Needs authorizing:** several connectors need sign-in before they can be used: Figma (in your claude.ai connector settings) and the data plugins amplitude, amplitude-eu, atlassian, bigquery and hex (through `claude mcp` or `/mcp` in an interactive session). The `definite` connector failed to connect. None of these were needed in this cycle.

## GROUND TRUTH 2 - what the real judge wrote to next.json
{"file_path": "G:\\Codes\\LabVIEW_Codes\\MinLab\\zz_LabView VI\\AAA_UNIST\\2. Tracking\\V6_ParallelLoop\\tools\\bench\\next.json", "content": "{\n \"schema\": \"next/1\",\n \"cycle\": 164,\n \"act\": \"P5 step 4 round 3 (PD399): group J gets the P4 delete form (delete_wire w23460 first, RLE w23519 after delete_object #23501) -> plan_ring_p5s02d = J+K3 (MAIN<=675) -> gates + prior-art release -> ONE scratch on a copy of 564d8cbe -> adopt D1_ring_p5s02d; offline beside it: K3f/K4f inner-face facts\",\n \"task_kind\": \"build\",\n \"plan\": {\n  \"path\": \"docs/d1/ring-p5c.md\",\n  \"md5\": \"1611e1e7d521453b6db49d51135ba99b\"\n },\n \"pass\": [\n  \"Inputs hashed first and quoted: VI 564d8cbe, graph 3d5196ab, EL 26d45c71, memory_model 8fb432e4, r_in 4d93c82d, plan_ring_p5s02d 872822f3\",\n  \"Gates quoted from graph 3d5196ab BEFORE the edit: w23460 endpoints all on #23042/#23501 terminals; w23519 keeps >= 1 sink outside #23042 and #23501 (PD399(a))\",\n  \"plan_ring_p5s02r_in.json group J: NEW delete_wire w23460 after A53 and before A54, NEW wire_remove_loose_ends w23519 after A55; JSON compare vs 4d93c82d = exactly these 2 added actions; old -> new md5\",\n  \"plan_ring_p5s02d.json on 3d5196ab = J (10 rows) + K3 (A61..A69), final True, X10 MAIN <= 675 quoted (J alone if J+K3 > 675); K3f/K4/K4f not in it\",\n  \"stagesim end graph of the plan: w23460 absent and w23519 sinks exactly {t23450, t23241, t7606}, quoted; any other result = hand back\",\n  \"Recipe pair stage_d1_ring_p5s02d{,_scratch}.py = step-3 recipe inputs on the shared stagekit gates, re-made on the new plan\",\n  \"Dry of both PASS or PASS-UNVERIFIED (CEN2 only); PB rows quoted; a PB block = hand back with the row, no class added\",\n  \"prerun PASS; --check-launch PASS (launch card names 'DRY-UNVERIFIED-OK: CEN2 new-object census' if CEN2-only); --scratch-required exit quoted\",\n  \"Predicted step-4-end Error List from 26d45c71: items cited to actions, rest named UNPREDICTED; file + md5\",\n  \"Prior-art review c164-a2-3 released by FIXED: lines under '## What was done with it' (A1 -> the new plan rows, A3 -> docs/d1/ring-p5c.md:57), or a new review on the re-made plan with verdict novel; STOP RECORDs on both recipes cleared (quote check_launch)\",\n  \"ONE scratch on a NEW byte copy of 564d8cbe: peak <= 675 and every BLOCK gate PASS quoted; else RETURN, no 2nd run\",\n  \"On PASS adopt claudeDev D1_ring_p5s02d_<ts>.vi (in-between, not counted); md5\",\n  \"Adopted file: graph read + md5; w23519 real sinks quoted vs the stagesim prediction; full Error List vs prediction item by item\",\n  \"memory_model.json: ONLY one load_by_vi entry for the adopted md5 (MB line cited); other keys equal, fail_above_mb 680\",\n  \"Measured census written into plan_ring_p5s02d_pred.json by a script citing the graph reads; census keys only; md5s\",\n  \"Offline facts card (labview none), PD399(c): w_k3f/w_k4f design rows + their PD374/PD379 source; what sits on t8776/t24342 in 3d5196ab; any adopted stage that wired an inner tunnel face (log cite or 'none found'); whether an outer-face rewrite carries the same value into the same frame -- facts only, no route chosen\",\n  \"Originals not opened; eb1d0f31, 7f2582ae, 94ffff94, f9ae7751, 564d8cbe unchanged; LabVIEW closed and verified gone\"\n ],\n \"blocked_by\": null,\n \"stop_requested\": false,\n \"advances\": [\n  \"M3\",\n  \"M8\",\n  \"R1\"\n ],\n \"note\": \"Hand-back 164-2 accepted: prior-art review right (PD321(b)/PD323(a) delete form; PD397(d) line 57 corrected). K3f unroutable inner face -> step 5. PD397(e) PB tightening, fp-86 drain, re-pins, fn batch deferred to cycle 165 (last round of 3). gates_due: violations answered by PD397(d)/(e); gate-fp hook entries -> chat; retro-undisposed stale (retro163:518).\"\n}\n"}

{"replace_all": false, "file_path": "G:\\Codes\\LabVIEW_Codes\\MinLab\\zz_LabView VI\\AAA_UNIST\\2. Tracking\\V6_ParallelLoop\\tools\\bench\\next.json", "old_string": "\"act\": \"P5 step 4 round 3 (PD399): group J gets the P4 delete form (delete_wire w23460 first, RLE w23519 after delete_object #23501) -> plan_ring_p5s02d = J+K3 (MAIN<=675) -> gates + prior-art release -> ONE scratch on a copy of 564d8cbe -> adopt D1_ring_p5s02d; offline beside it: K3f/K4f inner-face facts\",", "new_string": "\"act\": \"P5 step 4 round 3 (PD399): J in P4 delete form (dw w23460, RLE w23519) -> p5s02d = J+K3 -> gates + prior-art release -> ONE scratch on copy of 564d8cbe -> adopt; offline: K3f/K4f facts\","}

{"replace_all": false, "file_path": "G:\\Codes\\LabVIEW_Codes\\MinLab\\zz_LabView VI\\AAA_UNIST\\2. Tracking\\V6_ParallelLoop\\tools\\bench\\next.json", "old_string": "  \"Prior-art review c164-a2-3 released by FIXED: lines under '## What was done with it' (A1 -> the new plan rows, A3 -> docs/d1/ring-p5c.md:57), or a new review on the re-made plan with verdict novel; STOP RECORDs on both recipes cleared (quote check_launch)\",", "new_string": "  \"Prior-art c164-a2-3 released: FIXED: lines (A1 -> new plan rows, A3 -> docs/d1/ring-p5c.md:57) or a new review novel; both recipes' STOP RECORDs cleared (check_launch quoted)\","}

{"replace_all": false, "file_path": "G:\\Codes\\LabVIEW_Codes\\MinLab\\zz_LabView VI\\AAA_UNIST\\2. Tracking\\V6_ParallelLoop\\tools\\bench\\next.json", "old_string": "  \"Offline facts card (labview none), PD399(c): w_k3f/w_k4f design rows + their PD374/PD379 source; what sits on t8776/t24342 in 3d5196ab; any adopted stage that wired an inner tunnel face (log cite or 'none found'); whether an outer-face rewrite carries the same value into the same frame -- facts only, no route chosen\",", "new_string": "  \"Offline facts file per PD399(c) (labview none): w_k3f/w_k4f design + source PD; t8776/t24342 contents; prior inner-face wiring (cite or none); outer-face value/frame match. No route chosen\","}

{"replace_all": false, "file_path": "G:\\Codes\\LabVIEW_Codes\\MinLab\\zz_LabView VI\\AAA_UNIST\\2. Tracking\\V6_ParallelLoop\\tools\\bench\\next.json", "old_string": "\"note\": \"Hand-back 164-2 accepted: prior-art review right (PD321(b)/PD323(a) delete form; PD397(d) line 57 corrected). K3f unroutable inner face -> step 5. PD397(e) PB tightening, fp-86 drain, re-pins, fn batch deferred to cycle 165 (last round of 3). gates_due: violations answered by PD397(d)/(e); gate-fp hook entries -> chat; retro-undisposed stale (retro163:518).\"", "new_string": "\"note\": \"Hand-back 164-2 accepted: prior-art right (PD323(a) delete form; ring-p5c.md:57 corrected). K3f inner face unroutable -> step 5. PB tightening, fp-86, re-pins, fn batch -> cycle 165. gates_due: violations per PD397(d)/(e); hook gate-fps -> chat; retro-undisposed stale.\""}

## GROUND TRUTH 3 - what the NEXT assignment round then found (runner_supervisor.log:551 ASSIGN cycle 164 round 3 end -> PURPOSE_MET, all 17 pass items met)
### cards/assign_result_164_3.json
{
 "schema": "assign-result/1",
 "cycle": 164,
 "round": 3,
 "status": "PURPOSE_MET",
 "cards": [
  "164-3-1", "164-3-2", "164-3-3", "164-3-4", "164-3-6", "164-3-5", "164-3-7"
 ],
 "pass_evidence": [
  {"item": 0, "met": true, "evidence": ["tools/bench/diag_c164_a3_1_facts.md 7b0ec0d4", "tools/bench/diag_c164_a3_5_facts.md:9 hashes before 11/0"]},
  {"item": 1, "met": true, "evidence": ["tools/bench/diag_c164_a3_1_facts.md 7b0ec0d4", "tools/bench/diag_c164_a3_3_facts.md 08beb042"]},
  {"item": 2, "met": true, "evidence": ["tools/bench/diag_c164_a3_1_facts.md 7b0ec0d4", "plan_ring_p5s02r_in.json 9dadb0c1, aside copy plan_ring_p5s02r_in_pre164r3.json 4d93c82d"]},
  {"item": 3, "met": true, "evidence": ["tools/bench/plan_ring_p5s02d.json 97837e2a final True, 19 rows A53..A71, MAIN 647.8 <= 675", "tools/bench/diag_c164_a3_6_facts.md:6-15"]},
  {"item": 4, "met": true, "evidence": ["diag_c164_a3_6_facts.md:12-13 END w23460 0 rows; w23519 src t8494 sinks {23450, 23241, 7606}"]},
  {"item": 5, "met": true, "evidence": ["tools/recipes/stage_d1_ring_p5s02d.py f3581d02", "tools/recipes/stage_d1_ring_p5s02d_scratch.py 3d77e914", "diag_c164_a3_6_facts.md:23"]},
  {"item": 6, "met": true, "evidence": ["diag_c164_a3_6_facts.md:24-26 dry PASS-UNVERIFIED (CEN2 only) both recipes; PB 31/31 PASS, 5 RECORD rows"]},
  {"item": 7, "met": true, "evidence": ["diag_c164_a3_6_facts.md:27-30 prerun PASS 16/0, --scratch-required rc 3", "diag_c164_a3_5_facts.md:10 check_launch ALLOW on recipe and brief form"]},
  {"item": 8, "met": true, "evidence": ["tools/bench/errorlist_predicted_D1_ring_p5s02d_end.json 2c1edf78 from 26d45c71", "diag_c164_a3_6_facts.md:17-19 cleared 0 raised 0 unpredicted 3 standing 53"]},
  {"item": 9, "met": true, "evidence": ["diag_c164_a3_6_facts.md:35-36 prior art c164-a2-3 released by FIXED lines; STOP RECORDs of both recipes released"]},
  {"item": 10, "met": true, "evidence": ["diag_c164_a3_5_facts.md:12-17 ONE scratch PASS 21/0, peak 652.6 <= 675, GATE MEM PASS, E1 0 at 9 checkpoints, PB 31/31"]},
  {"item": 11, "met": true, "evidence": ["claudeDev D1_ring_p5s02d_20261010_152518.vi md5 6dcd5c3d506f69947a5ce259ccbe2221", "diag_c164_a3_5_facts.md:20-21; adopted_scratch.jsonl 332e9ca6 -> 8d7a8651"]},
  {"item": 12, "met": true, "evidence": ["graph_ring_p5s02d_20261010_154830.json 2a5fa0c4; w23460 absent; w23519 real sinks {t23450, t23241, t7606} == prediction", "Error List 53 == pred 2c1edf78, extra 0 missing 0 (diag_c164_a3_5_facts.md:22-25)", "E5 by uid failed on LabVIEW re-use of 23501; by identity every deleted node is gone (diag_c164_a3_7_facts.md, prep_c164_a3_7_ident.log:5-10)"]},
  {"item": 13, "met": true, "evidence": ["tools/bench/memory_model.json 8fb432e4 -> ff0fabca: one load_by_vi key 6dcd5c3d = 603.9, fail_above_mb 680.0 (prep_c164_a3_7_write.log:13,18)"]},
  {"item": 14, "met": true, "evidence": ["tools/bench/plan_ring_p5s02d_pred.json 87a65b89 -> 5a7bfc81, census keys only from scratch log :223 (prep_c164_a3_7_write.log:14,19)"]},
  {"item": 15, "met": true, "evidence": ["tools/bench/diag_c164_a3_2_facts.md 0312feb4 K3f/K4f inner-face facts, no route chosen"]},
  {"item": 16, "met": true, "evidence": ["originals eb1d0f31, 7f2582ae, 94ffff94, f9ae7751, 564d8cbe hashed unchanged (diag_c164_a3_5_hash_after.log 11/0; prep_c164_a3_7_write.log:10,29)", "tasklist shows 0 LabVIEW processes"]}
 ],
 "handback": null,
 "note": "Assumptions to overturn: (1) END1 'w23460 absent' read as 0 terminal rows (stagesim keeps the Wire object; real graphs drop it; real w23460 is absent). (2) plan_in renamed plan_ring_p5s02d_in2.json to satisfy gate L0. (3) E5 deletes-by-uid failed on LabVIEW uid re-use (#23501, #23481); accepted via an identity check, not by editing the gate; fp-87/fp-88 queued, detectors unfixed. Step-4 file is an in-between, not counted toward the cap of 6."
}


## ANSWER A
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

## ANSWER B
**Decision for cycle 164's hand-back 2 (round 3 of 3):** the prior-art review is right, so it is accepted, not refuted. Group J will be removed the same way P4 removed its scaffold nodes (PD321(b)/PD323(a)). Step 4 becomes J + K3. K3f and K4f are measured before anyone plans them.

What the record shows:
- **Deleting group J as planned would break live wiring.** The delete form is not the settled P4 one:
  - w23460 has no end outside the two deleted nodes (`diag_c164_a2_4_facts.md:4`). P4's form requires `delete_wire` before `delete_object` for such a wire (`ring-p4b.md:23-24`).
  - w23519 must NOT be deleted: three of its four sinks are live (`:3`). After `delete_object #23501` it only needs its loose ends removed. It keeps 3 sinks, so the P4 error 1055 (a loose-end removal on a wire with no remaining sink) cannot happen there.
  - PD397(d)'s line "`delete_object` has no passing launch yet" was wrong: it passed in P4 (`diag_c140_3_facts.md:14,22`). That line needs correcting at `ring-p5c.md:57`.
- **K3f and K4f cannot be planned yet.** Both connect to the inside face of an existing loop tunnel (#8776 and #24342). No tool route reaches that face (`stagexec.py:1930`), and each face still holds a dead stub wire. Changing them to connect from the outside face could change what is computed, so I won't assume it is equivalent. An offline facts card comes first.
- **J + K3 fits the memory limit.** It measured 642.5 MB against the 675 MB limit with 17 rows (`diag_c164_a2_1_facts.md:22`); the two added rows are cheap.
- **Tooling waits for the next cycle.** This is the last hand-back round, and the LabVIEW deliverable goes first. That covers the stricter check rules from PD397(e), the fp-86 drain, re-pinning the tests, and the batch of function descriptions.

As the judgement session I would also write PD399 into `docs/d1/ring-p5c.md`, fix line 57, add the INDEX line, and rewrite STATUS `## NEXT`. Per the BENCH instruction, no file was written.

`plan.md5` cannot be filled in here: shell access is disabled in this session, and it must be the md5 of `ring-p5c.md` after the PD399 write.

```json
{
 "schema": "next/1",
 "cycle": 164,
 "act": "Round 3/3 (PD399): J in P4 delete form (+delete_wire w23460, +RLE w23519) -> plan_ring_p5s02d = J+K3 -> gates -> ONE scratch on copy of 564d8cbe -> adopt p5s02d; then K3f/K4f facts",
 "task_kind": "build",
 "plan": {
  "path": "docs/d1/ring-p5c.md",
  "md5": "<md5 of ring-p5c.md after the PD399 write>"
 },
 "pass": [
  "Inputs re-hashed and quoted: VI 564d8cbe, graph 3d5196ab, EL 26d45c71, memory_model 8fb432e4, r_in 4d93c82d, stagekit dd57c1ca, stagexec a4df7e15, stagesim 95a162ba; drift = hand back",
  "Gates quoted from 3d5196ab before the edit: w23460 ends all on #23042/#23501 terminals; w23519 keeps sinks t23450, t23241, t7606 outside both nodes",
  "r_in group J per PD399(a): delete_wire w23489, NEW delete_wire w23460, delete_object #23042, #23501, NEW wire_remove_loose_ends w23519, A56..A60; JSON vs 4d93c82d = 2 added actions",
  "plan_ring_p5s02d.json = J + K3 (A61..A69) on 3d5196ab via shared mapping + stage_shared; SB REALSIM final True, 0 UNROUTABLE; X10 MAIN <= 675 quoted (J alone if over)",
  "Every delete_wire a checkpoint; stagesim end graph: w23460 absent, w23519 sinks == {t23450, t23241, t7606} exactly; anything else = hand back",
  "Recipe pair stage_d1_ring_p5s02d{,_scratch}.py as inputs on the shared gates; dry both PASS or PASS-UNVERIFIED (CEN2 only); PB rows quoted; PB block = hand back",
  "prerun PASS (X10/X14/X17/X8); --check-launch PASS, launch card names DRY-UNVERIFIED-OK: CEN2 new-object census; --scratch-required exit quoted",
  "Predicted step-4 Error List from 26d45c71: cleared/raised items cited to actions, rest named UNPREDICTED; file + md5",
  "Prior-art: c164-a2-3 review released by FIXED: lines citing the r_in edit and PD399, or a new review novel + disposition; card flags.peers include priorart",
  "ONE scratch on a NEW byte copy of 564d8cbe; SCRATCH- peak + GATE MEM quoted: peak <= 675, every BLOCK gate PASS, RLE w23519 no error; else RETURN, no 2nd run",
  "On PASS adopt claudeDev D1_ring_p5s02d_<ts>.vi (in-between, not counted); hashlib md5; graph read + md5 shows w23460 absent, w23519 sinks as predicted",
  "Adopted file: full Error List compared with the prediction item by item; extra/missing items listed",
  "tools/bench/memory_model.json: ONLY one load_by_vi entry for the adopted md5 (post-load MB line cited); all other keys equal incl. fail_above_mb 680, JSON compare",
  "Measured census written into plan_ring_p5s02d_pred.json by a script citing the graph reads; census keys only; old -> new md5",
  "AFTER the LabVIEW card, offline facts only (PD399(c)): w_k3f/w_k4f design + PD374/PD379 source, stubs w10362/w25232 on t8776/t24342 in 3d5196ab",
  "Same facts card: any adopted stage that wired an inner loop-tunnel face (log cite or 'none found'); whether an outer-face rewrite carries the same value (facts, no plan)",
  "Originals not opened; eb1d0f31, 7f2582ae, 94ffff94, f9ae7751, 564d8cbe hashed unchanged; LabVIEW closed and verified gone at card end"
 ],
 "blocked_by": null,
 "stop_requested": false,
 "advances": ["M3", "M8", "R1"],
 "note": "Hand-back 2 judged (PD399): prior-art right (J delete form, delete_object passed in P4); step 4 = J+K3; K3f/K4f measured first; PD397(e) PB tightening, fp-86, re-pins, fn batch -> cycle 165. Last round."
}
```