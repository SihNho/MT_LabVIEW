---
card: 165-3-2
date: 2026-10-10
status: current
---
# 165-3-2 facts (offline; no LabVIEW) - PASS 92/0: plan_ring_p5s02e.json re-made, final True, fd23974e (`prep_c165_a3_2_mk.log:204`, BGRUN END rc=0 43 s :205)
**How the maker ran:** `prep_c165_a3_2_mk.py` executes the maker's OWN file `prep_c165_a2_1_mk.py` 70f7e553 (`:35`) with 8 asserted substitutions, because run verbatim
its M0 reads pins from task_165-2-1.json (stagexec 6ea6637f, `prep_c165_a2_1_mk.py:28`) = a certain fatal M0 FAIL, and its side files are 165-2-1's names.
Substituted: pin source -> task_165-3-2.json minus the 2 outputs (+ plan_ring_p5s02d 97837e2a); side files prep_c165_a2_1_* -> prep_c165_a3_2_*; pd401b card id;
gate object (one RESULT line). NOT changed: card tag "c165-2-1", goal/probe texts, groups, graph, sources, census rows -> plan_in byte-equal b5b35f8a (`:177`).
**1. md5 first** (`:3-25`, 23/0, python hashlib bytes only): all 21 card inputs == pins (incl. plan_ring_p5s02e.json 20bde81a `:14`); VI D1_ring_p5s02d_20261010_152518.vi
6dcd5c3d506f69947a5ce259ccbe2221 (`:24`); stagexec 1d5309f4 (`:25`). No drift. Maker M0 PASS (`:36`).
**2. Aside:** plan_ring_p5s02e_prev20bde81a.json 20bde81a copied before the maker (`:26`) and again by keep_prev (`:41`, gate ASIDE `:138`).
**3. Binding / prefixes:** new:OK3 -> sim -18 -> real #31803 (`:51`), B1 PASS (`:140`); SYMBOLS CQ7 31308, f0 31506, f1 31517, OK3 31803 (`:139`). Census f9c8aaf5 (== 165-2-1's).
| prefix | rows | checkpoints | delete_wire ops | MAIN | peak | log |
|---|---|---|---|---|---|---|
| K3f | 2 | [0,1,2] | [1] | 642.6 | 637.5 | :72, :141 |
| K3f+K4 | 11 | [0,1,3,4,6,7] | [1] | 657.1 | 652.0 | :75, :142 |
| K3f+K4+K4f | 13 | [0,1,3,4,6,7,8,9] | [1,8] | 665.0 <= 675 | 659.9 | :78, :143 |
RULE plan = K3f+K4+K4f A72..A84, 13 rows (`:80`); no prefix cut.
**4. Gates (all PASS):** GRP [(72,73,2),(74,82,9),(83,84,2)] `:40`; STUB `:68`; C x3 every delete_wire a checkpoint `:72/:75/:78`; X10 `:79`; SPLIT `:81`; PROBE `:82`;
TIE `:84`; S1 13 actions / 24 open pairs `:85`; SB REALSIM final True, failed None, 13/13, 0 PROVISIONAL, route PASS, 0 UNROUTABLE `:132-133`
(ROUTE k=2 connect w_k3f / k=9 branch w_k4f = connect_term_uid `:124/:131`); C-OUT MAIN 665.0 `:134`; IDS dw_10362..w_k4f `:135`; X8 `:136`; X17 `:137`; RC 13 `:145`; E2 `:160`; U `:176`.
**PRIME-SKIP** (stagexec.dry_run on the new plan, PASS `:182`, exactly 2 `:183`):
`:179` PRIME-SKIP end #8776 (LoopTunnel #5204 inner sink, base w10362) of action 2 (w_k3f, op 2): left to its step - w10362 is deleted by checkpointed op 1 (action 1 dw_10362)
`:180` PRIME-SKIP end #24342 (LoopTunnel #10404 inner sink, base w25232) of action 13 (w_k4f, op 9): left to its step - w25232 is deleted by checkpointed op 8 (action 12 dw_25232)
`:181` PRIME 0 terminal indexes proved at base; 0 ControlTerminal end(s) by 179(b); unprovable []
**5. PD401(b)** `prep_c165_a3_2_pd401b.json` 2ea89c4b (expectation; sim values only, none measured in LabVIEW): dw_10362+w_k3f: face t8776 wire 0 after delete (sim step 1),
census in [{}, {'Wire': 1}], face on OK3.outer net (sim w31792, src t31815), is_broken False; dw_25232+w_k4f: t24342 wire 0 (sim step 12), same census, OK4.outer net
(sim w-15, src t-11 on sim OK4 #-10), is_broken False. DWSTEP gates `:168/:175`.
**6. Sim end graph** (step_13_wire.json 33e6f4d7, read-only): w10362 / w25232 0 terminal rows, Wire object absent (`:163/:170`).
K3f net w31792: t31815 SRC #31803 SelectorTunnel Outer (OK3), t8776 SINK #5204 LoopTunnel Inner, t31767 SINK #31756 RightShiftRegister Inner (`:164-166`), END-FACE `:167`.
K4f net w-15: t-11 SRC #-10 SelectorTunnel Outer (OK4, sim uid; made in this step), t24342 SINK #10404 LoopTunnel Inner, t-3 SINK #-1 RightShiftRegister Inner (`:171-173`), END-FACE `:174`.
Per step face rows `:146-159`: t8776 10362 -> 0 (n1) -> 31792 (n2..); t24342 25232 -> 0 (n12) -> -15 (n13).
**Artefacts:** plan_ring_p5s02e.json fd23974e (final True); plan_ring_p5s02e_in.json b5b35f8a (unchanged); prev 20bde81a; pd401b 2ea89c4b; session 79ecbe13;
census f9c8aaf5; probe in a97de1b2; maker wrapper prep_c165_a3_2_mk.py.
**UNCHANGED after the run** (POST 20/0 `:184-203`): stagexec 1d5309f4, stagesim 95a162ba, stagekit dd57c1ca, stage_prerun 7605116f, stage_shared b688edd4, r_in 0b895983,
graph 2a5fa0c4, memory_model ff0fabca, VI 6dcd5c3d, every other card input; maker U gate (VIs 564d8cbe / 94ffff94 / f9ae7751, plans a-d) PASS `:176`. No tool / hook / doc edit.
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| prep_c165_a3_2_mk.log | no failing log (no JEV-LADDER row owed) | - | built wrapper, ran | PASS 92/0 |
OPEN: prep_c165_a2_1_mk.py cannot be re-run for another card without text substitution (pins / side-file names hard-coded at :28, :52, :64, :124); a parameterized step-5 maker (or its post-checks :78-125 moved into prep_plan_flow_lib) is outside this card's write globs.
OPEN: OK4 / w-15 are sim uids; the K4f END-FACE and PD401(b) for t24342 are sim facts until the real run binds new:OK4.
