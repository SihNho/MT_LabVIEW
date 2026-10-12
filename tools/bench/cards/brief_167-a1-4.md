---
card: 167-a1-4
status: current
date: 2026-10-12
---
# Brief 167-a1-4 (assignment 167-1) - P6-0 (g), OFFLINE: P6-2 replay readiness facts

Plan: `docs/d1/ring-p6.md` PD404(g) (lines 87-90) and (a) row P6-2 (line 52). Offline, stored files and source reading only: NO LabVIEW, no VI opened, no camera, no motor, and NO tool is built or edited. Facts only.
Replay chain to read (F5 of `tools/bench/p6_facts.md` lists it): `tools/recipes/stage_replay_swap.py`, `tools/bench/drive_m8_replay_110.py`, `tools/bench/m8b_replay_compare.py`; the records of card 110-6 (`tools/bench/cards/result_110-6.json`, `grep -rn "110-6" docs/ tools/bench/*.md | head`), the stored replay results `tools/bench/m8_replay_s1*.json` / `m8_v5_replay_s1*.json`.
Graphs: S1 `docs/wiki/subvi/D1_s1_copy.json` 5de014fe; P5 final `tools/bench/graph_ring_p5s02e_20261012_173009.json` 7815af09.

## Produce (one file pair `tools/bench/p6_replay_ready.md` + `.json`, every cell with a file:line or json-path source; unread = the word "unread")
1. **Swap sites:** each call site the m8 replay swap replaces (by S1 uid and class/name as the recipe states it), and for each: present in 7815af09 or not (same uid? same class and name? moved owner? say which). A site the recipe resolves by label/name, not uid: say that and show how the graph finds it.
2. **How card 110-6 stayed off the motors:** the exact mechanism (which call sites/inputs were swapped or stubbed, the hardware flag, the gate) with file:line. "hardware none" alone is not an answer.
3. **Saved files compared:** which files the replay compared (X/Y/Z log, saved data files), with the compare script and what 'bit-identical' meant there (rows, common rows, file bytes), file:line; whether the saved files are compared byte-for-byte or by value.
4. **Missing pieces:** what a ring file (`D1_ring_p6_<ts>.vi`) would need that the chain does not have today (swap sites absent from 7815af09, new loops not covered, the recorded-frame source, anything hard-coded to S1 paths/uids). List each as a fact with its source; do NOT propose a design and do NOT build or edit any tool.
Script `tools/bench/diag_c167_a1_4_ready.py` (scope header `# labview: none`, `RESULT {...}` line, `bgrun --material`, CALL shared functions). Facts `tools/bench/diag_c167_a1_4_facts.md` (<= 30 lines).

## Checks
Hash first the inputs and the seven VIs (75773b0d 7f2582ae 94ffff94 f9ae7751 564d8cbe 6dcd5c3d eb1d0f31; names as in `tools/bench/diag_c166_a1_1_hash.py`); drift = RETURN; hash again at the end, unchanged; `tasklist` shows no LabVIEW; outputs' md5 quoted.

## Not in this card
No LabVIEW, no new tool, no edit of the replay tools or any shared module, no STATUS / plan / hook edit, no design for P6-2.
