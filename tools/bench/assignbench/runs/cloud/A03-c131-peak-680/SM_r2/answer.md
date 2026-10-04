ACTION: ISSUE
CARD: Run stage_d1_ring_p3b1_el.py on the existing scratch VI. Read the Error List count only, compare it with the expected 54, and let the script delete the scratch. Do not rerun pin4 and do not launch the real recipe.
REASON: Card 131-3 passed every gate except S2 peak memory. The 680.8 MB came only from the final whole-VI read after op 31, +17.4 MB against the usual ~+4 (pin4.log:446-447). E1, FS tunnels, names and handles all matched the sim, and the bed md5 is unchanged.
REASON: S3 needs no ruling on the peak. It measures the Error List count on the scratch VI that is already on disk and clears it, whichever way the model question goes. Rule 2c says to finish the independent part first.
REASON: Whether to accept the 680.8 MB, raise `fail_above`, or re-cut the memory model is a threshold decision. It goes to judgement once S3 has returned its facts.
HANDBACK-QUESTION: -