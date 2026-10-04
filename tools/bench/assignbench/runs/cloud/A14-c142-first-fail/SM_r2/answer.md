ACTION: RETRY
CARD: Re-issue 142-1: build RingPickSlot_v0.vi (P4 slot selection), with our script fixed so the generator For's constants are deleted without the per-object verify and the Constant set is re-read afterwards. Keep the script to ≤120 lines. RUN it on 7 known vectors and re-run 2 from the saved file in a fresh instance.
REASON: The card failed once, so its failure budget of 2 is not spent and escalation is not yet due.
The failure came from our own script's assumption. Deleting Constant #50 made 2 Constants vanish, and the likely second one is k0 #138 inside the already-deleted For (diag_c142_1_facts.md:19-21).
Num route, For deletion and bed state are clean: gates are 9 pass and 1 fail, the bed is unchanged, and LabVIEW is gone (log:10-15, 31-32).
Nothing needs a design, threshold or rule-1a decision. The retry changes only our build script's delete order and verify handling, not the original's computation. The cost is about 10 of 180 minutes.
HANDBACK-QUESTION: -