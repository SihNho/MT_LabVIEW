# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-3-6.md
# ---
r"""prep_c164_a3_6_pred - card 164-3-6 (OFFLINE, no LabVIEW): plan_ring_p5s02d_pred.json + the sink-gate census prep_c164_a3_4_session.json
(the file the recipes read) on the plan RE-MADE by prep_c164_a3_6_mk.py (97837e2a, plan_in plan_ring_p5s02d_in2.json). Inputs only; the flow is
prep_c164_a2_3_lib.pred (called); CFG of prep_c164_a3_4_pred.py with the new plan / plan_in / session pins. Run AFTER _licence.py and _el.py;
then prep_c164_a3_4_pd399.py 97837e2a adds key pd399a.
PREDICTION CONTRACT (as prep_c164_a3_4_pred.log): 19 actions, 15 ops, E1 [0,1,2,6,7,11,12,14,15], START 581.8, MAIN 647.8, peak 642.7, X17,
  DW 2, DO 2, WS, RT PASS, SP keyed to 97837e2a.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c164_a3_6_pred.log -- py -u tools/bench/prep_c164_a3_6_pred.py"""
import os, sys                                                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep_c164_a2_3_lib as LB                                                             # noqa: E402
B, T = LB.B, LB.T
RRP, SESS = os.path.join(B, "plan_ring_p5s02d.json"), os.path.join(B, "prep_c164_a3_6_session.json")
GRAPH = os.path.join(B, "graph_ring_p5s02c_20261010_131658.json")
CFG = {"RRP": RRP, "PP": os.path.join(B, "plan_ring_p5s02d_pred.json"), "SESS": SESS, "SGF": os.path.join(B, "prep_c164_a3_4_session.json"),
       "ELF": os.path.join(B, "errorlist_predicted_D1_ring_p5s02d_end.json"), "LIC": os.path.join(B, "plan_ring_p5s02d_licence.json"), "GRAPH": GRAPH,
       "PINS": {RRP: "97837e2a", GRAPH: "3d5196ab", os.path.join(B, "plan_ring_p5s02d_in2.json"): "dc309d2c",
                os.path.join(B, "plan_ring_p5s02r_in.json"): "9dadb0c1",
                os.path.join(B, "memory_model.json"): "8fb432e4", os.path.join(T, "stagesim.py"): "95a162ba", os.path.join(T, "stagexec.py"): "a4df7e15",
                os.path.join(T, "stagekit.py"): "dd57c1ca", os.path.join(T, "stage_prerun.py"): "7605116f", os.path.join(T, "stage_shared.py"): "b688edd4"},
       "BEDVI_MD5_PREFIX": "564d8cbe", "A0": 53, "LIMIT": 675.0, "MAIN_SRC_READS": 2, "N_DW": 2, "N_DO": 2, "CARD": "164-3-6",
       "STEP_TXT": "P5-2 step 4",
       "NOTE": "RING P5-2 step 4 (PD397(d), PD398, PD399; groups J in the P4 delete form + K3 = A53..A71) on the saved p5s02c file "
               "D1_ring_p5s02c_20261010_125755.vi (564d8cbe), planned on its real graph 3d5196ab (prep_c164_a3_1_mk.py, re-made with plan_in "
               "plan_ring_p5s02d_in2.json by prep_c164_a3_6_mk.py); start = stage_prerun.x10_start; MAIN <= 675"}
sys.exit(LB.pred(CFG))
