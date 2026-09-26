# Brief 97-2 — five scripting tools for the #1359 display-rate gate (plan Pre-decided 206(d))

The design they serve is Pre-decided 206(c) in `docs/d1-loop12-17-split-plan.md`. This card builds and MEASURES the
tools only; it does NOT build the gated VI (that is card 97-3).

T1 **nested case create**: create a Case Structure whose owner is a given loop-BODY diagram (a For loop body and a
   While loop body), by uid. Now `build_case` only takes the top-level diagram (`gscript.py:3173`). Read back the new
   structure's uid and owner diagram uid, plus the uids of its two frames (True/False) under a boolean selector.
T2 **move node set into a case frame, wires kept**: move a set of nodes (by uid) from a loop body into frame k of a case
   structure on the SAME body. Every wire that joined a moved node to a node left outside must come back through a
   case tunnel, with the same source terminal → sink terminal, read back after the move. Today move_in severs wires
   (`docs/cycle27-plan.md:846-851`). Gate: a before/after table of (source uid:term → sink uid:term) matches, with
   tunnels as the only new objects.
T3 **same for a control/indicator block-diagram terminal**: move it into a case frame, its input wire kept via a tunnel
   (ctlterm move_in route, `docs/d1-build-plan.md:213-222`).
T4 **label writer**: set the label text of a newly created front-panel control, and its default value (I32), read back.
T5 **output tunnel "use default if unwired"** setter (property id 5D251C00, `docs/NAMES.md:1036`), read back.

Every tool: an op VI in `claudeDev` (Op*_v0.vi) or a function in `tools/gscript.py` / `tools/stagekit.py`, whichever
matches the existing pattern for that verb class; documented in `docs/toolkit-capabilities.md` + `docs/NAMES.md`;
self-tested on a SCRATCH VI (not S1) that has a For loop inside a While loop with a small chain of nodes, including a
NEGATIVE case per tool (e.g. T2 on a node whose owner is a different diagram must refuse); 20 consecutive calls with
the handle count flat (±100); every VI Server reference closed.

Also run `py tools/protocol.py requires` on a card that lists the five by their final names, and put that output in
the result, so card 97-3 can cite them.
