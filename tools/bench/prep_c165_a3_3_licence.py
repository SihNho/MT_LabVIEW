# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_165-3-3.md
# ---
r"""prep_c165_a3_3_licence - card 165-3-3 (OFFLINE, json only): plan_ring_p5s02e_licence.json on plan fd23974e (step 5, K3f + K4 + K4f,
A72..A84). Inputs only; the flow is prep_c164_a2_3_lib.licence (called), CFG of prep_c164_a3_6_licence.py with the step-5 plan, the 165-3-2
session and this card's X11 log (py tools/stage_prerun.py --buildarray-check tools/bench/plan_ring_p5s02e.json -> prep_c165_a3_3_x11.log).
PREDICTION CONTRACT: L0 plan md5 == prep_c165_a3_2_session.json's (fd23974e); X11 == the log; R renames (zero allowed); W read-back; X11 after.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c165_a3_3_licence.log -- py -u tools/bench/prep_c165_a3_3_licence.py"""
import os, sys                                                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep_c164_a2_3_lib as LB                                                             # noqa: E402
B = LB.B
CFG = {"PLAN": os.path.join(B, "plan_ring_p5s02e.json"), "LIC": os.path.join(B, "plan_ring_p5s02e_licence.json"),
       "X11LOG": os.path.join(B, "prep_c165_a3_3_x11.log"), "SESS": os.path.join(B, "prep_c165_a3_2_session.json"),
       "STAGE": "ring_p5s02e", "CARD": "165-3-3", "STEP_TXT": "P5-2 step 5 (groups K3f + K4 + K4f, A72..A84)",
       "PD": "docs/d1/ring-p5c.md PD400, PD401, PD402", "PRECEDENT": "tools/bench/plan_ring_p5s02d_licence.json (card 164-3-6)",
       "MAKER": "tools/bench/prep_c165_a3_3_licence.py"}
sys.exit(LB.licence(CFG))
