---
card: 161-a3-2
status: current
date: 2026-10-10
---
# Brief 161-a3-2 (assignment 161-3, retry of 161-a3-1) - OFFLINE: finish PD394(b) - restate the stored X10 numbers on the shared checkpoint rule, re-make the pred

`labview: none`, no `--launch`, no `tools/hooks` edit, no env bypass. Read `tools/bench/diag_c161_a3_1_facts.md` (all) and `docs/d1/ring-p5b.md` PD394(b) (276-279), `docs/script-writing.md`.
PB classes 1/2 are DONE and green in 161-a3-1 (stagekit 9b8f82c1, `selftest_c161_pbinherit` 10/0): do not touch `pb_*` code or that self-test.

## Measured by 161-a3-1 (cause of the stop)
PD394(b) is applied: `prep_c156_a1_1_lib.py:99` now takes the checkpoints from `SX.checkpoint_ops` (ops 0,1,2,3,4,5,7,8,9,10). Result `prep_c161_a3_1_pred.log:10`: MAIN 661.3 at start 599.7,
**665.0** at START_ASSUMED 603.4 (Executor peak **659.9**), limit 675 respected. The pred maker's X10 gate (`prep_c160_c3_1_pred.py:88-90`) additionally requires equality with the STORED session numbers
(`prep_c160_b3_1_session.json` key `x10`: exec_peak 652.3, main 657.4), which were computed with the OLD hand-coded rule `BIND|{0,n}`; so it stops before any write. Same cause: `prep_c156_a1_1_lib.py --selftest` T3
stored 680.0 vs 682.5; `selftest_c161_delckpt` D2 and P (written against pred 48b50b29) fail 9/2 before and after.

## Decision (already in the plan: PD394(b) "pred MAIN recomputed on the real checkpoint set; limit 675 unchanged") - the stored numbers move WITH the rule, the gate stays an equality
1. Do NOT edit `prep_c160_b3_1_session.json` (a b3-1 record). Write a NEW record `tools/bench/prep_c161_a3_2_x10.json` with the shared-rule numbers (exec_peak, main at START_ASSUMED, the checkpoint list, the rule's
   function name + stagekit/lib md5, the old numbers 652.3 / 657.4 and the cause "PD394(b) checkpoint rule"), produced by calling the lib (script `tools/bench/prep_c161_a3_2_x10.py`, <= 60 lines, no pasted
   arithmetic). The pred maker's X10 gate keeps `==` and `<= LIMIT`, and now compares to the new record's numbers (fail if the record is missing or its stored md5 pins differ). Nothing about 675 changes.
2. Re-run `prep_c160_c3_1_pred.py` (it re-makes the pred; pin only what the stagekit/lib md5 change requires), then the licence and EL makers ONLY if their inputs moved. Name every changed file with the cause.
   Plan f4520b10, stagesim 95a162ba, stagexec a4df7e15, stage_prerun 7605116f, EL items 79ec3207 must stay unchanged; the only pred difference allowed is the one that follows from the checkpoint set
   (quote the diff of keys that moved). Anything else moving in the pred = stop and report.
3. Restate the two consumers that failed for the SAME cause, reading the new record or calling the shared rule (no literals): lib `--selftest` T3 (expect 3/0 or the lib's own count), and `selftest_c161_delckpt`
   D2/P against the new pred (expect 11/0). A case failing for another reason: quote the line, do not loosen.
4. Re-run and quote counts: `selftest_c161_pbinherit` 10/0, `selftest_stagexec_s4` 24/0, `selftest_c156_b2_2_invcheck` 20/0, `selftest_c157_innerface` 13/0, `prep_c160_c3_1_md5`, and every self-test that pins the
   pred md5 (grep `18729409`/`187294099b` over `tools/bench/selftest_*.py`, list BEFORE editing; re-pin only the md5).
5. guard_write warned: the OPEN card `160-c3-2` pins stagekit 0b5bb678. Report whether that card is closed; do not edit it.
6. Background anything slow under `py tools/bgrun.py --material --max-min N --log ... -- ...`. Hook false positive: `py tools/gate_fp.py log ...`; never edit a hook.

## Report `tools/bench/diag_c161_a3_2_facts.md` (<= 40 lines, facts only)
the new record (path, md5, numbers), the maker's X10 line quoted, new pred md5 (18729409 -> ?) + key diff, counts of every re-run, md5 unchanged list, `OPEN:` lines (measurements only).
**MAIN > 675 = stop and hand back.**
