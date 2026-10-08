---
card: 153-a2-2
status: current
date: 2026-10-09
---
# Brief 153-a2-2 - 20-run handle hygiene of the 4 OpQueue*_v0 ops (docs/d1/ring-p4d.md PD371(d))

Read `docs/d1/ring-p4d.md` PD371(d) (line 190), `gscript.hygiene_run` (`tools/gscript.py:366`, docstring: workload(copy) = ONE op call on an open copy,
returns ''/None when good; `total`, `per_round`, `recycle`, `record_path`), and the closest prior hygiene run for a similar op
(`tools/recipes/build_opwiringrules_v0.py`-style or `tools/bench/op_hygiene/OpFsAddFrame_v0.json` and the recipe that produced it; reuse its shape,
do not invent a new harness). CLAUDE.md "Reference hygiene" rule 2: a new op is accepted only if 20 runs leave the handle count flat (+-100).

Ops (all under `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\`): `OpQueueObtain_v0.vi`, `OpQueueEnqueue_v0.vi`,
`OpQueueDequeue_v0.vi`, `OpQueueRelease_v0.vi`. Their call signature and how stagexec/`build_opqueue.py` (`tools/recipes/build_opqueue.py`) drives them are in
`tools/stagexec.py` (grep OpQueue) and `tools/bench/diag_queue_donor2.py`; read those, not NAMES.md (it has no entry).

## What to do
1. `py tools/protocol.py requires` is already satisfied by existing files; confirm each op VI exists and quote md5.
2. ONE script (<= 120 lines on `tools/stagekit.py`, `tools/bench/diag_c153_a2_2_queue_hygiene.py`), run ONCE under bgrun (`--max-min 40`): make ONE fresh
   scratch VI under claudeDev (unique name `scratch_c153_a2_2_<stamp>.vi`, a byte copy of a small bed or a new empty VI - whichever the prior hygiene records
   used), and for EACH of the 4 ops call `gscript.hygiene_run(op_path, workload, source, total=20, per_round=20, recycle=False or True as in the prior
   record, record_path="tools/bench/op_hygiene/<OpName>.json", card="153-a2-2")`. The workload is the op's real use on that scratch VI (Obtain: obtain
   a queue with an element type constant; Enqueue/Dequeue: on a queue made in the same copy; Release: release it) - the SAME operation the build recipes
   use. Quote handles before/after per op (h_pre, h_post, h_closed) and the verdict; the band is +-100.
3. Afterwards: scratch VI deleted, no `scratch_c153_a2_2*` left, LabVIEW verified gone (`tasklist | grep -i labview` empty), handle count read once more.
4. Records exist in `tools/bench/op_hygiene/OpQueueObtain_v0.json`, `...Enqueue_v0.json`, `...Dequeue_v0.json`, `...Release_v0.json`.

## Stop rules
- A fail (handle drift > 100, an op error, an unexpected result): STOP after that op, close LabVIEW, return the facts (`OPEN:`); the judgement session decides.
  Do not edit an op VI to fix it. Failure budget 2 (one retry only for a harness defect of your own script).
- This card must not run beside a card that writes `tools/vigraph.py` or any stage tool; it writes none itself. No bed (`D1_ring_*.vi`) is opened or
  saved; the original is not touched. No tools/hooks edit; no motor or camera.

## Invariants (md5 before/after, quote)
the four op VIs; s09 VI eb1d0f31; stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun c739eb86, stagesim 78b8d5a1.

## Return (<= 30 lines)
Per op: calls, errors, h_pre/h_post/h_closed, verdict, record path + md5; scratch deleted; LabVIEW gone; md5 table. `OPEN:` for anything needing judgement.
