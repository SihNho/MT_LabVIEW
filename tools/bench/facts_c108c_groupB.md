# Card 108-3 - group B consumer/producer tables (OFFLINE, structural; measure only, no destination)

Data: `tools/bench/facts_c108c_groupB.json` (bed = `graph_l2a1_bed_20260927.json` md5 `93d153dd`, VI `D1_l2_a1_20260925_235224.vi` `51d9b8a3`; S1 = `par1359_95_graph.json`, VI `D1_s1_copy.vi` `3e3d23ce`). Script `tools/bench/diag_c108c_groupB.py` + `diag_c108c_graph.py`, log `tools/bench/diag_c108c_groupB.log`. Every cell's cite is in the JSON row (`cite`/`cite_b`); S1 cites are `par1359_95_graph.json:<line>`, bed cites are `term_uid` (single-line file).

## T1 - outputs, walked through tunnels/SRs/FS/Local relays to the first non-carrier (s1.T1, bed.T1)
| B node | output -> first sink | tag | bed |
|---|---|---|---|
| #1359 | tunnel 9227 -> SR #9018/#9025 on #637 -> #1359 in-tunnel 9087 (`:24626`,`:24616`) | B internal (ring) | same |
| #1359 | tunnel 11363 -> #11261 `array` (`:24386`) | B internal | same |
| #2222 | `Z out` -> #9833; `X out` -> #6104 (`:24566`,`:25446`) | B internal | same |
| #2626 | `appended array` -> #376 `save trace.vi` 'current frame data array in' (`:26506`) | **saved-data (1.7)** | UNWIRED (w4517, QRT-owed) |
| #6104 | `subarray` unwired (`:25456`) | none (dead output in S1 too) | same |
| #8885 | `x*y` -> #29874 (30135), #1359 (10004) (`:17966`,`:24646`) | B internal | same |
| #9833 | `subarray` -> #8885 `x` (`:24426`) | B internal | same |
| #11261 | -> indicator #8323 'Force (pN) vs Extension (nm) ' (`:27576`), no Local reader | display-only | same |
| #29874 | -> indicator #28786 'Extension (nm) vs Time (Frame #)' (`:27876`); -> SR #29505/#29512 -> own in-tunnel 29911 (`:17956`) | display-only / B internal | same |
Motor consumers: 0. 1.2 or 1.5 computation consumers: 0. Interior of B: 0 indicators, 0 Local/Global/Property, 1 control (`Exp Baseline` #8476, `:25406`), 7 subVIs, none motor/save (JSON `addenda.interior_census_s1`).

## T2 - vs `plan_disp.json` (S1 branch)
#1359: PARTIAL - 9 interior nodes moved (`mv_8775` :46, `mv_8795` :59, `mv_8741` :72, `mv_8764` :85, `mv_28180` :98, `mv_28233` :111, `mv_27716` :124, `mv_29009` :137, `mv_11310` :150), tunnel 11363 deleted (`del_11363` :311); #1359 itself, #8634, #28083 not moved. #11261: YES (`mv_11261` :298; element via `r6_wlc_element` :591, output via Local write `r6_force_write` :618). #2222, #2626, #6104, #8885, #9833, #29874: NO row. (Lines = `tools/bench/sim/disp/plan_disp.json`.)

## T3 - inputs from outside B (distinct source terminals; JSON `addenda.T3_crossings`)
- from 1.2: #5058 'x,y,z array out' -> #2222 and #2626 (`:26336`); on the bed both sinks are UNWIRED (w505 half-wire).
- from 1.1: #10068, #30117 Property Value (target UNKNOWN), #5119, #4580 Property Value, #11608 Bundler (WLC), #29240 = 6.
- pre-loop (enter #637 by tunnel / SR init): #8953, #28124 (SR inits), #27605 Max Trans Pos, #5426, #5556 (FS, bed resolution) = 5.
- panel: the 4 controls only; constants on 639: #6404, #9050, #9906.
- crossings if all 8 go to 1.2: 6 in + 1 out (#376) = **7**; to a display loop: 7 in + 1 out = **8**; both: 5 pre-loop tunnels/SR inits, 2 indicators, 2 B-only SR pairs on #637 to re-create.
- #2626 has no data edge to any other B node (in 1.2 x1, 1.1 x3, out 1.7); the other 7 are one chain whose only exits are the 2 indicators.

## T4 - the 4 controls (readers; no Local of any of the 4 in either graph)
| control | readers (all inside B) | in plan_disp moved set |
|---|---|---|
| Z/dZ #47 (#403) | case #2222 selector tunnel #2276 (`:25486`, manual addendum) | no |
| Correction Factor #9289 (#9306) | #5696 N bead plot dZ, #6085 N bead plot Z (in #2222) (`:25586`,`:25726`) | no |
| Force smoothing #28148 (#28170) | #27716 index, #28180 half-width (in #1359) (`:24846`,`:25026`) | both yes |
| Extension median #28996 (#29091) | #29009 (in #1359, `:24796`/`:24806`), #30306 (in #29874, `:18086`/`:18096`) | #29009 yes, #30306 no |
Per destination: every reader is a B member, so if all of B goes to one loop, each control has readers in that loop only (bed and S1 agree). Under plan_disp's partial move, #28996 has readers in two loops (PD212(h)2).

## Caveats
Script gate G3 failed on its own contract (P0 lists data tunnels; #7922/#29914 are unwired N terminals); tables unaffected; the corrected rerun was refused by `guard_peer` (review owed, card has no peers).
