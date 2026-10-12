---
type: facts
status: current
date: 2026-10-12
card: 166-a1-2
---
# 166-a1-2 facts: P5 expected Error List written (47 items, c94be128), bed moved to the P5 final, broken-file count 6 of 6; offline, no LabVIEW.
## 1 Hashes (diag_c166_a1_2_hash.py; CALLS protocol.input_md5_changes + prep_c156_a1_1_lib.md5/Gate; VI pin list copied as data from diag_c166_a1_1_hash.py:24-27)
- before 8/0: 9 card inputs equal, 7 VIs equal (diag_c166_a1_2_hash_before.log:3-11).
- after 10/0: 8 inputs equal (INDEX.md excluded, edited: 5404626f -> a8d26b4b), 7 VIs unchanged (diag_c166_a1_2_hash_after.log:3-11).
## 2 Expected Error List (diag_c166_a1_2_elexp.py, log diag_c166_a1_2_elexp.log, RESULT PASS 7/0 :16, rc 0 :17)
- old file absent (:3); R 47 == n_reported 47 (:4); V p5 and p5s02e both 75773b0d, read bed = p5s02e at that md5 (:5); S 2a8e2984 / 0c0664d8 (:6).
- RECORD compare(read, predicted 2a8e2984): extra 0, missing 2 (:7) - record only, PD354(a).
- Dropped item 4 (w4337 has no source): predicted :167 entry, :182 clears_by 'A70 w_k3f', cleared[] :46 w_k3f -> A73 (:8).
- Dropped item 49 (w9636 While Loop to SubVI): predicted :993 entry, :1009 clears_by 'A80 w_k4f', cleared[] :54 w_k4f -> A84 (:9). Gate D PASS (:10).
- C every read item 0..46 cited once via read_index, no headers, no ambiguous (:11); X compare(read, new) extra [] missing [] (:12); T total 47 (:13).
- WROTE tools/bench/errorlist_expected_D1_ring_p5_20261010_172913.json md5 c94be128e4e8cb9275abf7bacb1fa192, 46 entries (one count 2), cleared[] 2 (:14).
- Per-item cite = compare() on growing read prefixes (no matcher re-implemented); calls errorlist_check.compare/norm/class_counts (tools/errorlist_check.py:415,315,471).
## 3 Bed move (editor tools only)
- STATUS.md:133 current-bed -> D1_ring_p5_20261010_172913.vi; :134 'Moved 2026-10-12 by cycle 166 (PD403(c))...' prepended, older text untouched.
- STATUS.md:135 new WORK VI line (P5 final, 75773b0d, EL 47, c94be128, graph 7815af09, 647.8 MB graph.log:24 / 599.4 tun.log:25, 6 of 6); :136 p4s09 -> (history) WAS.
- docs/d1/INDEX.md:26 Work VI -> P5 final; :27 broken count 6 of 6; :317 PD403 line + 'bed moved 2026-10-12 (card 166-a1-2)'. ## NEXT untouched.
- Machine key: current_bed_text(STATUS.md 261856f8) -> claudeDev\D1_ring_p5_20261010_172913.vi, gate K PASS (diag_c166_a1_2_hash_after.log:13-14); no gscript/lv_errorlist imported (:15).
## 4 Copies found (script-writing.md rule 4; not extracted: tools/*.py outside this card's write globs)
- elcls inline: diag_c165_a3_4_elexp.py:50-57, diag_c164_a3_5_elexp.py:50-57 and diag_c150..c163 *_elexp.py:48/50, prep_c147..c154 *_pred.py, recipes stage_d1_ring_p4_s06..s09v18_scratch.py:95/98, p5s01a_scratch.py:98; no shared copy.
- norm_ocr inline in the same files (c165:43-47, c164:43-47) == tools/errorlist_check.py:331 norm_ocr (shared, already exists).
## Not done / not touched
- No LabVIEW started (tasklist empty before and after); no original opened; no recipe/plan/licence/predicted-EL/stage-tool/hook edit; no peer (no gate failed, no Jev row).
- STATUS.md is 154 lines (> ~110); relocation not done: the card limits STATUS edits to the bed lines.
