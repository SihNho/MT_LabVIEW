---
card: 154-a2-1
status: current
date: 2026-10-09
---
# Brief 154-a2-1 - build `claudeDev\DonorQueue_v0.vi` BY SCRIPT and record its uids (docs/d1/ring-p5.md PD375(a)); LabVIEW, alone

Why: round 1 (`tools/bench/diag_c154_a1_1_facts.md`) found no queue donor, so the `primitive` route (`gscript.create_primitive_nested`, `gscript.py:4790`) cannot place Obtain / Enqueue / Dequeue / Release. This card builds the donor. Nothing else.

## Facts this card starts from (do not re-measure)
- The four ops `claudeDev\OpQueueObtain_v0.vi`, `OpQueueEnqueue_v0.vi`, `OpQueueDequeue_v0.vi`, `OpQueueRelease_v0.vi` passed 20-call hygiene in cycle 153; `gscript.queue_node(kind, container, cls, src_index, src_name, ...)` drives them (`gscript.py:1480`). Working call form and a donor-node pick: `tools/bench/diag_c153_a2_8_queue_hygiene.py` (`find_donor`, `workload`, `one()`).
- Earlier donors (`DonorRAS1D_v0`, `DonorRingConst_v0`, `DonorBoolF_v0`, `DonorSRInit_v0`) are claudeDev VIs built by script, each holding the nodes the `primitive` route copies; their builders and the way their uid was recorded: `tools/bench/prep_c141_1_mkv16.py:37,118` and the `diag_c139_*` / `diag_c140_*` scripts that cite them. Copy that build and recording form; do not invent a new one. Use `tools/stagekit.py` helpers (<= 120 lines new file).
- Obtain needs its 'element data type' input typed. In the donor the element type comes from ONE 1-D DBL array constant in the same VI, wired to Obtain's 'element data type' so the queue is DBL 1-D. The donor must contain: Obtain Queue, Enqueue Element, Dequeue Element, Release Queue, and that 1-D DBL constant (empty array of DBL, uid recorded).

## What to do
1. Make a fresh scratch VI (never an original, never saved over anything); put the five objects on its block diagram by script (queue nodes through `gscript.queue_node` with the donor-node pick from the hygiene script, or by the route the earlier Donor builders use - whichever those builders actually use). Wire only what the donor needs: the DBL 1-D constant to Obtain's 'element data type'. Wiring Obtain -> Enqueue -> Dequeue -> Release is optional; if you wire them say so, but the donor's purpose is that each node can be copied UNWIRED by `create_primitive_nested`.
2. Read back, by script, for EACH of the five objects: uid, Traverse class, label, and every terminal NAME with its index and source/sink flag (the same reader the earlier donors' json used). Write `tools/bench/donor_queue_v0.json` (schema like the other donor records; if none exists, keys: `file`, `md5`, `objects` -> `{role, uid, class, label, terminals:[{index,name,is_source}]}`).
3. Save as `claudeDev\DonorQueue_v0.vi` (autonomous save under claudeDev is allowed; COM `SaveInstrument` on a NON-broken VI). Record md5 of the file in the json. If the VI is broken because the queue nodes are unwired, report ExecState and the Error List read; a donor VI is allowed to be broken only if saving works (if it hangs, STOP with the facts - do not use the GUI save).
4. Reference hygiene (CLAUDE.md section 3): LabVIEW handle count read before and after the build; growth must be within +-100. Close every reference you opened. Close the scratch/donor VI WITHOUT a second save.
5. Cold check: open `DonorQueue_v0.vi` read-only in a FRESH LabVIEW instance (or after a restart) and re-read the five uids; they must equal the json. Then close it.
6. LabVIEW gone at the end: `tasklist | grep -i labview` empty (restart authority stands).
7. Invariants: md5 before = after for `D1_ring_p4s09_20261009_060515.vi` (eb1d0f31), `stagekit.py` 604529e8, `stagexec.py` 1bab9cf9, `stagesim.py` 78b8d5a1, `gscript.py` 1a80236e, `stage_prerun.py` c739eb86, `vigraph.py` a7eb58c7, `addrcheck.py` 207beb0d, `memory_model.json` 6f2b5687, the four `OpQueue*_v0.vi`, every existing `Donor*_v0.vi`. No `tools/hooks/**` edit, no originals opened.

## Run
`py tools/bgrun.py --material --max-min 40 --log tools/bench/diag_c154_a2_1_donor.log -- py -u tools/bench/diag_c154_a2_1_donor.py` (a stage/diagnostic file <= 120 lines on stagekit; header `# labview: build`, `# hardware: none`).

## Return conditions
A queue op that cannot be called (error), a save that hangs or fails, handle growth beyond +-100, a cold re-read whose uids differ, a protected md5 moved, a second failure at the same place.

## Report `tools/bench/diag_c154_a2_1_facts.md` (<= 30 lines)
Build route used (file:line), the five objects (role, uid, class, terminals), json path + md5 of the donor VI, handle counts before/after, cold-read result, invariants, LabVIEW gone. `OPEN:` line. Facts only.
