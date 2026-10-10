# Blind case 165_1

## GROUND TRUTH 1 - what the real judge decided (its final message)
I wrote a revised purpose for cycle 165 after its first hand-back, so the runner will start a new assignment round from it.

**Why it came back:** the assignment session's card (165-1-1) stopped on one item. The earlier run I had cited as proof (`diag_c161_p5s02b_scratch.log:97`) connects a wire from a source that had no wire yet. The next step needs it to work from a source that is already wired, so that citation was my error.

**What I decided (PD401 in `docs/d1/ring-p5c.md:181`, linked from `docs/d1/INDEX.md`):**
- **Accepted:** the other six of the card's seven checks, all done offline with LabVIEW never started:
  - The two stub-wire checks pass on graph 2a5fa0c4.
  - The new `stagexec.loop_inner_face_sink` (md5 6ea6637f) passes its self-test 25/0.
  - The six stored plans compile unchanged.
  - The plan input gained exactly two `delete_wire` rows (now 0b895983).
- **Proof that now counts:** `diag_c127_1_fsinner.log:81-102`. There, three connects from an already-wired source each joined the existing wire (same wire id, no new objects, nothing broken). It doesn't cover the exact terminal types used here. Those are checked by the step-5 scratch run itself, which runs on a byte copy and returns at the first surprise. No separate test VI is owed, because that rule only applies after two stage runs fail on the same function.
- **Tool change kept:** the card changed `stagexec` before checking the proof, which was out of order, but the change is self-tested and alters no stored plan.
- **Stale card:** card 160-c3-2 is closed with a result file so the write check stops flagging it.

**New purpose (`tools/bench/next.json`, passes `protocol.py validate`):**
1. Re-hash the inputs.
2. Build the step-5 plan on 2a5fa0c4 (groups K3f, K4, K4f, within the 675 MB memory limit).
3. Run the gates and the prior-art review.
4. Run one scratch build on a fresh byte copy of `6dcd5c3d`. For each new wire it must show: no wire left after the delete, no unexpected new objects, the terminal joined to the right wire, and nothing broken.
5. Adopt the result: `D1_ring_p5_<ts>.vi` if it reaches A80, otherwise `D1_ring_p5s02e_<ts>.vi`.
6. Then the checker tightening and the gate false-positive drains (fp-86/87/88).

STATUS.md's NEXT section says the same. I ran no retrospective, as the purpose flow requires.

