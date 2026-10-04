ACTION: CLOSE
CARD: -
REASON: Pass items 1 and 2 are met. Card 131-1 built the crossing table (18 crossings) and the stagesim self-test passes 105/0. P3b-1 31 + P3b-2 39 = the unsplit 70, and P3b-1 dry 31/31 and prerun 15/0 both pass.
Item 3: the scratch pin4 run missed two predictions. Peak memory was 680.8 MB against 663.4 predicted (131-3), and the Error List count was 53 against 54 (131-4). Judgement then set PD272/273/274 to take these up. Under them, the ONE launch passed 22/0 at a 680.4 MB peak, under the 690 cap. It saved D1_ring_p3b1_20261002_060910.vi with the input bed unchanged (131-5, stage_d1_ring_p3b1.log:430-474).
PD274(c) is met by measurement: a full Error List read found 53 items with 0 extra and 0 missing, the only class change is loose ends 24→22, and the expected file is re-pinned (131-6, final2.log:94,113-115).
What is still open is judgement work, not a card. Two questions: should current-bed move to the new file, and is a per-wire test of the #6810 nets (w3040 vs w653/w3747) needed before the 53 baseline is trusted? Carry both, and the open items from 131-1 and 131-2, into the next NEXT.
HANDBACK-QUESTION: -