---
card: 169-a2-1
status: current
date: 2026-10-12
---
# Brief 169-a2-1 (assignment 169-2) - PD406(e): the bed moves to the saved runnable P6-1 file

Plan: `docs/d1/ring-p6.md` PD406(e), PD407. Card 169-a1-3 (`tools/bench/diag_c169_a1_3_facts.md`) read the SAVED file
`C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_ring_p6_20261012_212645.vi` (md5 c2d9c13cb40c0a5cab7433896d1df157, 511194 B) from a byte copy:
ExecState 1, DN [11261], E5 ok, graph fbc7b7ee, S-5 30 vs 30, peak 615.1 <= 675; then the final Error List (0 items, `errorlist_expected_D1_ring_p6_20261012_212645.json` 5e2a4e6f),
then ONE load_by_vi entry (603.7, memory_model 8b4a9b48). These are the conditions PD406(e) sets for moving the bed. This card moves it. It is a text edit.

## Steps (stop at the first unexpected result and RETURN with the facts)
1. Hash the inputs and the saved file's bytes (python md5; do not load it in LabVIEW). Drift = RETURN.
2. STATUS.md (editor tool, one Edit per change, never a heredoc): (a) `current-bed:` line -> `D1_ring_p6_20261012_212645.vi`; (b) prepend to the comment line below it
   a sentence in the style of the existing "Moved 2026-10-12 by cycle 166 ..." one; (c) add the new bed paragraph "THE WORK VI (bed) IS NOW ..." above the P5 one and turn the
   P5 paragraph into "(history) ... WAS ..." exactly as the earlier moves did. The new paragraph says RUNNABLE: ExecState 1, Error List 0, broken-file count stays 6 of 6 (the P6 file is a
   runnable file, not a counted broken one), cites file:line from `diag_c169_a1_3_facts.md` and `launch_c169_p6.json`, and names the inputs kept (75773b0d P5 final and the in-between files).
3. docs/d1/INDEX.md: the 'Work VI (bed)' line, same style as the previous move.
4. `current_bed_text()` of `tools/errorlist_check.py` -> quote the value it returns.
5. Facts `tools/bench/diag_c169_a2_1_facts.md` (<= 25 lines): the md5s before/after of STATUS.md and INDEX.md, the line numbers changed, the `current_bed_text()` output, `git diff --stat` of the two files, a `skipped:` line.

## Not in this card
No LabVIEW, no ## NEXT edit, no plan edit, no memory_model edit, no fp drain (card 169-a2-2), no recipe, no hooks.