## GROUND TRUTH 2 - what the real judge wrote to next.json
{"file_path": "G:\\Codes\\LabVIEW_Codes\\MinLab\\zz_LabView VI\\AAA_UNIST\\2. Tracking\\V6_ParallelLoop\\tools\\bench\\next.json", "content": "{\n \"schema\": \"next/1\",\n \"cycle\": 165,\n \"act\": \"P5 step 5 (PD400, PD401): route + r_in done by 165-1-1 (kept); precedent = diag_c127_1_fsinner.log:81-102, face-class residue checked by the scratch itself -> K3f K4 K4f plan on 2a5fa0c4 -> gates -> ONE scratch on copy of 6dcd5c3d -> adopt; then PB/E5 tooling\",\n \"task_kind\": \"build\",\n \"plan\": {\n  \"path\": \"docs/d1/ring-p5c.md\",\n  \"md5\": \"5bf39c6198acdd2a43d292593c571ca8\"\n },\n \"pass\": [\n  \"Already met by 165-1-1, cite only (PD401): inputs hashed (diag_c165_a1_1_facts.md:8-14); stub gates (:15-17); route stagexec 6ea6637f (:26-33); self-test 25/0 (selftest_c165_innerface.log:68); stored plans byte-equal (:40-43); r_in 0b895983 = 2 added delete_wire (:44-45). Re-hash stagexec, r_in, VI 6dcd5c3d, graph 2a5fa0c4 before planning; any drift = hand back\",\n  \"Precedent (PD401(a)): diag_c127_1_fsinner.log:81-102 quoted (wired source #32868, wire 32859 returned, census {}); no separate scratch-VI card\",\n  \"Stale open card 160-c3-2 closed by its result/1 citing PD401(c), validated; guard_write no longer reports it on a stagexec write\",\n  \"Step-5 plan on 2a5fa0c4, new:* bound from step 4's binding record (diag_c164_p5s02d_scratch.log STEPX bound lines): longest whole-group prefix of K3f, K4, K4f, X10 MAIN <= 675 from 6dcd5c3d, rows <= 40\",\n  \"Step-5 plan: every delete_wire a checkpoint, final True, MAIN quoted; A70/A80 predicted per PD401(b): census in [{}, {'Wire': 1}], face on OK3 / OK4.outer net, Is Broken? False\",\n  \"stagesim end graph: w10362 / w25232 absent; t8776 / t24342 on the OK3 / OK4.outer nets (groups in the plan), quoted\",\n  \"Recipe pair = step-4 recipe inputs on the shared stagekit gates; dry of both PASS or PASS-UNVERIFIED (CEN2 only); PB rows quoted; PB block = hand back\",\n  \"prerun PASS; --check-launch PASS ('DRY-UNVERIFIED-OK: CEN2 new-object census' if CEN2-only); --scratch-required exit quoted\",\n  \"Predicted step-5-end Error List from step 4's expected file (errorlist_expected_D1_ring_p5s02d_20261010_152518.json c74200f2): items cited to actions, rest UNPREDICTED; file + md5\",\n  \"Prior-art review of the step-5 plan: novel + disposition (flags.peers include priorart), or released by FIXED:/REFUTED: lines\",\n  \"ONE scratch on a NEW byte copy of 6dcd5c3d: peak <= 675, every BLOCK gate PASS, and per stub-delete + connect pair the PD401(b) facts (face wire 0 after delete; census; face on the OK net; Is Broken? False; EL delta) quoted; any other result = RETURN, no 2nd run\",\n  \"On PASS adopt claudeDev D1_ring_p5_<ts>.vi if it reaches A80 (P5 final, 6 of 6), else D1_ring_p5s02e_<ts>.vi (in-between); md5\",\n  \"Adopted file: graph read + md5; t8776 / t24342 real sources vs stagesim prediction; full Error List vs prediction item by item\",\n  \"memory_model.json: ONLY one load_by_vi entry for the adopted md5 (MB line cited); other keys equal, fail_above_mb 680\",\n  \"Measured census written into the step-5 pred by a script citing the graph reads; census keys only; md5s\",\n  \"AFTER the LabVIEW card: PD397(e) PB tightening (provenance, per-frame coverage, chain_tunnel_case newest-wins) + self-test incl. 3 negative cases\",\n  \"PB self-test: stored p5s02c / p5s02d / step-5 PB inputs still RECORD every row; then fp-86 drained citing line + self-test\",\n  \"E5 + reuse detectors judge a deleted node by identity (class, owner, owner uid, pos) in the shared module; self-test on step-4 data, planted survivor caught\",\n  \"fp-87 and fp-88 drained citing line + self-test\",\n  \"Gate-run suites re-pinned once after the stagekit/stagexec changes (names listed); one fn-descriptions batch (~60) into docs/fn_descriptions.json\",\n  \"Originals not opened; eb1d0f31, 7f2582ae, 94ffff94, f9ae7751, 564d8cbe, 6dcd5c3d unchanged; LabVIEW closed and verified gone\"\n ],\n \"blocked_by\": null,\n \"stop_requested\": false,\n \"advances\": [\n  \"M3\",\n  \"M8\",\n  \"R1\"\n ],\n \"note\": \"Hand-back 1 judged (PD401): 165-1-1 items 0-4,6 accepted; PD400(b)'s precedent was from an unwired source; c127 FS-inner run is the wired-source precedent; face-class residue = the step-5 scratch's own check (byte copy, return on first surprise). stagexec 6ea6637f kept. Hook gate-fps -> chat. A80 reached -> cycle 166 = P6 run.\"\n}\n"}

{"replace_all": false, "file_path": "G:\\Codes\\LabVIEW_Codes\\MinLab\\zz_LabView VI\\AAA_UNIST\\2. Tracking\\V6_ParallelLoop\\tools\\bench\\next.json", "old_string": "\"P5 step 5 (PD400, PD401): route + r_in done by 165-1-1 (kept); precedent = diag_c127_1_fsinner.log:81-102, face-class residue checked by the scratch itself -> K3f K4 K4f plan on 2a5fa0c4 -> gates -> ONE scratch on copy of 6dcd5c3d -> adopt; then PB/E5 tooling\"", "new_string": "\"P5 step 5 (PD400/PD401): route+r_in kept from 165-1-1; precedent c127 -> K3f K4 K4f plan on 2a5fa0c4 -> gates -> ONE scratch on copy of 6dcd5c3d -> adopt; then PB/E5 tooling\""}

