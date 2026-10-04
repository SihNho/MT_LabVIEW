ACTION: ISSUE
CARD: Offline: P4 step re-cut against X10 (memory) and the 42-action count. Use v14 meta. Keep step 1 at ≤39 actions, with the checkpoint set reduced so predicted peak is ≤690 MB. Re-cut steps 2–5 to ≤41 actions each. Then regenerate the step-1 plan and its pred, and rerun dry/prerun/X10 (no LabVIEW).

REASON: 139-7 failed only on the X10 gate: predicted peak 750.7 MB against a 690 MB limit, with 29 whole-VI reads from checkpoints {0, end} plus the bind ops (plan_ring_p4s1_pred.json:384-388). Step 1's plan is FINAL and its route check passes (prep_c139_7_s1.log:147-148), so the fault is sizing, not the plan.
139-6 left step 2 at 43 actions, over the 42 cap, and 139-7 raised the same sizing question for steps 2–5. Both are offline re-cut work, so one offline card covers them, and no LabVIEW card is needed until the step-1 prerun passes.
Which checkpoints to drop or how to re-cut is a design choice, but it stays inside the existing ≤~40-edits-per-session rule and does not touch computation (rule 1a). If the re-cut cannot meet X10 with fewer checkpoints, that returns to judgement.
Failure budget: 139-7 failed once on this gate, so this is a new card and not a retry.

HANDBACK-QUESTION: -