The next.json for round 3 is below; nothing was written, as the bench asked. I accept the hand-back: the fault is a gap in my round-1 tool fix (my PD400(b) decision), not a new problem.

**Why the plan was refused.** Before step 1 runs, the build script checks every wire end in the plan against the starting graph (the "PRIME" check, `tools/stagexec.py:2629-2640`). It only checks ends that already have a wire there. The two inner faces t8776 and t24342 still hold their leftover wires w10362 and w25232 at that point, because the plan's own deletes haven't run yet. So the check goes through the old address lookup, which refuses inner faces (`stagexec.py:1930-1934`). Round 1's self-test covered compiling the plan and each step's route, but not this start-of-run check. That matches card 165-2-1's facts: the simulated replay ran all 13 steps cleanly and only this check refused.

**Decision (would be PD402):**
- **The fix stays narrow.** The start check skips an end only if all three hold:
  - it is a LoopTunnel inner face used as a wire's destination;
  - the wire on it at the start is removed by a `delete_wire` that comes earlier in the plan;
  - that delete is a checkpoint, so the graph is re-read before the connect.
- **Every skip is logged.** That face then gets its address at its own step, from the re-read, through the round-1 route.
- **The script still refuses four wrong orderings:** no delete, a delete of a different wire, the delete placed after the connect, and an inner face of the other tunnel kinds (Case or Flat Sequence).
- **This fix runs before the deliverable** only because the step-5 plan can't be finalised without it, so the step can't be launched at all.
- **Other open items:** the step-5 plan file on disk (20bde81a, not final) is overwritten when the plan is re-made. The maker's import of the step-4 script is accepted.
- **This is the last hand-back round (3 of 3).** If the fix fails its self-test or the practice run returns, the cycle closes on this next.json and the same purpose carries to cycle 166.

The plan md5 below (ffb92f59) is the md5 of `docs/d1/ring-p5c.md` once PD402 is in it; that is the file currently on disk. I couldn't re-hash it in this session.

```json
{
 "schema": "next/1",
 "cycle": 165,
 "act": "Round 3/3 (PD402): PRIME skip fix first (step-5 plan cannot finalize, stagexec.py:2629-2640) + self-test -> step-5 plan K3f K4 K4f on 2a5fa0c4 -> gates -> ONE scratch on copy of 6dcd5c3d -> adopt",
 "task_kind": "build",
 "plan": {
  "path": "docs/d1/ring-p5c.md",
  "md5": "ffb92f59acef4c1539f59acd61e59072"
 },
 "pass": [
  "Already met by 165-1-1 / 165-2-1, cite only (PD401, PD402): diag_c165_a1_1_facts.md:8-45; diag_c165_a2_1_facts.md hashes 23/0 + c127 precedent; result_160-c3-2.json PASS",
  "Re-hash stagexec 6ea6637f, r_in 0b895983, VI 6dcd5c3d, graph 2a5fa0c4, EL c74200f2 before the edit; any drift = hand back",
  "PD402(b): PRIME skips ONLY a LoopTunnel InnerTerminal sink whose base wire = wire_uid of an EARLIER checkpointed delete_wire; each skip logged (end, wire, op)",
  "Every other end is primed as before; new stagexec md5 quoted",
  "Self-test on 2a5fa0c4: step-5 plan finalizes in SB REALSIM, route PASS, 0 UNROUTABLE; real-backend PRIME does not raise for t8776 / t24342",
  "Negatives still refuse: n1 no delete_wire, n2 delete of another wire, n3 delete_wire after the connect, n4 wired SelectorTunnel / FS inner face",
  "Six stored plans (p5s01a/b, p5s02a-d) compile + dry byte-equal; c157/c158/c165 innerface, stagesim, stagexec self-tests green (counts quoted)",
  "plan_ring_p5s02e.json re-made on 2a5fa0c4 (overwrites 20bde81a), new:* from diag_c164_p5s02d_scratch.log:208; K3f+K4+K4f A72..A84, MAIN <= 675 quoted; final True",
  "Every delete_wire a checkpoint; per pair PD401(b) prediction written: wire 0 after delete, census in [{}, {'Wire': 1}], face on OK3 / OK4.outer net, not broken",
  "stagesim end graph: w10362 / w25232 absent; t8776 / t24342 on the OK3 / OK4.outer nets, quoted",
  "Recipe pair = step-4 recipe inputs on the shared stagekit gates; dry both PASS or PASS-UNVERIFIED (CEN2 only); PB rows quoted; PB block = hand back",
  "prerun PASS; --check-launch PASS ('DRY-UNVERIFIED-OK: CEN2 new-object census' if CEN2-only); --scratch-required exit quoted",
  "Predicted step-5 Error List from c74200f2 (step-4 expected): items cited to actions, rest UNPREDICTED; file + md5",
  "Prior-art review of the step-5 plan incl. the PRIME change: novel + disposition (flags.peers include priorart), or released by FIXED:/REFUTED: lines",
  "ONE scratch on a NEW byte copy of 6dcd5c3d: peak <= 675, every BLOCK gate PASS, PRIME-SKIP lines for t8776 / t24342 quoted; else RETURN, no 2nd run",
  "Scratch, per stub-delete + connect pair: PD401(b) facts quoted (wire 0, census, face on OK net, Is Broken? False, EL delta); anything else = RETURN",
  "On PASS adopt claudeDev D1_ring_p5_<ts>.vi if A84 reached (P5 final, broken file 6 of 6), else D1_ring_p5s02e_<ts>.vi (in-between); md5",
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
 "note": "Hand-back 2 judged (PD402): 165-2-1 items 0-3 accepted; refusal = base PRIME check on inner faces still holding stubs before the plan's own deletes (my PD400(b) gap). Last round 3/3. A84 reached -> cycle 166 = P6 run."
}
```