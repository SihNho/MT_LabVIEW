---
card: 160-e4-1
status: current
date: 2026-10-10
---
# Brief 160-e4-1 (assignment 160-2) - OFFLINE tooling: RingSession.gate_l0 accepts a numbered input plan `<stem>_in<N>` (gate-fp fp-82)

`labview: none`, no `tools/hooks` edit, no plan / pred edit. ONE tool edit is allowed: `tools/stagekit.py` (1441bb4c), function `RingSession.gate_l0` (`stagekit.py:2404-2413`), and nothing else in it.

## Why
Card 160-c3-1 (recipe pair for step 2, p5s02b) was blocked at the dry's first gate: L0 requires `os.path.splitext(fz["plan_in"]["path"])[0].endswith(st + "_in")` (line 2410), and the final plan
`plan_ring_p5s02b.json` (f4520b10) has `finalized.plan_in = plan_ring_p5s02b_in2.json` (`plan_ring_p5s02b.json:350-353`) - the input plus the two PD391(a) stub-delete rows, made by card 160-b3-1.
Every other L0 clause holds (diag_c160_c3_1_facts.md, `prep_c160_c3_1_dry.log`). The in2 name is a numbered revision of the same input; the clause's purpose (the plan's input file belongs to the SAME plan stem)
is not weakened by a trailing revision number. Logged in `tools/bench/gate_fp_queue.jsonl` as fp-82 (`checker:stagekit:L0`).

## Do
1. Change line 2410's suffix test to accept exactly `<stem>_in` OR `<stem>_in<digits>` (a regex `re.fullmatch` on the basename stem, anchored at both ends: `_inx`, `_in_old`, `_out`, a different stem and an empty digit run
   with other letters stay REFUSED). Keep every other clause of the gate and the gate's label text (the label shows `{st}_in` today; show `{st}_in[N]`). The function keeps its docstring, extended by one clause.
   Do not touch any other function; `re` is NOT imported in stagekit today: adding `import re` to the import block (:50-58) is the one allowed extra line (or use str methods and no import).
2. New self-test `tools/bench/selftest_c160_l0stem.py` (header `# labview: none`, `# hardware: none`; ≤ 60 lines; imports stagekit and CALLS the same predicate - if the predicate is inline in `gate_l0`, first
   extract it as a module-level function `plan_in_matches_stem(path, stem)` with a docstring naming this self-test, and call it from `gate_l0`): accepts `plan_ring_p5s02b_in.json` and `_in2.json` and `_in12.json`
   for stem `plan_ring_p5s02b`; refuses `_inx`, `_in_2`, `_in2b`, `plan_ring_p5s02a_in.json` for that stem, `plan_ring_p5s02b.json`, and `plan_ring_p5s02b_out.json`. Log `selftest_c160_l0stem_c160_e4_1.log`.
3. Regression: run `tools/bench/selftest_c160_stagemap.py` (505b793e; its last result is the baseline - quote before/after), and every self-test that exercises RingSession / the stagekit mapping functions
   (grep `RingSession` and `stagekit` in `tools/bench/selftest_*c15*.py selftest_*c16*.py`; run those that import stagekit, quote RESULT lines before (from their last log) and after). A count that differs
   from its last pass is a FAIL of this card, not a re-pin. Do not re-pin any file outside your globs: list the files that pin stagekit's old md5 `1441bb4c` as `OPEN:` with file:line.
4. Confirm the p5s01a (ed62e8d6) and p5s02a recipes' L0 still pass: call `gate_l0`'s predicate on their plans' `finalized.plan_in` paths (stems `plan_ring_p5s01a`, `plan_ring_p5s02a`) and quote the result.
   The bare minimum is the predicate, not a LabVIEW run.

## Report `tools/bench/diag_c160_e4_1_facts.md` (<= 25 lines, facts only)
Old/new line text for :2410; the predicate's file:line; the self-test RESULT; before/after RESULT lines of every regression suite run; md5 stagekit before/after; md5 UNCHANGED: stagesim 95a162ba,
stagexec ddf23a31, stage_prerun 7605116f, all `tools/bench/plan_ring_*`, `tools/hooks/**`; `OPEN:` lines (pins of 1441bb4c).
