---
card: 162-a2-3
status: current
date: 2026-10-10
---
# Brief 162-a2-3 - TOOLING (offline, no LabVIEW): the 3 copied blocks of PD392(e) move into ONE new shared module; their callers call it

Context: cycle-162 pass item 9 / `docs/d1/ring-p5b.md` PD393(e) (lines 238-242) and PD392(e) (lines 202-205). The ONE pin sweep before the edits is DONE: card 162-a2-1 (`tools/bench/prep_c162_a2_1_pinsweep.log`, facts `diag_c162_a2_1_facts.md`), and card 162-a2-2 re-pinned the one stale pin it found in scope.
Read `docs/script-writing.md` (rules: shared functions, never copies). Offline: no LabVIEW, no VI, no motor or camera. The LabVIEW scratch of p5s02b is DONE (adopted f9ae7751) and is not touched.

## The three blocks (the "copies" - they were pasted into several scripts; grep for each block's distinctive lines to find EVERY copy, not only these three sites)
1. **Licence rename table** - `tools/bench/prep_c156_a1_1_licence.py:49-60` (builds `own` / `wr` / `ren` from the plan's `wire` actions whose dst term uid is a BASE sink: `{"node", "term_uids", "why"}` entries).
2. **Pred E1 checkpoint table** - `tools/bench/prep_c156_a1_1_pred.py:79-82` (`cpe`: `{"op","kind","action","step_file","md5"}` for each checkpoint `k` in `cps`, via `step_files` and `ops[k-1]["acts"]`).
3. **Stub-delete insertion** - `tools/bench/selftest_c160_regface.py:70-79` (a temp plan copy with a `delete_wire` action `dw_<id[2:]>` for the `DW` wire uids inserted before the group's wire action).

## Steps
1. **Grep** each block's distinctive lines under `tools/` and `tools/bench/` (`*.py`) and list every copy: file, line range, and whether it is byte-identical or differs (say how). Save the list as `tools/bench/prep_c162_a2_3_copies.log` (a script, not hand-typed).
2. **New module `tools/stage_shared.py`** (a NEW file; labview none header; do NOT put it into `stagekit.py`, `stagexec.py`, `stagesim.py` or `stage_prerun.py`: their md5 pins are carried by launch gates and by many self-tests, and editing them is outside this card). One function per block, taking its inputs as arguments (no module globals), docstring one line. Where copies differ, the function takes the difference as an argument or the copy stays and is listed in OPEN.
3. **Equivalence before the rewrite (rule 1a spirit - the tool output must not change):** for each function, run the OLD block and the NEW function on the same real inputs (`plan_ring_p5s02a`/`p5s02b` plan + licence + pred + graph json that the callers read) and compare the output by JSON equality. Save the comparison script and log. Any difference = RETURN with the facts.
4. **Rewrite the callers** (every copy from step 1 that is byte-identical or argument-only different) to call the new module. Edit with the Edit tool. Each edited file gets its self-test re-run (the `selftest_c15*` / `selftest_c16*` that cover it, found by grep of the file's name) - all green with the SAME counts as before the edit (take the before counts from the existing `*_c16*.log` or run the self-test before editing).
   The md5 of every file edited is recorded old -> new. Re-run `prep_c162_a2_1_pinsweep.py` afterwards: any NEW stale pin caused by these edits is re-pinned (pin only) and listed, a content failure is RETURNed.
5. A self-test for the new module (`tools/bench/selftest_c162_stage_shared.py`, <= 120 lines, on `tools/stagekit.py`-style gates): each function on the real inputs equals the stored old-block output.
6. NOT edited: `tools/hooks/**`, stage tools, recipes (`tools/recipes/**`), plan / licence / pred / EL json (their md5s must be unchanged after the card: hash them before and after), originals, `STATUS.md`.

## Report `tools/bench/diag_c162_a2_3_facts.md` (<= 40 lines)
The copy list (count, files); the module + function names; the equivalence compare results; callers rewritten (file, md5 old -> new, self-test counts before -> after); the pin re-sweep; the frozen-file hashes before/after; `OPEN:` lines (measurements only, e.g. copies that differ and were left).
