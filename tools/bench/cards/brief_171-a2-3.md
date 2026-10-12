---
card: 171-a2-3
status: current
date: 2026-10-13
---
# Brief 171-a2-3 (assignment 171-2) - offline: prior-art review of the patch, drain fp-103, queue c130_5 T3

Plan: `docs/d1/ring-p6b.md` PD413(e). State: `tools/stage_prerun.py` is PATCHED af6937e8 (`diag_c171_a2_2_facts.md`): plan-170 A2 UNVERIFIED (`diag_c171_a2_2_dry170.log:10,28`),
selftest_c134_1_dry 11/0, selftest_c171_a1_1_taint 9/0, c130_5 T3 FAIL at the same GATE PB text as the unpatched checker (`diag_c171_a2_1_c130_5_unpatched.log:8`).
Offline only (`flags.labview none`). The patch is NOT edited here. Edit/Write tools only, never a heredoc.

## Step 1 - prior-art review of the patch (peers priorart)
Run the review the earlier cards ran, for the change `tools/bench/diag_c171_a1_2_patch.diff` (the name-taint criterion in `stage_prerun.py`: a name bound in a stub-touching unit
is tainted when its value is a Fake / holds a Fake / is an empty container / is unbound; scalars stay clean). Invocation shape: `tools/prior_art_review.py`; example files
`tools/bench/cards/review_priorart-c170-paced60.json` and `archive/peer/2026-10-13-priorart-c170-paced60.md` (read them for the shape; do not copy their text).
Question for the reviewer: does an established dry-run / taint-tracking / mock-data approach already handle "a value read from a stub is tainted, a gate on it is unverified, a gate on simulated data still fails",
and does the patch's value criterion match or contradict it? Write the disposition paragraph "What was done with it" in `archive/peer/2026-10-13-priorart-c171-taint.md` and quote the reviewer's VERDICT line.
A verdict that the criterion is WRONG (contradicts the prior art in a way that lets a false gate pass) = RETURN with the quoted verdict; do not edit the patch and do not drain.
A verdict of "known approach / acceptable shortcut / adopt as is" = go on.

## Step 2 - drain fp-103 and queue c130_5 T3 (only after step 1 is not WRONG)
`py tools/gate_fp.py drain --id fp-103 --fixed "stage_prerun.py name-taint by value criterion (PD413(a)), md5 af6937e8" --selftest "tools/bench/selftest_c171_a1_1_taint.py"`.
Then queue the stale self-test as a gate-fp entry: `py tools/gate_fp.py log --gate "checker:selftest_dry_c130_5:T3" --card 171-a2-3 --cmd "py tools/bench/selftest_dry_c130_5.py" --why "T3 fails at GATE PB on the UNPATCHED db81a1d3 and on af6937e8 (same text, diag_c171_a2_1_c130_5_unpatched.log:8); stored record 3/0 predates the PB criterion of PD370(b); fixed after P6-2 (PD413(c))" --log tools/bench/diag_c171_a2_1_c130_5_unpatched.log --line 8`. Quote both output lines (entry ids).
Do NOT touch fp-102 (last, PD409(g)) or fp-104 (hook gate, the chat's); no hook edit. Run `py tools/gate_fp.py list` afterwards and quote the fp-103 line and the new entry.

## Facts file `tools/bench/diag_c171_a2_3_facts.md` (<= 15 lines, file:line)
Reviewer verdict line (file:line), disposition paragraph path, drain line, new fp id and its list line, stage_prerun md5 (must still be af6937e8).

## Hygiene
No LabVIEW process before/after (`tasklist`), no `.vi`, no hook edit, `stage_prerun.py` byte-identical (af6937e8), no STATUS/INDEX/plan edit. Unexpected result = RETURN with the facts.
