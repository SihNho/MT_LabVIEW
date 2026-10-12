ATTACK this claim (cycle 171 judgement PD413(c), docs/d1/ring-p6b.md:12-40).

Failure: card 171-a1-2 ran `tools/bench/selftest_dry_c130_5.py` with the patched dry checker (stage_prerun af6937e8,
patch tools/bench/diag_c171_a1_2_patch.diff); T3 (full dry of tools/recipes/stage_d1_ring_p3b2a.py) FAILed with
"GATE PB frame-keyed cdiff(S1, real end) == the bed's 16 rows and the plan's 11 open (node, term) pairs (FATAL, before
save)" - log tools/bench/diag_c171_a1_2_which_t1.log (script tools/bench/diag_c171_a1_2_which.py). Recorded verdict of
that self-test: 3/0.

Claim under attack: "c130_5's stored records (cycles 134, 152) predate the PB-criterion change of PD370(b) (cycle 153,
docs/d1/ring-p5b.md:165), so the T3 FAIL may predate the patch; one run on the UNPATCHED stage_prerun db81a1d3 decides
it: same GATE PB FAIL unpatched = stale self-test, not caused by the patch."

Attack: (1) Is the PB-criterion change really the only change between the record and now that can flip T3 at GATE PB?
Read the git history of tools/stage_prerun.py, tools/stagekit.py and the recipe since the c130_5 record. (2) Could the
value-criterion patch alter the PB gate's input rows (taint of the `real` rows) so that the unpatched run is NOT a fair
baseline? (3) Is there a cheaper or more decisive test than the unpatched run? Offline only: read code and logs, run
nothing that touches LabVIEW. Answer with the weakest point of the claim and what would refute it.
