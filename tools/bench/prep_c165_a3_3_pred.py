# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_165-3-3.md
# ---
r"""prep_c165_a3_3_pred - card 165-3-3 (OFFLINE, no LabVIEW): plan_ring_p5s02e_pred.json + the sink-gate census prep_c165_a3_3_sg.json (the file
the step-5 recipes read) on plan fd23974e. Inputs only; the flow is prep_c164_a2_3_lib.pred (called); CFG of prep_c164_a3_6_pred.py with the step-5
plan / session / graph pins. Run AFTER _licence.py and _el.py; then prep_c165_a3_3_pd402.py adds keys pd401b / pd402.
PREDICTION CONTRACT (diag_c165_a3_2_facts.md): 13 actions, 9 ops, E1 [0,1,3,4,6,7,8,9], START from stage_prerun.x10_start(6dcd5c3d) == session 609.8,
  MAIN 665.0 <= 675, peak 659.9, X17, DW 2, DO 0, RT PASS, SP keyed to fd23974e.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c165_a3_3_pred.log -- py -u tools/bench/prep_c165_a3_3_pred.py"""
import os, sys                                                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep_c164_a2_3_lib as LB                                                             # noqa: E402
B, T = LB.B, LB.T
RRP, SESS = os.path.join(B, "plan_ring_p5s02e.json"), os.path.join(B, "prep_c165_a3_2_session.json")
GRAPH = os.path.join(B, "graph_ring_p5s02d_20261010_154830.json")
CFG = {"RRP": RRP, "PP": os.path.join(B, "plan_ring_p5s02e_pred.json"), "SESS": SESS, "SGF": os.path.join(B, "prep_c165_a3_3_sg.json"),
       "ELF": os.path.join(B, "errorlist_predicted_D1_ring_p5s02e_end.json"), "LIC": os.path.join(B, "plan_ring_p5s02e_licence.json"), "GRAPH": GRAPH,
       "PINS": {RRP: "fd23974e", GRAPH: "2a5fa0c4", os.path.join(B, "plan_ring_p5s02e_in.json"): "b5b35f8a",
                os.path.join(B, "plan_ring_p5s02r_in.json"): "0b895983",
                os.path.join(B, "memory_model.json"): "ff0fabca", os.path.join(T, "stagesim.py"): "95a162ba", os.path.join(T, "stagexec.py"): "1d5309f4",
                os.path.join(T, "stagekit.py"): "dd57c1ca", os.path.join(T, "stage_prerun.py"): "7605116f", os.path.join(T, "stage_shared.py"): "b688edd4"},
       "BEDVI_MD5_PREFIX": "6dcd5c3d", "A0": 72, "LIMIT": 675.0, "MAIN_SRC_READS": 2, "N_DW": 2, "N_DO": 0, "CARD": "165-3-3",
       "STEP_TXT": "P5-2 step 5",
       "NOTE": "RING P5-2 step 5 (PD400, PD401, PD402; groups K3f + K4 + K4f = A72..A84) on the saved p5s02d file "
               "D1_ring_p5s02d_20261010_152518.vi (6dcd5c3d), planned on its real graph 2a5fa0c4 (prep_c165_a3_2_mk.py, plan_in "
               "plan_ring_p5s02e_in.json); start = stage_prerun.x10_start; MAIN <= 675; PRIME-SKIP #8776 / #24342 (stagexec 1d5309f4, card 165-3-1)"}
sys.exit(LB.pred(CFG))
