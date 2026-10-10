# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-3-4.md
# ---
r"""prep_c164_a3_4_licence - card 164-3-4 (OFFLINE, json only): plan_ring_p5s02d_licence.json for P5-2 step 4 on the RE-MADE plan
plan_ring_p5s02d.json 725cd68e (groups J in the P4 delete form + K3 = A53..A71, card 164-3-1). Inputs only; the flow is
prep_c164_a2_3_lib.licence (called, not copied).
PREDICTION CONTRACT: L0 plan md5 == session table's (prep_c164_a3_1_session.json); X11 flags == the --buildarray-check log
(prep_c164_a3_4_x11.log: CLEAN, 0 flags); R renames (ZERO ALLOWED); W read-back; X11 after.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c164_a3_4_licence.log -- py -u tools/bench/prep_c164_a3_4_licence.py"""
import os, sys                                                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep_c164_a2_3_lib as LB                                                             # noqa: E402
B = LB.B
CFG = {"PLAN": os.path.join(B, "plan_ring_p5s02d.json"), "LIC": os.path.join(B, "plan_ring_p5s02d_licence.json"),
       "X11LOG": os.path.join(B, "prep_c164_a3_4_x11.log"), "SESS": os.path.join(B, "prep_c164_a3_1_session.json"),
       "STAGE": "ring_p5s02d", "CARD": "164-3-4", "STEP_TXT": "P5-2 step 4 (groups J + K3, A53..A71)",
       "PD": "docs/d1/ring-p5c.md PD397(d), PD398, PD399", "PRECEDENT": "tools/bench/plan_ring_p5s02c_licence.json (card 163-a1-3)",
       "MAKER": "tools/bench/prep_c164_a3_4_licence.py"}
sys.exit(LB.licence(CFG))
