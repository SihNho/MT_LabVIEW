---
title: L2-A2 split page - group-A remainder on the L2-A1 bed (plan §2 row L2-A2)
date: 2026-09-27
card: task_107-2.json
source: docs/d1-loop12-17-split-plan.md:70 (§2 L2-A2), PD219(f)(2b) :1870, PD180(c)/181(c)/182(c)/183(c) :669-677,708-711,729-732,755-758
status: plan
---
# L2-A2 — cycle 107 (one page)

**Input (anchor):** `claudeDev\D1_l2_a1_20260925_235224.vi`, md5 `51d9b8a3…` (the bed, PD195(a)), never modified. Its
graph did not exist on disk; `tools/bench/diag_c107b_bedgraph.py` reads it READ-ONLY from a byte copy →
`tools/bench/graph_l2a1_bed_<date>.json` (the stagesim base; `stage_prerun.find_graph` finds it by md5).

## 1. The bed's open rows (F1) — frame-keyed cdiff(S1, bed), 9 rows

Measured on the bed's own state just before its save (`tools/bench/stage_d1_l2a1_86-5.log:731-739`, saved as md5
`51d9b8a3…` at `:751`) and re-measured on the file by `diag_c107b_bedgraph.py` (log `tools/bench/diag_c107b_bedgraph.log`).

| # | sink (uid 'terminal') | S1 source | §1 group of the row | owner stage / carrier | verb for a re-make |
|---|---|---|---|---|---|
| 1 | `#376 'current frame data array in'` | `#2626 'appended array'` (w4517) | W ← B | QRT (PD175, 1.2→1.7) | queue (QRT) |
| 2 | `#376 'frame index'` | `#644` i of `#637` (w3268) | W ← 1.1 | QRT (PD175) | queue (QRT) |
| 3 | `#2626 'array'` | `#5058 'x,y,z array out'` | B ← K | L2-B (moves `#2626` into 1.2) | wire / connect (exists) |
| 4 | `#5058 'Image In'` | `#6810 'Image Out'` | K ← 1.1 | QRT (PD177(e)) | queue (QRT) |
| 5 | `#5696 'x,y,z array'` | `#5058 'x,y,z array out'` via `#2222` tunnel 2765 f1 | B ← K | L2-B | tunnel_outer / OpTunOuterWire_v1 (exist) |
| 6 | `#6085 'x,y,z array'` | same, f0 | B ← K | L2-B | same |
| **7** | **`#9703 'x'`** (in `#10407`'s frame, loop 1.5, fed by selector tunnel `#10978` ← Local `#23523` of indicator `#23541`) | **`#10757 'element'`** | **A** | **see §2 — re-makeable INSIDE 1.2** | **`wire` → ControlTerminal sink: `OpCtlSinkWire_v1` (exists, PD191(a)/192; same class as L2-A1's `rw_10988_17272`)** |
| 8 | `#10382 'x'` (Not, 1.1) | `#9647 'x .and. y?'` | A → 1.1 | QRT (PD182(c)) | none same-loop: 1.2→1.1 crossing |
| 9 | `#11529 'x'` (Less?, 1.1) | `#10150 'x+1'` / `#9907 'Value'` via `#10445` tunnel 11336 | A → 1.1 | QRT (PD182(c)) | none same-loop: 1.2→1.1 crossing |

## 2. The group-A remainder = ONE executable row

