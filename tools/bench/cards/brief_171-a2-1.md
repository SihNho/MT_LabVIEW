---
card: 171-a2-1
status: current
date: 2026-10-13
---
# Brief 171-a2-1 (assignment 171-2) - offline: re-hash, then ONE measurement: selftest_dry_c130_5 on the UNPATCHED stage_prerun db81a1d3

Plan: `docs/d1/ring-p6b.md` PD413 (lines 12-35), esp. (c). Read first: `CLAUDE.md`, `docs/script-writing.md`.
Offline only (`flags.labview none`): no LabVIEW, no camera, no motor, no VISA. Edit/Write tools only, never a heredoc.

## Step 0 - re-hash (drift = RETURN with the table, nothing else)
The script `tools/bench/diag_c171_a1_1_hash.py` already does the 18-row table (read-only hashing). Call it; do not write a second hasher.
Two edits to that file only (it is under your write glob): (1) swap its two stand-in hashes to the labels PD413(d) accepted:
`replay_imaqdx_get_image_buf.vi` = a89dafc1, `replay_get_buff_image.vi` = 842ecad9 (round-1 facts `diag_c171_a1_1_facts.md:3-4`);
(2) add one row: `tools/bench/diag_c171_a1_2_patch.diff`, want f8f1fd95.
Run: `py tools/bgrun.py --max-min 3 --log tools/bench/diag_c171_a2_1_hash.log -- py tools/bench/diag_c171_a1_1_hash.py`.
Expected: all rows OK, 7f2582ae found. Any DIFF / MISSING = RETURN (drift hands the purpose back); quote the table.

## Step 1 - the ONE measurement (PD413(c))
First check `git diff --stat tools/stage_prerun.py` is empty and its md5 is db81a1d3 (unpatched). Then run, once:
`py tools/bgrun.py --max-min 10 --log tools/bench/diag_c171_a2_1_c130_5_unpatched.log -- py tools/bench/selftest_dry_c130_5.py`
(expect ~2 min). Do not edit anything before or after; do not re-run it. Quote: the per-test verdict line of T1, T2, T3 and the totals line;
for T3 quote the `first_fail` line verbatim with its log line number (round 1 saw `DRY FAIL first_fail=GATE PB frame-keyed cdiff(S1, real end)
== the P2b bed's 16 rows ... unverified 1`, `diag_c171_a1_2_c130_5.log:8`; the record is 3/0, `selftest_dry_c130_5_c134_2.log:10`).
Classify T3 as ONE of: (A) FAIL at GATE PB, same text as `diag_c171_a1_2_c130_5.log:8`; (B) PASS; (C) FAIL elsewhere / different gate. State the class and the line, nothing more: the decision (re-apply the patch or hand back) is the assignment session's.
Both runs write prerun records only if the self-test does so itself; do not add `--no-record` handling of your own.

## Facts file `tools/bench/diag_c171_a2_1_facts.md` (<= 25 lines, file:line)
Step 0 table (name -> hash), the c130_5 per-test lines, class A/B/C, stage_prerun md5 before and after the run (must be equal).

## Hygiene
No LabVIEW process before/after (`tasklist`), no `.vi` written, no hook edit, no STATUS/INDEX/plan edit, `stage_prerun.py` byte-identical. A new unexpected result = RETURN with the facts.
