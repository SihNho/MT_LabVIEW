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