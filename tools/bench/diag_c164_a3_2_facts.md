---
card: 164-3-2
date: 2026-10-10
status: current
---
# 164-3-2 facts (offline, no LabVIEW): K3f / K4f inner-face wiring. Inputs read: graph 3d5196ab, plan both164 4c8d3645, ring-p5c 1611e1e7
Helper `diag_c164_a3_2_rows.py` (vigraph.dedupe_rows, protocol.result_line) -> `diag_c164_a3_2_rows.log:15-40` RESULT 2/0 (second run; :1-11 = first run, TypeError in the helper).
**1. Design.** A70 = `w_k3f`, A80 = `w_k4f` (numbering `attrib_c159_p5s02a.md:30-31`). Rows `plan_ring_p5s02r_in_both164.json:849-858` / `:955-964`:
op `wire`, src `new:OK3.outer` / `new:OK4.outer`, dst `{uid 5204, term_uid 8776}` / `{uid 10404, term_uid 24342}`. No `frame` key on either end; why "PD379(b) #6384/#2048 take the value that reaches R.inner".
OK3/OK4 = case out-tunnels of `new:CQ7` made in frame `CQ7.f0` (not-timed-out), parent 23405 (`:789-798`, `:895-904`). The same OK.outer feeds SK.R.inner (`w_k3r` :810-816, `w_k4r` :916-922).
Source decision: PD379(b) `docs/d1/ring-p5.md:181-187` ("keep out-tunnels #5204 / #10404, re-fed from that net, or feed from R.outer - either form, the same value; the plan maker picks the one with existing routes"); PD374(d) `ring-p5.md:48-53`.
Value per design: per 1.7 iteration, #376 t3 'file progress' / t4 'file number to append out' (not-timed-out frame) or the SR's L.inner value passed through (timed-out frame); after exit, the last real #376 call's value (`ring-p5.md:51-52`, `:181-185`). Frame: 1.7 body 23405, outside the case.
**2. Graph 3d5196ab** (`diag_c164_a3_2_rows.log:18-38`): LoopTunnel #5204 (obj :37, owner WhileLoop) has exactly 2 rows: t9631 OuterTerminal 'file progress' frame 686 wire 4337; t8776 InnerTerminal frame 23405 wire 10362 (:19-20).
LoopTunnel #10404 (obj :38): t24363 OuterTerminal 'file number to append out' 686 w9636; t24342 InnerTerminal 23405 w25232 (:22-23). Every row is_source false. No conditional-terminal row on either tunnel.
w10362 has ONE end (t8776) and w25232 ONE end (t24342) (:33-36): sink-only stubs, no source. In P5-1 the source end was #376 t5704 / t5739 (`attrib_c159_p5s02a.md:30-31`).
w4337 ends: t9631, #6384 'actual # data points' t6480, #2048 'length' t3182, all sinks, all frame 686 (:26-29). w9636 ends: t24363, #6384 'file # to append' t6511, both sinks, 686 (:30-32).
So today nothing sources either net; `attrib_c159_p5s02a.md:33-34` lists #5204/#10404 as 'undirected'.
**3. Prior inner-face wiring by a tool route.** Searched: `tools/bench/diag_c1*_facts.md`, `tools/bench/creation_map/*.jsonl` (17 files), `docs/d1/*.md`, plus the adopted P5-2a / P5-2b scratch logs.
- BASE LoopTunnel inner face as wire SOURCE, wire 0: `connect_term_uid #5760 <- #24360` / `#5778 <- #24367` (`diag_c158_p5s02a_scratch.log:254`, `:262`; RESULT 23/0 :315, adopted `adopted_scratch.jsonl:11`). Route `loop_inner_face_route` `stagexec.py:1673-1692`: only InnerTerminal, wire 0, owner a While/For loop (:1681-1689); PD385(a) `ring-p5.md:295-298`.
- BASE RightShiftRegister inner face as SINK after its stub is deleted: `delete_wire w24264` then `connect_term_uid #24139 <- #3934` (`diag_c161_p5s02b_scratch.log:89`, `:97`; RESULT 20/0 :197; `adopted_scratch.jsonl:12`); PD391(a)(c) `ring-p5b.md:140`, `:150`.
- PLAN-MADE LoopTunnel inner face as sink only inside its own `tunnel` group: `p4_t_n1_in` src PS1 -> `new:TN1.inner` (`plan_ring_p4_s04v18.json:498-512`, f349c39a), one op acts [21,22,23] -> LoopTunnel #30094 (`creation_map/plan_ring_p4_s04v18_f349c39a_20261007_215246.jsonl:73`; adopted `adopted_scratch.jsonl:3`).
- A BASE LoopTunnel INNER face as a wire SINK (the K3f/K4f shape, a stub present): none found in the searched globs.
- `stagexec.py:1928-1931` (md5 a4df7e15): in `Addr._triple`, any owner class in FACE_ROUTED (SelectorTunnel, Tunnel, LoopTunnel; :1351, :1365-1366) whose face is not OuterTerminal raises "ADDRESS: #.. is an INNER face of ..: only the outer face's owner route is measured (l2a1_faces_81.log)".
  Why: the only measured face address is a tunnel's OUTER face via its owner structure's Terminals[] (`stagexec.py:1345-1350`, `:1359-1364`; `l2a1_faces_81.log:31-51` M1 5/5, all OuterTerminal rows of SelectorTunnels).
