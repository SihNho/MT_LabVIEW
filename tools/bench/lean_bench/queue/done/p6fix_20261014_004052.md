# Lean task 3: fix P6's one-lap-old per-row values (column 0, and TransPos/RotPos if they share it), then re-accept P6-2
One session, <= 180 min, <= $60. Real project work (user 2026-10-13 "진행하도록").

Read `CLAUDE.md` (the lean rules) first, then your own reports `tools/bench/lean_bench/lean_report.md` (P6-2) and
`lean_report_p63.md` (P6-3, section "Column-0 finding") - reuse every tool and route from them.

## The finding (P6-3 report, re-checked by the chat from the raw tra files)
In loop 1.2 the `FrameIdx` local read (#30239 -> IndexArray #30240, wire 30267) has no input wire, so it is not ordered after
the slot pick and not covered by the n1 -> track -> n2 seqlock. When 1.2 keeps up, each row gets the slot's PREVIOUS
occupant's value: column 0 = buffer number of frame k-20 (P6-2 2518/2518 rows with index >= 20, W40 2520/2520; the first 20
rows -1). The original (S1) stores the row's OWN buffer number. `TransPos` / `RotPos` very likely use the same read form
(P6-2's B4: trans row 0 = 0.0 vs S1 21.6852) - check it in the graph; the replay data alone cannot show it (init-segment
trans differs between any two runs, S1 vs S1 included, because it is a hardware readback).

## The acceptance that matters most (user 2026-10-13: "과부하가 걸리더라도 버퍼 넘버의 정확성이 데이터의 정확성을 결정하는듯")
Every saved row's buffer number (column 0) must be the buffer number of the frame whose X/Y/Z are on that row - at normal
load, with a gapped source AND under overload. Skipped frames are allowed; a row whose number is not its own frame's is
corruption (U7: the buffer number is the time axis; U9: a mismatched pair is corruption). The same holds for any other
per-slot value written with the row (TransPos/RotPos). This is the first PASS/FAIL item of the report, per condition.

## Do
1. Graph facts first (offline): every per-slot value loop 1.2 reads from the ring besides the image (FrameIdx, TransPos,
   RotPos, anything else), how each is read, and whether it is ordered after the pick and before n2.
2. Write the fix design and your predictions into the report BEFORE any LabVIEW edit: what changes, why it touches no
   per-bead maths (rule 1a: only the ORDER of a read changes; the values come from the same slot arrays), and the expected
   result of the re-run (column 0 = own buffer number on every row; X/Y/Z still bit-identical).
   Keep the ring's pick / discard behaviour exactly as built (the user has not yet decided on U8 latest-wins).
3. Build the fixed P6 from a byte copy of the bed `claudeDev\D1_ring_p6_20261012_212645.vi` (c2d9c13c, read-only) and save it
   ONLY under `claudeDev\bench\lean\` as `D1_ring_p6fix_<ts>.vi`, ExecState 1 warm and cold, edge diff = exactly the intended
   change. If copying a node into the big VI breaks it again (P6-3 section 4), find a route that does not (e.g. reorder by
   wiring existing outputs, or a small subVI swap as in P6-3) and say which.
4. Re-run P6-2 on it (replay copy by plan 170's swaps, S1 leg of P6-2 reused as reference, motor sessions with readback,
   LabVIEW gone after each run) and compare with column 0 INCLUDED: X/Y/Z bit-identical per row, column 0 == S1's column 0
   of the matched frame, cal outside the date field, trans/rot post-init; report trans/rot init rows as facts.
5. Re-run the three P6-3 conditions on the fixed copy with the same test routes (gap wrapper; RingSeqCheck W40 / W100
   copies): column 0 == own buffer number on EVERY row in each (gap: the gapped number 2k+1 of the row's own frame), X/Y/Z
   bit-identical, rows strictly ordered. Report per condition: rows, own-number rows / total, lost, damaged.

Do NOT edit `tools/hooks/**`, `tools/motor_gate.py`, `tools/bench/motor_limits.json` or `CLAUDE.md`. Do not commit.

## Report `tools/bench/lean_bench/lean_report_p6fix.md`
Graph facts, design + predictions (written first), timeline, the fixed VI (path, md5, exact change), re-run numbers vs
predictions, what failed and how you fixed it, shared scripts edited, motor readback lines, LabVIEW-gone, input md5s start vs
end, then `RESULT {"p6fix": "PASS|FAIL|INCOMPLETE", "col0_own": {"p62": "n/N", "gap": "n/N", "w40": "n/N", "w100": "n/N"}, "xyz": "n/N", "minutes": N}`.
