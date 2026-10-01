# Brief for card 124-2 — the `frame` field for case-tunnel faces (offline; cycle 124 judgement, 2026-10-01)

Decision: `docs/d1-loop12-17-split-plan.md` Pre-decided **249(c)(d)(f)**. Runs beside LabVIEW card 124-1, which builds the
LabVIEW side. NO LabVIEW, no gate files (`tools/stage_prerun.py`, `tools/hooks/**` are not yours).

## Facts you start from
- 123-8 (`tools/bench/cards/result_123-8.json`, `tools/bench/plan_ring_p3a_sim.log:21`): `plan_ring_p3a_in.json` action 20
  `p3a_w_true_pass` cannot be expressed: stagesim keeps only the body frame's inner face of a plan-made case tunnel
  (`tools/stagesim.py:358-362`), stagexec sends a wire from a created tunnel to kind `branch` (`tools/stagexec.py:473-474`), and
  case data-tunnel creation is unmeasured in stagesim (`tools/stagesim.py:812-820`).
- 123-9 MEASURED case data-tunnel creation (`tools/bench/diag_c123_casetun.log:38,45,69`): a tunnel made by a cross-border
  `connect_nested_v1` into a `case_wired` case = SelectorTunnel +1, OuterTerminal +1, InnerTerminal +2 (one per frame); the case's
  `Terminals[]` lists the selector and the OUTER faces only. (Its junk `Invoke`s are being purged by 124-1; model Invoke +0.)

## The LabVIEW-side contract (fixed; 124-1 implements it — compile to it, do not call LabVIEW)
`gscript.case_frame_wire(target, case_uid, frame_index, src, dst)` with `src`/`dst` each `{"tunnel": <uid>}` (that tunnel's
inner face in this frame) or `{"node": <uid>, "term": "<name>"}` (a node on this frame's diagram); returns `{"wire_uid",
"src_term_uid", "dst_term_uid", "broken", "purged", "invoke_left"}`. `gscript.case_inner_face(target, tunnel_uid, frame_index)`
returns `{"term_uid", "tunnel_uid", "frame_index", "diagram_uid"}`. Frame index = the case's frame order (boolean case:
False = 0, True = 1, as stagesim's `_create_case_wired` names them).

## Work
1. `docs/protocol/stageplan.json`: an optional `frame` (frame NAME, e.g. "True"/"False") on a wire end that addresses a case
   tunnel face.
2. `tools/stagesim.py`: model a case data tunnel per 123-9's measured facts (one inner face per frame, outer face listed on
   the case), resolve `frame` to that frame's inner face, and simulate a wire inside one frame between inner faces / frame nodes.
3. `tools/stagexec.py`: compile such a wire to a new route `case_frame_wire` calling the contract above (frame name → index from
   the simulated case's frame order). Census for the route: declare it UNMEASURED (no sample — 124-1 records the real one), so
   `--scratch-required` keeps the scratch run.
4. Self-tests (new file `tools/bench/selftest_case_frame_c124.py` + log): a minimal plan with a True-frame pass-through simulates
   and compiles to `case_frame_wire` with the right frame index; `tools/bench/plan_ring_p3a_in.json` with action 20 re-addressed
   by `frame` (write it as `tools/bench/plan_ring_p3a_in_v2.json`; the original file stays) passes stagesim end to end; the
   existing self-tests stay green (stagexec 124/0, case_wired 14/0, census hook-in 12/0, launch_gate 29/0, c120_routes 29/0,
   census_predict 14/0).
Related edits land together, self-tested, or not at all. Return at the first unexpected result.