{"replace_all": false, "file_path": "G:\\Codes\\LabVIEW_Codes\\MinLab\\zz_LabView VI\\AAA_UNIST\\2. Tracking\\V6_ParallelLoop\\tools\\bench\\next.json", "old_string": "  \"Already met by 165-1-1, cite only (PD401): inputs hashed (diag_c165_a1_1_facts.md:8-14); stub gates (:15-17); route stagexec 6ea6637f (:26-33); self-test 25/0 (selftest_c165_innerface.log:68); stored plans byte-equal (:40-43); r_in 0b895983 = 2 added delete_wire (:44-45). Re-hash stagexec, r_in, VI 6dcd5c3d, graph 2a5fa0c4 before planning; any drift = hand back\",", "new_string": "  \"Met by 165-1-1, cite only (PD401): diag_c165_a1_1_facts.md:8-17 hashes+stub gates, :26-45 route 6ea6637f, self-test 25/0, plans byte-equal, r_in 0b895983\",\n  \"Re-hash stagexec 6ea6637f, r_in 0b895983, VI 6dcd5c3d, graph 2a5fa0c4 before planning; any drift = hand back\","}

{"replace_all": false, "file_path": "G:\\Codes\\LabVIEW_Codes\\MinLab\\zz_LabView VI\\AAA_UNIST\\2. Tracking\\V6_ParallelLoop\\tools\\bench\\next.json", "old_string": "  \"ONE scratch on a NEW byte copy of 6dcd5c3d: peak <= 675, every BLOCK gate PASS, and per stub-delete + connect pair the PD401(b) facts (face wire 0 after delete; census; face on the OK net; Is Broken? False; EL delta) quoted; any other result = RETURN, no 2nd run\",", "new_string": "  \"ONE scratch on a NEW byte copy of 6dcd5c3d: peak <= 675 and every BLOCK gate PASS quoted; else RETURN, no 2nd run\",\n  \"Scratch, per stub-delete + connect pair: PD401(b) facts quoted (wire 0 after delete, census, face on OK net, not broken, EL delta); other = RETURN\","}

{"replace_all": false, "file_path": "G:\\Codes\\LabVIEW_Codes\\MinLab\\zz_LabView VI\\AAA_UNIST\\2. Tracking\\V6_ParallelLoop\\tools\\bench\\next.json", "old_string": "bound from step 4's binding record (diag_c164_p5s02d_scratch.log STEPX bound lines)", "new_string": "bound from step 4's binding record (diag_c164_p5s02d_scratch.log)"}

{"replace_all": false, "file_path": "G:\\Codes\\LabVIEW_Codes\\MinLab\\zz_LabView VI\\AAA_UNIST\\2. Tracking\\V6_ParallelLoop\\tools\\bench\\next.json", "old_string": "\"Hand-back 1 judged (PD401): 165-1-1 items 0-4,6 accepted; PD400(b)'s precedent was from an unwired source; c127 FS-inner run is the wired-source precedent; face-class residue = the step-5 scratch's own check (byte copy, return on first surprise). stagexec 6ea6637f kept. Hook gate-fps -> chat. A80 reached -> cycle 166 = P6 run.\"", "new_string": "\"Hand-back 1 judged (PD401): 165-1-1 items 0-4,6 accepted; c127 FS-inner run is the wired-source precedent; face-class residue = the step-5 scratch's own check. stagexec 6ea6637f kept. Hook gate-fps -> chat. A80 reached -> cycle 166 = P6 run.\""}

## GROUND TRUTH 3 - what the NEXT assignment round then found (runner_supervisor.log ASSIGN cycle 165 round 2 -> HANDBACK (route check refuses inner faces))
### cards/handback_165_2.json
{
 "schema": "handback/1",
 "cycle": 165,
 "round": 2,
 "trigger": "session",
 "detail": "165-2-1 FAIL: route check refuses connects onto inner faces t8776/t24342 (UNROUTABLE 2, mk.log:68,75). Face still wired by stub at base, so stagexec.py:1934 refuses; fix edits pinned stagexec 6ea6637f.",
 "cards": [
  {
   "id": "165-2-1",
   "status": "FAIL",
   "first_fail": "SB REALSIM FINAL: route check FAIL, UNROUTABLE 2 (w_k3f #8776, w_k4f #24342: 'INNER face of LoopTunnel ... only the outer face's owner route is measured')",
   "class": "ff:sb realsim final: route check fail, unroutable 2 (w_k3f #, w",
   "retry_of_card": null
  }
 ],
 "assign_result": "tools/bench/cards/assign_result_165_2.json",
 "next_md5": "d7373d95dbf4f2f5ebd41b19e130b176",
 "cost_usd": 5.981317799999999,
 "minutes": 12.0
}

