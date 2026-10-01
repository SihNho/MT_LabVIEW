# Brief for card 124-1 — the case-tunnel inner-face op (cycle 124 judgement, 2026-10-01)

Decision: `docs/d1-loop12-17-split-plan.md` Pre-decided **249(f)** (read 249(c)(d)(f)). Facts: `tools/bench/cards/result_123-9.json`
and `tools/bench/diag_c123_casetun.log:31-88` — input/output tunnels made by `connect_nested_v1` into a `case_wired` case are
SelectorTunnel +1, OuterTerminal +1, InnerTerminal +2 (one per frame) each; the case's `Terminals[]` lists only the selector and
the OUTER faces (`:69`); no existing verb reaches a tunnel's inner face in a given frame (`:70`); three junk `Invoke`s come from
cross-border `connect_nested_v1` / `connect_from_wire` (`:71`). `case_wired` (`tools/gscript.py:4837`) already purges its own
junk with `_purge_new_invokes` (`tools/gscript.py:4747`).

## The interface is FIXED by this brief (card 124-2 compiles to it in parallel — do not change names or shapes)
Two functions in `tools/gscript.py`:
- `case_inner_face(target, tunnel_uid, frame_index)` → dict `{"term_uid": int, "tunnel_uid": int, "frame_index": int,
  "diagram_uid": int}` — the tunnel's inner terminal in frame `frame_index` (the case's `Frames[]`/`Diagrams[]` order; a
  boolean `case_wired` case is False = 0, True = 1 — confirm this order by read-back, do not assume it). Raises on a bad index.
- `case_frame_wire(target, case_uid, frame_index, src, dst)` → dict `{"wire_uid": int, "src_term_uid": int, "dst_term_uid":
  int, "broken": bool, "purged": int, "invoke_left": list}`. `src` and `dst` are each `{"tunnel": <uid>}` (that tunnel's inner
  face in this frame) or `{"node": <uid>, "term": "<terminal name>"}` (a node on this frame's diagram, resolved with
  `term_index`, which raises). Purges its own junk `Invoke`s like `case_wired`.
If the measured API forces a different shape, STOP before writing code and return FAIL with the fact (card 124-2 would then be
re-cut); never silently change the contract.

## STEP 1 — fact + op
- The LabVIEW scripting property/method that returns a case tunnel's inner terminal(s) per frame and the wire-creation route
  between two terminals on one frame's diagram: a `-Kind fact` peer question (external search is mandatory), then confirmed on the
  machine. Use existing op VIs where they reach it; a NEW op VI goes in `claudeDev\Op*_v0.vi` and gets its hygiene record
  under `tools/bench/op_hygiene/` (≥ 2,000 calls, 0 errors, handle count flat ±100) before it is used in STEP 2.

## STEP 2 — scratch proof (one LabVIEW run, a byte copy of `claudeDev\D1_ring_p2b_20261001_140658.vi`, ≤ 120-line stagekit script)
Repeat 123-9's scenario (`tools/bench/diag_c123_casetun.py` is the starting point): on body `639` a fresh `Equal?` and a
`case_wired` case; an I32 value from outside enters through an INPUT tunnel; the False frame wires it through `Increment` to an
OUTPUT tunnel; **the True frame wires the input tunnel's inner face to the output tunnel's inner face with `case_frame_wire`**;
the output tunnel's outer face feeds a sink outside. Read back per frame: tunnel uids, each frame's inner-face uids, wires,
`Is Broken?` False on every new wire, and the classes created. Record a census sample for `case_frame_wire` (log lines) in
`tools/bench/census_samples.json` and a `tools/bench/scratch_verify/` record. Bed md5 `652b1447…` unchanged; scratch deleted;
LabVIEW verified gone.

## STEP 3 — junk-Invoke purge
Give the cross-border `connect_nested_v1` / `connect_from_wire` paths the same `_purge_new_invokes` treatment as `case_wired`
(wherever stagexec's routes call them — gscript or stagekit wrapper level, your choice, one place), proven by the STEP 2 run's
census showing Invoke +0, and keep the existing self-tests green (stagexec 124/0, case_wired 14/0, census hook-in 12/0,
launch_gate 29/0, c120_routes 29/0, census_predict 14/0). Do NOT edit `tools/stagesim.py`, `tools/stagexec.py` or
`docs/protocol/stageplan.json` — card 124-2 owns them in parallel.

## Rules
- No stage recipe is run. Return at the first unexpected result (finish the step, LabVIEW closed, facts recorded).
- A failing log → its Jev ladder row in your result; an owed hypothesis review is dispatched, never bypassed.
