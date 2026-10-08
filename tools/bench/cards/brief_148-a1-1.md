---
card: 148-a1-1
status: current
date: 2026-10-08
---
# Brief 148-a1-1 - drain gate-fp fp-51..59, re-pin selftest_c147_b1_2 (offline tooling card, ALONE)

No LabVIEW process. Plan of record: `docs/d1/ring-p4c.md` PD358(b)(d). Run ALONE: no other card is live. `tools/stagekit.py` (06b8d844), `stagexec.py` (1bab9cf9), `gscript.py` (1a80236e), `elrule.py` (a5ee7d5c), `memory_model.json` (88eeb037), the s06 plan/pred/in/licence/recipes are NOT edited.

## Authorised edits (PD358(b), gate-fp drain only)
`tools/stage_prerun.py`, `tools/hooks/guard_cycle.py`, and the hook/checker each of fp-51..58 names (`guard_bash.py`, `guard_write.py`, `guard_assign.py`, `bgrun.py` as the entries point). Nothing else. A new case may be appended to an existing self-test; no other self-test line changes.

## To produce
1. For each of fp-51..fp-59 in `tools/bench/gate_fp_queue.jsonl` (read the entry's `why` and cited `file:line`): either (a) fix the hook/checker line that caused it and add or extend a self-test that fails before the fix and passes after (quote `path:line`, rc and counts), or (b) a cited not-a-false-positive note. fp-55 is NOT a false positive (PD357(d)): drain it with that note. Mark each entry `drained` through `tools/gate_fp.py` (never hand-edit the queue file, never an env bypass).
2. fp-56: in `tools/stage_prerun.py` re-pin the `VI_MOD_EXEMPT_PATHS` sha256 for `selftest_stagekit.py` (current sha256 starts 0007d034; compute it from the file) and make `--dry` / the header routing stop reading the self-test's intentional FAIL rows as DRY FAIL (or route it by its header). Then ONE plain run of `selftest_stagekit.py` under its header via bgrun: rc 0, 0 fails, quote the count line.
3. fp-59: `tools/hooks/guard_cycle.py` re-run exemption glob (the entry cites the line) so a `--retry-card ... stage_*_scratch.py` re-run is not refused for its own previous log; self-test it with the exact command text of fp-59 and with a command that MUST still be refused.
4. Re-run every existing self-test of each file you edited (find them by grepping `tools/bench/selftest_*` for the file name; at minimum the guard_peer-free ones for guard_cycle/guard_bash/guard_write/guard_assign and the stage_prerun ones): rc + pass/fail counts, before and after if a count changed.
5. Re-pin `tools/bench/selftest_c147_b1_2.py` P0 to licence `7f70bbf9` and build recipe `d947df5d` - ONLY those pin lines; run it: 17 pass / 0 fail, rc quoted.
6. After: md5 list of every file edited and the invariant files above; LabVIEW process count 0 before and after.

## Report (`tools/bench/diag_c148_a1_1_facts.md`, <= 40 lines)
Table fp-id -> drained as fix (`path:line`, self-test rc/counts) or note (citation); selftest rc/counts per edited file; md5 list; `OPEN:` line. Facts only.