Row 7 is the edge PD180(c)/181(c) ordered ("`#10757 'element'` → `#23541` wired (179(b) reader) … keeps w23556's source
and name"), which L2-A1 did not make: the simulator bared w23556 at `#23541` in the joint move
(`tools/bench/sim_l2a1_81b.log:7`, `(23556, 23541)`) and left `#10757`'s out-row AMBIGUOUS because its S1 partner is the
selector tunnel `#10978`, not `#23541` (`:20`, `pd182c_qrt false`). The bed's CT read shows `#23541` with no partner
(`stage_d1_l2a1_86-5.log:671`). Both ends sit in 1.2's body `#23166` (`sim/l2a1/step_46_wire.json`; the live read
confirms). On D1_k — where w23556 existed — `cdiff_frame(S1, D1_k)` has NO `#9703` row (178(c)'s 10 rows; offline replay
of this card's cdiff code on `graph_k_80_owners.json`), so the re-make is predicted to close row 7 through the S3a
carrier (indicator `#23541` → Local `#23523`, loop 1.5 `#23032`, `tools/bench/ct23541_facts_80.log:3-9`), the same carrier
S3 was accepted with. MEASURED on the bed (`tools/bench/diag_c107b_bedgraph.log:250,263`): `#10757` and `#23541` are owned by
`Diagram #23166` (1.2 body), `#10874 'element'` and `#23541` both `wire_uid 0`. Simulated: `tools/bench/plan_l2a2_sim.log:3-4`
(FINAL, end cdiff 8 rows == §4's PB). Prior-art `archive/peer/2026-09-27-priorart-c107b-l2a2.md` = novel.
⚠️ PD183(c) classed row 7 as "QRT-owed, a 1.2→1.1 crossing". The measured topology is a SAME-LOOP edge in 1.2 plus the
existing Local carrier to 1.5. Proceeding under 180(c)/181(c); the contradiction is returned as OPEN.
Rows 8 and 9 have no same-loop re-make (rule 1a: the S1 edge crosses 1.2→1.1); they stay open → QRT (PD182(c)).

## 3. Sub-steps and saved files

| step | what | saved file | pass criterion |
|---|---|---|---|
| 0 (card 107-2, read only) | byte copy of the bed → read_live + mloops + owner walk; cdiff(S1, bed) | `tools/bench/graph_l2a1_bed_<date>.json` | 9 rows == §1; `#23541` partners []; bed md5 unchanged; scratch deleted; LabVIEW gone |
| 1 (card 107-2, offline) | stageplan `plan_l2a2` = 1 `wire` action (src `#10757` t10874 → dst ControlTerminal `#23541`), `open_rows` = rows 1–6, 8, 9; stagesim finalize | `tools/bench/plan_l2a2.json` | FINAL; end cdiff == the 8 open rows; X9 pass; X10 printed |
| 2 (card 107-2, offline) | recipe `tools/recipes/stage_d1_l2a2.py` (≤ 120 lines, rows only from the plan); TOP-LEVEL `stage_prerun --dry` and `--prerun` | records in `tools/bench/prerun_records.jsonl` | dry PASS, pre-run PASS |
| 3 (judgement's next card — NOT launched here) | fresh LabVIEW, copy of the bed, the 1 op, gates below, gui_save (rule 6) | `claudeDev\D1_l2_a2_<ts>.vi` | §4 |

## 4. §3 criteria of the stage run (predicted)

| gate | predicted | determined earlier? |
|---|---|---|
| input md5 / pins | `51d9b8a3…`, unchanged | hygiene |
| E1 each checkpoint read == simulated step | diff 0 (1 op) | no — gate |
| CT 179(b) reader on `#23541` | partners real == sim == [`#10874`] | no — gate (sink_gates entry, PD183(d) pattern) |
| PB frame-keyed cdiff(S1, end) (FATAL, before save) | == the 8 open rows (rows 1–6, 8, 9) | no — gate |
| diff(bed, new) | +1 wire `#10874`→`#23541`, no node added/removed, no other edge changed | op semantics — gate on the row list |
| FU frame-uid sets of `#5540`/`#10445` | [5582, 5592, 10453, 10459] equal | 181(b) — gate |
| ExecState | 0 (rows 1, 2, 4, 8, 9 open) | by design — NOT a gate; gui_save (CLAUDE.md §3 rule 6), never run |
| RBW on a scratch of the saved file | deletes no wire of the re-made sink | gate |
| LabVIEW gone at exit | true | hygiene |
