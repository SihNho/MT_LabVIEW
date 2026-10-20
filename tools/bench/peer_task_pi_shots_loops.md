ATTACK this claim (judgement session, 2026-10-19), about the failure in tools/bench/pi_shots_loops.log
(script tools/bench/pi_shots_loops.py; first failure: "W P6L #637 ... error 1 Write PNG File.vi / Check Color Table
Size.vi", pi_shots_loops.log:229; facts in tools/bench/cards/result_chat-PI3.json and pi_shots_20261016/loops_p6l.json).

Claim: Node.Get Image (6358C01, via OpGetImage_v0) cannot image the P6L While loops because those loops report GObject
Bounds height 0 (8860x0, 36528x0, 3710x0, 35789x0, all at y 223) - they sit inside a FlatSequenceFrame (owner hops
there give error 1055), so the zero-height image makes Write PNG fail; the two loops that did image came out all white
for a related reason. Handles are NOT the cause (flat after the first shot). The original VI's While #637 imaged fine
because it is not inside such a frame. Therefore the next step should NOT retry Node.Get Image on P6L loops, but take
the WHOLE block diagram of both the original copy and the P6L copy with the verified VI method BD.Get Image Scaled
(42C, OpGetBDImage_v0.vi, hygiene PASS) with Maximum Width/Height wired (e.g. 4000) so LabVIEW scales the huge P6L
diagram down - one fresh LabVIEW per VI.

Attack it: is "height 0 because of the FlatSequenceFrame" supported by the log, or could it be the headless load (no
diagram window opened), a stale layout, or the P6L copy's missing subVIs? Would BD.Get Image Scaled hit the same
zero-height / white-image problem on a headless P6L load? What one check before the run would tell? Read:
tools/bench/pi_shots_loops.log, tools/bench/pi_shots_20261016/loops_p6l.json, tools/bench/cards/result_chat-PI3.json,
tools/bench/cards/result_chat-PI2b.json, tools/bench/pi_shots_20261019.log (P6-1 vs P6L run).
