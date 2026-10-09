---
card: 156-a1-2
status: current
date: 2026-10-09
---
# Brief 156-a1-2 - PD379(b) narrow tool fix: a case in-tunnel's PASS wire to an out-tunnel face in another frame; OFFLINE, LabVIEW 0

Why: card 156-a1-1 (`tools/bench/diag_c156_a1_1_facts.md` lines 17, 36) compiled 13 of 15 P5-2 groups and found two GAPs. The t3/t4
shift-register groups K3 / K4 (`#376` 'file progress' t3 / 'file number to append out' t4) are: SR L.inner -> case in-tunnel IK ->
pass wire (timed-out frame) -> case out-tunnel OK -> SR R.inner, with `#376` t3/t4 -> OK in the other frame. The compile ACCEPTS the
in-tunnel group (the frameless pass wire is its one out-wire, `stagexec.py:853-859`), but `stagesim.py:1536` refuses action 69
`w_k3pass` / `w_k4pass`: source IK3.inner on diagram -30, sink OK3.inner on diagram -29. Cause per the facts file: a frameless
OK3.inner resolves to its group frame f0 (`case_tunnel_frame`, `stagesim.py:832-836`) while IK3's group face is f1; with a `frame`
end the wire stops being a group wire (`stagexec.py:853-859`). `docs/d1/ring-p5.md` PD379(b) authorises the narrow fix, in
`stagexec.py` / `stagesim.py` ONLY, "only if existing routes cannot compile t3/t4" - that is now measured (facts file :17).

Read first: `diag_c156_a1_1_facts.md`, PD379 in `docs/d1/ring-p5.md` (lines 166-206), `brief_155-a1-1.md` + `diag_c155_a1_1_facts.md`
(the last tool fix of this kind: how it was scoped, its self-test, its regression list). Nothing else needed.

## What to build
1. MEASURE first, then decide the narrowest form. Reproduce the refusal offline on `plan_ring_p5s02r_all.json` (15da9551, 60 actions;
   K3 actions around 66-70, K4 around 71-75 - find them by the `w_k3pass` / `w_k4pass` aliases) and show the exact two resolved
   terminals (uid, class, frame_diagram) the sim compares. State which of the two ends would have to change for the wire to be legal in
   LabVIEW terms: both ends are INNER faces of one case's two tunnels; in LabVIEW a wire between them inside ONE frame of that case is
   a plain same-diagram wire. Say which frame LabVIEW places each tunnel's inner face on (the `tunnel` action's `body`, op_tunnel ->
   _case_tunnel; measured, not assumed). Do not invent a frame rule: cite the code or a recorded graph (e.g. the three cases at
   `stagesim.py:1315`, graph_qrt_pool_20260928.json #2222/#2857/#3826, or P5-1's own graph 6716c499 #30726).
2. Implement the smallest change in `tools/stagexec.py` and/or `tools/stagesim.py` that lets a plan express the pass wire of a case
   in-tunnel group so that (a) stagexec compiles it to ops with the SAME op kinds the other 13 groups use where possible, (b)
   stagesim replays it as a legal same-diagram wire in the frame the plan names, (c) the compiled op list for every existing plan is
   unchanged. If it needs a new plan field (for example a `frame` on the pass wire that is still a group wire), say which, with the
   reason, and make the refusals for malformed use specific.
3. Reuse existing helpers; add no new route family beyond what the measurement shows is needed. Every new public function gets a
   docstring (first line: what it does and returns; names its self-test). `docs/script-writing.md`: call shared functions, no copies.
4. NEW self-test `tools/bench/selftest_c156_passwire.py` (header `labview: none`, `hardware: none`): replays RECORDED data - the graph
   `graph_ring_p5s01_20261009_125622.json` (6716c499) and the K3 rows of `plan_ring_p5s02r_all.json` (actions from the facts file).
   Cases: (a) the K3 group (SR L.inner -> IK3 -> pass -> OK3 -> SR R.inner, plus `#376` t3 -> OK3 in the other frame) compiles and
   simulates to the end with 0 PROVISIONAL; (b) the same for K4; (c) the refusal at the old message still fires for a pass wire
   between two faces on genuinely different diagrams with no tunnel (the real border error); (d) a plan-made case with ordinary groups
   behaves exactly as before.
5. The sim result the later plan needs: after K3/K4 simulate, the `#6384` / `#2048` sinks that took t3 / t4 in P5-1 are fed by the
   R.inner net (quote the sim's sink rows, file:line of the output).

## Regression (quote counts)
- Op lists BEFORE vs AFTER your edit are identical for: `plan_ring_p5s01a.json` (ed62e8d6), `plan_ring_p5s01b.json` (75a77a00),
  `plan_ring_p5s01_in.json`, `plan_ring_p5s02a.json` (4284c22a, the 156 step-1 plan; K rows absent) and the 155 step plans
  `plan_ring_p5s02*.json` that exist. Store the BEFORE lists first (compile with the current tools and write them under
  `tools/bench/sim/ring_p5s02pw/` or into the facts file hashes), then edit, then compare. Quote equal / not equal per plan.
- Existing self-tests PASS with their last counts: `py tools/stagexec.py selftest`, `py tools/stagesim.py selftest`,
  `selftest_c155_basecase_frame.py`, `selftest_c120_caseshape.py`, `selftest_case_frame_c124.py`, `selftest_stagexec_gate.py`,
  `selftest_stagesim_tunnel_naming.py`, `selftest_fs_c126.py`, `selftest_t6_regress.py`. Quote each. A pin-drift failure in a FROZEN
  cycle self-test is not yours: name it, do not re-pin it.
- Pins that must NOT change: stagekit aec03c6c, stage_prerun 9decb20f, vigraph a7eb58c7, addrcheck 207beb0d, gscript 1a80236e.
  Report the new md5 of stagexec.py and stagesim.py (they change only if the measurement says they must).

## Rules
Offline; `tasklist` shows no LabVIEW before or after. No `tools/hooks/**` edit; no edit to any stored recipe / plan / pred / P5-1a /
P5-1 file; no rewrite of `plan_ring_p5s02*` (the next card re-makes the plan with K3/K4). Rule 1a: only how the stage tools ADDRESS a
wire changes; no VI content or computation. A gate false positive in a hook: `py tools/gate_fp.py log ...` and go on. If the change
cannot be shown to leave the other compiled plans untouched, RETURN with the row. Run the self-tests under `bgrun --material`.

## Report `tools/bench/diag_c156_a1_2_facts.md` (<= 40 lines, facts only, `OPEN:` line)
The measured terminals and frames; the change (file:line); the new field if any; the sim sink rows; before/after op-list equality per
plan; each self-test result; new md5s; pins; invariants. Facts only; no result-dependent action.
