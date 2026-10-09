---
card: 154-a2-2
status: current
date: 2026-10-09
retry_of: 154-a2-1
---
# Brief 154-a2-2 - RETRY of 154-a2-1: read back the SAVED `claudeDev\DonorQueue_v0.vi` and write `donor_queue_v0.json` (LabVIEW, alone)

Card 154-a2-1 built and saved the donor (ExecState 1, md5 `81dba822efec5226123b3b88ee4383bc`, `tools/bench/diag_c154_a2_1_facts.md`) and then died on a script bug of its own: `tools/bench/diag_c154_a2_1_donor.py:82` indexed `g.node_labels(DON, 0, strict=False)` rows as `x["uid"]`, but the rows are lists (TypeError). NEXT-ACTION from that card: rerun only the read-back. **Do NOT rebuild and do NOT re-save the donor** - the script's gate S refuses an existing donor, keep it so.

## Judgement already taken (do not re-ask)
- The 1-D DBL constant is `ArrayConstant #52` = DBL[20] 0.0, a copy of `DonorRingConst_v0` uid 101. PD375(a) names exactly that ("from that donor or DonorRingConst_v0 uid 101"); an Obtain typed by a DBL array is DBL 1-D regardless of the length. Accepted as is.
- Obtain / Enqueue / Dequeue / Release being wired from Obtain 'queue out' (as `queue_node` does) is accepted; the `primitive` route copies nodes unwired.

## What to do
1. New file `tools/bench/diag_c154_a2_2_readback.py` (<= 120 lines on stagekit, header `# labview: build`, `# hardware: none`). Copy only the read-back part of `diag_c154_a2_1_donor.py` (open DonorQueue_v0.vi, the five uids from its log lines C1..Q: ArrayConstant #52 (+ element #73), Obtain #108, Enqueue #44, Dequeue #45, Release #46). Open the saved file with the same route the donor script used to reopen a claudeDev VI; do not call SaveInstrument.
   Row handling: read `gscript.node_labels` (and the terminal reader the earlier Donor records use, e.g. `g.node_terms_uid`, rows with `name`, `is_source`) by looking at the actual return shape FIRST and print it once; do not guess the keys.
2. Write `tools/bench/donor_queue_v0.json`: `file`, `md5` (of the VI file), `objects` -> `{role, uid, class, label, terminals:[{index,name,is_source}]}` for the five objects (class = Traverse class as read, `Function` for the four queue nodes per the earlier log, `ArrayConstant` for #52).
3. Handle count: read before and after (bench_prep / the handle reader the hygiene scripts use); within +-100. Close every reference you opened; close the VI WITHOUT saving.
4. Cold check: close LabVIEW (restart authority stands), start a FRESH instance, open DonorQueue_v0.vi read-only, re-read the five uids and compare with the json. Close it.
5. `tasklist | grep -i labview` must be empty at the end.
6. Invariants md5 unchanged: DonorQueue_v0.vi must STILL be `81dba822efec5226123b3b88ee4383bc` after your run (the read-back must not dirty/save it), s09 `eb1d0f31`, stagekit 604529e8, stagexec 1bab9cf9, stagesim 78b8d5a1, gscript 1a80236e, stage_prerun c739eb86, vigraph a7eb58c7, addrcheck 207beb0d, memory_model 6f2b5687, four `OpQueue*_v0.vi`, existing `Donor*_v0.vi`. No `tools/hooks/**` edit, no original opened.

## Run
`py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c154_a2_2_readback.log -- py -u tools/bench/diag_c154_a2_2_readback.py`

## Return conditions
The donor md5 changed; a reopen that fails; handle growth beyond +-100; cold uids differing from the json; a second failure at the same place.

## Report `tools/bench/diag_c154_a2_2_facts.md` (<= 30 lines)
Row shapes seen, the five objects (role, uid, class, terminals), json path + md5, donor md5 before/after, handles before/after, cold-read result, invariants, LabVIEW gone. `OPEN:` line. Facts only.