### cycle_165_handback_2.log
I've judged hand-back 2 and revised the purpose. Cycle 165 now starts its third and last assignment round.

- **What went wrong:** card 165-2-1 sized step 5 to the full set of three groups, K3f, K4 and K4f. That is 13 rows at MAIN 665.0, under the 675 limit, and all 13 replay in the simulator. The plan still would not finalize, because the route check returned UNROUTABLE 2.
- **Why:** a check that runs before the first operation (PRIME, `tools/stagexec.py:2620-2642`) proves every wired end on the starting graph. The two inner faces still hold their stub wires there, so it refuses them at `:1934`, before the plan's own stub deletes run. A real launch would stop at the same place. The per-step route was already correct. The gap is mine: PD400(b) asked 165-1-1 to test compile and the per-step route, not this check.
- **The fix (PD402, `docs/d1/ring-p5c.md:206`):** the check skips an end only when it is a loop-tunnel inner face used as a sink, and its starting wire is removed by an earlier, checkpointed `delete_wire` in the same plan. Every skip is logged.
- **How it is tested:** on the step-4 graph the plan must finalize with 0 unroutable rows. Four negative cases must still be refused, and the six stored plans must compile byte-equal.
- **After that:** the step-5 plan, its gates and the prior-art review, then one scratch run on a copy of the step-4 file. If the run reaches A80, the result is adopted as the P5 final file and cycle 166 runs P6.
- **If it fails:** a failed self-test or a returned scratch run closes the cycle on this purpose.

I validated `tools/bench/next.json`, updated the index entry in `docs/d1/INDEX.md`, and rewrote the NEXT section of `STATUS.md`. Nothing is waiting on you.

## ANSWER A
I'd write a revised next.json, which starts hand-back round 2 of 3. The decision: card 165-1-1's offline work stands, the c127 run counts as the precedent for connecting from an already-wired source, and the step-5 scratch run is where the new loop-tunnel inner-face case gets measured. No separate LabVIEW experiment is added.

**Hand-back 165-1 judged (this would be PD401 in `docs/d1/ring-p5c.md`):**
- **Accepted:** items 0–4 and 6 of the round-1 purpose.
  - The stub checks pass on graph 2a5fa0c4.
  - The new `stagexec.loop_inner_face_sink` (stagexec 6ea6637f) passes its self-test 25/0, and the 6 stored plans compile and dry-run byte-equal.
  - The regression suites pass: c157 13/0, c158 24/0, stagesim 106/0, stagexec 141/0.
  - The plan-input file gains exactly the 2 `delete_wire` rows (9dadb0c1 → 0b895983).
  - The change was made before the precedent check ran. The byte-equal results make that slip harmless, so I keep 6ea6637f and don't revert.
- **The precedent question:** I cited `diag_c161_p5s02b_scratch.log:97`, but its source #3934 had no wire, so the citation was wrong.
  - `diag_c127_1_fsinner.log:81-102` does show what `connect_term_uid` does from a source that already has a wire, on LabVIEW itself. Three connects all returned the existing wire 32859, with no new wires (census `{}`), so it branches onto that wire.
  - That run used a different face class, a Flat Sequence inner face. The new part here is the sink: an inner face of a loop tunnel. The plan has no earlier run of that.
  - Same rule as PD390: the step-5 scratch run on a byte copy measures it, with a stated prediction for each delete-and-connect pair. A result that differs means the card returns.
- **Card 160-c3-2:** it is a closed cycle-160 card, and its stagexec pin (ddf23a31) was already stale before this round. By PD396(a)(4) it is history: retire it, don't re-pin it.

