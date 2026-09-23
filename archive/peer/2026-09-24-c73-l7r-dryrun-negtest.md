# c73-l7r-dryrun-negtest

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.0984  in 16 / out 10654 / cache-create 89616 / cache-read 715771  (118s, 15 turn(s))
- **date:** 2026-09-24 06:51:23
- **outcome:** ANSWERED (122s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about a failed prediction in tools/bench/dryrun_l7_r_address.log (script tools/bench/dryrun_l7_r_address.py, an OFFLINE stub dry run, no LabVIEW, of the ends tools/recipes/stage_d1_l7_r.py hands to stagekit.Stage.address through the recipe's own `at()`).

OBSERVED: the log's line 15 reads `FAIL  A1 #2048 Terminals[3] is the unwired 'length' sink (name tie-break) {... 'wire': 4337}`; line 16 `PASS D3 the tie-break REFUSES (Stop) while Terminals[3] still carries w4337`; line 23 `overall PASS`; bgrun then reported an INNER FAILURE because of line 15.

CLAIM: line 15 is not a defect in the recipe or in stagekit. It is the dry run's own deliberate NEGATIVE test D3: the harness sets #2048's Terminals[3] wire back to 4337 and calls the recipe's `at()`, which must refuse; `at()` refuses through the recipe's real `s.gate(..., fatal=True)`, which prints the token `FAIL` before raising `stagekit.Stop`. The harness caught the Stop and scored D3 PASS. So the prediction ("the tie-break REFUSES while Terminals[3] is still wired") held; only the harness printed a FAIL token for an expected refusal. Fix applied: during D3 the Stage's `gate` is replaced by a silent stub that raises Stop without printing; the recipe is unchanged.

Already ruled out: (1) the positive tie-break case (line 7-8, wire 0 -> Terminals[3]) passed; (2) plain address raises on two unwired 'length' sinks (line 14 PASS) so the tie-break is needed; (3) all 6 verify ends by verify_term_uid passed (lines 17-22).

Questions: is there a reading under which line 15 reveals a real defect in `stage_d1_l7_r.py`'s `at()` (e.g. the tie-break accepting or refusing the wrong terminal in the LIVE run, where Terminals[] indices or the `wire` field could differ from the stubbed NODETERMS table parsed from tools/bench/c73_l7r_live.log)? Is replacing `s.gate` with a silent stub hiding anything the recipe needs? What is the cheapest discriminating test?


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict: the claim holds as a reading of line 15. I could not refute it, and I found no defect in `at()` that this line exposes. But "the prediction held" says more than the dry run can show, and the silent stub removes the evidence that line 15 was carrying.**

**1. Strongest reason the claim is wrong: the dry run cannot answer the live-run question it is being used to settle.**
- The stub table comes from NODETERMS #2048, measured on the unedited input (`c73_l7r_live.log:92`). The harness then zeroes the wires in `del_w` (`dryrun_l7_r_address.py:16`).
- In the live run, `at(2048,'length')` runs only after w3957 on `'array'` has been deleted and a new accumulator wire has landed on `'array'` (`stage_d1_l7_r.py:70,80,82`).
- #2048 is an Array Subset (`l7_r_prediction.json:72`). Array functions resize their index inputs to the dimensions of whatever array is wired into them ([LabVIEW arrays guide](https://www.scribd.com/document/959550897/Chapter-4-1), [mindmajix](https://mindmajix.com/labview/array-functions-and-auto-indexing)).
- I found no source on what happens to the Terminals[] order or the terminal uids when the array input is unwired and then rewired ([LabVIEW Wiki](https://labviewwiki.org/wiki/Array_Subset_function) is silent). The evidence does not settle it either way.
- The tie-break can only tell the two `'length'` sinks apart by index. Both have the same name and direction, and both are unwired after the deletes. So its correctness depends entirely on index 3 still being the row length at call time. A stub with a frozen table can never test that.

**2. Is the silent stub hiding anything the recipe needs?** Nothing the recipe needs, but it does lose evidence:
- The real `gate` only prints, appends to `s.fails` and raises (`stagekit.py:186-193`). The recipe relies on none of that in `at()`.
- The loss is on the harness side. The old FAIL line carried the detail `{'wire': 4337, name 'length', sink}`, which showed *why* it refused. The new stub scores D3 PASS on any `Stop`: a uid echo mismatch, a name mismatch or an `is_source` flip would all count.
- Attribution now rests on the positive case (line 7) sharing every other input with D3. That happens to be true today, but nothing asserts it.

**3. Could the gate accept the wrong terminal live?**
- On the input, the index is measured, not assumed. Terminal uid 3182 is `'length'` on w4337 (`c73_l7r_live.log:42`), and w4337 sits on Terminals[3] (`:92`). The wire uid joins them, so index 3 is the terminal the old wire fed.
- If the index shifted live and the gate took Terminals[5] (the column length), that would be a computation change under rule 1a. Two checks would catch it before save (`stage_d1_l7_r.py:113`):
  - The second pass addresses the sink by terminal uid 3182 through `match_term_uid`, which raises on an unwired terminal (`stagekit.py:1129-1132`).
  - PC2 expects the edge TFP → #2048 terminal 3182 (`l7_r_prediction.json:224-229`).
- So a live index shift is caught, as a refusal after the edit, not silently accepted. Caveat: `second()` only catches `IndexError` (`stage_d1_l7_r.py:53`). I did not check that `K.run` turns the resulting `RuntimeError` into a stop rather than a crash that skips the save.
- The `wire` key is consistent between stub and live: `node_terms` rows carry `"wire"` (`stagekit.py:699,800`).

**Alternative explanation of the same evidence:** none survives. Line 15's detail shows wire 4337, which is only set at `dryrun…py:58`, and it sits between D2 (line 14) and D3 (line 16). The only other possibility, that a D1 call printed it, is ruled out: the D1 call for `'length'` passed with wire 0 at lines 7-8.

**What would falsify the claim:**
- The fixed harness still printing any `FAIL` line.
- The FAIL line carrying wire 0.
- A live run where Terminals[3] of #2048 is not uid 3182 when `at()` is called.

**Cheapest discriminating tests:**
1. Takes 0 s, no LabVIEW. Change the D3 stub to record `(label, ok_, detail)` instead of discarding it. Assert that exactly one gate fired, and that its detail has `wire==4337`, `name=='length'`, `is_source False`. Rerun and expect no FAIL token.
2. For live fidelity, one read-only fact line in the recipe. Just before the tie-break, log `node_terms_uid(#2048)` together with the terminal uid at index 3 from `allterms`. Stop if index 3 is not uid 3182. This moves the uid-3182 check to before the edit, which the second pass only does after it.

**What would change my mind:** a measured Terminals[] dump of #2048 taken after w3957 is deleted and the new wire is on `'array'` (for example on the PMV scratch copy the recipe already opens). If index 3 still maps to uid 3182 there, I have no remaining objection.

## Sources

(extract from answer)

## What was done with it

Classification: ANSWERED, claim NOT refuted (line 15 was the harness's expected-negative D3 printing through the recipe's real gate); two gaps accepted and acted on (cycle 73 material, 2026-09-24 07:0x):
- Test 1 applied: `tools/bench/dryrun_l7_r_address.py` D3 now RECORDS every gate call and passes only if exactly one fired, refusing with wire 4337 / name 'length' / sink. Rerun: `tools/bench/dryrun_l7_r_address.log:26-48`, overall PASS, no FAIL token, BGRUN END rc=0.
- Test 2 applied, stronger than a fact line: `tools/recipes/stage_d1_l7_r.py:72-73` gate A0 (FATAL, before any edit) requires #2048 Terminals[3] to carry w4337 AND terminal uid 3182 to carry w4337 on the live input (index 3 == uid 3182). The tun_fp row now runs FIRST, so nothing but the wire deletes touches #2048 between A0 and the tie-break; the 'array' re-wire the review worried about comes after.
- The residual risk (index shift after an edit) stays covered after the edit, before any save: the uid-3182 second pass (a RuntimeError there ends the run through K.run with no save), PC2 (edge TFP -> 2048:3182), and PB FATAL.
- Not adopted: a Terminals[] dump on the PMV scratch after a mock 'array' re-wire - it would add a build step to the probe outside Pre-decided 175; A0 + the ordering answer the same question on the work copy itself.

SAME-ROW: stage_d1_l7_r.log (2026-09-24 07:08:19)
  This later failure of the SAME script was released without buying a new peer review: one review per row per cycle (CLAUDE.md, user 2026-09-22). The review above is the evidence; this line records which re-run was charged to it.
