---
type: facts
status: current
date: 2026-10-08
card: 147-a1-2
---
# Card 147-a1-2 facts: the s06 maker allows branch -> connect for a source made in an earlier session; op 116 ALLOWED; the s06 sim end equals v18's sim after the same action (cdiff 0); the negative control is refused

Offline only. `prep_c147_a1_2_mk_r3.log:69` RESULT PASS 17/0 (`BGRUN END rc=0 after 64s`, `:70`). No stage tool, v18, s05 file, recipe or memory_model.json was
edited (`prep_c147_a1_2_check_after.log`: A after == before for 156 files, pins hold).

## 1. Gate diff (`tools/bench/prep_c147_a1_2_mk.py` md5 d57fdd4f vs `prep_c146_a1_5_mk.py` 94275a2c)
- Logic, all in the X10s kind gate:
  - `:276` MKOP maps `new:<sym>` to the v18 op that creates it.
  - `:279-293` `kdec()`. A same-kind pair passes. wire_sr -> connect on an earlier register passes, which is the 146-a1-5 rule, unchanged (`:283-284`). branch -> connect
    passes only when the source tunnel's creating v18 op is before the session's first op AND the s06 src is an int uid (`:285-292`). Any other pair is refused.
  - `:296-303` one decision per s06 op; `kinds_ok` = all decisions pass.
  - `:305-310` negative control.
  - `:313` gate label only.
  - `:317-330` V18E end comparison, a new gate.
  - `:338-340` the new keys in the session json.
- Label-only edits: `:5-12` docstring, `:31` log name, `:53` FACTS -> `prep_c147_a1_2_session.json` (the card's write globs), `:228,259-260,262` card-id strings
  in goal/why, `:337` `"card"`. Every other line is byte-identical to the original (`diff -U0` hunks listed in the run record).

## 2. Kind decisions on s06 ops 115..129 (`prep_c147_a1_2_mk_r3.log:44-58`)
- 14 ops have the same kind in v18 and s06: connect x9, move_in x2, tunnel x2, create x2. They PASS.
- **op 116** `p4_w_idx_frameidx`: `FACT KIND op 116 branch -> connect action p4_w_idx_frameidx: PASS - branch -> connect ALLOWED (PD353(e)): source tunnel new:TS1 created by v18 op 98; session first op 115; s06 src uid -1` (`:45`).
- There is no other kind difference (`srx` = [(116, None)]). X10s gate PASS: Executor 674.2 == table 674.2; MAIN 679.3 <= 680 (`:62-63`).

## 3. Cut, start, sensitivity (unchanged from 146-a1-5)
- START = **623.5** PROVISIONAL = 605.4 (load_by_vi[95e408ff]) + 0.719 x 17 s05 ops + op0_read 5.9. Counting actions instead of ops would give 626.4, which is
  not used (`:3-6`).
- The cut is **ops 115..129**, 19 actions from `p4_w_arr_frameidx` to `p4_ia_bufdiff`. MAIN is 679.3, leaving a margin of 0.7 to 680 and 15.7 to MEMSTOP 695.
  The first op over the limit is 130. 61 of 190 ops are left.
- Sensitivity: 618.5 -> op 131 (MAIN 679.6, 21 actions). 623.5 -> op 129 (679.3, 19). 628.5 -> op 127 (679.1, 17).
- C2: 9 cross refs, all to s05 symbols mapped to negative uids. R: 0 s01..s04 symbols. SA replays. TIE 15/15. SB FINAL on the provisional base, open_rows_match
  with 10 pairs (`:37-43`).

## 4. End comparison, s06 sim vs v18 sim over the same ops (`:64-67`)
- v18 sim summary: `sim/ring_p4_v18/ring_p4_v3/summary.json`, md5 07bc69e6 (plan_in ae6861c6). The last s06 action, `p4_ia_bufdiff`, is v18 action #141. The last
  s05 action, `p4_ia_frameidx`, is v18 action #122.
- Base: s06 step 0 has 16 rows and v18 after #122 has 16 rows. Rows only in one of them: 0.
- **End: s06 has 15 rows and v18 after #141 has 15 rows; only s06 [], only v18 [] -> cdiff 0.** `GATE PASS | V18E` (`:67`).

## 5. Negative control (`:60-61`)
- No s06 op is a branch whose source is created inside ops 115..129. The control therefore re-runs op 116 with the session starting at TS1's creating op (98) and
  a fake src uid -999. Result: `REFUSED - branch -> connect REFUSED (source not made in an earlier session): source tunnel new:TS1 created by v18 op 98; session first op 98`.
  The `kdec()` call writes no file.

## 6. Runs that did not pass (this build step, offline)
- r1 (`prep_c147_a1_2_mk.log:1-65`): my MKOP was keyed by the bare `as` symbol, while the compiled op carries `new:TS1`, so op 116 was refused and the X10s gate
  FAILED. Fix: `:276` keys `new:` + as.
- r2 (`prep_c147_a1_2_mk.log:66-114`): `SA pass A simulate returned | [WinError 5] access denied` deleting `_passA/ring_p4_s06v18a/step_19_create.json` (an old step
  file; steps 00-18 had been deleted). r3 ran without change and passed. The lock holder was not identified.

## 7. Files
| file | md5 |
|---|---|
| tools/bench/prep_c147_a1_2_mk.py | d57fdd4f9d038a6f99cc5919e43ca42c |
| tools/bench/plan_ring_p4_s06v18.json | 0bc28fde1c7461b1caa435f0ec88b992 (was 8f33ad75; `git diff --stat`: 14 lines, labels / finalized md5s) |
| tools/bench/plan_ring_p4_s06v18_in.json | 703a51fc0ff54711e8709dee0edca7a3 (was 08b8dbe2) |
| tools/bench/prep_c147_a1_2_session.json | 3b9ad8e5e6ddc01636b4a9c1985d1286 |
| tools/bench/sim/ring_p4_s06v18/s05end/base_provisional.json | a6762a055fed468f1c3a2a6f58beb8f3 (unchanged) |
| tools/bench/prep_c147_a1_2_check.py / _probe.py | f8eda8d2 / 14858851 |

Protected md5s are identical before and after: stagexec.py 1bab9cf9, stagekit.py 9a3fceaf, stagesim.py 748bbf30, stage_prerun.py 61d6f590, v18 2ea6cafa,
s05 plan 1fc9b486 (and the whole sim/ring_p4_s05v18 tree), memory_model.json 559be4cf.

LabVIEW: none before (`check_before.log`). After: one `LabVIEW.exe`, PID 10464, 688 MB, CPU 0:01:03 (`check_after.log`). This card's scripts are all `labview: none`
and import no LabVIEW module, so the process is attributed to the parallel LabVIEW card 147-a1-1.

## 8. Jev ladder
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| prep_c147_a1_2_mk.log | no JEV-LADDER row (`jev_gate.log:4922,4924` RULE-OFFLINE-CARD: not gated) | - | fixed my own key bug (r1); rerun after file lock (r2) | r3 PASS 17/0 |
