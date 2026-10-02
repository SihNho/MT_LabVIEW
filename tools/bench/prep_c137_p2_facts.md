# Card 137-P2 facts (offline, 2026-10-02; no tools/*.py edited, no LabVIEW). Inputs: plan v3 d14c1bba, graph p3b2b 50595c62
## 1. v4 = v3 with the 5 ControlTerminal ends re-addressed by their own uid
- Output `tools/bench/plan_ring_p4_v4.json` md5 **a30f7700dcc2e89293c28f89131d0070**, written by scratch `mk_v4.py` (json.dump
  indent=1, same as stagesim's writer `tools/stagesim.py:2409-2410`, so v3 line numbers still hold). Log `tools/bench/prep_c137_p2_mkv4.log`.
- New form `{"uid": <ct>, "term_uid": <ct>}` = node_of convention (`tools/vigraph.py:57-60`, `tools/stagesim.py:122-123`) and
  the executor's CT route (`tools/stagexec.py:1493-1496`).
- Full key-level json diff v3 -> v4 (`prep_c137_p2_mkv4.log:10-15`): exactly 5 changed keys, nothing else (stage, goal,
  base, finalized untouched; `stage` stays `ring_p4_v3`):
| step | action id (v3 line) | key | v3 | v4 |
|---|---|---|---|---|
| 102 | p4_x_fd (`plan_ring_p4_v3.json:1465`) | /actions[101]/src/uid | 686 | 8936 |
| 104 | p4_x_dt (`:1484`) | /actions[103]/src/uid | 686 | 28844 |
| 115 | p4_rbA_re1 (`:1619`) | /actions[114]/dst/uid | 23166 | 3173 |
| 116 | p4_rbA_re2 (`:1632`) | /actions[115]/dst/uid | 23166 | 9519 |
| 143 | p4_rbD_sel_t25573 (`:1984`) | /actions[142]/dst/uid | 23166 | 25573 |
- Graph rows of the 5 (`prep_c137_p2_mkv4.log:4-8`): t8936 '# FD points' CT src, owner Diagram 686, wire 9000; t28844 '# DT points'
  CT src, 686, wire 29006; t3173 'Pos within cal image' CT sink, 23166, wire 23807; t9519 'Pos: Diffraction Pattern' CT sink,
  23166, wire 23807; t25573 'autofocus reset count (1.2 to 1.1)' CT sink, 23166, wire 25386. All `owner_class` Diagram.
- No other plan end of the owner form (Diagram uid + CT term_uid) remains in v4 (`prep_c137_p2_mkv4.log:9`, "[]").

## 2. stagesim replay of v4 on graph_ring_p3b2b_20261002_133824.json (`tools/bench/prep_c137_p2_sim.log`)
- Command: `py -u tools/stagesim.py simulate tools/bench/plan_ring_p4_v4.json <graph> --out-root tools/bench/sim/ring_p4_v4
  --plan-out tools/bench/sim/ring_p4_v4`; `BGRUN END rc=1 after 122s` (`:108`). Because `stage` is unchanged the step files
  are under `tools/bench/sim/ring_p4_v4/ring_p4_v3/` and the re-written plan is `tools/bench/sim/ring_p4_v4/plan_ring_p4_v3.json`
  md5 a50460d5b8eeb8697035c920405261ce (`:107`); v3 and v4 in tools/bench were not overwritten.
- BASE-FLIPS 6 on [9503, 10177, 29777] (`:3`), steps 1-101 ok, cdiff 16 to step 97, 18 at 98, 20 at 99-101 (`:100-104`) -
  identical to the v3 replay (`tools/bench/prep_c136_p2_p4v3.md:21-22`).
- **Last step reached: 102. Stop: step 102 `wire` id `p4_x_fd`** (`prep_c137_p2_sim.log:105-106`): "wire {'uid': 8936,
  'term_uid': 8936} -> {'uid': 10068, 'term': 'y'}: source on diagram 686, sink on diagram 23166 - a border needs a
  tunnel/register action first". Raised at `tools/stagesim.py:1366-1368` in `op_wire`. final=False, end_cdiff_rows=None,
  candidates 18 (`:106`).
- So the address now resolves: the old stop was `resolve_addr` `tools/stagesim.py:680-681` "#686 owns no terminal"
  (`prep_c136_p2_p4v3.md:23`); `op_wire` passes both `resolve_addr` calls (`:1341`, `:1360`) and stops at the diagram check.

## 3. Is the new stop the SAME class (an address form the simulator rejects)? No.
- It is a border-crossing refusal: `op_wire` models a cross-diagram wire only across two frames of a plan-made Flat Sequence
  (`tools/stagesim.py:1362-1363`) or from outside INTO a plan-made FS frame (`:1364-1365`); any other cross-diagram wire under
  the connect_from_wire model (`same_diagram` true) is refused (`:1366-1368`). Here 686 -> 23166 crosses the base While #10170
  border (plan `why`, `plan_ring_p4_v3.json:1474`: "connect_term_uid ... across While #10170 border").
- Same class was already recorded for P3b: "no stagesim model for a border-crossing connect: opmodels connect_from_wire
  same_diagram true" (`tools/bench/plan_ring_p3b_make.py:18-19`).
- The v3 meta lists this route class as UNMEASURED "connect_term_uid @ base While #10170 body 23166", 3 actions: p4_x_fd,
  p4_x_dt, p4_x_n2_out (`tools/bench/plan_ring_p4_v3_meta.json:815-821`). Inference, not replayed: step 104 p4_x_dt (686 CT ->
  #29240 'y', `plan_ring_p4_v3.json:1484-1493`) has the same shape and would stop on the same line.
- Per the card, nothing was fixed; no list of address-form uses is owed (class differs). Steps 104/115/116/143 not reached.

OPEN: the next stop is a missing simulator model (connect_term_uid across a base While border, `stagesim.py:1366`), not a plan
address - model it in stagesim (tool edit, outside this card) or route these crossings differently in the plan?
