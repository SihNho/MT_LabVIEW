---
type: brief
status: current
date: 2026-10-08
---
# Brief 146-a1-3 — RETRY of 146-a1-2: re-cut s05 so the MAIN recipe's prerun X10 passes — offline, ALONE

Card 146-a1-2 (FAIL, failure 1 of 2; `tools/bench/diag_c146_a1_2_facts.md`, `result_146-a1-2.json`) did items 1 (load key) and 2 (ONE start =
`x10_start(95e408ff)` = 605.4 + 5.9 = 611.3 in maker, pred and prerun), made the `*_prov2` copies, the hygiene copy, and cut s05 at op 115
(Executor X10 678.8). The main recipe's prerun then read X10 683.9 = Executor 678.8 + 2 `census_snapshot` source reads (`stage_prerun.py:2590-2593`) > 680.
Its OPEN question was which X10 decides. **Decided (cycle-146 purpose, pass item 2): "dry PASS + prerun 0 FAIL on both recipes" — the binding number is the
gate's own X10 as the MAIN recipe's prerun prints it (Executor + its census source reads). The scratch recipe (0 source reads) is always <= the main one.**

## Do
1. Re-cut s05 from the maker `tools/bench/prep_c146_a1_2_mk.py` (card-local; edit only that copy, or a `prep_c146_a1_3_*` copy): the longest v18 prefix from op 98
   that splits no 'of' group and whose MAIN-recipe prerun X10 is <= 680.0. The arithmetic says op 114 = 680.0 (margin 0.0), op 113 = 676.1: try op 114 FIRST and
   take the gate's own verdict (does the prerun print it as PASS or FAIL?); if FAIL, op 113, and so on down. Do not hand-pick: the prerun's own line decides.
2. Rebase on the real s04 graph 094ba298 as before (`stage_prerun.py --rebase`, FALLBACK 0, no hand patch). Keep the existing `*_prov2` copies untouched; the a1-2
   outputs (plan/pred/in at md5 1e29b4a1 / dcfabeb3 / ee64efa6) are the thing being replaced.
3. Pred EL by `tools/elrule.py`, base 58; regenerate `plan_ring_p4_s05v18_pred.json`; report total and counted classes.
4. Dry (sandbox) AND prerun of BOTH `tools/recipes/stage_d1_ring_p4_s05v18.py` and `_scratch.py` on the new bytes: 0 FAIL required on each; the scratch MEM_STOP stays 680.0.
5. X11 / #2626: ops 118/119 will be in s06 (the cut is before op 116), so X11 must PASS unlicensed; no licence file in this card. Report the session that carries
   118/119/132/150 under the same start rule (formula only; the s06 start is unmeasured).
6. Report cut op, MAIN X10 and scratch X10, margin to 680 and to MEMSTOP 695, first op over 680 under the MAIN number, the new s05 file md5s.
7. md5 before/after: every protected file in a1-2's list unchanged (s04 files, v18, s03 282301ca, bed 39511877, every stage tool, memory_model.json now 559be4cf). No LabVIEW process.

## Never
LabVIEW, camera, motor; a scratch or real launch; editing a stage tool, v18 or any s04 file; changing a memory_model.json parameter; clearing a refusal by editing the plan.
If a stage tool must change, RETURN with the file:line.

## Return
`result/1` (status PASS only if every gate passes) and the facts file `tools/bench/diag_c146_a1_3_facts.md`.