```json
{
 "schema": "next/1",
 "cycle": 165,
 "act": "Round 2/3 (PD401): keep stagexec 6ea6637f; c127 = wired-source precedent -> step-5 plan K3f K4 K4f on 2a5fa0c4 -> gates -> ONE scratch on copy of 6dcd5c3d -> adopt -> tooling",
 "task_kind": "build",
 "plan": {
  "path": "docs/d1/ring-p5c.md",
  "md5": "<md5 after the PD401 append>"
 },
 "pass": [
  "Met by 165-1-1, cite only (PD401): diag_c165_a1_1_facts.md §1-§6; selftest_c165_innerface.log:68 25/0; r_in 0b895983",
  "Re-hash stagexec 6ea6637f, r_in 0b895983, VI 6dcd5c3d, graph 2a5fa0c4, EL c74200f2, memory_model ff0fabca before use; any drift = hand back",
  "Card 160-c3-2 retired as history per PD396(a)(4) (no re-pin); guard_write no longer flags it, quoted",
  "Step-5 plan on 2a5fa0c4, new:* from diag_c164_p5s02d_scratch.log bindings: longest whole-group prefix of K3f, K4, K4f, MAIN <= 675 from 6dcd5c3d, rows <= 40",
  "Step-5 plan: every delete_wire a checkpoint, final True, MAIN quoted",
  "A70/A80 predicted per PD401: face wire 0 after the stub delete, then a branch onto the OK3/OK4.outer wire (c127: same wire back), census {}, not broken",
  "stagesim end graph: w10362 / w25232 absent; t8776 / t24342 on the OK3 / OK4.outer nets, quoted",
  "Recipe pair = step-4 recipe inputs on the shared stagekit gates; dry both PASS or PASS-UNVERIFIED (CEN2 only); PB rows quoted; PB block = hand back",
  "prerun PASS; --check-launch PASS ('DRY-UNVERIFIED-OK: CEN2 new-object census' if CEN2-only); --scratch-required exit quoted",
  "Predicted step-5-end Error List from c74200f2: items cited to actions, rest UNPREDICTED; file + md5",
  "Prior-art review of the step-5 plan incl. loop_inner_face_sink: novel + disposition (flags.peers include priorart), or FIXED:/REFUTED: lines",
  "ONE scratch on a NEW byte copy of 6dcd5c3d: peak <= 675 and every BLOCK gate PASS quoted; else RETURN, no 2nd run",
  "Scratch, per stub-delete + connect pair: wire 0 after the delete, connect census, face on the OK net, not broken, quoted vs PD401; any other result = RETURN",
  "On PASS adopt claudeDev D1_ring_p5_<ts>.vi if A80 is reached (P5 final, 6 of 6), else D1_ring_p5s02e_<ts>.vi (in-between); md5",
  "Adopted file: graph read + md5; t8776 / t24342 real sources vs stagesim prediction; full Error List vs prediction item by item",
  "memory_model.json: ONLY one load_by_vi entry for the adopted md5 (MB line cited); other keys equal, fail_above_mb 680",
  "Measured census written into the step-5 pred by a script citing the graph reads; census keys only; md5s",
  "AFTER the LabVIEW card: PD397(e) PB tightening + self-test (3 negatives); stored p5s02c/d + step-5 PB inputs still RECORD every row; fp-86 drained",
  "E5 + reuse detectors judge a deleted node by identity (class, owner, owner uid, pos) in the shared module; self-test, planted survivor caught; fp-87/88 drained",
  "Gate-run suites re-pinned once (names listed); one fn-descriptions batch (~60) into docs/fn_descriptions.json",
  "Originals not opened; eb1d0f31, 7f2582ae, 94ffff94, f9ae7751, 564d8cbe, 6dcd5c3d unchanged; LabVIEW closed and verified gone"
 ],
 "blocked_by": null,
 "stop_requested": false,
 "advances": ["M3", "M8", "R1"],
 "note": "Hand-back 165-1 judged (PD401): 165-1-1 items 0-4, 6 accepted; c161:97 citation was wrong, c127 = wired-source precedent; new sink face class measured by the scratch. Round 2/3. A80 reached -> cycle 166 = P6 run."
}
```

As the bench asked, I wrote no files. In a live run this round would also need:
- PD401 appended to `docs/d1/ring-p5c.md` and the plan md5 filled in, which is still a placeholder;
- a one-line link to PD401 in `docs/d1/INDEX.md`;
- STATUS.md's `## NEXT` rewritten to match;
- a check with `protocol.py validate`.

The next.json on disk already describes a later round 3 (PD402). I left it untouched.

## ANSWER B
I'm sending the purpose back to the assignment session with revised items (outcome 1), not closing the cycle and not asking you. The open question has an answer on file. This is a bench run, so I wrote nothing to disk; the `next.json` I would write is at the end.

