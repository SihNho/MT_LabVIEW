# c135-2-launch-compare-r2

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.3292  in 16 / out 9927 / cache-create 119687 / cache-read 865523  (108s, 18 turn(s))
- **date:** 2026-10-02 12:48:55
- **outcome:** ANSWERED (112s)
- **verdict-card:** VERDICT-CARD hyp-c135-2-launch-compare verdict=supported -> tools\bench\cards\verdict_hyp-c135-2-launch-compare.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id hyp-c135-2-launch-compare, role hypothesis) ---
CLAIM: launch_p3b2_c135.log failed (compare DIFFERENT -> finalize F3 FAIL) by our-script-bug only: compare used STORED borders and ref 102553 predates the 134-6 'status' annotation (stagesim.py:386); re-annotated, the a-file graph equals the ref on every field, so plan b ae6b6111 applies unchanged.
PREDICTED: C EQUAL (LabVIEW uid allocation deterministic, PD290(d)) -> plan b ae6b6111 as is -> session b
OBSERVED: C DIFFERENT on 'borders' only (launch_p3b2_c135.log:43): 7 nested-FS borders carry status UNMEASURED in 123012, not in 102553; F3 10363 != 10334 (+29 a-created rows). Re-annotated compare offline: EQUAL, ref changes = 7 x status added (diag_c135_2_compare.log); self-test 9/0.
ALREADY RULED OUT: a real border difference: the re-annotation diff on the reference is ONLY an added 'status' key, no removed/changed field (diag_c135_2_compare.json reannotation_changes)
ALREADY RULED OUT: a terminal/wire/frame difference: graph_key fields node_classes, terminals (full rows), wires, fs_frames EQUAL in both the old and the new compare (launch_p3b2_c135.log:43, diag_c135_2_compare.log)
ALREADY RULED OUT: F3 as a computation difference: PD290(b) accepted +29 object rows as representation (no simulated Wire/Terminal object rows); F3's reference is 04204133's end, not the a-file
ATTACHMENT: tools/bench/launch_p3b2_c135.log (md5 baabf65168b18bbe5c61f03ce89fb016)
ATTACHMENT: tools/bench/launch_p3b2_c135_f.log (md5 None)
ATTACHMENT: tools/bench/launch_p3b2_c135.py (md5 16e941a61d3cf0695d58f6a921fc767f)
ATTACHMENT: tools/bench/launch_p3b2_resume_c135_compare.py (md5 None)
ATTACHMENT: tools/bench/selftest_c135_2_compare.log (md5 None)
ATTACHMENT: tools/bench/diag_c135_2_compare.log (md5 None)
ATTACHMENT: tools/bench/diag_c135_2_compare.json (md5 None)
ATTACHMENT: docs/d1/ring-p3b.md (md5 None)
--- END REVIEW CARD ---

Refute the claim in the attached review/1 card (launch_p3b2_c135.log failure = our-script-bug in compare C; plan b applies unchanged to the a-file). Read the attached logs and scripts.

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"hyp-c135-2-launch-compare","verdict":"<one of: refuted | supported | unverified>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

**Verdict: the claim mostly holds.** I couldn't refute its core: no LabVIEW graph difference produced the DIFFERENT result. But two of its words are wrong: "only" and "every field". And "plan b applies unchanged" has not been tested directly on the new a-file graph.

**1. Strongest reason the claim is wrong: "our-script-bug only".** The gate that failed first was F3, not the compare. Compare C only logged a FACT line (`launch_p3b2_c135.log:43`); the FAIL is F3 at `:46` and `launch_p3b2_c135_f.log:9`. F3 is a separate script defect:
- It compares against 04204133's end count of 10334 objects.
- PD290(b) had already accepted 10363 (+29 Wire/Terminal object rows) as a representation difference for any finalize on a real graph (`docs/d1/ring-p3b.md:326-329`). The gate was never changed.
- This run hit exactly 10363, with object classes Terminal 18, OuterTerminal 1, InnerTerminal 2, Wire 8.
- So the runner's DIFFERENT branch would fail no matter what the graph was. That is a second bug, and it was knowable before launch. PD294(c) concedes it (`ring-p3b.md:388`).

The claim's own premise also needs a correction:
- The `borders` field is not a LabVIEW measurement. The reader computes it offline with `stagesim.fs_measured_state` from the terminal rows and `fs_frames` (`diag_c134_1_graph.py:68-69`).
- Since terminals and `fs_frames` compared EQUAL, a DIFFERENT result on `borders` could only come from the code that derives them changing. This supports the cause the claim names, more strongly than the claim argues.

**2. Alternative explanation of the same evidence.** "Equal on every field" is overstated. `graph_key` compares five things (`launch_p3b2_c135.py:57-66`):
- (uid, class) of every object
- terminal rows
- wire → terminal uids
- `fs_frames`
- `borders`

