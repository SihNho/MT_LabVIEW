ACTION: RETRY
CARD: Re-issue 130-3 from P1, with one change. First dispatch the owed hypothesis review of `diag_c130_2_suite_gb.log` (flags.peers already include hypothesis) so guard_peer releases the block, filing the review under 130-2's log. Then:
- **P1:** rerun the fixed X10 self-test with the L0 gate printing each of its 8 conditions, and record the review's falsifier lines ("L0 PASS, no K1/DRY line").
- **P2:** run the P3b re-cut with `plan_ring_p3b_split.py`.
- **P3:** run X10, dry and prerun on both halves.
- **P4:** run the old `stage_prerun` self-tests.

If P1 does not pass, revert `stage_prerun.py`'s X10 to md5 88abd9c6 and stop before the re-cut.
REASON: The block in 130-3 is mechanical and the facts explain it. fp-24 shows guard_peer blocking on 130-2's log `diag_c130_2_suite_gb.log` (Jev new-problem p=0.712, review owed, not dispatched), and the one GATE-FP slot this cycle was already used by fp-22. Dispatching that one review is the legitimate release. Changing OFFLINE_SELFTESTS would be a gate edit outside the fp-queue drain.
The review in P0 (130-3) found the LF/CRLF fix safe. Its open point, alt (a), is a measurement question: the per-condition L0 lines and the falsifier answer it, so no design decision is needed.
Time used is 54 of 180 min and no LabVIEW has been touched. The scratch run and launch (pass item 3) remain for a later card once X10 passes.
HANDBACK-QUESTION: -