# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-3-6.md
# ---
r"""prep_c164_a3_6_licence - card 164-3-6 (OFFLINE, json only): plan_ring_p5s02d_licence.json on the plan RE-MADE by prep_c164_a3_6_mk.py
(97837e2a; rows == 725cd68e, only plan_in name differs). Inputs only; the flow is prep_c164_a2_3_lib.licence (called), the CFG of
prep_c164_a3_4_licence.py with the 164-3-6 session and X11 log.
PREDICTION CONTRACT: L0 plan md5 == prep_c164_a3_6_session.json's; X11 CLEAN (prep_c164_a3_6_x11.log); R 0 renames; W read-back; X11 after.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c164_a3_6_licence.log -- py -u tools/bench/prep_c164_a3_6_licence.py"""
import os, sys                                                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep_c164_a2_3_lib as LB                                                             # noqa: E402
B = LB.B
CFG = {"PLAN": os.path.join(B, "plan_ring_p5s02d.json"), "LIC": os.path.join(B, "plan_ring_p5s02d_licence.json"),
       "X11LOG": os.path.join(B, "prep_c164_a3_6_x11.log"), "SESS": os.path.join(B, "prep_c164_a3_6_session.json"),
       "STAGE": "ring_p5s02d", "CARD": "164-3-6", "STEP_TXT": "P5-2 step 4 (groups J + K3, A53..A71)",
       "PD": "docs/d1/ring-p5c.md PD397(d), PD398, PD399", "PRECEDENT": "tools/bench/plan_ring_p5s02c_licence.json (card 163-a1-3)",
       "MAKER": "tools/bench/prep_c164_a3_6_licence.py"}
sys.exit(LB.licence(CFG))
