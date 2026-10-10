# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-a2-3.md
# ---
r"""prep_c164_a2_3_el - card 164-a2-3 (OFFLINE, json only): the PREDICTED step-4-end Error List of P5-2 step 4 (groups J + K3 = A53..A69,
plan_ring_p5s02d.json 872822f3) -> tools/bench/errorlist_predicted_D1_ring_p5s02d_end.json, item by item from the 53-item expected file of the
564d8cbe bed (errorlist_expected_D1_ring_p5s02c_20261010_125755.json 26d45c71, NOT edited). Inputs only; the flow is prep_c164_a2_3_lib.el
(= prep_c163_a1_3_el.py as a function, + delete rows' uids as named, + stale = clears_by action not in the plan, + delete_object with wires
UNPREDICTED).
PREDICTION CONTRACT: M0 pins; B compare(read 53, file) 0/0; CL cleared rows each tied to an A53..A69 action (0 expected: no row's object is
#23489 / #23042 / #23501 or another named base uid); ST stale = items 4, 6, 7 (A70 w_k3f) and 8, 49, 50 (A80 w_k4f) - not in this plan; R elrule
new items attributed (0 expected: cond re-wired by A60, LR7 / EQ7 / KI3 / SK3 wired at the end); U = the 2 register_end_case_border groups A64 /
A67 (+ each delete_object row whose sim pre-state carries wires); F / PC / W (the file's own entries accepted by errorlist_check.compare).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c164_a2_3_el.log -- py -u tools/bench/prep_c164_a2_3_el.py"""
import os, sys                                                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep_c164_a2_3_lib as LB                                                             # noqa: E402
B = LB.B
PLAN, SESS = os.path.join(B, "plan_ring_p5s02d.json"), os.path.join(B, "prep_c164_a2_2_session.json")
EXPF = os.path.join(B, "errorlist_expected_D1_ring_p5s02c_20261010_125755.json")
GRAPH = os.path.join(B, "graph_ring_p5s02c_20261010_131658.json")
CFG = {"PLAN": PLAN, "SESS": SESS, "EXPF": EXPF, "OUT": os.path.join(B, "errorlist_predicted_D1_ring_p5s02d_end.json"),
       "PINS": {EXPF: "26d45c71", PLAN: "872822f3", SESS: "746dd63c", GRAPH: "3d5196ab"}, "A0": 53, "N_REB": 2,
       "STEP_TXT": "P5-2 step 4, groups J + K3 A53..A69", "CARD": "164-a2-3 (docs/d1/ring-p5c.md PD397(d), PD398)", "MAKER": "tools/bench/prep_c164_a2_3_el.py",
       "ELR_SPAN": "step_00 -> step_17 of tools/bench/sim/ring_p5s02d",
       "UNPRED_WHY": {"reb": "connect_term_uid register_end_case_border (tunnel + register face through the case border, new SR SK3): step 2's same verb "
                             "left +2 'Wire has loose ends.' items (diag_c162_a1_2_facts.md), step 3's left none (diag_c163_a2_2_facts.md:31); not "
                             "decidable offline - the step-4 scratch measures it",
                      "delobj": "delete_object of an object that carries wires in the sim pre-state: whether LabVIEW leaves the wires as loose-end / "
                                "no-source items is outside tools/elrule.py's classes (L / C / SR / A); the step-4 scratch measures it"}}
sys.exit(LB.el(CFG))
