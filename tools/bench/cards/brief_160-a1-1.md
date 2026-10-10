---
card: 160-a1-1
status: current
date: 2026-10-10
---
# Brief 160-a1-1 (assignment 160-1) - OFFLINE: termless-Wire delete branch in stagesim + stagexec, self-test on the 94ffff94 graph (PD390(a)(b))

Offline, `labview: none`: no LabVIEW process, no `tools/hooks` edit, no stage launched. Read `docs/d1/ring-p5b.md` PD388(a), PD390(a)(b)(e) and
`docs/script-writing.md` first (call shared functions, no pasted blocks; a NEW function carries a docstring naming its self-test).

## Why
`delete_wire` resolves its wire by terminal rows (`tools/stagesim.py:1424-1426`, `tools/stagexec.py:2843-2851`), so the wire `w10394` of the adopted
in-between file 94ffff94 (a Wire object with 0 terminal rows, left behind by step 1's A13) cannot be deleted: REALSIM says "wire 10394 is not in the current graph"
(`tools/bench/diag_c159_c1_1_facts.md:25`). The decision (PD390(a)) is ONE new branch in each of the two tools.

## What to build (this card edits `tools/stagesim.py` and `tools/stagexec.py` only)
1. `stagesim.op_delete_wire` (and whatever lookup it calls): a new branch taken ONLY when the uid is in the CURRENT simulated object list with class `Wire` and has
   0 terminal rows. The branch removes that object from the simulated state and nothing else (no terminal row, no pair, no other wire changes). Every other case keeps
   today's code path unchanged: a uid with terminal rows keeps the terminal-resolved delete; a uid absent from the object list is refused; a non-Wire uid is refused.
   An "already gone" case is never counted as a successful delete.
2. `stagexec`'s `delete_wire` compile: the same condition, producing an op whose live act is the existing uid path `stagekit.delete_wire` (`tools/stagekit.py:687`) -
   read that function first and call it, do not re-implement it. `remove_bad_wires` is NOT used (it removes every broken wire, not one uid).
3. A shared self-test `tools/bench/selftest_c160_delwire.py` (+ its log `tools/bench/selftest_c160_delwire.log`) replaying the SAVED graph
   `tools/bench/graph_ring_p5s02a_20261010_032547.json` (94ffff94; load it the way `tools/bench/selftest_c159_cen2_ends.py` does). Cases, each quoted in the facts file:
   (T1) delete `w10394`: succeeds in the simulator and compiles in stagexec to the uid-path op; the full terminal-row set and the full (source, sink, frame) pair set
   after are IDENTICAL to before except the one object (compare by the existing shared pair/row functions, not a new diff); (T2) absent uid refused;
   (T3) a non-Wire uid refused or, if it has terminal rows, the old path is taken; (T4) a Wire WITH terminal rows keeps the old terminal-resolved path (give one
   real wire from the graph; show the result is the same as with the pre-edit tools, e.g. by comparing against an unedited copy of the two files kept in a temp dir
   and deleted at the end); (T5) the branch is not taken when the uid is only in the base list and was already deleted earlier in the same plan.
   Print `RESULT <pass>/<fail>`.

## Then, on the NEW bytes of stagesim / stagexec (pass items 2 of the purpose)
Re-run `tools/bench/selftest_c159_cen2_ends.py`, `tools/bench/selftest_c158_runcheck.py` and `tools/bench/selftest_c158_wire0face.py`. Those two c158 suites pin
`tools/stagesim.py` (eb99c6ba) and print stagexec; re-pin ONLY the stagesim/stagexec md5 prefixes that the edit moved (edit the PINS dict and its docstring line,
name the old and new prefix, e.g. "re-pinned 160-a1-1 from eb99c6ba"), then run them. Counts must equal their last passing logs
(`selftest_c159_cen2_ends_final.log` 8/0, runcheck 10/0, wire0face 24/0). Any count that differs from its last pass is a FAIL of this card, not a re-pin.
Quote the three final result lines.

## Report `tools/bench/diag_c160_a1_1_facts.md` (<= 35 lines, facts only)
The two diffs (file:line of each new branch), the self-test log lines for T1..T5, the three suite results with old and new pins, md5 before and after of
`tools/stagesim.py`, `tools/stagexec.py`, and md5 UNCHANGED of `tools/stagekit.py` (ac3a8f57), `tools/stage_prerun.py` (7605116f), `tools/addrcheck.py`, `tools/vigraph.py`;
VIs 94ffff94 / s09 eb1d0f31 / P5-1a 2482fe7b / P5-1 7f2582ae unchanged; `tools/hooks` untouched. If T1 cannot pass without touching terminal rows or other wires,
STOP and return FAIL with the line (do not fall back to another delete route; PD390(e)). `OPEN:` lines with file:line.
