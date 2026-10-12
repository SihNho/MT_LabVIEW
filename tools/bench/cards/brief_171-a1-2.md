---
card: 171-a1-2
status: current
date: 2026-10-13
---
# Brief 171-a1-2 (assignment 171-1, the ONE retry of 171-a1-1) - narrow the name-taint so card-134-1's T1 still FAILs FR

Read first: `tools/bench/cards/brief_171-a1-1.md` (UNCHANGED - steps 1-3, the rule, the self-tests, prior-art, drain, hygiene all apply), then `tools/bench/diag_c171_a1_1_facts.md`, `tools/bench/diag_c171_a1_1_patch.diff`, `tools/bench/diag_c171_a1_1_st134.log`.
Offline only (`flags.labview none`). `tools/stage_prerun.py` is at db81a1d3 again (the first attempt was reverted); the first attempt's patch is kept as the diff above.

## What 171-a1-1 found (facts)
- Step 0 had no drift. The two "DIFF" rows were the brief's stand-in names swapped against their hashes: on disk `replay_imaqdx_get_image_buf.vi` = a89dafc1 and `replay_get_buff_image.vi` = 842ecad9 (same as `docs/d1/ring-p6.md:313-315`). Accepted as a label error; re-check by hash, quote name -> hash.
- The first patch (AST statement units + per-frame tainted-name set + OR at the gate's `tainted` line, `diag_c171_a1_1_patch.diff`): plan-170 dry gives `UNVERIFIED A2` and ends `DRY PASS-UNVERIFIED`, unverified 7, no FAIL (`diag_c171_a1_1_dry170.log:10,28`).
- But `selftest_c134_1_dry.py` T1 (the 133-3 bytes, which must `DRY FAIL` naming FR) now ends `first_fail=GATE PB`, unverified 2 (`diag_c171_a1_1_st134.log:4`; record `selftest_c134_1_dry_c160_f3_1.log:4`: first_fail=GATE FR, unverified 0). The name taint relabelled the FALSE gate FR (card 134-1's FR-hiding class). That is the one failure to fix.
- Baselines before any edit already differ from the stored dry records for plans 78 and 110 (FAIL A2, the pre-134-1 stored records say PASS unverified 14 / 7) and the ring recipe `stage_d1_ring_p5s02c` (DRY PASS now, stored FAIL PB `prep_c163_a1_3_dry.log:56`); plan 95 has no graph (`_pre95.log:6`). Report the post-edit verdict next to BOTH the stored record and that pre-edit baseline.

## New step 1a - DIAGNOSE FIRST (a fact, before any narrowing)
Re-apply the first patch with the Edit tool (same text), run T1's recipe bytes (the reconstructed 133-3 recipe `selftest_c134_1_dry.py` builds) under the dry with the patch, and find which NAME(S), bound in which statement(s) (file:line of the reconstructed recipe),
made the FR gate (and the gates after it) score tainted. Write them to `diag_c171_a1_1_facts.md` (<= 6 lines). Use a throwaway diag script `tools/bench/diag_c171_a1_2_which.py` (it may import stage_prerun; no edit of stage_prerun for the diagnosis beyond the re-applied patch).
Then compare with the plan-170 shape (`stage_replay_swap.py:39-42`: `c0` bound from the stub census statement, A2 gates `c0.get(u)`).

## New step 1b - narrow, by a PRINCIPLED criterion
The requirement from the judgement (PD412(b)/(c)): plan-170's A2 is UNVERIFIED AND T1's FR still FAILs AND the card-134-1 cases hold. Choose the narrowest rule that separates the two by what the code DOES, not by names/recipe/file/line:
the tainting statement's kind of stub touch (a stub READ/census versus a mutation op or `s.es`), whether the bound value is itself derived from a Fake (value-based, e.g. a Fake or a container of Fakes) versus built from an empty/simulated census, whether the gate's tested value flows from the tainted name or the name is merely read for a key, etc.
Evidence decides: show the T1 names/statements and the plan-170 names/statements side by side, state the criterion in one comment line, implement it. No recipe-specific string, no plan-170 literal, no new flag.
**If no such criterion separates the two cases** (T1's FR gate reads a name bound from a stub-touching statement in exactly the way A2 reads `c0`), do NOT bend either case: RETURN with the two statements side by side and the conflict stated as one question (PD412(b) literal rule versus card-134-1 T1) - that is the judgement session's, and the hook hands the purpose back. No third attempt.

## Then brief_171-a1-1.md steps 2-3 exactly
2.1 plan-170 dry (A2 UNVERIFIED, line where the dry ends, no other FAIL; a FAIL of any other gate = RETURN); 2.2 `selftest_c134_1_dry.py` with the SAME counts as its record (11/0, `selftest_c134_1_dry_c160_f3_1.log:15`) + the new `selftest_c171_a1_1_taint.py` asserts
(rewrite the 171-a1-1 draft file `tools/bench/selftest_c171_a1_1_taint.py` to match the final code; it must also assert the T1 shape: a gate FALSE on simulated data after a stub-touching statement whose name it reads, per the criterion you chose, and the plan-170 shape);
2.3 dries of plans 78/95/110 and ONE ring recipe (`stage_d1_ring_p5s02c` as before, `--no-record` where the first attempt used it) with the verdict next to the stored record and the pre-edit baseline - differences are FACTS; 2.4 `selftest_dry_c130_5.py` same counts. One at a time.
3 prior-art review (peers priorart), disposition paragraph under `archive/peer/`; drain `fp-103` with the new self-test name; fp-102 untouched. A dry run of plan 170 on the final checker leaves a PASS-UNVERIFIED record in `prerun_records.jsonl`: make sure the NEWEST plan-170 record is the one from the final checker.

Facts: append to `tools/bench/diag_c171_a1_1_facts.md` (keep <= 40 lines total; may rewrite the file to fit), quote the new stage_prerun md5. Hygiene as in brief 171-a1-1. A new unexpected result = RETURN with the facts (this is the retry; it is spent).
