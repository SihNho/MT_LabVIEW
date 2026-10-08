---
card: 147-c3-1
status: current
date: 2026-10-08
---
# Brief 147-c3-1 - case-J stub in selftest_stagekit.py (offline, PD357(c))

Offline, no LabVIEW process. `tools/stagekit.py` (06b8d844), stagexec, gscript, elrule are NOT edited.

## Why
Card 147-b1-4 (`tools/bench/diag_c147_b1_4_facts.md`) measured `selftest_stagekit.py` with every COM function stubbed to raise: PRE-EDIT stagekit 9a3fceaf and NEW 06b8d844 give the SAME 51 pass / 0 fail with a driver that routes `g.create_local_read` to the test's own creator stub (driver `tools/bench/diag_c147_b1_4_run.py`). Without that driver the test reaches COM at `tools/stagekit.py:794` (`g.create_local_read`, since cycle 102) because case J (`selftest_stagekit.py:322-345`) stubs only `K.mod("diag_s3b_l0_localname_v2")`; on 2026-10-08 that one real call got LabVIEW's 5507. PD357(c) (`docs/d1/ring-p4c.md`) orders the fix.

## To produce
1. Edit ONLY case J of `tools/bench/selftest_stagekit.py` so that it also stubs `K.g.create_local_read` (and restores it in the `finally`, with the other saved attributes) with the same effect the driver gave it: the call resolves the label over the stubbed `panel_wiring` and reaches the test's creator stub, J1/J2/J3 asserting the same things as now. Read `diag_c147_b1_4_run.py` for how it routed the call and what it returned (it also needed `is_source=[True]`), and `stagekit.py:779-800` for the real behaviour. Do NOT change any other line, assertion or check text. Quote the full `git diff` of the file in the facts.
2. Run the self-test with COM blocked: reuse `tools/bench/diag_c147_b1_4_run.py` in its blocking mode (its COM block + leak counter) but WITHOUT its case-J routing, so the leak counter shows whether the fixed test is self-sufficient. Required: `selftest_stagekit.py` on stagekit 06b8d844 = 51 pass / 0 fail AND 0 COM calls, rc 0. Also run it once plainly (`py tools/bench/selftest_stagekit.py` under `bgrun`, labview read) and quote rc + counts. If the driver cannot disable its routing, write the smallest new driver file `tools/bench/diag_c147_c3_1_run.py` for this.
3. Re-run `py tools/bench/selftest_c147_b1_2.py` (expect 17/0) and `selftest_td_key_c141_3.py` (expect 9/0): rc + counts.
4. md5 after: selftest_stagekit.py (new), stagekit.py 06b8d844, stagexec.py 1bab9cf9, gscript.py 1a80236e, elrule.py a5ee7d5c, memory_model.json 88eeb037, s06 plan/pred/in/licence/recipes (plan cfbd9823, pred c4a6a35a, in db72d8af, licence 7dce79aa, recipe 9150f15b, scratch 31009bfc) unchanged. LabVIEW process count 0 before and after.
5. A gate or checker false positive goes to `tools/bench/gate_fp_queue.jsonl` via `tools/gate_fp.py`, never an env bypass.

## Report (`tools/bench/diag_c147_c3_1_facts.md`, <= 25 lines)
Diff, commands + rc + counts, COM-call count, md5 list, `OPEN:` line.
