ATTACK this claim about the failed gate in tools/bench/diag_c128_2_donors.log (script tools/bench/diag_c128_2_donors.py).

Failure: gate `C2_W_frame0 op err '' and Is Broken? False` FAILED (diag_c128_2_donors.log:129-133). The op
`case_frame_wire` (tools/gscript.py) was asked to wire a DigitalNumericConstant #483 (created inside case frame 0,
uid 420, log:120-122) to the case's output tunnel; it raised `ValueError: #483 is not in Diagram[2].Nodes[]` before any
edit. The same constant pattern into frame 1 by `connect_term_uid(sink #448, src term #460)` passed (log:124-127).

Claim (128-2's explanation): `case_frame_wire` resolves its source by searching the frame diagram's `Nodes[]` array,
and LabVIEW constants are not members of `Diagram.Nodes[]`, so any constant source fails this op by construction; the
form C2 (error cluster on a case selector) is therefore unmeasured, not refuted, and the alternative route is
connect_term_uid on the tunnel's inner face. Consequence used by judgement (Pre-decided 261(a), docs/d1-loop12-17-split-plan.md:2828-2833):
the plan of record is form C1 (Unbundler + Select, 5 wires measured unbroken, log:56-101) and C2 is not used.

Attack: (1) Is the "constants are not in Nodes[]" reading right, or did the op look in the wrong frame diagram
(Diagram[2] vs frame 0's diagram uid 420)? Read tools/gscript.py case_frame_wire and the owner line log:120.
(2) Does anything about this failure undermine the C1 measurement the plan now relies on? (3) Cheapest discriminating
test. Answer in <= 25 lines with file:line evidence.
