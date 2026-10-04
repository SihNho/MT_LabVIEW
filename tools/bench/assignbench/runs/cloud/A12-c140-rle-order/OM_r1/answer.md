ACTION: CLOSE
CARD: -
REASON: Card 140-1 passed 7 of 7 gates, which covers all three pass items of the purpose:
- **X10 session table:** done for all of v14. Table A gives 9 sessions with peaks of 659.1–674.8. Table B gives 8 sessions with peaks of 672.0–674.8. Both are under the 675 limit (`prep_c140_1_sessions_r2.log:7-23`).
- **BIND-merge count:** step 1 can drop from 29 reads to 14, and the whole plan from 167 ops to 31 reads. Merging would need a stagexec edit (`stagexec.py:2031-2037`).
- **Facts file:** written with OPEN lines, and no tool was edited.

Card 140-2 went beyond the purpose (a LabVIEW build) and failed on its first unexpected result. Op 3 (wire_remove_loose_ends on w23255) hit error 1055 right after op 2 deleted #10171. Whether to change the plan order or the op's behaviour is a judgement decision. So is whether the 678.5 MB peak (over the 675 limit) is acceptable. Both are already in the OPEN lists of 140-1 and 140-2, so another card in this cycle would only pile up undecided questions.

HANDBACK-QUESTION: -