## Hand-back 165_1: my decision

**What I accept from card 165-1-1.** The work was offline and LabVIEW never started. Purpose items 0–4 and 6 are met:
- **Stub checks:** both pass on graph 2a5fa0c4. Each stub wire has exactly one terminal row, and that row is the loop's inner face (t8776, t24342), not a source.
- **New routing function:** `stagexec.loop_inner_face_sink` (`tools/stagexec.py:6345`, md5 6ea6637f) passes its self-test 25/0 (`selftest_c165_innerface.log:68`).
- **No regressions:** the six stored plans compile and dry-run byte-equal, and the c157, c158, stagesim and stagexec self-tests all stay green.
- **Plan input:** r_in 9dadb0c1 → 0b895983 adds exactly the two `delete_wire` rows.

**(a) The precedent question.** The precedent PD400(b) cited, `diag_c161_p5s02b_scratch.log:97`, does not count: its source #3934 had no wire.

The one I put in force is `diag_c127_1_fsinner.log:81-99`. Three `connect_term_uid` calls from the already-wired source #32868 each returned the existing wire 32859. Each showed no new wires, census `{}`, and Is Broken? False (lines 82, 84, 89, 92, 94, 99). So a connect from a wired source branches onto its existing wire, which is the behaviour A70/A80 need.

It does not cover these face types: the source here is the outer terminal of SelectorTunnel #31803, and the sink is an unwired loop inner face. The step-5 scratch run checks that remaining gap itself, on a byte copy. A separate scratch-VI card is not owed, because that rule only applies after two stage runs fail on the same function, and none has.

**(b) The stagexec change stays.** It was made before the precedent was checked, which is out of order. I keep it because it is self-tested, changes no stored plan, and only the scratch run can use it.

**(c) Stale card 160-c3-2.** It has no result file and pins an old stagexec md5 (ddf23a31), so the write guard keeps flagging it. It gets closed with a `result/1` that names this decision.

**(d) A gap I found in the code.** The step that proves every wired plan end before op 1 (`stagexec.py:2621-2648`) checks ends at the starting state. At that point t8776 and t24342 still carry the stubs w10362 and w25232. So that step would very likely refuse them before the plan's own stub deletes run.

The 165-1-1 self-test only checked compile and the per-step route, so it would not catch this. I added it to the purpose: measure it first. If it refuses, a narrow skip is allowed only for a loop inner-face end whose stub an earlier checkpointed `delete_wire` removes. Four negative cases must still refuse.

**Ordering and other gates.**
- The LabVIEW deliverable comes first. The only tool items ahead of it are the ones the step-5 plan needs before it can compile or start.
- The open false-positive queue (20 entries) is drained after the LabVIEW card: fp-86, fp-87 and fp-88 only.
- Hook entries (fp-75, fp-80, fp-89, …) stay for the chat to handle with you.
- No user question is open, so there is no STOP.

**What I'd also do outside bench mode:** add PD401 to `docs/d1/ring-p5c.md` plus its line in `docs/d1/INDEX.md`, then re-hash the plan and quote the new md5 in `plan.md5`, rewrite STATUS.md's `## NEXT` to the same first act, and run `py tools/protocol.py validate tools/bench/next.json`.

