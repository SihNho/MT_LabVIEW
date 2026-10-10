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