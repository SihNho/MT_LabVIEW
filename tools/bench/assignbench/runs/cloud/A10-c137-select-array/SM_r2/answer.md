ACTION: HANDBACK
CARD: -
REASON: The purpose needs P4 routes U1, U2, U3, U5, U6 and W1 Or each marked PASS/FAIL, but U3 and U6 are now measured as design problems, not connect defects.
- 137-7: Select.s takes only a scalar Boolean. A Boolean array on s breaks the wire whatever t and f carry (C1, C2, C3 broken; the scalar control C5 is fine). Reading the reader core as a Boolean-array Select is therefore a design change.
- 137-7: U6 exits fine with a typed source (U6' works), but the plan's unwired IAN.array gives a void output and a broken wire.
- Rule 1a applies. The reader's Select with a Boolean-array s computes something, and replacing it could change the computation. Only judgement can say whether another construction is equivalent.
- 137-6 and 137-4 add plan-level stops: p4_x_n2_out has no route, step 3 holds 41 actions against the cap of 40, and stagesim loses #10465 at step 159. These also need a plan decision.
- 137-1 and 137-3 are resolved: constants are found by read_terms by owner uid. Another route-measurement card would test a reader core that is already known not to wire.

HANDBACK-QUESTION: Select cannot take a Boolean array on s, so what construction replaces the P4 reader core's Select, and can you show it computes the same as the original (rule 1a)? Please also decide the p4_x_n2_out route and the step-3 re-cut (41 > 40).