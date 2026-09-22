---
type: reference
status: reference
date: 2026-09-23
tags: [d1, m3a, severed-rows, offline]
---

# M3a-1 severed rows — what `build_d1_m3a1.log` does and does not record

Derived offline by `tools/bench/diag_c90_severed_rows.py` → `tools/bench/diag_c90_severed_rows.log`
(5 gates pass / 0 fail) and `tools/bench/m3a1_severed_rows.json`. No LabVIEW was touched.

## 1. The finding: the pre-move WIRE census is NOT in that log

**None of the 11 wire uids appears anywhere in `tools/bench/build_d1_m3a1.log`** (3,436 lines,
5 BGRUN blocks; total hits 0, `tools/bench/diag_c90_severed_rows.log:56`). The file prints wire
uids on 216 lines (`…:57`), but every one belongs to the POST-move `[4]`/`[5]`/`[6]` censuses of
the NEW wires. Section `[2b]`'s BEFORE/AFTER lines record **per-node terminal counts only** — e.g.
`build_d1_m3a1.log:2756` "1 terminal(s), 1 WIRED". So all 11 rows are `status: unaccounted` in the
JSON, each carrying that reason. The endpoints in §3 come from OTHER files, marked as such.

## 2. What the log DOES record (delivering run = block 5, from `build_d1_m3a1.log:2717`)

Working copy cold `ExecState` **1** at `:2741`; section header `:2754` states the mechanism —
*"37(d) severs every wire on the moved object"*; `ExecState` **0** already at `:2778`, after the
first move; `Wire` census **unchanged at 1907** after all seven (`:2926`), i.e. severed into
half-wires, not deleted. **19 wired terminals were severed; 0 remain wired**
(`tools/bench/diag_c90_severed_rows.log:55`).

| # | moved node | class (per log) | WIRED before → after | BEFORE / MOVE / AFTER line |
|---|---|---|---|---|
| 1 | `#3529` `- Inc (PgDn)` | ControlReferenceConstant | 1 → 0 | `:2756` / `:2758` / `:2777` |
| 2 | `#3560` `+ Inc (PgUp)` | ControlReferenceConstant | 1 → 0 | `:2780` / `:2782` / `:2801` |
| 3 | `#3447` `Focus Step (F1)` | ControlReferenceConstant | 1 → 0 | `:2804` / `:2806` / `:2825` |
| 4 | `#48` `ASI_adjust focus-subvi.vi` | SubVI | 7 → 0 | `:2828` / `:2830` / `:2849` |
| 5 | `#10407` `Case Structure` | CaseStructure (autofocus) | 7 → 0 | `:2852` / `:2854` / `:2873` |
| 6 | `#23499` `Local (row 1 carrier)` | Local | 1 → 0 | `:2876` / `:2878` / `:2897` |
| 7 | `#23523` `Local (row 2 carrier)` | Local | 1 → 0 | `:2900` / `:2902` / `:2921` |

## 3. The 11 rows — endpoints from OTHER on-disk files (NOT from `build_d1_m3a1.log`)

Severing move = the first of the seven whose node owns an endpoint. All 11 are named and all 11
are attributed (`tools/bench/diag_c90_severed_rows.log:60-61`).

| wire | source end | sink end | severed by (log line) | endpoint source |
|---|---|---|---|---|
| 1731 | `LeftShiftRegister#4344` | `#48` t3 `VISA resource name` | #48 (`:2830`) | `tools/bench/c53_row_class.log:99`, `:121` |
| 1893 | `#3447` t0 `Focus Step (F1)` | `#48` t2 `Focus inc reference` | #3447 (`:2806`) | `tools/bench/c53_row_class.log:98`, `tools/bench/build_d1_m3a1.json:9437` |
| 2819 | `#3560` t0 `+ Inc (PgUp)` | `#48` t1 `+Inc reference` | #3560 (`:2782`) | `tools/bench/c53_row_class.log:97`, `tools/bench/build_d1_m3a1.json:9296` |
| 3947 | `LeftShiftRegister#4274` | `#48` t4 `In position` | #48 (`:2830`) | `tools/bench/c53_row_class.log:100`, `:125` |
| 4833 | `#3529` t0 `- Inc (PgDn)` | `#48` t0 `-Inc reference` | #3529 (`:2758`) | `tools/bench/c53_row_class.log:96`, `tools/bench/build_d1_m3a1.json:9155` |
| 7337 | `#10407` t4 `VISA out` | `RightShiftRegister#4334` | #10407 (`:2854`) | `tools/bench/c53_row_class.log:93` (`to-sr`), `docs/frame-loop-wire-graph.md:466` |
| 7388 | `#48` t5 `Out position` | `#10407` t5 `Out position` | #48 (`:2830`) | `tools/bench/c53_row_class.log:94`, `tools/bench/build_d1_m3a1.json:9797` |
| 9635 | `LoopTunnel#9641` | `#10407` t1 `# slices in stack` | #10407 (`:2854`) | `tools/bench/c53_row_class.log:90` (`from-tunnel`), `docs/frame-loop-wire-graph.md:465` |
| 11232 | `#48` t6 `Outgoing Handle` | `#10407` t3 `Outgoing Handle` | #48 (`:2830`) | `tools/bench/c53_row_class.log:92`, `tools/bench/build_d1_m3a1.json:9578` |
| 23502 | `#23499` t0 (Local, row 1) | `#10407` t0 `''` | #10407 (`:2854`) | `tools/bench/diag_c64_s3b_row1.log:199`, `tools/bench/build_d1_m3a1.json:10016` |
| 23540 | `#23523` t0 `index` (Local, row 2) | `#10407` t2 `index` | #10407 (`:2854`) | `tools/bench/diag_c65_s3b_row2.log:215`, `tools/bench/build_d1_m3a1.json:10157` |

⚠️ The four non-node owner uids (`#4344`, `#4274`, `#4334`, `#9641`) are the cycle-67 machine reads
carried in `STATUS.md`'s `labview-lock` `purpose_dispatch4`, not readings of these files.
`tools/bench/c53_row_class.log` independently confirms `#4344`'s inside wire is 1731 (`:121`) and
`#4274`'s is 3947 (`:125`), and classes w7337 `to-sr`, w9635 `from-tunnel`.
`c53_row_class.log`'s table is measured on the ORIGINAL VI's netmap, not on the M3a-1 bed, so rows
23502/23540 (created in S3b) are absent from it and come from the two S3b diagnostics instead.
