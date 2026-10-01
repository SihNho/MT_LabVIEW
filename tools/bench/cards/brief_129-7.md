# Brief for card 129-7 (cycle 129 judgement) — the FS outer tunnel's NAME after a crossing, from measured cases only

OFFLINE ONLY (runs beside the LabVIEW measurement card 129-6). No LabVIEW, no COM, no gate code (`stage_prerun.py`,
`protocol.py`, `tools/hooks/*` untouched).

## The failure (129-4, `stage_d1_ring_p3b1_scratch_pin2.log:472-477`)
Op 33 `connect_term_uid #28345 <- #6897` (`p3b_x_bn_n3`, plan rows `plan_ring_p3b1.json` ~599-605, source uid 6810's
`current image number` → SEL1.f, across case border 639→27219 and the FS border): E1 BINDING — the new
FlatSequenceOuterTunnel's terminals are named `current image number` in LabVIEW; stagesim predicted `''`. Ops 27/29/31
(`:412,432,452`, source #27373 `x-y*floor(x/y)` across the FS border) got `''` and matched. `diag_c126_6_cross.log` B1
(`#27881 <- #6897`, `:45-50`) also named both faces `current image number`; B2 `''` (`:61`). Review
`archive/peer/2026-10-02-hyp-c129-4-ring-p3b1-fsot.md:52,61-65`: model the MEASURED case, not "copy the source label".

## 0. Time arithmetic (budget 30 min)
table of every measured FS crossing ~8 min · sim rule + self-test ~8 min · re-finalize P3b-1/P3b-2 + replay + preds ~5 min ·
dry + prerun of the P3b-1 recipe (own processes) ~2 min · total ≈ 23 min.

## 1. The table first
Every measured FS-border crossing in the logs (`diag_c126_6_cross.log` B1–B4, `diag_c126_4_fs.log`, 127-1's rows, pin2 ops
27/29/31/33): case | log:line | source uid | source class (from the graph files, e.g. `tools/bench/graph_ring_p3a_20261001_190155.json`)
| source terminal name | is the source a tunnel (class) and its name | the crossing route | real new-tunnel name(s).

## 2. Then
If ONE recorded attribute separates the named outcomes from the `''` outcomes in EVERY row, model exactly that in stagesim's
FS crossing (the new tunnel's terminal names), with a self-test row per measured case (stagesim + stagexec self-tests stay
green), then re-finalize `plan_ring_p3b1.json` / `plan_ring_p3b2.json` from their `_in` files (same split; P3b-2 still
provisional on P3b-1's END), re-check the split equivalence (end graph == the unsplit 70-action replay), update the preds
by script, and run dry + prerun of `tools/recipes/stage_d1_ring_p3b1.py` (own processes). If no single attribute separates
every row, change nothing and return the table — that is the first unexpected result.

## 3. Return
`result/1` (`tools/bench/cards/result_129-7.json`), validated + `py tools/card_clock.py` OK: the table, the attribute and its
rows, stagesim lines changed, self-test counts, new plan/pred md5s, equivalence numbers, dry/prerun lines.
