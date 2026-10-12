---
card: 170-a3-3
status: current
date: 2026-10-13
---
# Card 170-a3-3 facts - the S1-vs-P6 leg-chain driver (offline; no LabVIEW, no motor, no VISA)

## Built
- `tools/bench/m8_legs.py` c2d5d6c4 - shared leg runner: wait_lv_gone :27, leg :37, motor_session :69, keep_leg_files :101, selftest :131.
- `tools/bench/drive_m8_replay_p6.py` cd09bbe3 - pins :41, lost0 :55 (+assert :63), leg_report :66, chain :79 (end in `finally` :105), selftest :139; D = 20 at :32 cites docs/d1/ring-p4b.md:21 (PD411(c)); 1500 rows at :33 (PD410(d)).
- `tools/bench/m8b_replay_compare.py` c2efe10d -> 82443af9: init_range :351 (+assert :366-367), compare_p6 :370 (calls compare_bc unchanged); selftest S7 gate replaced by a citation FACT (ring-p6.md:346-349 PD411(c)), S9/S10 added; no line above :349 moved.

## Copies (drive_m8_replay_110.py byte-unchanged, md5 4c564b8a832313cd0f5f8fd3b2465ee6)
- leg(): drive_m8_replay_110.py:33-59 -> m8_legs.py:37 (moved; globals G/rows/NPICK/RUN_S/LEGDIR made parameters, row gains frames_delta).
- LabVIEW test: drive_m8_replay_110.py:26 lambda = copy of drive_legguard.py:45-46 lv_running; its taskkill :48 = drive_legguard.py:51 kill_labview -> m8_legs CALLS both.
- motor start: drive_original_copy_v4.py:205-218 motor_gate(why) (start only) and :221 parse_motor; v4 imports drive_original_copy_v2 (LabVIEW client), so m8_legs calls motor_gate.parse_pi_limits/parse_asi_limits/parse_pi_ref/check_*_readback instead.
- dupcheck (`tools/bench/diag_c170_a3_3_dupcheck_json.log`, 426 files, 1018 blocks, min 6): 0 blocks name m8b_replay_compare.py; m8_legs.py, drive_m8_replay_p6.py and drive_m8_replay_110.py are OUT of its scope (not in tools/bench/capabilities_shared.json, dupcheck.py:14-15).

## Motor session (who calls what)
- v5 runs `motor_gate.py --session start` itself before LabVIEW opens (drive_original_copy_v5.py:549-561) and NEVER `--session end` (:51-52).
- The cycle runner opens a session at cycle start and releases it at cycle end (docs/rules/hardware.md:25-27); motor_session.json now: started 2026-10-12 23:26:25.
- So the driver's `--session end` after each leg is the only release inside the chain; it runs in `finally` after every start attempt (drive_m8_replay_p6.py:105), also when start was refused.
- The driver's own start + v5's start = two real PI reference moves per leg (motor_gate.py:385-403); none is skipped.
- Readback re-check: motor_session start needs rc 0, 'SESSION START OK', PI TMN/TMX = motor_limits.json, ASI SL/SU = file, REFSTATE FRF 1 POS 0, 'VERIFY-RESULT: OK'; end needs PI 0..52, ASI +-500 (m8_legs.py:69-98).

## Self-tests (one at a time, bgrun --material)
- m8_legs --selftest: 7/0 (`m8_legs_selftest.log`): recorded start (motor_session_start_cycle170.log) and end (motor_session_end_20260927_userstop.log) parse ok; no REFSTATE -> not ok; leg stub 15 picks -> run_dir, 14 picks -> 2 attempts None, VISA refused -> no run.
- driver --selftest: 7/0 (`drive_m8_replay_p6_selftest.log`): order start/leg/end S1 then P6 then compare; compare 4443 rows, 0 X/Y/Z differ, DISTINCT 4443/4443 at D 20; pin mismatch -> no step; S1 lost '3' -> no compare; P6 1000 rows -> no compare; start refused -> end still called; 110-7 dirs unchanged.
- m8b --selftest --slots 20: 10/0 (`m8b_replay_selftest_170a33.log`); recorded 170-a2-4 run was 8/1 with only S7 FAIL (diag_c170_a2_4_selftest.log:33); S0-S6, S8 verdicts identical; main json md5 0b459404 unchanged.
- driver --help: usage + RESULT PASS (`drive_m8_replay_p6_help.log`).

## Facts the next run should know
- 110-7 stored `facts.lost` is the STRING '0' (t0_legs/c110f_replay_20260927_184600/A_S1replay_a1/leg.json:437); lost0() accepts it.
- init range on 110-7 leg B: 56 init rows, trans 21.589..27.98125 mm inside PI 0..39, rot finite; ASI has no tra column -> NOT-EVALUATED (m8b_replay_selftest_170a33.log INITRANGE line).
- 110-7 B3 (58 stationary trans/rot rows differ) and B4 (init first/last != A) stay FAIL facts of those legs (PD411(d)).
- `stage_replay_swap_170.json` does not exist yet (card 170-a3-2 writes it): until then P1 stops the driver before any leg.
- Screenshots in tools/bench/m8_shots are not compared (timestamp names); the m8 jsons are kept per leg by keep_leg_files and compared by role name.
- No LabVIEW process before or after (tasklist count 0); no .vi opened or written; no hook/stage_prerun/STATUS/INDEX/memory_model edit.
