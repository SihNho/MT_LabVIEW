# Brief 157-a1-1 (assignment 157-1): PD381 (b)(c)(d) tool fix, offline

Read first: `CLAUDE.md`, `docs/script-writing.md`, `docs/d1/ring-p5.md` item 381 (b)(c)(d) and 379/380, and
`tools/bench/diag_c156_a3_1_facts.md` (facts M1-M5). Reference code for the existing cases: `tools/bench/selftest_c156_passwire.py`
(how a stagexec/stagesim self-test replays recorded data) and `tools/bench/diag_c156_a3_1_route.py` (the M1 cases: ops 16/17
wired vs wire 0). Base pins: stagexec 25a1494c, stagesim eb99c6ba, addrcheck 207beb0d, stagekit aec03c6c. No LabVIEW, no hook edit.

## What to build (three parts, one card; the tools are the deliverable)
**(b) Inner-face route for a While/For LoopTunnel.** When a plan wire's source is the INNER face of a LoopTunnel on a While or
For loop and the live-read face has wire 0, take its diagram from the graph (tunnel -> owner loop -> that loop's one body
diagram) and choose the route the WIRED case chooses (`cfw`, same dst). Wired behaviour must not change. An inner face of a
Case or Flat Sequence tunnel still stops with the existing text. Make the change in `stagexec` / `stagesim` / `addrcheck`
(whichever of the three owns the stop text at the M1 line; the facts file quotes the stop text, grep it). One function, called
from every site that needs it (script-writing.md rule 1); a docstring naming the self-test.

**(c) FATE lines.** After every `move_in` op, the executor prints one `FATE` line per wire the sim marked ambiguous at that step
(`allow_either` rows from `_apply_only_sink`, stagesim.py around :1065-1080 / :1238-1239). The line records the wire uid, or 0,
on the SOURCE terminal and on the MOVED SINK terminal, taken from that op's checkpoint read (so the move_in op must be a
checkpoint, see (d)). Format: one grep-able line `FATE step=<k> wire=<sim wire uid> src_term=<uid> src_wire=<uid|0> sink_term=<uid>
sink_wire=<uid|0>`. It reads and prints; it computes nothing and never changes a verdict. If the moved sink term still has a wire
when its own connect op later runs, that is not decided here (the plan's op returns as before).

**(d) Checkpoints.** `stagekit.RingSession.CHECKPOINTS` (stagekit.py:1927-1929) also contains every op whose kind is `move_in`.
Recipes stay inputs-only; no recipe attribute. For `plan_ring_p5s02a.json` the checkpoint list must be exactly
`[1,3,6,8,9,15,16,17] + [10,11,12]` (sorted, as the existing code orders it).

## Measure, in this order (report all as FACTS in the facts file)
1. BEFORE any edit: store the op lists of `plan_ring_p5s01a.json`, `plan_ring_p5s01b.json`, `plan_ring_p5s02a.json` as compiled by
   the current tools (use the compile entry point the c156 passwire self-test used), plus the CHECKPOINTS list of each recipe
   (`tools/recipes/stage_d1_ring_p5s0*.py`) and the pass counts of the existing stagexec/stagesim self-tests (find them by
   `grep -l stagexec tools/bench/selftest_*.py`; run the ones the c156 passwire facts file named, with their last counts).
2. After the edit: the same lists/counts. Op lists of p5s01a, p5s01b, p5s02a must be identical (CHECKPOINTS may differ only by
   the added move_in ops, and only where the plan has move_in ops). Any other change in an op list = return with the diff.
3. New `tools/bench/selftest_c157_innerface.py` on recorded data (the sim steps under `tools/bench/sim/ring_p5s02a/`): cases
   (i) op 16 and op 17 give `cfw` with the same dst when wired and when wire 0; (ii) a Case/FS inner face with wire 0 still stops
   with the existing text (use a recorded Case or FS inner-face row from the graph; if none is recorded, say so in OPEN and
   build the case from the p5s02a graph's Case tunnel); (iii) FATE lines: a replay of p5s02a's ops 10-12 yields FATE lines
   for the six ambiguous wires listed in the M3 section (w10394, w24091, w24153, w24285, w24312, w24330), with each wire
   uid or 0 taken from a synthetic checkpoint read that the self-test constructs and states; (iv) checkpoints = the list above.
4. Re-run the existing stagexec/stagesim/addrcheck self-tests and `selftest_c156_passwire.py` (20/0 before). All must keep their counts.
5. Write md5s of the new stagexec/stagesim/addrcheck/stagekit. Do NOT run X10 or `stage_prerun` here: the next card does.

Facts file `tools/bench/diag_c157_a1_1_facts.md` (<= 45 lines, facts only, an `OPEN:` line per unresolved thing, no fix proposed
beyond what is built). Return the standard <= 30-line summary. Failure budget 2: if the wire-0 route needs a diagram lookup that
no recorded graph row supports, return with the row you could not find instead of guessing a graph shape.
