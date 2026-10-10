---
card: 159-e1-1
status: current
date: 2026-10-10
---
# Brief 159-e1-1 (assignment 159-3) - OFFLINE: `gate_cen2` judges Wire by (source, sink, frame) end pairs + self-test (PD389(b))

Offline, no LabVIEW run, no hardware, no `tools/hooks` edit. You may edit `tools/stagekit.py` (this card's job) and nothing else under `tools/`
except the new self-test. Read `docs/d1/ring-p5b.md` PD389 (a)-(c) and `tools/bench/diag_c159_cen2_wire.md` first; `docs/script-writing.md` binds
you (extract before use, call shared functions, a docstring on every new shared function).

## What PD389(b) fixes (already decided; implement it)
`gate_cen2` (`tools/stagekit.py:2414`) counts a new Wire by uid; real and simulated ends differ only in uid (uid re-use, LabVIEW 31587 vs sim 24153;
24330 swapped), so it reads 11 vs 12 on a sound file. For the **Wire class** CEN2 must compare sets of (source terminal key, sink terminal key,
frame) pairs not present at c0, keyed like TD's position key (base uid / created-object class). Sim side from its terminal rows, real side from the
run's terminal rows (`real_end_rows`, `tools/stagekit.py:2436`). Equal end-pair sets PASS. The uid counts stay printed as a `UID-REUSE` fact line.
Other classes keep the uid census unchanged. A source-only stub in the sim that the real graph lacks is RECORDED (a line), not counted
(PD386(b) precedent: find how TD/PB record such a case and call the same helper).

## Self-test (new file `tools/bench/selftest_c159_cen2_ends.py`, header `labview: none`, <= 120 lines on `tools/stagekit.py` helpers)
Data: the real graph `tools/bench/graph_ring_p5s02a_20261010_032547.json` (94ffff94) and the p5s02a simulated end (find it through the p5s02a
dry record in `tools/bench/prerun_records.jsonl` / `tools/bench/sim/`; quote where). Cases, each with a printed expectation:
1. end-pair CEN2 on 94ffff94 vs the p5s02a sim end -> PASS; the old uid-count CEN2 on the same data still reads 11 sim / 12 real (print both).
2. a copy of the real rows with ONE real (source, sink, frame) pair removed -> FAIL, naming the pair.
3. the sim-only source-only stub 24091 -> RECORDED, not a failure.
4. a non-Wire class (any class `gate_cen2` already handles) -> verdict identical to the pre-edit gate.
Report each case PASS/FAIL and the totals. Do NOT run `selftest_stagekit` or `selftest_c134_1_dry` (they carry `labview: read`; another card runs them).

## Report `tools/bench/diag_c159_e1_1_facts.md` (<= 30 lines, facts only)
The diff summary of `gate_cen2` (function names + line ranges), the self-test log path + totals, the 4 cases' outputs, stagekit md5 before
(9cd8822e) and after, stagesim/stagexec/stage_prerun md5 unchanged (7605116f for stage_prerun), `tools/hooks` untouched. `OPEN:` lines for anything
the PD cannot express (file:line). Do not re-pin other self-tests and do not re-run any dry/prerun - other cards do.
