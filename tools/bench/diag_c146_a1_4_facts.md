---
type: facts
status: current
date: 2026-10-08
card: 146-a1-4
---
# Card 146-a1-4 facts: s05 scratch FULL PASS 22/0, Error List 55 != predicted 57 -> RETURN, NOT adopted

## Before
- `diag_c146_a1_4_check.log` 16/0: 12 card inputs md5 == card; s04 95e408ff (318509 B), s03 282301ca, bed 39511877 unchanged; no LabVIEW.
- Scratch recipe dry PASS (`diag_c146_a1_4_scr_dry.log`), prerun 16/0, X10 674.9, X11 PASS (`diag_c146_a1_4_scr_prerun.log:96,114`);
  `--scratch-required` rc 3, census unpredicted (`diag_c146_a1_4_scrreq.log`). No gate refused the launch.

## Scratch (ONE run) `tools/bench/diag_c145_p4s05v18_scratch.log` (BGRUN END rc=0, 401 s; log name fixed by the recipe), md5 5adac5e4
- RESULT 22/0. E1 real == sim at all 17 ops (:284); NG, FR (6 created on #23166, :286), D new 11 == 11 / lost 1 == 1 (:287), TD (:292),
  PB 16 rows / 11 open pairs (:294), HB, PS, H2, H3, H5 (15/15 refs), H6 PASS; PRIM PASS #30119 (:158), #30216 (:219), #30240 (:280).
- METERED start 577.8 MB (k0, :53), op-0 read 583.7 (:54); PEAK 607.7 MB (k17 read, :282); X10 674.9, d -67.2; MEM_STOP 680 / MEMSTOP 695 not hit;
  MEM / MEML / IN / GONE PASS. Handles post-open 45689 -> before-save 46226 (+537), exit 40235.
- Saved work copy `claudeDev\D1_ring_p4s05_20261008_002621.vi` md5 3f9ac26b69179eb53c202d90407ce7ee (319045 B, ExecState 0 by design).
- Census written into the pred from log :290 (`diag_c146_a1_4_census.log` 5/0): {IndexArray 3, InnerTerminal 2, Local 3, LoopTunnel 2,
  OuterTerminal 2, Terminal 12, Wire 11}; lost 1 (w28794). Pred 961f30c4 -> d083ff5f.

## Error List (prediction MISSED) `tools/bench/diag_c146_a1_4_el.log` (rc=1, 765 s, --role final, vs the s04 expected file)
- 55 items == window N 55, 55 double-clicked (:90). Pred 57. Verdict MISMATCH; BY-DESIGN STOP (:89); extra 0, missing 3.
- Missing vs s04 expected (`diag_c146_a1_4_elfacts.log`): entry 0 SubVI 'Image In' not wired (1) matched 0; entry 11 Shift Register x2 matched 0
  (predicted closed). Index Array items 3 (pred implies 4); Local rows 2 (== pred). Every item uid null.
- Read file `errorlist_D1_ring_p4s05_20261008_002621_20261008_003324.json` md5 06a59001. Handles 37238 -> 31282.

## Review (owed by the Jev ladder)
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| diag_c146_a1_4_el.log | new-problem 0.556 | hypothesis review owed (old path) | dispatched `-Role hypothesis` | ANSWERED $1.37, `archive/peer/2026-10-08-c146-a1-4-el55.md` |
- Review: total 55 consistent with the planned end; elrule `session_prediction` calls `predict` without `carry` (`tools/elrule.py:225`), so base
  input items closed by s05 rows (#29843 by p4_t_slot_out + p4_w_pool_in; #5058 'Image In' by p4_w_img_trk) are not subtracted; which IA raises
  the 3 items is unread (uids null). Disposition written; nothing applied (card: no stage-tool edits, return at first miss).

## Not done (return at the first miss): adopt, EL expected file, fresh load, graph read, #2626 table. Scripts ready, unrun:
   diag_c146_a1_4_adopt.py, diag_c146_a1_4_mkgraph.py, diag_c146_a1_4_graph.py, diag_c146_a1_4_t2626.py.
## After: `diag_c146_a1_4_check_after.log` 15/0: inputs (pred rewritten on purpose), s04 95e408ff, s03 282301ca, bed 39511877 unchanged; no LabVIEW.
