---
type: facts
status: current
date: 2026-10-03
---
# Card 143-2 — the 2 extra Error List items of P4 session 2's scratch file (MEASURED, read-only)

File: `claudeDev\D1_ring_p4s02_20261003_110001.vi`, md5 84cac48781c7c915c8f0d7e8fb079341 (unchanged after the read,
`tools/bench/diag_c143_1_graph.log:304`). Not adopted, not edited, not saved.

## Step 1 — fresh-instance load + graph read
- Run: `tools/bench/diag_c143_1_graph.py` (prepared by 143-1), dry/prerun PASS with `--graph graph_ring_p4s01_20261002_234419.json`
  as stand-in (precedent `diag_c141_3_graph_dry.log:12`), `diag_c143_1_graph_dry.log`, `diag_c143_1_graph_prerun.log` (15/0).
- Gates 15 pass / 0 fail, `BGRUN END rc=0 after 173s` (`diag_c143_1_graph.log:324-328`). E5 PASS: the 6 made objects, 4 deleted
  nodes, 5 deleted wires and 4 new wires of session 2 are all in the file (`:295`).
- Memory: 596.0 MB after load, 607.6 MB after the full read and FS reads (`:24,271,296`).
- Handles: 45,625 after load -> 45,899 after the reads (+274, within one script) (`:24,296`). LabVIEW gone at exit (`:327`).
- Graph: `tools/bench/graph_ring_p4s02_20261003_112505.json` md5 eda9db4088d1be89623e6333268e09ff — 5,964 rows, 10,395
  objects, 24 loops, 22 FS (`:297`). (Name carries the read time, not the file stamp `_110001`.)

## Step 2 — offline lists (`tools/bench/diag_c143_2_offline.py`, `diag_c143_2_offline.log`, `diag_c143_2_offline.json`)
Representation (measured): a WhileLoop owns NO terminal row; its conditional terminal is the `''` SINK row owned by its body
Diagram. The six While bodies (graph `owners`): 639->#637, 15266->#15173, 23058->#23032, 23166->#10170, 23405->#23041,
25392->#25380.
- (a) While loops whose conditional terminal has no wire: **ONE — While #10170, body #23166, cond terminal #23246, wire 0**.
  The other five are wired (648<-w3457, 15276<-w19456, 23080<-w23145, 23456<-w23489, 25410<-w1737). In s01 #23246 was wired
  by w23310 (`diag_c143_2_offline.log`, s01 (c) rows).
- (b) Locals with an unwired terminal: **ONE — Local #6902, terminal #23310 'StopAll', is_source true (READ), on body #23166,
  wire 0**. s01: none (23 Locals, all wired). #6899 (StopAll WRITE, on #639) is wired (w6929).
  Note: #6902's terminal uid 23310 equals the deleted scaffold wire's uid 23310 (uid reuse after delete).
- (c) #23166's `''` terminals: #23225 (source, the loop's `i`) wire 0 in s01, s02 and sim alike; #23246 (sink = cond) wire 0
  in s02 (was w23310 in s01).
- (d) unwired in s02 but wired in s01, key (term_uid, owner_uid, name): **2** —
  #23246 on #23166 (s01 w23310) and LoopTunnel #23417 inner #23435 '' source (s01 w23255). Both wires are PLANNED cuts of
  s02v18: `p4_dw_23310` (`plan_ring_p4_s02v18.json:325-327`, scaffold stop #10171 -> #10170 cond) and `p4_dw_23255`
  (`:331-333`, tunnel #23417 inner -> #10171 x,y; PD321(b)).

## Step 3 — against the s02v18 simulated end and s03's first action
| item | open in s02 real | open in sim end (`sim/ring_p4_s03v18_s02end/base_provisional.json`) | wired by s03's FIRST action |
|---|---|---|---|
| While #10170 cond #23246 (EL "Conditional terminal is not wired") | yes | yes (wire 0) | yes — `p4_w_stop12` dst #10170 'cond' (`plan_ring_p4_s03v18.json:77-84`) |
| Local #6902 'StopAll' read (EL "Local Variable ... not connected") | yes | yes (as #-20, term #-21, wire 0) | yes — `p4_w_stop12` src -20 (= #6902, bound `diag_c143_1_scratch.log:382`) |
| LoopTunnel #23417 inner #23435 | yes | yes (wire 0) | no (an unwired source; not in the EL extra list) |

- s03's first action names the Local's terminal `"value"` (`plan_ring_p4_s03v18.json:80`); the measured terminal name in both
  the real graph and the sim end is `'StopAll'` (s02v18 plan `:411` creates it as `StopAll`). Not tested here.
- Error List extra items (`errorlist_D1_ring_p4s02_20261003_110001_20261003_110836.json:5638-5642`): exactly these two, `missing` [].

## Step 4 — failed-prediction review
Card `tools/bench/cards/review_c143-2-el53.json`; `peer.ps1 -Agent claude -Role hypothesis`, `tools/bench/peer_c143-2-el53.log`
(BGRUN END rc=0 after 179s), archive `archive/peer/2026-10-03-c143-2-el53.md` (ANSWERED 177 s), verdict
`tools/bench/cards/verdict_c143-2-el53.json` = **supported**. Reviewer's alternative: the VI is in the plan's state and the
failed prediction is a PREDICTOR bug — `unwired_in()` counts sink terminals only (a Local READ has one source terminal, never
counted) and the cut While cond went only into `alternative_total` 52 (`plan_ring_p4_s02v18_pred.json:115-131`,
`prep_c142_5_pred.py:65-87`); same defect in `prep_c143_p1_pred.py:44-89` (`gone_unw` not subtracted). 'value' vs 'StopAll':
no risk, documented alias (`tools/stagesim.py:735-736`). Discriminating test proposed (offline): recompute the s02 EL prediction
counting source-only Locals and newly unwired While conds -> expect 53. NOT run here (judgement's call).
Also covers `diag_c143_2_offline.log` run 1 gate H-a FAIL (Jev ladder `new-problem p=0.810`, review owed): the script looked
for cond rows owned by the WhileLoop; fixed (owner = body Diagram) in `diag_c143_2_offline.py`; run 2
`diag_c143_2_offline2.log` 4 pass / 0 fail.
