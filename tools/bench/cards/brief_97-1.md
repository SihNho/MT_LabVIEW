# Brief 97-1 — the detail behind task_97-1.json's pass items (judgement, cycle 97)

(A) Every object linked to indicator #8323: Property Node / Invoke Node on a control reference, Control Reference
constant, Local variable, static VI Server ref, event-structure registration. Per object: uid, class, owner diagram,
what it reads/writes, every sink of anything it outputs. End with the explicit line
`NON-DISPLAY READER OF #8323: yes|no`.

(B) Every node in #1359's body diagram: uid, class, label/callee, and whether it lies on a path to out tunnel 11363
only, to 9227 only, or to both. List every wire that crosses between the two sets (source uid:terminal -> sink
uid:terminal). Confirm or refute: IndexArray #8741 reads the Insert #8634 output (vs the loop input).

(B') Terminals involved: #637's loop `i` terminal uid; #1359 input tunnels that feed only the graph set; out tunnel
11363's indexing mode; owner diagram uid of BuildArray #11261 and of #8323's block-diagram terminal (#639 frame? #637
body?).

(C) For each verb class the gate build needs, name the op VI / stagekit / gscript function that does it, or MISSING
(the `py tools/protocol.py requires` style check):
1. create a Case Structure inside a For-loop body; and inside #637's body / #639 frame
2. move existing nodes (a For-body node set; a BuildArray) into a case frame, keeping their wires
3. move a front-panel indicator's block-diagram terminal into a case frame
4. wire a While loop's `i` terminal
5. create Quotient & Remainder and Equal? / Equal To 0? primitives
6. create a new I32 front-panel control with label and default value
7. a boolean selector tunnel through a For-loop border, non-indexed
8. set an output tunnel's "use default if unwired"
