---
card: 171-a1-1
status: current
date: 2026-10-13
---
# Brief 171-a1-1 (assignment 171-1) - offline: re-hash, then the stage_prerun dry's taint follows names (PD412(b)-(c), fp-103)

Plan: `docs/d1/ring-p6.md` PD412 (lines 361-385). Read first: `docs/script-writing.md`, `CLAUDE.md` rule 1c-never-7 (a refusing gate is obeyed; this card FIXES the checker, it never routes around it).
No LabVIEW, no camera, no motor, no VISA: `flags.labview none`. The dry is an offline check; self-tests use stored data and stubs.

## Step 0 - re-hash (drift = RETURN, edit nothing)
Compute md5 (first 8 hex) and compare: bed `claudeDev\D1_ring_p6_20261012_212645.vi` c2d9c13c; `claudeDev\D1_ring_p5_20261010_172913.vi` 75773b0d; `tools/bench/graph_ring_p6_20261012_212645.json` fbc7b7ee;
`claudeDev\D1_s1_copy.vi` 3e3d23ce; `claudeDev\replay\D1_s1_replay_20260925_075422.vi` 126f8497; stand-ins in `claudeDev\replay\`: `replay_imaqdx_get_image_buf.vi` 842ecad9, `replay_get_image_cal.vi` afce0d04, `replay_get_buff_image.vi` a89dafc1,
paced `replay_imaqdx_get_image_buf_paced60.vi` e40ec867 and `replay_get_buff_image_paced60.vi` 59ec66b6 (if a file name does not carry the hash, search `claudeDev\replay\` for the listed hash and quote name -> hash); `tools/bench/p6_replay_frames_manifest.txt` 9055d98a;
`tools/bench/m8b_replay_compare.py` 82443af9; `tools/bench/plans/plan_replay_swap_170.json` 01c21526; `tools/recipes/stage_replay_swap.py` fa94e80c; `tools/stage_prerun.py` db81a1d3; also 7f2582ae (P5-1 file; locate it by hash in `claudeDev\`) and 75773b0d.
Read the files only (hashing; no open in LabVIEW). Any mismatch or missing file = RETURN with the table; no edit.

## Step 1 - the fix, in `tools/stage_prerun.py` (the only tool edit)
Today: taint is scored per STATEMENT (`stage_prerun.py:816-820`: `tainted = D.taint != (D.line_taint if D.line_taint is not None else D.gate_taint)`). A gate whose statement reads a name that an EARLIER statement bound from a COM-stub read
(plan-170 case: `stage_replay_swap.py:39` binds `c0` from the stub census, `:42` gates on `c0`) therefore scores untainted and FAILs on stub data (fp-103; `stage_replay_swap_170_dry.log:9`, `_dry2.log:10`).
The rule to implement (PD412(b), the card-134-1 rule at `:824-825` made exact): **a name bound in a statement that touched a stub is tainted; a gate whose statement reads a tainted name scores as tainted.**
Keep: the statement-scoped snapshot (the 134-1 reason: an unrelated stub-touching statement between two gates must not relabel the next gate); a FALSE gate on simulated / real-graph data with no tainted name still FAILs; `DRY_RESULT_GATES` handling at `:828` unchanged.
Edges to decide in the code and say in one comment line (rule 13 if a shortcut): a tainted name REBOUND in a statement that touched no stub becomes clean; the scope is the recipe's frame(s) the tracer already follows; names read via attribute/subscript count by their base name.
Rules: no change to which gates are RESULT gates, no new option or flag, no change to `_gateclass`, `orig["gate"]`, the address/op wrappers. Docstring for any NEW function (rule 9) naming its self-test.
Pin: the edit is made on `stage_prerun.py` db81a1d3; quote the new md5 (first 8 hex) and the diff size. Edit tool only, never a heredoc.

## Step 2 - self-tests, ONE AT A TIME (new decision logic -> one assert-based self-check, rule 14: `tools/bench/selftest_c171_a1_1_taint.py`)
Run each under `py tools/bgrun.py --max-min 10 --log <file> -- <cmd>` if more than a few seconds; wait for each before the next; read the log, never infer.
1. **PD412(c)1:** the plan-170 dry `py -u tools/stage_prerun.py --dry tools/recipes/stage_replay_swap.py --plan 170` (log `tools/bench/diag_c171_a1_1_dry170.log`): gate A2 prints `UNVERIFIED` (not FAIL); quote that line and the line where the dry ENDS and its verdict
   (the pass says "where the dry ends is quoted"). If the fixed dry still FAILs A2, or FAILs ANY other gate -> RETURN with the log lines; **no second tool change is tried** (PD412(d)).
2. **PD412(c)2:** the card-134-1 cases: `tools/bench/selftest_c134_1_dry.py` (stored result `result_134-1.json`, logs `selftest_c134_1_dry.log`) - same pass/fail counts as its record; plus in the new self-test: (a) a FALSE gate on simulated/real-graph data FAILs;
   (b) a stub read by an unrelated statement between two gates does not relabel the next gate; (c) the plan-170 shape: name bound from a stub read, gate on it one statement later -> UNVERIFIED; (d) the same name rebound clean then gated FALSE -> FAILs.
3. **PD412(c)3:** dries of plans 78, 95, 110 of `tools/recipes/stage_replay_swap.py` (`--plan 78|95|110`) and of ONE ring stage recipe that has a stored dry log (e.g. the `prep_c163_a1_3_dry.log` recipe `stage_d1_ring_p5s02c`; name your pick and its stored log):
   each prints the same verdicts (PASS / UNVERIFIED lists, fail list) as its stored record (`stage_replay_swap_110_dry78.log`, `_dryb.log`, `_dryc.log`, `prep_c163_a1_3_dry.log` etc. - find the matching stored record, quote file:line).
   A difference is a FACT to report (list it), not a reason to edit again.
4. Existing dry self-test `tools/bench/selftest_dry_c130_5.py` still passes with its recorded counts.
Do not run any other suite. Plans 78/95/110 md5 unchanged (cdc14e32 / ea7cf810 / 6b5ef7e5), `stage_replay_swap.py` fa94e80c, plan 170 01c21526 unchanged.

## Step 3 - prior-art review and drain
This edit sets which gates fail, so it gets `peers ["priorart"]`: run the prior-art review for the stage_prerun change as the earlier cards did (`tools/prior_art_review.py`, see `archive/peer/2026-10-13-priorart-c170-paced60*` and `tools/bench/cards/review_priorart-c170-paced60.json` for the invocation shape), write its "What was done with it" paragraph under `archive/peer/`, quote the verdict.
Then drain: `py tools/gate_fp.py drain --id fp-103 --fixed "stage_prerun.py taint follows names bound from stub reads (md5 <new>)" --selftest "tools/bench/selftest_c171_a1_1_taint.py"`. Do NOT touch fp-102 (it is last, PD409(g)) or any hook.

## Facts file `tools/bench/diag_c171_a1_1_facts.md` (<= 40 lines, file:line)
Step 0 table; new md5 of stage_prerun.py and the changed lines; the A2 UNVERIFIED line and where the dry ends; per-self-test result; the 78/95/110/ring comparison table; prior-art verdict; drain line.

## Hygiene
No LabVIEW process before/after (`tasklist`), no VISA, no `.vi` written, no hook edit (`tools/hooks/**`), no STATUS/INDEX/plan-of-record edit, `memory_model.json` untouched. A new unexpected result = RETURN with the facts.
