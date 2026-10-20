ATTACK this claim (judgement session, 2026-10-19), about the failure in tools/bench/pi_shots_ops.log
(script tools/bench/pi_shots_ops.py, gate at :114, failure line: "H handles at end <= start + 1000 (34003 -> 35474)").

Claim: the +1,471 rise in the LabVIEW process handle count during pi_shots_ops.py is NOT a reference leak of our ops and
does not invalidate the seven Op PNGs, because (1) the script's own ref counter says refs opened 7 / closed 7 / live 0
(pi_shots_ops.log:56-57); (2) the rise happened after loading seven Op VI copies into one LabVIEW (each load brings its
subVIs, front panels and diagrams into memory, which costs OS handles that LabVIEW keeps until the VIs leave memory);
(3) OpGetBDImage_v0.vi itself passed the 2,000-call op_hygiene run with max_dev_closed 23
(tools/bench/op_hygiene/OpGetBDImage_v0.json, build_op_getbdimage_v0b.log:51); (4) LabVIEW was killed and verified gone
afterwards, so nothing persists.

Attack it: what else could explain +1,471 handles (BD.Get Image Scaled loading the diagram/front panel of each VI,
image buffers, Write PNG File, unclosed VI refs inside OpGetBDImage_v0, the 1000 threshold being arbitrary)? Which of
these would matter for the planned next step - one more run of tools/bench/pi_shots_loops.py that opens ONE large VI
(P6L, 54f7cd2f) alone in a fresh LabVIEW and calls OpGetImage_v0 (Node.Get Image) on 6 While loops? State what check
would distinguish "loaded-VI handles" from "op leak" cheaply, and whether the Op PNGs should be trusted.
Read: tools/bench/pi_shots_ops.log, tools/bench/pi_shots_ops.py, tools/bench/op_hygiene/OpGetBDImage_v0.json,
tools/bench/build_op_getbdimage_v0b.log, tools/bench/cards/result_chat-PI2b.json.
