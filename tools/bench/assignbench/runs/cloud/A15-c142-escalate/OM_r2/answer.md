ACTION: ESCALATE
CARD: Rung 1 (Opus max), same goal as 142-1/142-2: build claudeDev RingPickSlot_v0.vi per brief_142-1.md from build_ringpickslot_v1.py. Fix the lookup so that `lo`/`last` come from the terminal row's term_uid (#84), not from owner_uid. Keep the script at ≤120 lines. RUN the 7 vectors, then re-run 2 of them from the saved file in a fresh instance. LabVIEW must be gone at the end.
REASON: The card goal has now failed twice on the default model (142-1 and 142-2), so the rule says the next rung is Opus max.
Both failures are explained by our own script, so no handback is needed. 142-1 tripped a delete-verify, and v1 fixed it: the Constant traverse ended empty (build_ringpickslot_v1.log:14-21). 142-2's failure is the owner_uid=3 lookup hitting two controls (log:32,39; build_ringpickslot_v1.py:43), and the fix is already named.
The bed and s01 md5 are unchanged, so the start state is clean. Time used is 30 of 180 min and no cost has been reported.
No PREP card goes beside it: 142-P1's open question about the rebind key (uids 28004/28979 re-used) is a design decision for judgement, not offline material work.
HANDBACK-QUESTION: -