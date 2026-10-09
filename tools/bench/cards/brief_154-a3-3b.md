---
card: 154-a3-3b
status: current
date: 2026-10-09
---
# Brief 154-a3-3b - RETRY of 154-a3-3: the launch was refused by a heading-format false positive (fp-75); fix the heading's TIME FORMAT, then launch ONE P5-1a scratch

Read `tools/bench/cards/brief_154-a3-3.md` first (the whole launch / adopt / EL / graph / `load_by_vi` / invariants / LabVIEW-gone procedure stands, unchanged) and `tools/bench/diag_c154_a3_3_facts.md` (9f1b00b0: what 154-a3-3 already did). Only these changes:

## Changes against brief_154-a3-3.md
0. **Heading time format, FIRST (the only edit outside the card's earlier globs).** `guard_cycle` refused the launch because `docs/violation-decisions.md:1992` is headed `## inference-over-measurement — 2026-10-09 07:0x (...)`; `tools/violations.py:94` DEC_RE needs `HH:MM`, so the stamp reads 00:00 and the decision is not "after" the retrospective (`:206`). The same format fix was made twice before by a judgement cycle (`docs/violation-decisions.md:1469` and `:1504`: "time = lower bound of the '03:3x' window, rewritten so violations.py DEC_RE parses it"). Do the same: with the Edit tool change ONLY `07:0x` to `07:00` in that one heading line (keep the rest of the line; add nothing else; no word of the decision body, no other heading, no tool, no hook, no threshold changes). Quote md5 of the file before/after and `git diff` of that file (must be exactly one changed line). Then confirm the gate reads it: `py tools/violations.py` (or the `guard_cycle` check the refusal came from) no longer lists `inference-over-measurement` as DUE. If it still refuses: `py tools/gate_fp.py log`, RETURN with the refusal text; no env bypass, no hook edit.
1. **Skip the string fix and the prior-art review: they are done.** MAIN recipe is now `stage_d1_ring_p5s01a.py` aee20128 (was f3cbe6a0), scratch `_scratch.py` 3b02d9a7 unchanged; prior-art on the string change ANSWERED `novel` (`archive/peer/2026-10-09-priorart-priorart-c154-a3-3-p5s01a-strings.md:293`). Verify both md5s; then re-quote dry 1/0, prerun 16/0 (X10 MAIN 677.3 / Executor 672.2, X17 PASS), `--scratch-required` rc 3 and `--check-launch` ALLOW against these bytes (they are the launch's own pre-checks). A different md5 / number is a RETURN.
2. Steps 3-9 of brief_154-a3-3.md as written (ONE scratch on a NEW byte copy of s09 eb1d0f31; adopt `D1_ring_p5s01a_<stamp>.vi`; final EL; fresh load + graph; ONLY a `load_by_vi` entry; invariants with the recipe md5 aee20128 in place of f3cbe6a0 and `docs/violation-decisions.md` expected to differ in that one line; LabVIEW closed and verified gone). Copy the `diag_c152_b3_1_*` scripts to `diag_c154_a3_3_*` (names, ids, pins, paths only).

## Report `tools/bench/diag_c154_a3_3b_facts.md` (<= 45 lines)
Heading fix (md5s, one-line diff, gate now clear); pre-check numbers on aee20128; then the report list of brief_154-a3-3.md. `OPEN:` line. Facts only.
