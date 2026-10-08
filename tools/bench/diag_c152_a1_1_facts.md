---
type: facts
status: current
date: 2026-10-09
card: 152-a1-1
---
# Card 152-a1-1 facts: FS #29721 owner read = Diagram #23166, echo 29721 (pass items 1-2 met); run FAIL 15/2 on control C + handles H
## Before
- `diag_c152_a1_1_inv_before.log` 23/0 (stagekit 604529e8, addrcheck 207beb0d, stagexec, gscript, stage_prerun, vigraph, stagesim, s08 f99e8414, graph 44858dbf, card inputs); tasklist LabVIEW 0.
- Reader `diag_c152_a1_1_owner.py` d6ad9848 (plan `diag_c152_a1_1_owner_plan.json` 11790178): dry 1/0 (`_dry.log`); prerun 15/0 (`_prerun.log` 2nd segment; 1st segment 10/5 before the plan file existed - X2/X3/X5/X6/X9).
## The ONE read `diag_c152_a1_1_owner.log` RESULT 15/2 (:65), BGRUN END rc=1 after 117 s (:67)
- (a) FS #29721: owner 'Diagram' uid 23166, echo 'FlatSequence'#29721, no error (:25, :29); gate A PASS (:32); strict owner_of agrees (:33).
- (b) frame #29869: owner 'FlatSequenceFrame' uid 0, echo 'Diagram'#29869, error 1055 (:26, :30) == graph owners ['FlatSequenceFrame', 0] (:34).
- (c) control FS #681 (face-derived #536, borders 28377/28809/57284/59090, :4): read 'TopLevelDiagram' uid 536, echo 681 (:27, :31) - uid agrees, CLASS STRING differs; gate C FAIL (:35, gate demanded 'Diagram').
- H handles 45687 -> 45789 (+102) over 4 reads incl. the first op-VI load: FAIL (:36). H5 VI-Server counter opened 4 == closed 4 (:48); exit 33994 (:60).
- MEM after load 598.3 MB (:24). Input md5 unchanged (:37, :51); scratch deleted (:50); files left [] (:59).
- Graph: diagram #23166 is owned by WhileLoop #10170 (graph 44858dbf owners).
## Derived file (read A met PD368(c) as written)
- `tools/bench/graph_ring_p4s08_20261009_033522_fsowner.json` e26b4d90924f79791e52329c43a872ca = graph text + `fs_owner_read` {"29721": ["Diagram", 23166]} + `fs_owner_read_cite` (read_log `diag_c152_a1_1_owner.log:25`, vi/graph md5, echo) (:39 D1 PASS, :43).
- Loads through stagesim.base_state / fs_measured_state / vigraph.reach (:40); base_state fs_unmeasured still [2499, 14682, 29721, 43914] (stagesim not yet extended) (:41).
- Graph 44858dbf unchanged (:42).
## Review `archive/peer/2026-10-09-c152-a1-1-owner-ctl.md` (hypothesis, ANSWERED, $1.45)
- C: class-name miss is a KNOWN class (`diag_c124_opconnecttermuid.log:28,36`; `gscript.py:4864-4867` accepts TopLevelDiagram only for the top-level uid). Control was the weak top-level case; nested-parent control (16543/17398/17710/18024) untested.
- H: 4/4 counter cannot rule out op-internal growth (`gscript.py:463-467`); no op-hygiene/1 record of OpOwnerChain_v1; a warm 20-read hygiene run is owed.
- PD368(c) literal "class Diagram" would demote a top-level FS with faces if faced FSs are cross-checked.
## After `diag_c152_a1_1_inv_after.log` 23/0 (all pins, s08 f99e8414, graph 44858dbf, no scratch_c152_*); tasklist LabVIEW 0.
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| diag_c152_a1_1_owner.log | new-problem 0.798 | hypothesis review owed | dispatched c152-a1-1-owner-ctl, waited, disposed | ANSWERED; C = known class-name class, H unmeasured |
OPEN: accept TopLevelDiagram (top-level uid only) in PD368(c)? warm 20-read OpOwnerChain_v1 hygiene + nested-parent control read before stagesim uses fs_owner_read?
