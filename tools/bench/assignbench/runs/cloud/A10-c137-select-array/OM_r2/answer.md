ACTION: ISSUE
CARD: Build/run a read-only reader on a byte copy of the bed for base While #10170: read its conditional terminal mode (Stop If True? vs Continue If True?) and the Mechanical Action of the `stop` (end) Boolean control. Record both values under scratch_verify/. Do not edit the bed, run no wires, and stay within 45 min.
REASON: Pass item 2 ("#10170 Stop If True? and stop (end) Mechanical Action read on the machine") is the only pass item no card has attempted yet. Items 1, 3 and 4 have results:
- Item 1: 137-5 gives PASS/FAIL with Is Broken? for every route (U1/U2/U5/W1 PASS, U3/U6 FAIL), and 137-7 measured why.
- Item 3: 137-P1 named the step-102 cause at vigraph.py:57-60 / stagesim.py:681.
- Item 4: 137-P1 built the session table. It is not fully within 675: U05 alone is 676.9 > 675.

The open questions do not affect item 2, so per rule 2c it runs first and they go to judgement at close: the Select Boolean-array redesign (137-7, rule 1a), the p4_x_n2_out route, step 3 = 41 > 40, and the #10465 rewire. There is 59 min left of the 180-min cap, enough for one 45-min LabVIEW card.
HANDBACK-QUESTION: -