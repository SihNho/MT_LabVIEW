---
type: facts
status: current
date: 2026-10-10
card: 160-b2-1
---
# 160-b2-1: why routes 4/7 of plan_ring_p5s02b are UNROUTABLE (offline; reader diag_c160_b2_1_read.log, shared stagexec.state_addr/route_on_state)
## 1. Rows on graph_ring_p5s02a_20261010_032547.json (read.log:4-27)
- t24139: RightShiftRegister #24083, **InnerTerminal**, 'error out', sink, wire 24264 (stub: its only row, read.log:24), frame_diagram 23405. t24235: RSR #24150, InnerTerminal, '', sink, w24300 (stub), 23405.
- LSR contrast: t24190 LSR #24133 InnerTerminal 'error out' **source**, w24285 (stub); t24288 LSR #24187 InnerTerminal '' source, w24312 (stub); both on 23405.
- Outer faces on #686: RSR 24178 (w9610) / 24280 (w5050); LSR 24205 (w4969) / 24291 (w3543). owners 23405 = WhileLoop #23041; 31506 / 31517 = CaseStructure #31308 (frames of CQ7).
- Loop #23041 right_uids [24083, 24150, 31347], left_of 24083->24133, 24150->24187 (read.log:16); base_registers/loop_of give loop 23041 for all four (read.log:22-23).
- Act-10 source t3934 (#376 'error out') is UNWIRED (wire 0) on frame 31506 (read.log:8).
## 2. Where it falls through (stagexec.py c4a6e0b6)
- Compile: act 7 `tunnel` t_go (loop 31308) + w_gout + w_gr -> op kind `tunnel` at :877, because the outside end (w_gr dst) is a DICT end, so `oh` is None and `reg` = "" (:865-867); the `connect_term_uid` register_end_case_border branch (:868-874) needs a plan-made `srL`/`srR` symbol.
- Executor :2784-2788 `tunnel` -> be.connect(src 3934, dst 24139) -> connect_route :1489 `dt, hd = addr.triple(real, dst, False, loop_of)` runs BEFORE any wired-source shortcut (:1491).
- Addr._triple: :1874 `node = V.node_of(r)` = 24083; :1883 `owner_class in FACE_ROUTED` false (FACE_ROUTED = SelectorTunnel/Tunnel/LoopTunnel, :1306/:1321); :1888 `owner_class in SR_CLS and term_class == "OuterTerminal"` false (InnerTerminal); -> :1918-1920 `uids = self.rd.node_uids(didx)`; `if node not in uids: raise ExecStop("ADDRESS: node #... not in Diagram[...].Nodes[]")`.
- Reproduced: route_on_state(3934 -> 24139) = STOP same text (read.log:28); triple(24139/24235) STOP (read.log:30-31); Diagram 23405 Nodes[] holds neither #24083 nor loop #23041 (read.log:32).
- LSR rows route: in route 3/6 the LSR face is the SOURCE (wired, stub w24285) and the dst is #376's input (a Nodes[] node) -> triple ok, :1491 `if rs["wire_uid"]: return "cfw"`.
## 3. Precedent
- Same geometry, PLAN-MADE RSR (unwired inner sink) via register_end_case_border, LabVIEW diff 0: diag_c154_p5s01a_scratch.log:229 (t_co/w_co_r -> new:SN1R.inner, plan_ring_p5s01a.json:425-427); diag_c155_p5s01b_scratch.log:137 (t_qo/w_qo_srq -> new:QS1R.inner on BASE case #30726, plan_ring_p5s01b.json:200-222).
- wire_sr RightIn into a register of loop #23041 from a body Nodes[] source passed: diag_c158_p5s02a_scratch.log:104 (reg[2] = #31347, plan-made in P5-2a).
- A BASE RSR inner face as the outside end of a tunnel group, or a stub-carrying RSR sink: **no precedent found** (Grep register_end_case_border / RSR / RightShiftRegister over plan_ring_p*.json, stagexec/stagesim/gscript, docs/NAMES.md, docs/d1/*.md, opmodels; STEPX connect_term_uid / wire_sr over *p5s01*.log, diag_c15[068]_*scratch.log).
- Prior same-class fact: docs/d1/ring-p5.md:137-153 (card 154-a4-1: SR face -> base-case tunnel fell back to plain `tunnel`; fixed for BASE CASES, not base registers).
## 4. Options (facts only)
| opt | change | files | new LabVIEW measurement | rule 1a | sim / route result |
|---|---|---|---|---|---|
| a1 plan-only, keep form | none possible inside current compile: any tunnel group with a dict RSR-inner end compiles to `tunnel` (:866-877) and fails at :1919 | plan_ring_p5s02b_in.json | - | no change | routes 4/7 stay UNROUTABLE |
| a2 plan: delete stubs w24264/w24300 first | +2 delete_wire acts | plan only | yes (sink unwired then) | none: same error wire #376->RSR | alone still UNROUTABLE (term_class InnerTerminal unchanged); with b1 it meets the dry check :4109-4110 |
| b1 router: treat a base-graph RSR/LSR InnerTerminal dict end like srR/srL at :866-868 | compile -> connect_term_uid register_end_case_border | stagexec.py (+stagesim if it shares compile) | yes: base register + MERGE onto stub not measured (PD388(c)); dry check :4109-4110 refuses a wired sink ("already wired") unless a2 or b2 | none: routing only, same terminals | REALSIM effects unchanged (route check only); census = ROUTE_CENSUS :310 (Wire 2) unless stub merge differs |
| b2 router: Addr._triple branch for SR InnerTerminal (via loop Shift Registers[] / wire_sr) | new address route | stagexec.py, op path | yes: wire_sr needs a body Nodes[] source; #376 sits in case frame 31506 (nested) - unmeasured | none | unknown until measured |
| c design: new registers instead of #24083/#24150 | plan + loop structure | plan | yes | per-bead none, but changes the loop's register set (design call) | not simulated |
md5 unchanged (diag_c160_b2_1_md5.log, 10/0): stagekit 1441bb4c, stagesim a3261b56, stagexec c4a6e0b6, stage_prerun 7605116f, plan_in 56bfddd3, plan 09ebc7a6, VIs 94ffff94 / eb1d0f31 / 2482fe7b / 7f2582ae. tools/hooks: only hook-written material_marker.log.
OPEN: route 4/7 fix - plan (a2) + router (b1), router b2, or design c? b1/a2 each need one scratch measurement (base RSR via connect_term_uid; stub merge vs delete).
OPEN: keep the MERGE assumption (PD388(c)) on stub-carrying sinks, given the dry connect_term_uid check refuses a wired sink (:4109-4110)?
