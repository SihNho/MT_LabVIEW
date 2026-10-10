---
type: facts
status: current
date: 2026-10-10
card: 163-a3-1
---
# 163-a3-1: K3/K4 GAP facts (PD396(f)), offline, no LabVIEW, nothing edited but this file and diag_c163_a3_1_read.py
Graph read: `py tools/bgrun.py --material ... diag_c163_a3_1_read.py` -> RESULT PASS 3/0, graph md5 3d5196ab (diag_c163_a3_1_read.log:3,96-97).
## 1. Where the ends resolve (-30 / -29)
- Plan rows (plan_ring_p5s02r_in.json d84634bd): A69 `w_k3pass` src `new:IK3.inner` dst `new:OK3.inner` (:835-840); A79 `w_k4pass` src `new:IK4.inner` dst `new:OK4.inner` (:933-938). Both FRAMELESS strings.
- IK3/IK4 = `tunnel` dir in, body `new:CQ7.f1` (:817-826, :915-924); OK3/OK4 = `tunnel` dir out, body `new:CQ7.f0` (:789-798, :887-896).
- Sim (P5-1 graph 6716c499): CQ7 #-28 frames [['False', -29], ['True', -30]] (prep_c156_a1_2_measure.log:8). OK3 case_tunnel_frame -29, IK3 -30 (:6-7).
- Ends: src (-131, owner IK3 #-128, SelectorTunnel, InnerTerminal, frame -30) | dst (-125, owner OK3 #-123, SelectorTunnel, InnerTerminal, frame -29) (:9). K4 same: src -132 on -30, dst -125 on -29 (:20).
- So source = in-tunnel's face on 'True' (timed-out); sink = out-tunnel's face on 'False', because a frameless dst resolves to OK's own group frame (stagexec.py:6278-6280; :10,:21 gates PASS).
## 2. Borders crossed and the intended tunnels
- Only ONE border: the two frames of case CQ7 (False -29 / True -30); both tunnels belong to CQ7 on loop-1.7 body 23405 (plan :792-794, :820-822). No loop or sequence border between the ends.
- OK3 has an InnerTerminal on every CQ7 frame: -29 and -30 (measure.log:7,11); its 'True' face is -126, on the source's diagram (:12 F3b PASS; K4 :23).
- PD379(b) (docs/d1/ring-p5.md:180-183): "SR L.inner -> case in-tunnel -> pass wire in the timed-out frame -> case out-tunnel -> SR R.inner; #376 t3/t4 -> the same out-tunnel in the not-timed-out frame. The in-tunnel's one out-wire IS the pass wire."
- Intended: IK<k> inner 'True' face -> OK<k> inner 'True' face, between SK<k>L.inner (w_k<k>l :827-833) and SK<k>R.inner (w_k<k>r :810-816).
## 3. Existing route that could carry it
- In the adopted p5s02c graph CQ7 is base case #31308 with frames 31506 / 31517 (graph owners "31506"/"31517": ["CaseStructure", 31308]); #376 sits on 31506 (read.log:9), so 31506 = 'False' by plan group D placement.
- No tunnel or SR carries #376 t5704 / t5739 yet: t5704 wire 24330 goes only to #3453 on 31506 (read.log:13); t5739 wire 0 (read.log:9).
- #5204 inner t8776 (23405) wire 10362 and #10404 inner t24342 wire 25232 have NO other end (read.log:21-26); outer faces still feed #6384 t6480 / #2048 t3182 and #6384 t6511.
- SRs on 23405: 24083/24133, 24150/24187, 31347/31352, 31659/31666 (read.log:67-68,88-93); none touches t5704/t5739. Carrying route for t3/t4: none exists.
- Same shape already adopted in the graph: SR 31666 L -> case in-tunnel 31718 -> wire 31722 on frame 31517 -> out-tunnel 31735 -> SR 31659 R (read.log:41-42,92-93); also wires 31561 (31593/31598) and 12079 (31628/31640) on 31517 (read.log:37-40).
- Those came from plan rows w_gpass A33, w_hpass A40, w_c7_pass A52 with `frame: "True"` on BOTH ends (plan_ring_p5s02r_all.json:432-444, :511-523, :650-662).
- Tool route: stagexec.case_pass_wire (stagexec.py:6273-6302) accepts a pass wire with dst `frame` = the in-tunnel's body frame (plan case: frame name; base case: '#<diagram uid>', :6298-6299). Self-test 20/0 (selftest_c156_passwire_c160_e5_1.log:34); A31/A41 compile + A32/A42 sim 70 actions, 0 provisional, with frame 'True' (:6-7,:14-15).
## 4. "action 69" for K4
- Text: session.json:426 "action 69 (wire w_k4pass): wire new:IK4.inner -> new:OK4.inner: source on diagram -30, sink on diagram -29 ..."; K3 :396 same with w_k3pass.
- Full-plan numbering: A69 = w_k3pass, A70 = w_k3f, A71..A78 = sr_k4 .. w_k4l, A79 = w_k4pass, A80 = w_k4f (plan_ring_p5s02r_in.json ids :836,:843,:853-927,:934,:941; diag_c163_a1_1_probe.log:92,102).
- The census numbers the ROUND's live list: `live` = groups still OK, `flat(live)`, `n` = failed position (prep_c156_a1_1_mk.py:291-297,317-318,351-353). Round 1 dropped K3 (n 69), K3f went BLOCKED (:300-309); round 2 K4 filled positions 61..69 (mk2.log:86-88, 3 rounds).
- So "action 69" in K4's text = position 69 of round 2's list = A79 of the full plan: a round-local index, not a different action.
## 5. Which check reports the GAP
- stagesim.py:1557-1559 `SimError("wire {0} -> {1}: source on diagram {2}, sink on diagram {3} - a border needs a tunnel/register action first")`, reached when src/dst frame_diagram differ and no FS rule applies (:1550-1556).
- Called by the 156-a1-1 census SS.simulate (prep_c156_a1_1_mk.py:334), stored as stage "sim" (:353), logged mk2.log:86-87, session.json:396,426; reproduced by selftest_c156_passwire C2 (c160_f3_2.log:24).
OPEN: selftest_c156_passwire.py:27 and its gate text cite "stagesim.py:1536"; the raise is now at stagesim.py:1558 (95a162ba). Stale citation only.
OPEN: plan_ring_p5s02r_in.json K rows address `new:CQ7` / `new:CQ7.f0|f1`; on the p5s02c base CQ7 is #31308 (31506/31517). Not measured whether the step-4 maker rebases these.
