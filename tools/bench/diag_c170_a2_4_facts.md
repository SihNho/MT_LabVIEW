---
card: 170-a2-4
status: current
date: 2026-10-13
---
# 170-a2-4 facts - m8b_replay_compare (b)/(c) extension, self-test on the stored 110-7 legs (offline, no LabVIEW)

Run: `py -u tools/bench/m8b_replay_compare.py --selftest --slots 20` -> `tools/bench/diag_c170_a2_4_selftest.log` (8 pass / 1 fail, :35).

## Build
- Extension appended after `main()` so `tra`/`cal`/`main` keep their lines (`m8b_replay_compare.py:15-59`); the old CLI `<a> <b> [--out]` runs unchanged without `--slots` (`:405-406`); `--slots D` adds the (b)/(c) report (`compare_bc` `:309`); `--slots` absent with `--selftest` = REFUSED (`:390-392`).
- MOVED from `diag_c170_a2_1_cal.py` (old :32-35 NUM/SIZE, :43-65 td_label, :79-113 walk, :116-119 walk assert, :122-133 run_dirs) to `m8b_replay_compare.py:69-163` (td_label :79, walk :107, run_dirs :151); only change: walk's row 'type' comes from a `canon` argument (`:107`, `:139`), so the diag passes `g._td_canon` and keeps its output (`diag_c170_a2_1_cal.py:34` import, `:87` call). The diag was NOT re-run (labview: read header; card is labview none).
- Cal type from the stored read, no gscript: `cal_type()` reads `diag_c170_a2_1_f4.json` types.cluster_const_out tds/top (`m8b_replay_compare.py:170-173`).
- New functions with one assert each: `xyz_match` :207 (assert :232), `distinct` :235 (assert :249); `cal_field` :176, `cal_compare` :193, `trans_rot` :252, `dir_files` :271, `files_compare` :280, `find_text` :287, `y_source` :293.

## Self-test, 110-7 (A = m8_out/replay_s1_20260927_184651, B = leg.json run_dir)
- Leg B run_dir = `replay_s1_20260927_185846` (`t0_legs/c110f_replay_20260927_184600/B_dispreplay_a1/leg.json:491`), same dir as `p6_replay_facts.md:103`; S0 PASS (log :3, :26).
- Old main() G1-G3 PASS: rows A 4443 / B 8548, common 4443, 0 X/Y/Z rows differ (log :7, :27).
- tra 'actual data points': A [4443, 48], B [8548, 48] (log :10).
- MATCH: 4443 common rows, 0 rows not bit-identical, drop signature n/a (log :11, :28-29). PASS.
- Finite cells compared per bead: beads 1-14 13329 each (= 4443 x 3), bead 15 4443; NaN cells A 8886 = B 8886, all in bead 15 (log :11).
- DISTINCT (slots 20): 4443 of 4443 rows pass, first fail none (log :12, :30). PASS.
- cal: walk consumes 857376 of 857376 B in both; field 'Date and time' offset 857264, length 40, text offset 857268 in both; text A `...\r오후 6:51:02\r`, B `...\r오후 7:02:38\r`; 5 bytes differ, 0 outside the field (log :14, :31). PASS (matches diag_c170_a2_2_cal.log:45,60,64).
- Files per dir: cal001, tra001-000 only; both present in both dirs, both md5 differ (tra sizes 1706560 vs 3282880) (log :15).
- 'Lost Frames' text: NOT FOUND in any run-dir file (log :16); frame-counter delta not in the run dirs (card 170-a2-6).
- trans/rot (NOT in the expected list - a FACT): A's last trans/rot change at row 55, boundary 56; stationary rows 4387, 58 differ A vs B, first at row 56; init rows of B 56, non-finite 0; first value A [21.5372, 0.0] vs B [21.589, 0.0], last A [30.0, 192118.32] vs B [27.98125, 192118.32] -> ITEM B3 FAIL, B4 FAIL (log :13, :20-21).
- Envelope check NOT-EVALUATED: `motor_gate.py:14-17` (script-level envelope deleted, limits in controllers), `:20-21`/`:32` (rotor: no envelope) (log :13).

## D (slot count) and the graph
- Graph `graph_ring_p6_20261012_212645.json:1` (md5 fbc7b7ee, VI c2d9c13c): ring counter Q&R #27373 'y' (t27416, wire 27911) <- DigitalNumericConstant #27433 (log :24; S6 PASS :32).
- The graph JSON stores objs as uid/class/pos/owner only and terminals without values (`diag_c170_a2_4_graph.log:5-6`, :24): #27433's VALUE is not in it. S7 FAIL (log :33). D = 20 was passed on the command line from U13 / `ring-p4b.md:21`, NOT confirmed from the graph.

## Hygiene
- 110-7 run-dir md5 before (shell, this card) = after (log :25, S8 PASS :34): A cal001 e5570a96, tra001-000 47f87a74; B cal001 ea1ed8a3, tra001-000 2571a2ea.
- No LabVIEW, no hardware; written: m8b_replay_compare.py, diag_c170_a2_1_cal.py, m8b_replay_selftest_170.json, m8b_replay_selftest_main.json, diag_c170_a2_4_{graph.py,graph.log,selftest.log,facts.md}.