**4. Outer-face comparison.** OUTER face today: t9631 (686) and t24363 (686) have no source (w4337 / w9636, all ends sinks, item 2). Inner-face design: source OK.outer on 23405, which reaches the sinks through the tunnel's last value.
- Tunnel mode: IndexMode 0 on #5204 and #10404, measured on `D1_s4_loop17.vi` (`stage_d1_l7_r_r2.log:128`, `:203`), equal to the original #1929 / #5020 (`:37`; `l7_r_predict.log:9`). Not in 3d5196ab (obj row has uid/class/pos/owner only, rows log :37-38) and not re-read since.
- Alternative "feed from R.outer" (PD379(b) :186-187): SK3/SK4 are added on loop 23041 with parent 686 (`plan ...both164.json:753-761`, `:859-867`), so R.outer sits on 686, the same frame as t6480 / t3182 / t6511.
- Values: per iteration the tunnel inner and SK.R.inner sit on one net (OK.outer, item 1). With IndexMode 0, tunnel outer = the inner value of the last iteration = the R.inner value of the last iteration = R.outer. **Equal if IndexMode 0 still holds on 564d8cbe; cannot be decided from 3d5196ab alone.**
- Original (plan docs): #1929 LoopTunnel on #637, inner <- #376 'file progress', outer -> #2048 'length' + #6384 'actual # data points'; #5020 inner <- #376 'file number to append out', outer -> #6384 'file # to append' (`docs/d1-loop12-17-split-plan.md:195`; `docs/frame-loop-wire-graph.md:285-286`, 'plain').
  In the original, #376 runs every #637 iteration with no case (`ring-p5.md:35-36`), so the tunnel carries the last call's value. Last REAL call vs timed-out frames = PD379(b) `ring-p5.md:181-185`.
**5. Other facts that bear on a later route choice** (none chosen):
- STUB: no plan `delete_wire` removes w10362 / w25232 (`diag_c164_a2_1_facts.md:32-33`). The P5-2b precedent deleted the sink stub BEFORE the connect (item 3).
- `gscript.connect_term_uid` joins terminal uid to terminal uid for any owner and diagram (`ring-p5.md:295-297`, cites `gscript.py:5141-5163`). Today only the K3/K4 R1 variants, the wire-0 source face and the base SR face reach it from a plan (`diag_c164_a2_1_facts.md:14-19`; item 3).
- An outer-face form leaves #5204 / #10404 with no source and no sink-carrying role. The plan has no delete for #5204 / #10404 or w4337 / w9636 (grep of both164: only :854 / :960 name 5204 / 10404).
- PD399(b) puts K3f, K4 and K4f in step 5 (`ring-p5c.md:124-129`). make_step_plan does not check routability (`prep_plan_flow_lib.py:171`, via `diag_c164_a2_1_facts.md:44`).
- Side fact: this card's bgrun reported `BGRUN REAP marked KILLED: prep_c164_a3_1_hash.log pid=27112` (`diag_c164_a3_2_rows.log:14`). That is another card's log; I did not touch it.
OPEN: IndexMode of #5204 / #10404 on 564d8cbe is unmeasured since D1_s4_loop17 (2026-09-24); the equal-value claim in item 4 rests on it.
OPEN: no adopted precedent for a BASE LoopTunnel inner face as a connect SINK, stub deleted first or not. Measured routes stop at stagexec.py:1930.