```json
{
 "schema": "next/1",
 "cycle": 165,
 "act": "Round 2 (PD401): c127 precedent in force, stagexec 6ea6637f kept, stale card 160-c3-2 closed -> prove the step-5 plan passes the start-of-plan proof step (narrow skip only if it refuses the stub-holding faces) -> step-5 plan K3f K4 K4f on 2a5fa0c4 -> gates -> ONE scratch on a copy of 6dcd5c3d -> adopt -> tooling",
 "task_kind": "build",
 "plan": {
  "path": "docs/d1/ring-p5c.md",
  "md5": "<md5 after PD401 is written; re-hash before dispatch>"
 },
 "pass": [
  "Met by 165-1-1, cite only (PD401): diag_c165_a1_1_facts.md:8-45 (stub gates, loop_inner_face_sink 6ea6637f, selftest 25/0, 6 plans byte-equal, r_in 0b895983)",
  "Precedent quoted from diag_c127_1_fsinner.log:81-99 (3x connect_term_uid <- #32868 -> w32859, new wires [], census {}, Is Broken? False); diag_c161:97 not cited",
  "Re-hash stagexec 6ea6637f, r_in 0b895983, VI 6dcd5c3d, graph 2a5fa0c4, errorlist_expected c74200f2 before any edit; drift = hand back",
  "Card 160-c3-2 closed by its result/1 naming PD401(c); guard_write no longer reports it; no other card touched",
  "Measured: r_in step-5 plan in SB REALSIM finalize AND non-collect PRIME (stagexec.py:2621-2648) on 2a5fa0c4; refusals quoted verbatim or 'none'",
  "Only if PRIME refuses t8776/t24342: skip ONLY a LoopTunnel InnerTerminal sink whose base wire = wire_uid of an EARLIER checkpointed delete_wire; skip logged (end, wire, op); all other ends primed as before; new stagexec md5",
  "If changed: negatives still refuse (n1 no delete_wire, n2 delete of another wire, n3 delete after the connect, n4 wired SelectorTunnel / FS inner face); 6 stored plans compile + dry byte-equal; c157/c158/c165 innerface, stagesim, stagexec self-tests green, counts quoted",
  "plan_ring_p5s02e.json made on 2a5fa0c4, new:* bound by quoting diag_c164_p5s02d_scratch.log; longest prefix of whole groups K3f, K4, K4f with MAIN <= 675 from load_by_vi 6dcd5c3d, rows <= 40; MAIN per prefix quoted; final True",
  "Every delete_wire a checkpoint; per stub-delete + connect pair predicted per PD401(b): face wire 0 after delete, census in [{}, {'Wire': 1}], face on OK3 / OK4.outer net, Is Broken? False",
  "stagesim end graph: w10362 / w25232 absent; t8776 / t24342 on the OK3 / OK4.outer nets, quoted",
  "Recipe pair = step-4 recipe inputs on the shared stagekit gates; dry both PASS or PASS-UNVERIFIED (CEN2 only); PB rows quoted; PB block = hand back",
  "prerun PASS; --check-launch PASS (CEN2-only unverified allowed, card names DRY-UNVERIFIED-OK); --scratch-required exit quoted",
  "Predicted step-5 Error List from c74200f2: items cited to actions, rest UNPREDICTED; file + md5",
  "Prior-art review of the step-5 plan (new op on a new face class, + any PRIME change): novel + disposition (flags.peers include priorart), or released by FIXED:/REFUTED: lines",
  "ONE scratch on a NEW byte copy of 6dcd5c3d: peak <= 675, every BLOCK gate PASS; first unexpected result = finish the step, RETURN, no 2nd run",
  "Scratch per stub-delete + connect pair: PD401(b) facts quoted (wire 0 after delete, census, face on OK net, not broken, EL delta vs prediction)",
  "On PASS adopt claudeDev D1_ring_p5_<ts>.vi if A80 reached (P5 final, 6 of 6), else D1_ring_p5s02e_<ts>.vi; md5",
  "Adopted file: graph read + md5; t8776 / t24342 real sources vs stagesim prediction; full Error List vs prediction item by item",
  "memory_model.json: ONLY one load_by_vi entry for the adopted md5 (MB line cited); other keys equal, fail_above_mb 680",
  "Measured census written into the step-5 pred by a script citing the graph reads; census keys only; md5s",
  "AFTER the LabVIEW card: PD397(e) PB tightening + self-test (3 negatives); stored p5s02c/d + step-5 PB inputs still RECORD every row; fp-86 drained",
  "E5 + reuse detectors judge a deleted node by identity (class, owner, owner uid, pos) in the shared module; self-test on step-4 data, planted survivor caught; fp-87/88 drained",
  "Gate-run suites re-pinned once (names listed); one fn-descriptions batch (~60) into docs/fn_descriptions.json",
  "Originals not opened; eb1d0f31, 7f2582ae, 94ffff94, f9ae7751, 564d8cbe, 6dcd5c3d unchanged; LabVIEW closed and verified gone"
 ],
 "blocked_by": null,
 "stop_requested": false,
 "advances": ["M3", "M8", "R1"],
 "note": "Hand-back 1 judged (PD401): 165-1-1 items 0-4, 6 accepted; precedent = diag_c127_1_fsinner.log:81-99, face-class residue checked by the step-5 scratch; stagexec 6ea6637f kept; PRIME at base addresses stub-holding faces before the plan's deletes (stagexec.py:2629-2636) - measured first this round. Hook fp entries (fp-75, fp-80, ...) go to the chat. If A80 reached -> cycle 166 = P6 run."
}
```