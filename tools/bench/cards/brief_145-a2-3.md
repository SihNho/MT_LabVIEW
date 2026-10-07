---
type: brief
status: current
date: 2026-10-07
---
# Brief 145-a2-3 — RETRY of 145-a2-1: build the pane-requiredness READER, measure PS1/SQ1, housekeeping (PD351(b)(e))

145-a2-1 did steps 1-4 and 7 (adopt 95e408ff by import, expected EL, load 605.4 MB, graph `graph_ring_p4s04_20261007_223245.json`
094ba298, facts `tools/bench/diag_c145_a2_1_facts.md`, table `diag_c145_a2_1_table.log`) and stopped at step 5: no existing op reads a
connector-pane terminal's Required / Recommended / Optional, and its brief wrongly forbade saving a VI. **That prohibition is lifted
here:** a new READER op saved as a NEW file under `claudeDev` is allowed (Save authority, CLAUDE.md §3). Everything else in the old
"Never" list stands. Do NOT redo steps 1-4 (the adopted file, expected EL, graph exist; check their md5 only).

## Steps
1. Read `diag_c145_a2_1_facts.md`, `diag_c145_a2_1_table.log:16-31` (PS1 inputs Num, last wired; SQ1 n1, last wired; n2, Latest,
   discards UNWIRED) and `archive/peer/2026-10-07-c145-a2-1-conpane-required-claude.md:37-53` (the API: ConnectorPane `WiringRules[]`
   239A8405, `Wiring Rule:Get` 239A8007; 1 Required, 2 Recommended, 3 Optional). A peer answer is a hypothesis: confirm it on the machine.
2. **Build the reader** from the existing `OpConPane_v0` pattern (`gscript.conpane`, `tools/gscript.py:3365`): input = a VI path, output =
   per connector-pane terminal index: control name + wiring rule. Scripted build only (no GUI clicking). Close every reference it opens.
   Accepted only if (a) a POSITIVE CONTROL reads back what was set: in a throwaway scratch VI set one terminal Required (`Wiring Rule:Set`),
   one Recommended, one Optional, read all three back; (b) 20 consecutive calls leave the handle count flat (+-100); (c) it never saves or
   edits the VI it reads. If the first read of any terminal gives a value you cannot explain, RETURN with the raw values.
   The scratch-VI rule applies: ≤ 120 lines, built per run and deleted in the same operation (name unique per run).
3. **Measure:** read the wiring rule of EVERY terminal of `claudeDev\RingPickSlot_v0.vi` (6fcf153f) and `claudeDev\RingSeqCheck_v0.vi`
   (0295a8d3), opened READ-ONLY (never saved; md5 checked after). Table: VI, terminal index, control name, rule, wired at PS1/SQ1 (from
   the s04 graph, step 1 rows). **Any unwired input at PS1 or SQ1 that reads Required = RETURN** (PD351(b)'s cause fails; name it).
4. **Housekeeping, only after step 3 succeeded:** delete `claudeDev\D1_ring_p4s04_20261007_212230.vi` (abb76d41) and its resume record
   (find it by name; report the path). Keep the adopted `D1_ring_p4s04_20261007_215031.vi` (95e408ff).
5. **Check after:** adopted file 95e408ff, s03 282301ca, bed 39511877, both subVI files unchanged; plan f349c39a, pred a2bbc8bf, recipes
   fe3f630c / f5e4bdf8 unchanged; LabVIEW closed and verified gone (`tasklist`); handles before/after.

## Never
- edit stagexec / stagekit / stagesim / stage_prerun / gscript / elrule (EL rule fix = card 145-a2-2, after this card); a gscript
  verb that is missing goes into the new op's own build script, not into gscript;
- save RingPickSlot_v0 / RingSeqCheck_v0 / the adopted s04 file / s03 / the bed, or open any of them for editing; run a scratch of any plan;
- touch the camera or any motor; touch s05 files.

## Return
`result/1` with: reader op file + md5, positive-control readback, handle series, the requiredness table, the verdict ("every unwired
input at PS1/SQ1 is not Required" or the offender), deleted files, md5s before/after, `tasklist` after. Facts file
`tools/bench/diag_c145_a2_3_facts.md` (the table citable by file:line).
