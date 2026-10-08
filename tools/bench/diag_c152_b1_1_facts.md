---
type: facts
status: current
date: 2026-10-09
card: 152-b1-1
---
# Card 152-b1-1 facts: graph read done; the ONE scratch run FAILED before the crossing (our script: FS placed on the TOP-LEVEL diagram, which `struct_copy_nested` refuses); RETURNED, no retry
## 1. Graph read (pass item 0), graph 44858dbf, `diag_c152_b1_1_graph4.log` (RESULT PASS, rc 0)
- (a) LoopTunnel #30179 owner = WhileLoop: obj row :61; its inner face is on Diagram #29699, owner ['WhileLoop', 16483] :66; WhileLoop #16483 on ['Diagram', 23166] :65,:56.
- (b) Inner face t30183 'min slot' (InnerTerminal, w30197) :53 is fed by **SubVI #29719** terminal t29754 'min slot' (w30197) :35,:59 = `RingPickSlot_v0.vi` (pane 2 'min slot', docs/d1/ring-p4b.md:138-139). w30197 has no other terminal.
- (c) Outer face t30192 'min slot' (OuterTerminal, source, w30166, on #23166) :26. **w30166 has FIVE other sinks, not one**: IndexArray.index of #30300, #30240, #30216, #30119, #29843, all on #23166 :14-17,:25.
- (d) Frame #29869 (owner FlatSequenceFrame :69) holds only #30002, #29879 IndexArray and #30016 Local (:18-24); no tunnel faces on it, so 0 border tunnels. FS #29721 is an obj :54 but has no owners row in 44858dbf (:68); its owner Diagram #23166 is the measured fact `diag_c152_a1_1_owner.log:25`.
## 2. Scratch case as built (`diag_c152_b1_1_cross.py`, 116 lines, plan `diag_c152_b1_1_cross_plan.json`)
- NEW minimal VI = `Stage.scratch` byte copy of EMPTY_v0 (`scratch_c152_b1_1_20261009_052442_min.vi`).
- Stage input = P3b2b bed 39511877. It is only the launch contract (dry graph `graph_ring_p3b2b_20261002_133824.json`) and the Index Array donor #3163.
- Why that input: an EMPTY_v0 input has no graph JSON, so dry fails. The fntest release (stage_prerun.py:2389-2399) needs a `fntest_*.py` name, which this card's write globs do not allow.
- Dry PASS (`diag_c152_b1_1_dry.log`). Prerun PASS 15/0 (`diag_c152_b1_1_prerun.log`), X10 676.4 MB. check-launch ALLOW.
- Pass 1 of the prerun failed X6 (literal 260) and X10 (696.6 MB). Positions moved to the plan and reads cut, offline only.
- Case built: While loop on top, then RingPickSlot_v0 in its body. P1 'min slot' -> Max & Min.x in the body makes the source wired.
- Next: P2 'min slot' -> IA_o.index on top creates LT. Then a 1-frame FS on top holding IA_f. X = IA_f.index <- LT outer face.
- Only ONE sink on LT's outer net, as PD369(d) says (graph has 5, see 1(c)).
## 3. The run: `diag_c152_b1_1_cross.log`, BGRUN END rc=1 after 124s; RESULT 26 pass / 1 fail
- Created: While #43 with body #110 :51. drop_subvi err '' :53. Max & Min #45 owned by Diagram #110 :55-56. IA_o #184 owned by TopLevelDiagram #3 :58-59.
- **First unexpected result: `struct_copy_nested` FS -> top raised** `new FlatSequence #204 is owned by ('TopLevelDiagram', 3), not Diagram #3` :61-63.
  - FS #204 WAS created, on #3. Only the wrapper's owner check refused it.
  - The check is `gscript.py:5064`: `('Diagram', uid)` only. `create_primitive_nested` also accepts `TopLevelDiagram` (`gscript.py:4864-4867`); struct_copy_nested does not.
- Then `fs_frames(W, 0)` raised ValueError :64-80. **No connect ran: P1, P2 and X were never reached, so no face name was measured.**
- `Is Broken?` not reached. No census delta was gated for the FS.
## 4. Hygiene
- H5 refs 6 opened / 6 closed :84-85. Both scratches deleted :87-88. H2 bed md5 same :89. H3 every pin holds :105. H6 files left [] :106-107.
- Every card pin's PIN-CARD gate passed before the run: stagekit, addrcheck, stagexec, gscript, stage_prerun, vigraph, stagesim, table, memory_model, s08 VI f99e8414, graph 44858dbf, RingPickSlot, EMPTY, the donors.
- Handles: 0 before the restart (LabVIEW not running), 33,995 after the restart :41-42, 42,688 after the work with the bed loaded :86, and 34,000 at exit after close's restart :108 (+5 vs after-restart).
- `LabVIEW gone at exit: True`; `tasklist` LabVIEW count 0 afterwards.
- No JEV-LADDER row exists for `diag_c152_b1_1_cross.log` yet (`jev_gate.log`).
OPEN: the measurement needs the FS (and the loop) inside a NESTED Diagram (e.g. the whole case inside one more structure's frame), or `struct_copy_nested` must accept `TopLevelDiagram` as create_primitive_nested does - which? Mirror 1 sink or s08's 5?
