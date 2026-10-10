# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-a2-3.md
# ---
r"""prep_c164_a2_3_licence - card 164-a2-3 (OFFLINE, json only): plan_ring_p5s02d_licence.json for P5-2 step 4 (plan_ring_p5s02d.json 872822f3,
groups J + K3 = A53..A69). Inputs only; the flow is prep_c164_a2_3_lib.licence (= prep_c163_a1_3_licence.py as a function).
PREDICTION CONTRACT: L0 plan md5 == session table's; X11 flags == the --buildarray-check log (prep_c164_a2_3_x11.log: CLEAN, 0 flags); R renames
(ZERO ALLOWED; no step-4 row wires a base sink BY TERM UID - w_k3out's term uid 5704 is a SOURCE); W read-back; X11 after.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c164_a2_3_licence.log -- py -u tools/bench/prep_c164_a2_3_licence.py"""
import os, sys                                                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep_c164_a2_3_lib as LB                                                             # noqa: E402
B = LB.B
CFG = {"PLAN": os.path.join(B, "plan_ring_p5s02d.json"), "LIC": os.path.join(B, "plan_ring_p5s02d_licence.json"),
       "X11LOG": os.path.join(B, "prep_c164_a2_3_x11.log"), "SESS": os.path.join(B, "prep_c164_a2_2_session.json"),
       "STAGE": "ring_p5s02d", "CARD": "164-a2-3", "STEP_TXT": "P5-2 step 4 (groups J + K3, A53..A69)", "PD": "docs/d1/ring-p5c.md PD397(d), PD398",
       "PRECEDENT": "tools/bench/plan_ring_p5s02c_licence.json (card 163-a1-3)", "MAKER": "tools/bench/prep_c164_a2_3_licence.py"}
sys.exit(LB.licence(CFG))
