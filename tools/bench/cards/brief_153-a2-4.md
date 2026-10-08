---
card: 153-a2-4
status: current
date: 2026-10-09
---
# Brief 153-a2-4 (re-issued on card 153-a2-5's wrapper) - adopt the position-keyed `vigraph.py` (candidate a7eb58c7), prove the REAL PB path on stored s06, re-score, drain fp-70 (docs/d1/ring-p4d.md PD371(b) + PD372(c)(d)); offline

Precondition (check first; if false STOP with `OPEN:`): `tools/bench/cards/result_153-a2-5.json` is PASS (it is: converter `convert_open_rows`,
t6_poskey 43/0, c147_b1_2 19/1 with only P0, compdiff_poskey 8/0 against the CANDIDATE through temp-converted preds and plans); card 153-a2-8 is done (no LabVIEW
running: `tasklist | grep -i labview` empty). PD372(c) accepts a2-5's rule: a plan open_row (node, name) is dropped when the conversion removed its pair entirely
(here only (2626,'array')).

## What to do
1. `tools/vigraph.py` takes the exact bytes of `tools/bench/diag_c153_b2_1_vigraph_poskey.txt` (md5 a7eb58c7e35a134f93df168ea4cdea80): copy, then quote the new
   md5 (must equal a7eb58c7) and the old one (13be0847). Run `selftest_c153_compdiff_poskey.py` (8/0) and the vigraph frame_80 self-test (12/0 before and after).
2. IDENTIFY, by reading, the REAL entry point through which the stage scoring runs the PB check on a stored plan + pred (stagexec.py ~4409-4485 `open_row_class` /
   e3 gates, stage_prerun.py ~1302 and the T6 suites' call chain; the a2-5 wrapper imports the per-case pipeline from `selftest_t6_poskey.py`). Quote the function
   and file:line. Run it on the STORED s06 plan `cfbd9823` + pred `c1bd6b3e` with NO temp conversion and the ADOPTED vigraph. Quote the result.
3. If step 2 passes: no converter is added anywhere. If it fails because the stored plan's name-keyed open_rows meet position-keyed rows: put
   `convert_open_rows` (selftest_c153_poskey_convert.py, 120 lines, self-test 10/0) into the ONE function that reads open_rows for the PB check (PD372(d): at most ONE
   tool file besides vigraph.py changes; quote the single file:line; old and new md5). If a second tool file would need a change: STOP with `OPEN:` and hand back.
4. On the FINAL bytes (vigraph + the one caller, if any): t6_poskey 43/0, c147_b1_2 19/1 (only the pre-existing P0 pins), compdiff_poskey 8/0. If a pin drift makes a P0
   gate in c147 name the one authorised caller, quote it as expected. The stored plan and pred files stay byte-unchanged (md5 before/after; s03 da66a030 s04 f349c39a
   s05 1fc9b486 s06 cfbd9823; preds s03 b212bb33 s04 a2bbc8bf s05 d083ff5f s06 c1bd6b3e).
5. Re-score with `tools/bench/diag_c153_b2_1_rescore.py` (run unchanged): s06..s09 stored end reads and S1-vs-s09. Quote the table: pair, old rows, new rows, removed.
   Expected: s06 PB 18 -> 14 (the #2626 rename), s07 19, s08 21, s09 21, S1-vs-s09 21, unchanged. Any other change => restore vigraph 13be0847 (and the caller), STOP, `OPEN:`.
6. Drain fp-70 with `tools/gate_fp.py` (the verb used for fp-72, `tools/bench/gate_fp_queue.jsonl:72`; read its usage), citing the new vigraph md5 and the logs. Quote the line.

## Invariants (md5 before/after)
stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun c739eb86, stagesim 78b8d5a1 - each unchanged EXCEPT the single caller step 3
authorises. s09 VI eb1d0f31, graph 22f967b5, stored plans/preds unchanged. No tools/hooks edit, no stagesim edit, no LabVIEW, no motor or camera.

## Return (<= 30 lines)
Old/new vigraph md5; the real entry point (file:line) and its s06 result; whether a caller changed (file:line, md5s); self-test counts with log paths; the re-score table;
the fp-70 drain line; `OPEN:` for anything needing judgement. Failure budget 2.
