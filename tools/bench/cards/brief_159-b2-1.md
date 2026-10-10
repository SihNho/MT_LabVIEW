---
card: 159-b2-1
status: current
date: 2026-10-10
---
# Brief 159-b2-1 (assignment 159-2) - OFFLINE: bump DRY_RULE (PD388(d))

Offline, no LabVIEW, no hook edit. Runs beside card 159-b1-1 (which does not touch `tools/stage_prerun.py`).

`tools/stage_prerun.py:3434` has `DRY_RULE = 2`; `check_launch` accepts only dry records whose `dry_rule` equals it (read lines ~4970-5000 and quote
them). Card 159-a4-1 repaired the dry (counts every UNVERIFIED-DRY line, a partial census is UNPREDICTED, PB/D/TD/CEN2 run on the simulated end), so
every dry record written before that repair must stop satisfying `check_launch`.

1. Change that one constant to the next integer (3), nothing else in the file. Quote the diff.
2. Self-test (new file `tools/bench/selftest_c159_b2_1.py`, calling `stage_prerun.check_launch` / the record filter, not copying it): a dry
   record carrying `dry_rule` 2 (build it from a stored record in `tools/bench/prerun_records.jsonl`, in a TEMP copy of the records file, never the
   real file) is REFUSED with the old-rule message; a record carrying `dry_rule` 3 and otherwise identical is accepted by the same check. State
   which `check_launch` arguments you used so the run is reproducible. Print counts.
3. Quote how many records in the real `tools/bench/prerun_records.jsonl` have `dry_rule` != 3 after the bump (read-only count), and whether the
   p5s02a MAIN / scratch recipes now have a valid dry record (expected: no).
4. Suites: run `tools/bench/selftest_c159_a4_1.py` before and after the bump (same counts expected; quote both). Do NOT run runcheck / wire0face /
   stagekit / c134_1_dry here (their pins move after the plan cards; a later card re-pins them).

## Report `tools/bench/diag_c159_b2_1_facts.md` (<= 25 lines)
The diff; the self-test counts; the record counts; before/after counts of selftest_c159_a4_1; the NEW md5 of `tools/stage_prerun.py`. `OPEN:` lines. Facts only.
