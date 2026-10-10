# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-3-4.md
# ---
r"""prep_c164_a3_4_pred - card 164-3-4 (OFFLINE, no LabVIEW): plan_ring_p5s02d_pred.json for P5-2 step 4 on the RE-MADE plan
plan_ring_p5s02d.json 725cd68e (groups J in the P4 delete form + K3 = A53..A71, FINAL on the REAL 564d8cbe graph 3d5196ab, card 164-3-1)
+ the sink-gate census file prep_c164_a3_4_session.json that stagekit.RingSession reads. Inputs only; the flow is prep_c164_a2_3_lib.pred
(called, not copied). The PD399(a) wire expectations are added by prep_c164_a3_4_pd399.py (next run). Run AFTER _licence.py and _el.py.
PREDICTION CONTRACT: M0 pins; RB plan FINAL, 19 actions == session, no negative uid, base = 3d5196ab with bed 564d8cbe; C 15 ops == session
  compile; E1 checkpoints == checkpoint_ops == session [0,1,2,6,7,11,12,14,15], each a step file with its recorded md5; X1 x10_plan_start ==
  x10_start(564d8cbe) == session start 581.8; X10 MAIN 647.8 <= 675, Executor peak 642.7; X17 PASS; DW 2 rows (dw_cond #23489, dw_23460
  #23460); DO 2 rows (#23042, #23501); OBJ LR7 / EQ7 / SK3L+R / KI3 / OK3 / IK3 bound; FM w_k3pass on #31517; WS every wire sink wired; RT
  route rows PASS; EL keyed; SG census written; SP pred keyed to the plan md5.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c164_a3_4_pred.log -- py -u tools/bench/prep_c164_a3_4_pred.py"""
import os, sys                                                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep_c164_a2_3_lib as LB                                                             # noqa: E402
B, T = LB.B, LB.T
RRP, SESS = os.path.join(B, "plan_ring_p5s02d.json"), os.path.join(B, "prep_c164_a3_1_session.json")
GRAPH = os.path.join(B, "graph_ring_p5s02c_20261010_131658.json")
CFG = {"RRP": RRP, "PP": os.path.join(B, "plan_ring_p5s02d_pred.json"), "SESS": SESS, "SGF": os.path.join(B, "prep_c164_a3_4_session.json"),
       "ELF": os.path.join(B, "errorlist_predicted_D1_ring_p5s02d_end.json"), "LIC": os.path.join(B, "plan_ring_p5s02d_licence.json"), "GRAPH": GRAPH,
       "PINS": {RRP: "725cd68e", SESS: "2aeaef24", GRAPH: "3d5196ab", os.path.join(B, "prep_c164_a3_1_plan_in.json"): "dc309d2c",
                os.path.join(B, "plan_ring_p5s02r_in.json"): "9dadb0c1",
                os.path.join(B, "memory_model.json"): "8fb432e4", os.path.join(T, "stagesim.py"): "95a162ba", os.path.join(T, "stagexec.py"): "a4df7e15",
                os.path.join(T, "stagekit.py"): "dd57c1ca", os.path.join(T, "stage_prerun.py"): "7605116f", os.path.join(T, "stage_shared.py"): "b688edd4"},
       "BEDVI_MD5_PREFIX": "564d8cbe", "A0": 53, "LIMIT": 675.0, "MAIN_SRC_READS": 2, "N_DW": 2, "N_DO": 2, "CARD": "164-3-4",
       "STEP_TXT": "P5-2 step 4",
       "NOTE": "RING P5-2 step 4 (PD397(d), PD398, PD399; groups J in the P4 delete form + K3 = A53..A71) on the saved p5s02c file "
               "D1_ring_p5s02c_20261010_125755.vi (564d8cbe), planned on its real graph 3d5196ab (prep_c164_a3_1_mk.py); start = "
               "stage_prerun.x10_start; MAIN <= 675"}
sys.exit(LB.pred(CFG))
