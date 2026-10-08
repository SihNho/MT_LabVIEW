---
type: facts
status: current
date: 2026-10-09
card: 152-b1-2
---
# Card 152-b1-2 facts: the ONE nested scratch crossing PASSED 44/0; the new FS border tunnel takes 'min slot' on BOTH faces (prediction (i))
Graph read (item 0) is not repeated: `diag_c152_b1_1_facts.md` section 1 / `diag_c152_b1_1_graph4.log`.
## 1. Scratch case as built (`diag_c152_b1_2_cross.py`, 120 lines; plan `diag_c152_b1_2_cross_plan.json`)
- Copied from `diag_c152_b1_1_cross.py`. Changed: names/paths (b1_2), the nesting (body lines 69-81), `fr` guard on fs 0 (:83), docstring. Pins and gates unchanged.
- NEW minimal scratch = byte copy of EMPTY_v0. OUTER While #43 on top #3, body OB #110 (`diag_c152_b1_2_cross.log:53`).
- ANCHOR RingPickSlot_v0 #44 on top, unwired: `loop_in` reads Traverse SubVI[0] and fails 1055 on an empty VI (`diag_c137_3_lookup.log:49`). Not on the measured net.
- INNER While #45 on OB by `loop_in`, body IB #168 :56. SubVI #46 RingPickSlot_v0 + Max & Min #47 in IB :58-61.
- IA_o #277 on OB :63. FS #300 by `struct_copy_nested` onto OB, owner ('Diagram', 110) :66-67, 1 frame #310 :69. IA_f #322 in #310 :71.
- Census F1 FlatSequence 1 + Diagram 1 PASS :68. FS border tunnels BEFORE X: [] (BUILT :73).
- Dry PASS (`diag_c152_b1_2_dry.log`); prerun PASS 15/0, X10 679.2 MB <= 680 (`diag_c152_b1_2_prerun.log`).
## 2. Face names (allterms rows: term, owner, name, is_source, frame_diagram, wire)
| when | object | face | name | source | on | wire | log |
|---|---|---|---|---|---|---|---|
| before X | LoopTunnel #243 | t249 outer | min slot | True | OB #110 | w237 | :93 |
| before X | LoopTunnel #243 | t245 inner | min slot | False | IB #168 | w252 | :93 |
| after X, pre-RLE | LoopTunnel #243 | t249 outer | min slot | True | #110 | w261 | :100 |
| after X, pre-RLE | LoopTunnel #243 | t245 inner | min slot | False | #168 | w252 | :100 |
| after X, pre-RLE | FSOuterTunnel #250 | t258 outer | min slot | False | #110 | w261 | :100,:105 |
| after X, pre-RLE | FSOuterTunnel #250 | t255 inner | min slot | True | frame #310 | w240 | :100,:106 |
| after RLE | all four faces | same | min slot | same | same | same | :108-109 |
- MIRROR row: LT outer face 'min slot' == graph #30179 t30192 :95. "LT faces unchanged by X" True :107.
- The other sink is IA_o.index #290 (P2 sink :86). It has no tunnel of its own; LT is the only tunnel on that net before X.
## 3. Census, Is Broken?, ExecState
- P1 {Wire 1} broken False :82. P2 {InnerTerminal 1, LoopTunnel 1, OuterTerminal 1, Wire 2}, gone [347], broken False :88.
- X {FlatSequenceOuterTunnel 1, Terminal 2, Wire 2}, gone [w237] (the outer net re-made as w261 + w240), broken False :99.
- RLE on every new wire: echo == uid, err '' :89-90, :101-102. ES 0 after each step (:84,:91,:103): both While conditional terminals are unwired by design.
## 4. Hygiene
- BGRUN END rc=0 after 135s; RESULT PASS 44/0 :142.
- Handles: 0 before (LabVIEW not running) :41. 34,010 after restart :42; 42,810 after work :115; 33,990 at exit :137 (-20 vs after-restart).
- Refs 9 opened / 9 closed :114. Both scratches deleted :116-117. Bed md5 unchanged :118. Every pin before == after (H3) :134. Files left [] :136.
- `LabVIEW gone at exit: True` :143; `tasklist` LabVIEW count 0 afterwards.
## 5. Five sinks (prediction only, not built)
- Both FS faces took the LoopTunnel source face's name. LT's name did not change when a second sink was added (:107).
- So s08's 4 extra IndexArray.index sinks on w30166 are predicted not to change the name. They are plain sinks, not tunnels.
OPEN: should the naming table / stagesim rule (stagesim.py:1892) record "LoopTunnel source (SubVI-named) -> FS border tunnel takes the source name on both faces" from this one row, or is a second row needed? (card 152-b1-1 step 5 assigns that edit to a later card)
