---
card: 147-c3-2
status: current
date: 2026-10-08
---
# Brief 147-c3-2 - s06 licence `renames` + recipe on the new gate API (offline, PD356(d), PD357(e)(f))

Offline, no LabVIEW process. `tools/stagekit.py` (06b8d844), stagexec, gscript, elrule, `memory_model.json`, the s06 plan/pred/in files are NOT edited. Runs beside the case-J stub card (147-c3-1, edits only `selftest_stagekit.py`); do not touch that file.

## Why
The s06 retry (147-a1-8) built the right graph but D/TD/PB failed on NAME keys: LabVIEW renamed #2626 inputs 2832/4160/4165 'array'->'element' and #9503 inputs 9505/9508 'Value'->'' on wiring. `stagekit` 06b8d844 now takes a licence-listed rename list (`licence_renames`, `term_identity_gates(base, sim, real, renames=, bind=)`, `pb_rename_rows(base, sim, real, renames)` - `tools/stagekit.py:1374-1540`; spec of the rules and usage: `tools/bench/selftest_c147_b1_2.py`, esp. `L5` at :27 and T1 at :155-170). Re-score on the stored read passed with the 5-rename licence: `tools/bench/diag_c147_b1_1_rescore2.log:22-30`. The licence file currently has `rename_by_uid` only (`tools/stage_prerun.py:1276` reads only that key).

## To produce
1. `tools/bench/plan_ring_p4_s06v18_licence.json`: ADD a `renames` list in the form `licence_renames` reads (see `selftest_c147_b1_2.py:27`): exactly 5 renames - node 2626, term_uids [2832, 4160, 4165], from "array" to "element"; node 9503, term_uids [9505, 9508], from "Value" to "". Keep `rename_by_uid` and every other key byte-for-byte; update `decided_by`/`why` text minimally to cite PD356(d) / PD357(e). Check with `stagekit.licence_renames(json)` that it returns exactly those 5 keys, and that `stage_prerun.pb_licences` still reads the file as before (same result as before the edit for the rename_by_uid part).
2. `tools/recipes/stage_d1_ring_p4_s06v18.py`: at :127 call `K.term_identity_gates(BASE["terminals"], L["terminals"], real, renames=<licence_renames of the licence file>, bind=<the executor's binding in the form selftest_c147_b1_2 T1 uses; read how it is built from `x.bind` before writing it>)`. At :139-144 (PB) pass the real rows through `K.pb_rename_rows(BASE["terminals"]?? - check the signature and which base rows the PB gate compares; the rows must be the SAME ones the PB gate used before)` and make the PB gate additionally require `unlicensed == []` (restored rows reported in the gate detail). Put the TD/D gate text/detail to show renames, reuse_noted, reuse_bad, unlicensed_renames. The licence is read from the file by path, never re-typed. Do not change any other gate or line. Then make the scratch recipe `stage_d1_ring_p4_s06v18_scratch.py` consistent (it runs `R.body(s)`, so likely no change; say so with file:line).
3. Run on the FINAL bytes of both recipes: py_compile; dry run of the build recipe; dry run of the scratch recipe (rc 3 where `--scratch-required` says so); offline `tools/stage_prerun.py` in the form the 147-a2-1 / 147-a1-3 cards used (`tools/bench/diag_c147_a2_1_facts.md` lists the exact commands and rc); `--el-advisory-selftest` of the scratch recipe if it exists. Quote each command and its rc, plus the new md5s of the licence and the two recipes. If the prerun records the licence md5, check what it pins and report it.
4. Offline check of the new D/TD/PB code path on the stored s06 retry read, as the recipe would call it (reuse `tools/bench/diag_c147_b1_1_rescore.py` if it fits): D/TD/PB ALL PASS and `unlicensed` empty.
5. md5 after: stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, memory_model 88eeb037, plan cfbd9823, pred c4a6a35a, in db72d8af unchanged. LabVIEW process count 0 before and after.
6. Gate/checker false positives -> `tools/bench/gate_fp_queue.jsonl` via `tools/gate_fp.py`. A defect in stagekit/stagexec/gscript: RETURN with `file:line`, do not edit.

## Report (`tools/bench/diag_c147_c3_2_facts.md`, <= 35 lines)
Diff summary by file:line for licence and recipe; commands + rc; new md5s; step-4 result; `OPEN:` line.
