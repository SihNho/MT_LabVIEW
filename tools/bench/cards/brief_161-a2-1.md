---
card: 161-a2-1
status: current
date: 2026-10-10
---
# Brief 161-a2-1 (assignment 161-2) - OFFLINE TOOLING: PB inherits the case-move frames of the adopted chain (one shared stagekit function + self-test), and the p5s02b pred MAIN peak is recomputed on the real checkpoint set

`labview: none`, no `--launch`, no `tools/hooks` edit, no env bypass. Read `tools/bench/diag_c161_b1_2_facts.md` (all), `docs/d1/ring-p5b.md` PD394 (lines 246-284) and `docs/script-writing.md`
(a shared function carries a docstring naming its self-test; callers CALL it, nobody pastes it). Current md5: stagekit 0b5bb678, stagesim 95a162ba, stagexec a4df7e15, stage_prerun 7605116f,
plan f4520b10 (must stay), pred 18729409 (will change, see 5).

## The measured defect (diag_c161_b1_2_facts.md)
Gate PB on the p5s02b sim end sees 31 frame-keyed rows; the pred / plan carry 26 / 24 open pairs. The 5 extra rows are sinks on `#376` (cal cluster path in, error in, file size, selected path,
total data array in), present from step 0 of p5s02b (base 94ffff94), unchanged by every action. Their sources are S1 terminals now tagged `@<tunnel>/f0`: p5s02a created a CaseStructure and moved them
into it. `case_move_frames` (`tools/stagekit.py:1942-1958`) reads only the CURRENT plan's `move_in` into cases the SAME plan creates, so for p5s02b `move_frames` is `{}`.

## Decision already taken (judgement PD394(a)) - apply, do not ask
PB's allowed frames = this plan's `case_move_frames` UNION the case-move frames INHERITED from the adopted chain (p5s01a, p5s01b, p5s02a: the plans whose artefact is in the base's ancestry).
Each earlier plan's symbolic frame is mapped to its real frame uid through THAT step's recorded run bindings (its adopt / resume / scratch record) - never by looking at where the node sits now.
An inherited row is RECORDED only if ALL hold: (i) the same sink's bound row is present identically in the frame-keyed PB of the BASE graph (step 0) and of the end; (ii) the source terminal uids equal S1's;
(iii) every tag's frame uid is an inherited frame of the sink's or source's node. Anything else BLOCKS exactly as today.
If an earlier step's bindings are not on disk, or any of the 5 rows is not matched by an inherited frame: STOP and report which (hand-back). Do NOT widen the rule further, do NOT make the rows `open_rows`,
do NOT change the pred maker's non-frame cdiff.

## Do
1. FIND the binding records first (read-only): for p5s01a, p5s01b, p5s02a which file holds the symbolic-frame -> real-frame-uid bindings (run bindings / adopt record / resume record / scratch log). Quote file:line for each of the
   three. A step with no record = stop (see above).
2. Write ONE shared function in `tools/stagekit.py` that returns the inherited case-move frames (with the mapping above) and extend PB's licence source so that the PB check takes
   `case_move_frames(this plan) UNION inherited`. Read `case_move_frames` and the PB function (`pb_check`, `pb_check_bound`, stagekit.py ~1942-2014) FIRST and extend them, do not write a second PB. All PB callers
   (the p5s02b recipe pair, stage_prerun, the older recipes through `pb_check`) must get the inherited frames by calling the same function - quote the call sites you changed or confirm they inherit it through `pb_check`.
   The new function(s) get a docstring (first line: what it does and returns, names its self-test) and, if the module lists functions elsewhere, the function list regenerates itself (`tools/gen_capabilities.py`, do not hand-edit).
3. Self-test `tools/bench/selftest_c161_pbinherit.py` (<= 150 lines, replays STORED data): (1) the p5s02b sim end -> the 5 `#376` rows RECORDED, PB ok, `pairs_extra_left` `[]`, the other PB outputs unchanged;
   (2) a synthetic row with a changed source terminal uid still BLOCKS; a tag naming a frame no adopted plan made still BLOCKS; (3) the stored p5s01a / p5s01b / p5s02a PB results REPRODUCE unchanged (replay each from its
   stored sim end / graph; quote old vs new row counts and verdicts).
4. Because stagekit's md5 changes, every self-test that PINS stagekit goes stale. Run ONE pin sweep over the self-tests that import or pin stagekit (`grep -l "0b5bb678" tools/bench/selftest_*.py tools/bench/prep_c16*.py`), quote the list BEFORE
   editing, re-pin only the md5 that differs, and re-run each (counts before/after). A case that fails for a reason other than the pin: quote the line, do not loosen it.
5. PD394(b): recompute the pred MAIN peak of p5s02b on the REAL checkpoint set from `SX.checkpoint_ops` (ops 1, 4, 8 included; call the shared function, as 161-a1-2 did in `selftest_stagexec_s4.py`) instead of the hand-coded `BIND|{0,n}`
   at `tools/bench/prep_c156_a1_1_lib.py:98`. Edit `prep_c156_a1_1_lib.py` so it calls the shared rule, re-run `prep_c160_c3_1_pred.py` (re-pin its stagekit pin only), then licence / EL makers if their inputs move. Name every file whose md5
   changed with its cause. X10 is READ-ONLY: report the planned MAIN number against 675 (`py tools/stage_prerun.py` X10 or the lib's own line). **MAIN > 675 = stop and hand back; no cut, no limit change.**
   Plan f4520b10, the end graph and the predicted Error List items must be unchanged; if anything beyond the checkpoint set in the pred moves, report it and stop.
6. Re-run the existing p5s01a / p5s01b / p5s02a gate self-tests that call PB, and `selftest_c161_delckpt.py` (expect 11/0), `selftest_stagexec_s4.py` (24/0), `selftest_c156_b2_2_invcheck.py` (20/0), `selftest_c157_innerface.py` (13/0): quote counts. (Pin drift is fixed per 4.)
7. Background anything slow under `py tools/bgrun.py --material --max-min N --log ... -- ...`. Hook false positive on your own command text: `py tools/gate_fp.py log ...`, report; never edit a hook.

## Report `tools/bench/diag_c161_a2_1_facts.md` (<= 45 lines, facts only)
binding records (file:line x3); the shared function name + signature + stagekit line; PB call sites; self-test counts (new + pin sweep + the 4 suites); new md5 of stagekit, pred (18729409 -> ?), and every other changed file with its cause;
planned MAIN number vs 675; md5 UNCHANGED: stagesim 95a162ba, stagexec a4df7e15, stage_prerun 7605116f, plan f4520b10; `OPEN:` lines.
