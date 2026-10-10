# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-a2-3.md
# ---
r"""prep_c164_a2_3_pred - card 164-a2-3 (OFFLINE, no LabVIEW): plan_ring_p5s02d_pred.json for P5-2 step 4 (plan_ring_p5s02d.json 872822f3,
groups J + K3 = A53..A69, FINAL on the REAL 564d8cbe graph 3d5196ab, prep_c164_a2_2_mk.py) + the sink-gate census file
prep_c164_a2_3_session.json that stagekit.RingSession reads. Inputs only; the flow is prep_c164_a2_3_lib.pred (= prep_c163_a1_3_pred.py as a
function + the DW / DO delete gates of prep_c160_c3_1_pred.py + the session route rows). Run AFTER prep_c164_a2_3_licence.py and _el.py.
PREDICTION CONTRACT: M0 pins; RB plan FINAL, 17 actions == session, no negative uid, base = 3d5196ab with bed 564d8cbe; C 13 ops == session
  compile; E1 checkpoints == checkpoint_ops == session [0,1,4,5,9,10,12,13], each a step file with its recorded md5; X1 x10_plan_start ==
  x10_start(564d8cbe) == session start 581.8; X10 MAIN 642.5 <= 675, Executor peak 637.4; X17 PASS; DW 1 row (dw_cond #23489); DO 2 rows
  (#23042, #23501); OBJ LR7 / EQ7 / SK3L+R / KI3 / OK3 / IK3 bound; FM w_k3pass on #31517; WS every wire sink wired; RT 17 route rows, PASS;
  EL keyed; SG census written; SP pred keyed to the plan md5.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c164_a2_3_pred.log -- py -u tools/bench/prep_c164_a2_3_pred.py"""
import os, sys                                                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep_c164_a2_3_lib as LB                                                             # noqa: E402
B, T = LB.B, LB.T
RRP, SESS = os.path.join(B, "plan_ring_p5s02d.json"), os.path.join(B, "prep_c164_a2_2_session.json")
GRAPH = os.path.join(B, "graph_ring_p5s02c_20261010_131658.json")
CFG = {"RRP": RRP, "PP": os.path.join(B, "plan_ring_p5s02d_pred.json"), "SESS": SESS, "SGF": os.path.join(B, "prep_c164_a2_3_session.json"),
       "ELF": os.path.join(B, "errorlist_predicted_D1_ring_p5s02d_end.json"), "LIC": os.path.join(B, "plan_ring_p5s02d_licence.json"), "GRAPH": GRAPH,
       "PINS": {RRP: "872822f3", SESS: "746dd63c", GRAPH: "3d5196ab", os.path.join(B, "plan_ring_p5s02d_in.json"): "40c0e512",
                os.path.join(B, "memory_model.json"): "8fb432e4", os.path.join(T, "stagesim.py"): "95a162ba", os.path.join(T, "stagexec.py"): "a4df7e15",
                os.path.join(T, "stagekit.py"): "dd57c1ca", os.path.join(T, "stage_prerun.py"): "7605116f", os.path.join(T, "stage_shared.py"): "b688edd4"},
       "BEDVI_MD5_PREFIX": "564d8cbe", "A0": 53, "LIMIT": 675.0, "MAIN_SRC_READS": 2, "N_DW": 1, "N_DO": 2, "CARD": "164-a2-3",
       "STEP_TXT": "P5-2 step 4",
       "NOTE": "RING P5-2 step 4 (PD397(d), PD398; groups J + K3 = A53..A69) on the saved p5s02c file D1_ring_p5s02c_20261010_125755.vi (564d8cbe), "
               "planned on its real graph 3d5196ab (prep_c164_a2_2_mk.py); start = stage_prerun.x10_start; MAIN <= 675"}
sys.exit(LB.pred(CFG))
