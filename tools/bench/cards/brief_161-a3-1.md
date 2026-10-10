---
card: 161-a3-1
status: current
date: 2026-10-10
---
# Brief 161-a3-1 (assignment 161-3) - OFFLINE TOOLING: PB records class 1 (inherited row) and class 2 (plan-wired into an inherited case) in ONE shared stagekit function; pred MAIN recomputed on the real checkpoint set

`labview: none`, no `--launch`, no `tools/hooks` edit, no env bypass. Read `docs/d1/ring-p5b.md` PD394 (246-284) and PD395 (286-321), `tools/bench/diag_c161_a2_1_facts.md` (all; it is the measurement of the
binding records and of the 5 rows), `docs/script-writing.md`. Current md5: stagekit 0b5bb678, stagesim 95a162ba, stagexec a4df7e15, stage_prerun 7605116f, plan f4520b10 (must stay), pred 18729409 (will change, see 5).

## Already measured and decided - apply, do not re-ask
Binding records on disk: p5s02a `adopted_scratch.jsonl:11` -> `diag_c158_p5s02a_scratch.log:161` (`STEPX 09 create c_case7 bound {-28:31308, -29:31506, -30:31517, -31:31485}`); p5s01b `:10` (log `:137`);
p5s01a `:9` (log `:229`). Inherited case-move frames = {376, 3052, 3453: [31506]} (from p5s02a only; p5s01a/b give {}). Of the 5 extra `#376` sinks: `cal cluster path` and `file size` are CLASS 1; `selected path`,
`error in`, `total data array in` are CLASS 2 (wired by p5s02b actions #4 `w_in3_376`, #7 `w_g376`, #15 `w_h376` through its own new CQ7 tunnels). The doubled S1 uids on `error in` / `total data array in` are one
per CQ7 frame (f0 31506, f1 31517); that is PD374(d)'s pass-through and is decided under rule 1a (numeric acceptance stays P6).

## Licence (PD394(a) + PD395(b)) - RECORDED only if the stated conditions hold, anything else BLOCKS exactly as today
Class 1 (inherited row): (i) the same sink's bound row is identical in the frame-keyed PB of the BASE graph (step 0) and of the end; (ii) source terminal uids equal S1's; (iii) every tag's frame uid is an
inherited frame of the sink's or source's node.
Class 2 (plan-wired into an inherited case): (i) at step 0 the sink is unwired (base `after` []) and at the end it is wired by a connect action of this plan; the record NAMES the action; (ii) the SET of source
terminal uids equals S1's, each uid's multiplicity being 1, or exactly the frame count of the case in (iii) when (iv) applies; (iii) every tag is (a tunnel this plan creates, a frame uid of a case an adopted plan
created); the case's frames come from that step's binding record, never from where nodes sit now; (iv) a tag on a frame OTHER than the sink node's inherited frame is allowed only for the sinks PD374(d) names as
pass-through registers (`#376` t0 `error in`, t1 `total data array in`). Do NOT widen further, do NOT make the rows `open_rows`, do NOT change the pred maker's non-frame cdiff.
If a binding record is missing, or a row is not matched by class 1 or class 2: STOP and report which (hand-back).

## Do
1. Read `case_move_frames` and the PB functions (`pb_check`, `pb_check_bound`, `pb_bound_rows`; stagekit ~1942-2014) and `prep_c161_a2_1_measure.py` (it already calls the helpers needed to bind the earlier
   steps and to read frame tags - CALL them / extract what repeats into stagekit, do not paste).
2. ONE shared function in `tools/stagekit.py` that records both classes (docstring first line: what it does and returns, names its self-test), extended into PB (extend `pb_check`, do not write a second PB).
   Every PB caller (the p5s02b recipe pair, stage_prerun, the older recipes through `pb_check`) must get it by calling the same function - quote the call sites changed or confirm they inherit it through `pb_check`.
   Function lists regenerate themselves (`tools/gen_capabilities.py`), do not hand-edit them.
3. Self-test `tools/bench/selftest_c161_pbinherit.py` (<= 150 lines, replays STORED data): (1) p5s02b sim end -> 5 `#376` rows RECORDED (2 class 1, 3 class 2 each naming its action), PB ok,
   `pairs_extra_left` `[]`, the other PB outputs unchanged; (2) each synthetic variant BLOCKS: changed source uid; a frame of a non-adopted case; an f1 tag on a sink outside (iv); a class-2 row with no connect
   action; a multiplicity other than 1 or the frame count; (3) the stored p5s01a / p5s01b / p5s02a PB results reproduce unchanged (replay from stored sim end / graph; quote old vs new row counts and verdicts).
4. stagekit's md5 changes, so every self-test that pins it goes stale. Run ONE pin sweep: list (`grep -l 0b5bb678` over `tools/bench/selftest_*.py` and `tools/bench/prep_c16*.py`) BEFORE editing, re-pin only the md5
   that differs, re-run each (counts before/after). A case that fails for another reason: quote the line, do not loosen it.
5. PD394(b): recompute the pred MAIN peak of p5s02b on the real checkpoint set from `SX.checkpoint_ops` (ops 1, 4, 8 included) by making `prep_c156_a1_1_lib.py` call the shared rule instead of the hand-coded
   `BIND|{0,n}` at `:98` (as 161-a1-2 did in `selftest_stagexec_s4.py`); re-run `prep_c160_c3_1_pred.py` (re-pin only its stagekit pin), then licence / EL makers only if their inputs move. Name every file whose md5
   changed with its cause. X10 is READ-ONLY: quote the planned MAIN number against 675 (`py tools/stage_prerun.py` X10 or the lib's own line). **MAIN > 675 = stop, hand back; no cut, no limit change.**
   Plan f4520b10, the end graph and predicted EL items 79ec3207 must be unchanged; if anything beyond the checkpoint set moves in the pred, report it and stop.
6. Re-run: `selftest_c161_delckpt.py` (expect 11/0), `selftest_stagexec_s4.py` (24/0), `selftest_c156_b2_2_invcheck.py` (20/0), `selftest_c157_innerface.py` (13/0), and the existing p5s01a / p5s01b / p5s02a gate
   self-tests that call PB. Quote counts.
7. Background anything slow under `py tools/bgrun.py --material --max-min N --log ... -- ...`. A hook false positive on your own command text: `py tools/gate_fp.py log ...`, report; never edit a hook.

## Report `tools/bench/diag_c161_a3_1_facts.md` (<= 45 lines, facts only)
shared function name + signature + stagekit line; PB call sites; self-test counts (new + pin sweep + the 4 suites); new md5 of stagekit, pred (18729409 -> ?), and every other changed file with its cause;
planned MAIN number vs 675; md5 UNCHANGED: stagesim 95a162ba, stagexec a4df7e15, stage_prerun 7605116f, plan f4520b10, EL 79ec3207; `OPEN:` lines (measurements only).
