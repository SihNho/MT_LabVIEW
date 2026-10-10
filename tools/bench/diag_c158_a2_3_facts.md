---
type: facts
status: current
date: 2026-10-10
card: 158-a2-3
---
# Card 158-a2-3 facts: offline PB-keying test + pair-keyed D/TD recount on the c158-a2-2 scratch (no LabVIEW, no edits)
Script `diag_c158_a2_3_measure.py` (calls stagekit / vigraph / stagesim, nothing copied) -> `diag_c158_a2_3_measure.log` run 3 (:120-223, BGRUN END rc=0), json `diag_c158_a2_3_measure.json`; runs 1-2 (:1-119) and `_probe.log` = my script build errors.
## Inputs verified
- Bindings from `diag_c156_p5s02a_scratch.log`: :442 `bound {-28: 31308, -29: 31506, -30: 31517, -31: 31485}`; :540 `{-44: 31546}`; :548 `{-49: 31557}` (== the brief's).
- Real end = json `real_end_rows` (5 columns); term_class / frame from the sim row of the same term uid, else same bound owner + name/direction:
  6113 same uid, 23 by name, 7 by order, 0 unmatched (log :123) [ASSUMPTION AL]. Check: it reproduces the logged PB extra (:158) and D 21/22, lost 12, TD unwired (:163).
## 1 Section-4 test (PB)
- S1 sources, untagged: cal cluster path <- 3391 'string', file size <- 1766 '32bit integer' (:130-131).
- Sim end: same sources tagged `@-44/f1`, `@-49/f1` (:134-135); frame -29 (CQ7.f0) gets ordinal 1, -30 ordinal 0 (:126).
- Sim + real uids (brief's 4 bindings, and all 12): `@31546/f0`, `@31557/f0` (:138-139, :142-143); 31506 -> ordinal 0 (:127-128). TAG FLIP: yes (f1 -> f0).
- Real end: `3391..@31546/f0`, `1766..@31557/f0` (:146-147) == sim+real-uids. Same source terminals as S1 on all four graphs.
- PB rows appear: YES on all four, INCLUDING the unmodified sim end: pb_check(S1, sim end, sim end) extra = 376 'cal cluster path', 'file size' (:154-157).
  Frame-keyed cdiff(S1, G) lists both #376 rows on sim / sim+M4 / sim+BOUND / real (:150-153): the tag itself (vs S1's untagged source) is the row.
- Merged-mode cdiff (`build4` without frame_keyed, the simulator's mode: stagesim.py:2665-2667 -> jev_candidates.py:90; S1 = stagesim.load_s1):
  sim end 29 rows == pred's 29 exactly; real end 29 rows == pred's 29 exactly; #376 rows there = current frame data array in, error in, frame index,
  selected path, total data array in (:159-160). PB builds both graphs frame-keyed (stagekit.py:1796, :1803, :2050; cdiff stagekit.py:1816).
- So the ordinal reversal the review named (vigraph.py:322) is real but does not decide PB; the review's s4 falsifier (rows absent after binding) did not occur either.
## 2 Pair-keyed D / TD (stagekit.wire_ends_pos position keys, sim owners mapped by the 12 bindings)
- (source, sink) pairs: base 2400, sim 2400, real 2400; new vs base sim 12 / real 12; lost sim 12 / real 12 (:164-170).
- One-sided full pairs: 2 per side, all on the CREATED shift register 31347 (index 0/1 of InnerTerminal/OuterTerminal swapped, sim vs real) (:171-172).
- Half wires (one end only): sim 11, real 10; only-sim = source-only (25223, 1, InnerTerminal) = wire 24091's kept source end (:173-177).
- TD row: node 25223 idx 1 wire 24091 in base and sim, 0 in real (:178-180) -> the TD 'unwired' entry is this end.
- D by wire: sim new 22 = real 21 + the 24091 source-only half wire; lost 12 == 12 both. Reconciled: yes, only by 24091 (sim keeps it, LabVIEW deleted it).
## 3 CEN2
- Declared (`plan_ring_p5s02a_pred.json:15-22`): CaseStructure 1, Diagram 2, Tunnel 1, OuterTerminal 1, InnerTerminal 2, Wire 1 = the Case op only;
  :23 `census_overall: UNPREDICTED`; :24-47 lists the other 22 action ids as unpredicted.
- Measured whole run (scratch log :553, classes kept to the pred's: stagekit.py:1926, :1949-1951): InnerTerminal 10, Wire 12, OuterTerminal 6, Diagram 2,
  CaseStructure 1, Tunnel 1; all classes :554-555 (SelectorTunnel 3, ParameterTerminal 13, Function 2, ...).
- FAIL line: stagekit.py:333 (`self.gate(label, not diff, ...)` in census_gate), called by gate_cen2 stagekit.py:2030. The UNPREDICTED (no-gate) branch
  stagekit.py:311-322 runs only for an EMPTY declared set; census_gate never reads `census_overall`. Declared side covers the Case op only: yes.
- Earlier ring cards wrote the scratch's measured census into the pred (`census_overall: MEASURED-SCRATCH`, e.g. tools/bench/diag_c148_a2_4_census.py:52).
## 4 FATE (wires into #376, base -> end; log :183-221)
- base: 24330 24360->5760 cal cluster path; 24153 24367->5778 file size; 24091 25235->5787 selected path; 24285 24190->5683 error in; 24312 24288->5782 total data array in.
- sim end: 5760 <- -48 from tunnel -44 (24330 kept as 24360 -> -45); 5778 <- -53 from -49 (24153 kept as 24367 -> -50); 24091 / 24285 / 24312 source-only; 5787 / 5683 / 5782 unwired.
- real end: 5760 <- 31346 from tunnel 31546 (24360 -> 31559 by NEW wire 31562); 5778 <- 31537 from 31557 (24367 -> 31577 by NEW 31587);
  24091 gone (25235 unwired); 24285 / 24312 source-only; 5787 / 5683 / 5782 unwired. Same topology as sim except 24091 and the wire uids.
OPEN: PB (frame-keyed) and the pred's cdiff rows (merged, stagesim) disagree on this plan by the two tagged #376 rows; which mode is the contract for a move into a new 2-frame case?
OPEN: D/TD differ from the sim only by the 24091 source-only end (sim keeps it, LabVIEW deletes it) - a simulator model gap or an accepted difference?
OPEN: CEN2 declared census covers the Case op only (pred census UNPREDICTED); is this scratch's measured census (log :553-555) to become the pred's?
