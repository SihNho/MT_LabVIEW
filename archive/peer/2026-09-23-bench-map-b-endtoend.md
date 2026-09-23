# bench-map-b-endtoend

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.8748  in 40 / out 22039 / cache-create 121088 / cache-read 2208891  (292s, 30 turn(s))
- **date:** 2026-09-23 17:49:31
- **outcome:** ANSWERED (295s)
- **why asked:** failed prediction in step 5b B run 1 (damage 20/6/14 instead of 9/0/9; 6/9 restored)
- **verdict:** review RIGHT on (a) and on the test design; (c) CONFIRMED by its own discriminating test (B run 2)

## Question

FAILED PREDICTION (connectivity-map plan step 5b, bench B: end-to-end repair, zero LLM turns, on a dated scratch of S1 =
`claudeDev\D1_s1_copy.vi`, the original's bytes). Attack the DIAGNOSIS below; find the strongest reason it is wrong.

WHAT RAN (`tools/bench/bench_map_20260923/b_endtoend.py`, log `tools/bench/bench_map_b.log`, JSON
`tools/bench/bench_map_b.json`, record `tools/bench/decision_bench_map_b.json`). 9 of the 11 M3a-1 wires exist in S1 (23502
/23540 were created later by S3b), each one source -> one sink on the frame-loop body (diagram uid 639); all 9 deleted
whole (`stagekit.delete_wire`, by uid via the live Wire traverse). Then: live re-read (OpAllTerms_v1 + GObject census; S1's
flat-sequence faces and Shift Registers[] reused) -> `jev_candidates.candidates` -> `jev_pairs.decide(by_rule=True,
risk_gates=False)` with PAIR NOT acting (bench A5 failed its held-out criterion) -> `stagekit.from_decision` -> ARM 2 with the
KNOWN S1 pair as verdict and the same op rule -> re-read -> `vigraph.diff` / `computation_diff` against S1.

PREDICTED: the damage read back = exactly the 9 S1 edges removed (0 added). OBSERVED: edges_removed 20, edges_added 6,
changed_sinks 14 (gate B0). After ARM 2: 6 of 9 restored (1893, 2819, 3947, 4833, 7388, 11232), ExecState 0, repaired diff
10 removed / 6 added, computation_diff 3 rows (#48 'VISA resource name', #9243 'x', #29815 'VISA resource name' unsourced).
Remaining diff rows: the VISA carrier (right register #4334 / left #4344 / FSIT #7468) appears in S1 with terminal name
'VISA out' and in the repaired scratch as 'Outgoing Handle' (6 edges - / 6 edges +: sr #4334->#4344, fs #7468, wires #4194->
#4344 outer, #4334 outer->#7468, #7468->#29815, #7468[3]->#7468[1]); `- wire #11263 'VISA out' -> #4334` (w7337);
`- wire #4344 'VISA out' -> #48` (w1731); `- wire #9641 -> #9623 outer` (w9635); `- wire #9623 InnerTerminal '# slices in
stack' [1] -> #9243 'x'` (a wire NOT deleted).

DIAGNOSIS UNDER ATTACK: (a) w1731 and w7337 failed at the CANDIDATE layer only because graph keys include the terminal NAME
(Pre-decided 137): cutting both wires of the VISA shift-register carrier makes LabVIEW rename the whole carrier's terminals
'VISA out' -> 'Outgoing Handle' (the name follows the remaining wire from #4194), so the S1 truth key no longer exists and
the 6 renamed edges are the extra -6/+6 of B0; (b) w9635 failed at the OP layer: Pre-decided 143's rule has no entry for a
LoopTunnel INNER source (no wire left on it, not node-addressable) and Jev's OP menu does not act; (c) the other extra
removed edges of B0 (and the lingering `#9623 inner -> #9243`) are INPUT TUNNELS whose feeding wire was cut: the tunnel's
direction becomes undetermined, its inner terminal is no longer read as a source, the inner wire has 0 sources and build4
emits no edge; restoring the feed (7388 -> #11348, 11232 -> #11220) brought theirs back. (c) is INFERRED - the severed
graph's flags were not dumped.

QUESTIONS: (1) Is there an alternative to (c) - e.g. the delete-by-traverse-index verb (`build_opfsinnertunnelconnect_v0.
del_wire`: uid -> index in report_all('Wire') -> gscript.delete_object) deleting a DIFFERENT wire, or the reader mis-keying
ordinals ([1]) after a rename? (2) Is (a) really a key-identity problem, or did LabVIEW change the carrier's TYPE (a VISA
refnum becoming a generic handle) - which would make it a computation change? (3) The cheapest discriminating test for (c)
and for (1).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**The diagnosis is wrong at (a), and (a) is its load-bearing part.** w1731 and w7337 did not fail at the candidate layer. The candidate layer produced the physically correct pair for both rows, and Jev ranked it first. They failed because the bench scores by exact S1 names, and because Jev's confidence fell below the threshold.

## 1. Strongest reason the claim is wrong

- **w1731:** the candidate list contains `#4344 InnerTerminal 'Outgoing Handle' -> #48 'VISA resource name'` (`tools/bench/decision_bench_map_b.json:157-162`). Jev ranked it top at p 0.558; the other four were ≤ 0.136 (`:864-869`, `:932-939`).
- **w7337:** its only candidate is `#11263 'VISA out' -> #4334 'Outgoing Handle'` (`:567-571`), at p 0.464 (`:1526-1549`). That is also the correct physical connection.

What actually failed:
- **(i) The bench's scorer.** `truth_in_candidates` and `best_is_truth` compare against S1 keys and names exactly (`b_endtoend.py:75-76`, `:82-83`). It never uses the fallback in `jev_candidates.map_key` (`tools/jev_candidates.py:250-253`). That fallback was written for this exact terminal: its docstring says #4344 reads 'VISA out' in S1 and 'Outgoing Handle' in the bed.
- **(ii) ARM 2 skipped both rows.** It uses the same exact-key test (`b_endtoend.py:90`), so the oracle arm never tried to rewire w1731 or w7337. Part of "6 of 9 restored" comes from the bench, not from the pipeline.
- **(iii) The verdict threshold.** Both p values are below 0.70. A likely cause: the intent line hands Jev the S1 name 'VISA out' as the hint (`b_endtoend.py:70-73`), and that name no longer exists on #4344 or #4334.

A smaller correction: the rename does not cover "the whole carrier". #11263 still reads 'VISA out' after the sever (`decision_bench_map_b.json:568`).

The 6 renamed edges are therefore probably a result of w1731/w7337 not being rewired, not a separate fault. The B0 prediction ignored a rename that had already been measured on the bed, so it was a prediction the project's own prior work already contradicted.

## 2. Alternative explanations

- **For (c), and your question 1:** the deletions were never verified. `del_wire` calls `gscript.delete_object(..., verify=False)` (`tools/recipes/build_opfsinnertunnelconnect_v0.py:341`). The docstring of `gscript.delete_object` says that setting "CANNOT TELL YOU WHETHER IT DELETED ANYTHING", and that the op's error indicator is dead (`tools/gscript.py:2368-2371`, `:2399-2401`). So the nine `err ''` lines (`bench_map_b.log:26-50`) prove nothing, and the "624 rows" census is a Node count, not a Wire count.
  - **Partial evidence against a wrong deletion:** each stray Invoke that ARM 2 created took uid 1731 (`log:82`), which suggests w1731's uid was freed. Nothing like that exists for the other eight.
  - **What a wrong deletion would look like:** a wire that was never deleted would still read as "restored". ARM 2 would then have wired an input that was already wired, giving a broken wire, and `ExecState 0` does not tell that apart from anything else. For w9635 the evidence does rule a wrong deletion out: `#9641 -> #9623 outer` is missing.
- **A second alternative for (c):** the inner wire still exists but is dropped by the reader. It could be missing from the terminal table, or `is_source` is unreliable on a tunnel whose direction is undetermined. In both cases `vigraph` records the wire as a flag and emits no edge (`tools/vigraph.py:289-293`). This is mechanically the same as (c), but it matters for question 1: "the wire exists" and "the wire was deleted" are different claims, and nothing recorded tells them apart. #9623, #11348 and #11220 are all SelectorTunnels, so each has one inner terminal per case frame. One cut feed can remove several edges.
- **On question 2 (type change):** LabVIEW's Help says a shift register "automatically changes to the data type of the first object wired to" it ([Princeton copy of LabVIEW Help](https://www.princeton.edu/~mae224/labmanual/labviewreference.pdf)). A tunnel's terminal name comes from the data type it carries, so the rename is a change in that type, at least in the name part. My search found nothing on whether the refnum class changed.
  - **Evidence for a name-only change:** in S1, #4194 (a flat-sequence inner tunnel, `docs/wiki/subvi/D1_s1_copy.json:19155-19161`) already fed #4344 while #4344 read 'VISA out', and S1 is `ExecState 1`. So the type now on the carrier is one S1 already accepted at the shift register's initial-value input.
  - **What would make it a computation change:** only if the final repaired VI keeps the 'Outgoing Handle' type. That is unmeasured.

## 3. What would falsify the claim

- **For (a):** re-scoring the saved decision record with `map_key` shows the true pair in the candidates and ranked first for both rows. The record already shows this, so (a) as a candidate-layer failure is falsified now.
- **For "the extras are renames":** after w7337 and w1731 are rewired, the carrier still reads 'Outgoing Handle'.
- **For (c):**
  - the Wire uid set after the sever differs from S1's by anything other than exactly the 9 requested uids; or
  - `#9623` InnerTerminal [1] is gone from the terminal table rather than present with no source.

## 4. Cheapest discriminating tests

1. **No LabVIEW at all, a few minutes.**
   - **Scoring:** re-run the scoring and the oracle-arm filter from `decision_bench_map_b.json` through `map_key`.
   - **Arithmetic:** in the S1 graph, count the wire edges whose source is an inner terminal of #9623, #11348 or #11220. B0 removed 20 edges. The 9 true edges, the 6 renamed ones and `#9623 -> #9243` make 16, so (c) must account for the other 4, or 5 if `#9623 -> #9243` is counted among them. A different count refutes (c) as the whole story.
2. **One scratch run, deletion and read only, no repair.**
   - Call `del_wire` with `verify=True`, or snapshot `g.uids(target, "Wire")` around each delete.
   - Dump the severed graph's `flags` and the terminal rows (`is_source`, `wire_uid`) for #9623, #11348, #11220, #4334 and #4344.
   - (c) predicts: exactly the 9 uids disappear, one per call, and #9623's inner [1] row keeps its `wire_uid` and shows up as a flag with no source.
   - Then rewire w7337 alone and read #4344's name. If it reads 'VISA out' again, the 6-edge rename is settled, and the type question goes away for the final VI.

I still think (b) holds as stated; nothing I read contradicts it. (c) is plausible but only inferred, and test 1 checks its edge count without touching LabVIEW.

Sources:
- [LabVIEW Help (Princeton copy)](https://www.princeton.edu/~mae224/labmanual/labviewreference.pdf)
- [NI forum: tunnel vs. shift register](https://forums.ni.com/t5/LabVIEW/tunnel-vs-shift-register/td-p/3213328)

## Sources

(extract from answer)

## What was done with it

MATERIAL session, 2026-09-23 17:5x. Accepted: (a) was a SCORER fault, not a candidate-layer fault. Test 1 arithmetic run
offline on the S1 graph: the inner wire edges of #9623 / #11348 / #11220 are 1 + 2 + 2 = 5, and 9 cut + 6 renamed + 5 = 20
= B0's removed count exactly. Test 2 was folded into B run 2 (`tools/bench/bench_map_20260923/b_endtoend.py`, second
BGRUN block of `tools/bench/bench_map_b.log`, run 1 kept as `raw/bench_map_b_run1.*`): every delete verified by the Wire
uid census (9/9 removed exactly the requested uid - the wrong-delete alternative is REFUTED); the severed graph's flags
show wires 5773, 9612, 11209, 11303 with n_src 0 and the tunnels' inner terminals read as SINKS - (c) CONFIRMED by
measurement; truth and oracle now mapped through `jev_candidates.map_key`. Result: the oracle arm restored 8/9 S1 rows
with EXACT S1 keys - after w1731 and w7337 were re-wired the carrier's terminals read 'VISA out' again, so the rename is
settled and the type question does not reach the final VI. Remaining: w9635 (op rule has no entry for a LoopTunnel inner
source), diff 2 rows, computation_diff 1 row (#9243 'x'), ExecState 0. B0's run-2 gate failed on MY bookkeeping only
(one edge, #11220 inner -> #11263 'VISA out', counted both as tunnel-inner and as renamed; 'unexplained removed' = []).

JEV-DISCHARGE: bench_map_b3.log (2026-09-23 18:44:47, p=0.868)
  This failing run was released without a NEW peer review: Jev judged, at the probability shown, that the failure above is the one this review already attacks (tools/bench/jev_gate.py, docs/jev-integration-plan.md row #1). The review itself is the evidence; this line only records which failure was charged to it.
