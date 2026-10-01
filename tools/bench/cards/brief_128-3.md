# Brief for card 128-3 (cycle 128 judgement, after result_128-1.json FAIL 7/1)

## Step 0 — the review gate on 128-1's failing log
`diag_c128_1_checks.log` is now a failing log; LabVIEW card 128-2 may be held by it (cycle-122 carry: an offline
card's log holds a LabVIEW card). Read the newest `JEV-LADDER` line for that log in `tools/bench/jev_gate.log` and
follow its NEXT-ACTION. If it says a hypothesis review is owed, dispatch it FIRST
(`peer.ps1 -Agent claude -Role hypothesis -TimeoutSec 780`, -TaskFile naming `diag_c128_1_checks.log` and
`diag_c128_1_checks.py`). Claim for it to attack: "X5's 123 is an over-count by `WIRE_VERB_RE`
(`stage_prerun.py:109`, `connect|wire|fs_inner`) of read/RLE/helper verbs, not 97 extra real wiring calls".

## Step 1 — MEASURE the X5 breakdown (no fix to X5, no gate_fp entry yet)
From the recipe's dry trace, list every one of the 123 counted ops: verb name, the plan action id it serves (or none),
and whether it edits the diagram (creates/deletes a wire) or only reads. Group: (a) per plan wiring row (12 wires + 14
crossings = 26), (b) RLE rows (15), (c) read-only verbs, (d) anything else. Report the four counts and every op in (d)
by name and line. Do NOT change X5 or log a gate false positive — judgement decides that from your table.

## Step 2 — two of our own tool bugs (fix, self-test)
1. `stage_prerun.py:601` installs `builtins.open = dry_open` and never restores it; restore `REAL_OPEN` in a
   `finally` after an in-process `--dry`. Add a self-test case (write after an in-process dry lands on disk).
2. Write `plan_ring_p3b_pred.json` with a per-row census source that `census_predict` reads (rows 1..63 currently
   CENSUS-UNPREDICTED). Values come only from measured census variants (`census_samples.json`) already used by
   stagesim; a row with no measured variant stays unpredicted and is listed.
Then rerun plan dry + prerun and recipe dry + prerun; record every check's result (X5 will still fail; record it).

## Not in this card
The prior-art review and the PD258(c) guard rows wait for card 128-2's measurement and the judgement decision.
