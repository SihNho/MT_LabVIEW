# Brief 125-2 — P3a bed graph read + the 55th Error List item traced; then the Flat Sequence creator (LabVIEW)

Decisions: `docs/d1-loop12-17-split-plan.md` Pre-decided **251(c)(d)**, **248(c)**, **246(c) A1**. The bed
`claudeDev\D1_ring_p3a_20261001_180540.vi` (md5 `4dfa44aac8fb32f706b3eb792ee7d3cc`) is never saved over; all building
happens on BYTE COPIES. Every script is a <= 120-line stagekit file. Card 125-1 just changed guard_peer/protocol/
stage_prerun (gate-fp drain + X16); if a gate refuses wrongly, log it with `tools/gate_fp.py log` and return.

## STEP A — real graph read of the P3a bed + trace of the 55th item (read-only)
1. Read the bed's graph with the same reader 123-8 used for P2b (`tools/bench/diag_c123_graph_p2b.*`, output
   `tools/bench/graph_ring_p2b_20261001_154542.json`) → `tools/bench/graph_ring_p3a_<ts>.json`. Bed md5 unchanged.
2. MEASUREMENT: list every wire in the P3a graph that has an end connected to nothing (or fewer than one source + one
   sink), and mark which of them are NOT present in the P2b graph (new in P3a). For each new one: wire uid, the
   terminal(s) it IS connected to (node uid, node class/name, terminal name), the diagram it lives on (frame/loop).
   Also cross-check with `plan_ring_p3a.json`: which plan row made it.
   PREDICTION (for the "first unexpected result" rule): exactly one new loose-end wire exists and its uid/ends are
   read. Whether it is "the one P3b consumes" is NOT your call — just report the facts.
3. Only if the graph diff cannot single it out: Error List double-click on the loose-end items (GUI, capture → locate →
   act → capture → confirm, `lv_gui.ps1 -Exception Approved -Evidence "PD251(c) trace"`), no save.

## STEP B — Flat Sequence creator (LabVIEW, scratch on a P3a byte copy)
Target: a Flat Sequence of N frames (here 3) on a given diagram — here the **False (new-frame) frame of P3a's case** in
While `#637`'s body (the place P3b will use). No donor, frame-add op or `FlatSequence.Diagrams[]` reader exists today
(`diag_c123_struct.log:47`). Mechanism is yours: a scripting method on the FlatSequence class (frame add), a donor VI
built once + `struct_copy_nested` (the `case_wired` pattern, `claudeDev\DonorCase_v0.vi`), or a new op. If the
FlatSequence API is uncertain, ask a `-Kind fact` peer first (CLAUDE.md "external search is mandatory") before
concluding anything is impossible.
- Read back: frame count, frame ORDER (left → right), each frame's diagram uid, the classes created (census delta), and
  that a wire from a frame-1 node to a frame-2 node is possible (one sequence tunnel; read the tunnel class and
  `Is Broken?`).
- Deliverables: the gscript function, an opmodel/census sample (`census_samples.json`), a `scratch_verify` record.
  Any NEW op VI gets its hygiene record (>= 2,000 consecutive calls, 0 errors, handles flat ±100,
  `tools/bench/op_hygiene/<op>.json`) — `gscript.op()` refuses it otherwise.
- NOT in this card (next card, offline): the stagexec route, the stagesim model, the stageplan field and self-tests.
  Record in the result exactly what the route will need (arguments, returned uids, created classes, frame naming).

## Rules
- No stage recipe is run. Bed md5 unchanged; scratch copies deleted or md5-recorded; LabVIEW closed and verified gone.
- Return at the first unexpected result (finish that step, LabVIEW closed, facts recorded). STEP A's result does not
  gate STEP B unless STEP A leaves LabVIEW in a bad state.
- A failing log → the Jev ladder row; an owed hypothesis review is dispatched (`-Agent claude -Role hypothesis`).
