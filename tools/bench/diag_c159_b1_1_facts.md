---
type: facts
status: current
date: 2026-10-10
card: 159-b1-1
---
# 159-b1-1 facts (offline, no LabVIEW): expected Error List of 94ffff94, CEN2 wire, failed copy deleted
Script `tools/bench/diag_c159_b1_1.py`; logs `diag_c159_b1_1_pre.log` (key bug: names of created terminals compared, fixed),
`_pre2.log`, `diag_c159_b1_1.log` (the --delete run), `_final.log` (RESULT FAIL 10/1, first_fail C3). Data `diag_c159_b1_1_raw.json`.
## 1. Expected Error List (`errorlist_expected_D1_ring_p5s02a_20261010_023239.json` 1fd016bf)
- 56 rows, one per observed item, same entry form as the P5-1 file (norm_all/count 1/label/cite + item/class/object/pairing/clears_by).
- errorlist_check.compare(56 observed items, the file): extra 0, missing 0 (gate E3).
- By clears_by: standing 45, action 10, delete_wire 1, unattributed 0.
- By class: notconnected 23, looseends 23, nosource 5, undirected 2, whilesubvi 1, unwiredinput 1, twotypes 1.
- By action: delete_wire 10394 s2 1; A28 w_gl s2 1; A35 w_hl s2 1; A32 w_gr s2 1; A39 w_hr s2 1; A70 w_k3f s3 3; A80 w_k4f s3 3.
- **Predicted totals: after step 2 = 51, after step 3 = 45** (removal of base items only; MERGE assumed per PD388(c) on A28/A35/A32/A39
  and on A70/A80 onto stub-carrying 8776/24342; items NEW from step-2/3 actions are not predicted by this file).
- Standing rows: 22 termless wires termless in P5-1 too; 2 source-only 10103/12256; 19 inherited loose-ends items with no 1:1 graph
  object; Build Array #2626; two-types (object unidentified). No A24..A80 action names any of their uids/terminal uids (stagesim._ints).
- Class sets of >1 item are paired with objects BY COUNT (no uid route); per-class counts are exact, item<->object is not readable.
## 2. CEN2 (`diag_c159_cen2_wire.md`)
- NOT w10394. Sim new Wire 11 (regenerated end == stored step_23 b1892ad9), real new Wire uids 12. Census-scope differences 3, all uid
  identity: real-only 31587 (24367 -> SelectorTunnel #31557, frame 23405, A22) and 31562 (24360 -> #31546, A19); sim-only -37 (5704 ->
  3453, A14). 24330 is a uid swap (net 0); the +1 = LabVIEW deleted 24153 and made 31587, the sim kept 24153.
- Topology: termed wires real-only 0, sim-only 1 (sim keeps a source-only stub 24091 on 25235; LabVIEW removed it); termless 10394
  real-only but not a new uid.
## 3. Deletions (`diag_c159_b1_1.log:28-29`)
- `claudeDev\D1_ring_p5s02a_20261009_152721.vi` md5 cac5236b171aab9d82283d7dff9611ef verified, deleted.
- Resume record `tools/bench/resume/resume_plan_ring_p5s02a_20261009_153334.json` (its `file` = the 152721 path) deleted. Nothing else.
  `tools/bench/creation_map/plan_ring_p5s02a_4284c22a_20261009_152941.jsonl` also names 152721; kept (not a resume record).
## Pins before == after
- 023239 94ffff9413599d51..., s09 eb1d0f3107bbba49..., P5-1a 2482fe7bf3426e18..., P5-1 7f2582ae54dc5bc4... (V0, V1).
- stagesim eb99c6ba, stagekit 9cd8822e, vigraph a7eb58c7, addrcheck 207beb0d, plan_ring_p5s02a 4284c22a unchanged; no tools/hooks edit.
OPEN: CEN2 is a uid-identity difference (LabVIEW re-creates the A22 wire, the sim re-uses 24153) - not the remnant; PD388(b) says hand back.
OPEN: whether the sim's kept stub 24091 on 25235 (LabVIEW removes it) should be modelled is a stagesim question for judgement.
