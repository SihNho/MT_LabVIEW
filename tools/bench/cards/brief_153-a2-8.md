---
card: 153-a2-8
status: current
date: 2026-10-09
---
# Brief 153-a2-8 - RETRY of 153-a2-2 (OpQueue*_v0 20-call handle hygiene); LabVIEW, alone, docs/d1/ring-p4d.md PD371(d) + PD372(e)

Why a retry: card 153-a2-2 FAILed gate D before any op was called. `find_donor` (tools/bench/diag_c153_a2_2_queue_hygiene.py:56-67) returned None
on a byte copy of the NI For Loop scripting example (`diag_c153_a2_2_queue_hygiene.log:6-9`). Everything else held: LabVIEW restarted and closed,
pins unchanged, op VI md5s unchanged (Obtain 095afd7e, Enqueue 88bfad7c, Dequeue a3571dec, Release 9ac89912). This is the card's own script, not an op fault.

## What to do (this brief states the MEASUREMENT; the action follows from what the machine returns)
1. READ FIRST, do not guess a third time: in a scratch LabVIEW session (one short diagnostic, labview build, bgrun --max-min 15) on a fresh byte copy of the
   example, print `g.count(W,"Diagram")`, `len(g.report_all(W,"Function"))`, and for diagram 0..3 the first 60 `g.node_terms_uid(W, d, k)` results
   (uid, class, terminal names + is_source). Quote them. This tells which of the three assumptions in `find_donor` failed (no Function-class rows /
   node index range / source flag). Also look at how `gscript.queue_node` (tools/gscript.py:1480) and `tools/recipes/build_d1_routeb_v*.py` obtain their
   donor Function, and reuse THAT, not a new kind of search.
2. Fix `find_donor` in YOUR script only (`tools/bench/diag_c153_a2_8_queue_hygiene.py`, a copy of the a2-2 script, plain gscript shape as there; no
   stagekit form: it is refused as a stage, gate-fp fp-73). Keep total=20, per_round=5, recycle=True (4 never-saved byte copies per op; accepted: one round
   would make max_dev_closed 0 by construction).
3. Run the 4 ops via `gscript.hygiene_run` in ONE script, ONE bgrun (--max-min 40). h_pre/h_post/h_closed quoted per op, flat within +-100, 0 errors;
   one record per op written by hygiene_run to `tools/bench/op_hygiene/OpQueue{Obtain,Enqueue,Dequeue,Release}_v0.json`, md5 quoted.
4. Cleanup: delete the 4 EMPTY dirs `claudeDev\scratch_c153_a2_2_20261009_0746{25,36,44,45}_hyg` left by the first card (PowerShell Remove-Item on exactly
   those four empty dirs; they are scratch artefacts of card 153-a2-2 and inside the write glob), the new scratch VI and its _hyg dir; then `tasklist`
   shows no LabVIEW. Handle count read before and after.

## Invariants (md5 before/after)
s09 VI eb1d0f31, stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun c739eb86, stagesim 78b8d5a1, vigraph 13be0847,
the 4 op VIs. No op VI edited or saved, no bed opened, no VI run. No tools/hooks edit. No motor or camera. Never beside a card that writes tools/vigraph.py.

## Return (<= 30 lines)
The step-1 readout (counts), the donor chosen and why, per-op hygiene numbers + record md5s, cleanup proof (dirs gone, tasklist), md5 table, `OPEN:` for
anything needing judgement. Failure budget 2; STOP at the first drift or error after finishing that op with LabVIEW closed.
