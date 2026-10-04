ACTION: HANDBACK
CARD: -
REASON: Card 140-3 failed at the Error List gate: the scratch run read 52 against a predicted 51 (alt 53). The scratch itself passed 19/0, with real ops matching sim, and peak 615.5 MB.
The review c140-3-el52 says the extra item is a node of p4_ras_bufdiff (donor #29157). It says that node is an Insert Into Array, while the plan names Replace Array Subset (diag_c140_3_facts.md).
That is a rule 1a question. If the node class is wrong, the ring's per-slot write is a different primitive than the original uses, and that changes the computation. Retrying the launch or escalating the model would not answer it.
A card cannot decide either choice: accepting 52 as the prediction, or correcting the node class. Both need a judgement call. The review is only SUPPORTED, not machine-verified. The answer should come from the original's node class (a read-only check), and then the plan or the prediction rule gets changed.
Offline prep is not issued. The 140-P1 FAIL (the provisional base holds session-1 objects) also awaits judgement, and any new prep would build on an unsettled session-1 plan.
Card minutes used are 97 of 180, so budget is not the constraint.

HANDBACK-QUESTION: Is the ring's per-slot write node (donor #29157, bed #29265/#29316) an Insert Into Array in the original, where plan_ring_p4_s01 names Replace Array Subset? Decide which of three is right, under rule 1a: (a) fix the plan primitive, (b) accept 52 as the session-1 Error List prediction and re-issue the launch, or (c) first order a read-only node-class check on the original and the bed, then decide.