It does not compare the graph's `owners` dict, other object attributes, or `fs_measured.read_err`. The simulator uses owner facts when it finalizes (PD289(f), `ring-p3b.md:313-320`). So the compare can say EQUAL while the a-file graph still differs in an input that plan b's simulation depends on.

The resimulation check (`diag_c135_2_resim.log:3`) does not close this gap. It re-ran ae6b6111 on base `b885fa4a` (the old 102553 graph), not on 123012 (the a-file graph). That proves the plan reproduces on its own base, not that it applies to the a-file.

There is also a loose end: `summary.json` is now `b866dd3d` while plan b records `19624439`, and that file is "not checked by load_final_plan" (`diag_c135_2_resim.log:8`).

**3. What would falsify the claim.** The finalize that ran on 123012 wrote `fae25fb3`, which is kept as `plan_ring_p3b2b_c135_1_fail.json` (`diag_c135_2_restore.log:4`). Its step files are kept in `sim/ring_p3b2b_c135_1_fail` (`diag_c135_2_resim.log:4`). The claim is falsified if, after removing the base path and md5 fields, `fae25fb3` differs from `ae6b6111` in any of these:
- the actions
- the route check rows
- `fs_routes`
- `end_cdiff_rows`
- any step file's state

**4. Cheapest test that separates the two (offline, about a second, no LabVIEW).** This existing result already plays the role of "ae6b6111 applied to the a-file graph":
1. Diff `plan_ring_p3b2b_c135_1_fail.json` against `plan_ring_p3b2b.json` (ae6b6111), ignoring `base`, `md5`, `path` and the `goal` text.
2. Diff the 19 step-file `state` objects in `sim/ring_p3b2b_c135_1_fail/` against `sim/ring_p3b2b/`.

If both diffs are empty, the claim holds completely, including for the fields the compare skips. If either is not empty, plan b does not apply unchanged and must be re-finalized on 123012.

What still supports the claim:
- The re-annotation changed only an added `status` key on the reference's 7 borders, and nothing on the new graph (`diag_c135_2_compare.log:4`).
- The compare self-test passes 9 of 9 and catches real changes to terminals, wires, frames and borders (`selftest_c135_2_compare.log`).
- The F run's F1, FB and F2 passed, and its +29 object count equals the 102553 result. That is what equal graphs would produce.

I used no external sources; every point above comes from the project's own logs and code.

VERDICT {"schema":"verdict/1","id":"hyp-c135-2-launch-compare","verdict":"supported","alternative":"compare graph_key omits owners/other obj fields the simulator reads; resim used 102553 not 123012, so 'applies unchanged' is untested on the a-file; F3 is a 2nd independent script bug (stale 04204133 ref, PD290(b)), so 'only' is false","discriminating_test":"offline diff fae25fb3 (plan_ring_p3b2b_c135_1_fail.json, finalized on 123012) vs ae6b6111 minus base/md5/path/goal, and sim/ring_p3b2b_c135_1_fail step states vs sim/ring_p3b2b; empty => claim holds fully","violations":[],"sources":["tools/bench/diag_c134_1_graph.py:68-69","tools/bench/launch_p3b2_c135.py:57-66","tools/bench/launch_p3b2_c135_f.log:9","tools/bench/diag_c135_2_resim.log:3","docs/d1/ring-p3b.md:326-329"],"note":"borders are derived offline from compared fields, so C DIFFERENT carried no LabVIEW information; summary.json md5 drift unchecked"}

## Sources

(extract from answer)

## What was done with it

Card 135-2 (material, 2026-10-02 12:5x). Verdict `supported` (verdict card `tools/bench/cards/verdict_hyp-c135-2-launch-compare.json`).
Recorded, nothing decided here (acceptance is the judgement session's):
- Point 1 (F3 is a second, independent script bug: stale 04204133 reference despite PD290(b)) agrees with PD294(c), which already
  carries it; the resume runner `tools/bench/launch_p3b2_resume_c135.py` has NO finalize branch, so F3 is not on its path.
- Point 2 (graph_key omits `owners` / other obj fields; the resim proved ae6b6111 on 102553, not on 123012) and the proposed
  discriminating test (diff `plan_ring_p3b2b_c135_1_fail.json` fae25fb3 vs ae6b6111 minus base/md5/path/goal/at, and the step
  states of `tools/bench/sim/ring_p3b2b_c135_1_fail/` vs `tools/bench/sim/ring_p3b2b/`) are passed to judgement as OPEN in
  `tools/bench/cards/result_135-2.json`; the test was NOT run inside the card (card chat-P2: return at the first unexpected result).
- summary.json drift (b866dd3d vs recorded 19624439) is a fact in the same result; load_final_plan does not check it.
