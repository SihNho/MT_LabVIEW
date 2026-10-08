---
card: 151-a3-3
status: current
date: 2026-10-09
---
# Brief 151-a3-3 - s07 stored end read RE-SCORED offline with the position-keyed result gates (docs/d1/ring-p4c.md PD367(f)(h), PD366)

OFFLINE, no LabVIEW, no licence. Purpose: the s07 scratch (cycle 150) was scored with the OLD name/uid-keyed D / TD / PB gates and failed on a false positive; merge 9dbd384b (card chat-T6, PD366) re-keyed them by POSITION. Re-score the STORED s07 end read with stagekit 604529e8 and report the verdict.

Inputs (stored, read-only): `tools/bench/diag_c150_p4s07v18_scratch.log` / `.json` / `_sum.json` (the s07 scratch run and its end read), `tools/bench/graph_ring_p4s07_20261008_224835.json`, the s07 plan/pred, `docs/d1/result-gates.md`, `docs/d1/ring-p4c.md` PD366/PD367.

Steps:
1. Find, from the files, how the scratch recipe scored D / TD / PB (stagekit functions and the stored end-read keys in the .json) and call the SAME stagekit 604529e8 gates on the stored end read, in a new script `tools/bench/diag_c151_a3_3_rescore.py` (labview: none; do not import a module that runs LabVIEW). No stagekit/stagesim edit.
2. Report per gate (D, TD, PB): verdict, counts (new/sim, lost, reuse, renames, unlicensed, cdiff rows/open pairs), next to the s07 original verdict (what the 150 log said) and to the s08 verdicts of `diag_c150_p4s08v18_scratch.log:267,272,274`.
3. If a gate cannot be called offline on the stored data, say which input is missing (file:line); do not fabricate and do not run LabVIEW.
4. Invariants md5 before = after: stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun c739eb86, vigraph 13be0847, stagesim 748bbf30, s07 b3f86b32, memory_model a28b6dd7, gate_fp_queue; no tools/hooks edit; tasklist LabVIEW count 0.

Report `tools/bench/diag_c151_a3_3_facts.md` (<= 30 lines): gate verdicts + counts, the s07-original vs re-score comparison, invariants, `OPEN:` line. Facts only; no decision.
