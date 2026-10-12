---
card: 166-a1-2
status: current
date: 2026-10-12
---
# Brief 166-a1-2 (assignment 166-1) - P5 CLOSE-OUT, OFFLINE: expected Error List file for the P5 final, then the bed moves (P5 ENDS)

Plan: `docs/d1/ring-p5c.md` PD403(a) (line 242-251) and PD403(c) (line 261-263). Card 166-a1-1 PASSED (`tools/bench/diag_c166_a1_1_facts.md`): graph read, rule-1a tunnel check equal, `load_by_vi`, census. No LabVIEW in this card.
The P5 final is `claudeDev\D1_ring_p5_20261010_172913.vi` 75773b0d (byte-equal to `D1_ring_p5s02e_20261010_172913.vi`). The read is `tools/bench/errorlist_D1_ring_p5s02e_20261010_172913_20261010_173731.json` 0c0664d8 (47 items).

## Steps
1. **Hash first** the card inputs (hashlib log). Drift = RETURN.
2. **Expected Error List file** `tools/bench/errorlist_expected_D1_ring_p5_20261010_172913.json`, written BY SCRIPT from the read 0c0664d8, item by item (47 items, each cited to its index in the read), `PD354(a)` record-only (no gate on counts).
   The prepared script `tools/bench/diag_c165_a3_4_elexp.py` (0a009b0a; card 165-3-4, never run) is the pattern: it builds exactly this file mechanically and compares it with the PREDICTED end `errorlist_predicted_D1_ring_p5s02e_end.json`.
   Do not paste its body again: if the helpers it carries (`norm_ocr`, `elcls`, the compare) are also in `diag_c164_a3_5_elexp.py` or in a shared module, CALL them (docs/script-writing.md rule 1/4; report the copies as file:line). The new script is `tools/bench/diag_c166_a1_2_elexp.py`.
   Record in the file and in the facts: total 47; the 2 predicted items that are not in the read are **item 4 (w4337 'has no source') and item 49 (w9636 'While Loop to SubVI')**, cited as CLEARED by `A73`/`A84` (the plan's numbering of A70/A80; `errorlist_predicted_D1_ring_p5s02e_end.json:180-186` and `:1005-1013`
   give `clears_by`), PD403(a). Name the file basename the way the earlier steps did (the VI is the `D1_ring_p5_` name). Quote old/new md5 and the compare line (extra, missing). The compare is RECORD: missing 2 / extra 0 here is the expected result, not a return.
3. **Bed moves (PD403(c)):** edit `STATUS.md` by the editor tools only: (a) the `current-bed:` line (STATUS.md:133) -> `D1_ring_p5_20261010_172913.vi`; (b) the HTML comment right under it: prepend one `Moved 2026-10-12 by cycle 166 (PD403(c), docs/d1/ring-p5c.md): P5 ended, ... adopted (md5 75773b0ded2a08586bb1a542ddda5af6, expected Error List tools/bench/errorlist_expected_D1_ring_p5_20261010_172913.json <md5>, 47 items), counted broken file 6 of 6.`
   in the same style as the existing "Moved ..." sentences; do not touch the older text. (c) The "THE WORK VI (bed) IS NOW ..." line (STATUS.md:134): make the new P5 line the live one and turn the old p4s09 line into a "(history) THE WORK VI (bed) WAS" line, as earlier moves did (look at how p4s09 replaced p3b2b); the new line states file, md5, END OF P5, Error List 47, graph `tools/bench/graph_ring_p5s02e_20261012_173009.json` (md5 from the card 166-a1-1 result), load 647.8 MB (cite `diag_c165_a3_4_graph.log:24`, and note that the tunnel read of the same file loaded at 599.4: `diag_c166_a1_1_tun.log:25`), STRUCTURAL ExecState 0 by design, never run, **broken-file count 6 of 6, P6 must RUN, no further COUNTED broken file; in-between files stay uncounted**.
   Edit `docs/d1/INDEX.md` the same way: the "Work VI (bed)" bullet (INDEX.md:26) and the broken-file count 6 of 6; the PD403 line (INDEX.md:317) may get "bed moved" appended. Do NOT touch STATUS.md's ## NEXT block or anything else (the runner and the judgement own it).
4. **Check the machine key:** run `errorlist_check.current_bed_text()` on the new STATUS text (a one-line script or `py -c` inside a script file under bgrun) and quote its output; it must name the P5 final file. Also `py tools/errorlist_check.py` is NOT run (it starts LabVIEW).
5. **End:** hash again; the seven VIs of the purpose (eb1d0f31, 7f2582ae, 94ffff94, f9ae7751, 564d8cbe, 6dcd5c3d, 75773b0d) unchanged; no original opened; no LabVIEW process was started. Facts `tools/bench/diag_c166_a1_2_facts.md` (<= 30 lines, file:line for every number).

## Not in this card
No LabVIEW, no hook edit, no recipe / plan / licence / predicted-EL edit, no tooling change (the predictor repair is another card), no `## NEXT` edit.
