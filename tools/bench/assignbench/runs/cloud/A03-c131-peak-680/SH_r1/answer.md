ACTION: ISSUE + PREP
CARD: S3: run `stage_d1_ring_p3b1_el.py` on the scratch VI already on disk to measure the Error List count against pred, with the scratch deleted by that script. No launch, no pin rerun. PREP (offline): tabulate the final-read memory deltas after the last op from every earlier pin and scratch run, and check whether the launch-gate X10 model counts that read. The prep card changes no threshold.
REASON: Card 131-3 FAILED only on S2 peak (680.8 MB at the final read after op 31, above the 675 fail_above, `pin4.log:446-447`). The other 22 gates passed (`scratch_pin4.log:608-611`), including E1 == sim through op 31, tunnel names as predicted, and bed md5 unchanged.
S3 (Error List count) does not depend on the peak question, and its scratch VI is still on disk. Pass item 3 owes that count, so it runs now (rule 2c: do all of the cycle that does not depend on the answer).
The final read adds +17.4 MB against the earlier ~+4.1 per read, and no fact explains why. The prep card measures the deltas from existing logs, so judgement gets facts and not a guess.
Whether to raise `fail_above`, re-cut P3b-1, or accept the peak is a threshold and design call, so I do not issue a re-pin, a retry or a launch. Only 63 of 180 card minutes are used, so there is time to go through S3 and the prep before handing back.

HANDBACK-QUESTION: -