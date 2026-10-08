---
type: facts
status: current
date: 2026-10-08
card: 149-a1-3
---
# Card 149-a1-3 facts: s06 EL really holds 51; -6 = three s05 sourceless wires that s06 sourced; void->I32 item new + unexplained; w23807 type-consistent, Is Broken? NOT read
## 1. Header - capture of byte copy `_elc_..._181243.vi` (569ffbf5, sys.path wrapper, card 149-a1-2), viewed as an image (not OCR)
- `errorlist_shots/errwin_181332_b0b.png`: "51 errors and warnings", Show Warnings unticked; last row `errwin_182200_b50_1.png`: scrollbar at
  bottom, item 50 selected -> 51 rows. s05 `errwin_012412_b0b.png`: "55 errors and warnings", Show Warnings unticked too. OCR alternative B refuted.
## 2. Captures (listing `diag_c149_a1_3_items.log`)
- s06 item 5 = s05 item 14: same detail "1D array of Void -> 1D array of cluster of 2 elements" (s06 json :281, s05 json :658); same view in
  `bd_181438_after5.png` / `bd_012727_after14.png`. s06 item 6 "source void -> sink long [I32]" (s06 json :322): no s05 or predicted counterpart;
  `bd_181450_after6.png` marks a spot at the left edge (x~22, y~900) of a selected structure.
- s05 items 7, 8, 10-13 (`bd_012551_after7` .. `bd_012710_after13`): all in the right-hand Force/Mag For-loop region (broken-wire X marks);
  none matches s06 item 5/6; none has an s06 counterpart.
## 3. w23807 in saved s06 (never-saved byte copy; `diag_c149_a1_3_wire.log` 9/0 :29, ExecState 0 :6)
- Source t5171 'pos in cal image out' SubVI #5058; sinks t10975 'array' #10969, t3173 'Pos within cal image' Diagram #23166 (:7-11) = the wire
  of op 21's 'target BROKEN' line (scratch log :990-994) and of gate SG/D (:998, :1002). Removed sinks t9519/t10871/t23798 now wire 0.
- Types (:15-17): source and both sinks 1D array of I32 -> w23807 is NOT item 6's wire; one source, no type mismatch on it.
- `Is Broken?` NOT read: the only by-uid reader (gscript.wire_remove_loose_ends) edits; the stagekit read script was gated as VI-modifying
  (discard_work in MODIFY_VERBS, stage_prerun.py:3136) -> gate-fp **fp-63**; reads ran in a plain gscript script instead.
- `diag_c149_a1_3_types.log` 7/0: the 11 terminals on wires around moved #10068/#29240 (tunnels #30287/#30290) are all I32 -> the guess that
  item 6 sits at the moved nodes ((40,900)/(40,960)) is NOT supported; item 6's wire is unidentified.
## 4. Per-class (read s06 / pred / s05; pred = s05 + sr 1 - local 1, pred json :198-227; cmp = `diag_c149_a1_3_cmp.log`)
| class | read/pred/s05 | d | status |
|---|---|---|---|
| loop tunnel undirected | 0/3/3 | -3 | explained: s05 sourceless w10166/w28684/w29766 ran into tunnels #10177/#9503/#29777 (cmp :81-90); s06 sources each tunnel (w30250/w30270/w30284); s06 sourceless 0 (cmp :80) |
| sinks but no source | 0/1/1 | -1 | explained: same 3 wires sourced |
| out tunnel -> SubVI | 0/1/1 | -1 | explained: w28684 = SubVI #28083 'Magnet position' + tunnel #9503, 2 sinks 0 sources (s05 json :490), sourced |
| out tunnel -> Replace Array Subset | 0/1/1 | -1 | explained: w10166 / w29766 sink GrowableFunction 'index (col)' #8634 / #29625, sourced (which is the RAS not read) |
| input | 4/6/6 | -2 | explained in part: s05 3 BA + 3 IA, s06 1 BA + 3 IA; BA #2626 t2832/t4160/t4165 newly wired, BA #29973 t29989 on now-sourced w29766; item->uid not read; pred's uncertain #10757 'array' (wire 0) shows no extra IA item |
| types mismatch | 2/1/1 | +1 | UNEXPLAINED: item 6 void->I32 (not w23807, not the 11 terminals) |
| not connected | 22/20/20 | +2 | explained: termless wires 20 -> 22, new w10187/w29787 = old outputs of moved #10068/#29240 (cmp :110-111) |
| loose ends | 21/20/20 | +1 | consistent with w10103 (tunnel #10114) losing its only sink t10080 (cmp :113-115); not proven |
| local, sr | 1/1/2, 1/1/0 | 0 | as predicted |
- 55 - 6 - 2 + 1 + 2 + 1 = 51. The predictor holds every 'other:' class at its s05 count (pred :216-227).
## 5. Invariants `diag_c149_a1_3_inv.log` 12/0 (s05 3f9ac26b, s04 95e408ff, s03 282301ca, bed 39511877, s06 569ffbf5, stagekit, stagexec, gscript,
elrule, errorlist_check, memory_model 88eeb037; no `_elc_*`/`_c149a13_*`); handles 48956 -> 42422 (wire.log :6, :24); tasklist no LabVIEW; no adopt.
OPEN: (1) accept item 6 (void->I32) unidentified, or read `Is Broken?`/the selected object under a card that allows an edit-verb or a uid op?
(2) fp-63: should a read-only stagekit diagnostic (discard_work only) pass the launch gate?
