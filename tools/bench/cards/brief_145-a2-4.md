---
type: brief
status: current
date: 2026-10-07
---
# Brief 145-a2-4 — RETRY of 145-a2-3 (one explained fault in our own gate): finish the requiredness measurement

Read first: `tools/bench/cards/brief_145-a2-3.md` (the whole job, unchanged) and `tools/bench/cards/result_145-a2-3.json`.

145-a2-3 built the reader `claudeDev\OpWiringRules_v0.vi` (02beb55f, cold ES 1) and read a scratch copy of RingSeqCheck_v0
uncontrolled: n=12, rules `[0,2,2,2,0,0,0,2,2,2,2,2]` (build_opwiringrules_v0.log:40-41). It then stopped at its OWN gate: the
setter `Wiring Rule:Set` 239A8001 reports 3 data sinks `['SetWireRule','TermIdx','Rule']` where the gate expected 2
(log:45-47). `SetWireRule` is the Invoke method-header row, not a data input.

## Do
1. Fix `tools/bench/build_opwiringrules_v0.py:79` only: the gate takes the 2 sinks other than the method-header row `SetWireRule`.
   Rebuild the reader only if the build script's output changes; otherwise reuse 02beb55f (md5 check). Report which.
2. Run the rest of brief 145-a2-3 steps 2(a)-(c) and 3-5: positive control (set Required / Recommended / Optional on a throwaway
   scratch, read back), hygiene (20 calls, handles flat +-100; the card record `tools/bench/build_opwiringrules_v0_hygiene.json`),
   the measure script `tools/bench/diag_c145_a2_3_measure.py` (5c6c3cfb; reads both subVIs read-only, joins the wired map from
   `diag_c145_a2_1_table.log`), then delete abb76d41 and `tools/bench/resume/resume_plan_ring_p4_s04v18_20261007_212913.json`
   ONLY on PASS of the table (no unwired Required input at PS1/SQ1).
3. Copying the hygiene record to `tools/bench/op_hygiene/` is not in this card's write glob: report it as OPEN, do not widen the glob.
4. Notice: free pane slots read 0 and assigned terminals read 2 (Recommended) on the unmodified file. A value that stays 2 for
   every assigned terminal, including the control-set ones, means the setter did not take: say so, do not infer.

## Never
Same as brief 145-a2-3. A second failure of the SAME gate class = RETURN with raw values.

## Return
`result/1`, facts file `tools/bench/diag_c145_a2_3_facts.md` (table citable by file:line).
