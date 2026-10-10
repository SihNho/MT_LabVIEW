# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-3-6.md
# ---
r"""prep_c164_a3_6_el - card 164-3-6 (OFFLINE, json only): the PREDICTED step-4-end Error List on the plan RE-MADE by prep_c164_a3_6_mk.py
(97837e2a) -> tools/bench/errorlist_predicted_D1_ring_p5s02d_end.json, from the 26d45c71 expected file (NOT edited). Inputs only; the flow is
prep_c164_a2_3_lib.el (called); CFG of prep_c164_a3_4_el.py with the new plan pin and the 164-3-6 session.
PREDICTION CONTRACT (as prep_c164_a3_4_el.log): cleared 0, raised 0, unpredicted 3 (A66 / A69 reb, A56 delobj), standing 53, stale 6, total 53
  (upper 56); compare 0/0.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c164_a3_6_el.log -- py -u tools/bench/prep_c164_a3_6_el.py"""
import os, sys                                                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep_c164_a2_3_lib as LB                                                             # noqa: E402
B = LB.B
PLAN, SESS = os.path.join(B, "plan_ring_p5s02d.json"), os.path.join(B, "prep_c164_a3_6_session.json")
EXPF = os.path.join(B, "errorlist_expected_D1_ring_p5s02c_20261010_125755.json")
GRAPH = os.path.join(B, "graph_ring_p5s02c_20261010_131658.json")
CFG = {"PLAN": PLAN, "SESS": SESS, "EXPF": EXPF, "OUT": os.path.join(B, "errorlist_predicted_D1_ring_p5s02d_end.json"),
       "PINS": {EXPF: "26d45c71", PLAN: "97837e2a", GRAPH: "3d5196ab"}, "A0": 53, "N_REB": 2,
       "STEP_TXT": "P5-2 step 4, groups J (P4 delete form) + K3 A53..A71", "CARD": "164-3-6 (docs/d1/ring-p5c.md PD397(d), PD398, PD399)",
       "MAKER": "tools/bench/prep_c164_a3_6_el.py", "ELR_SPAN": "step_00 -> step_19 of tools/bench/sim/ring_p5s02d",
       "UNPRED_WHY": {"reb": "connect_term_uid register_end_case_border (tunnel + register face through the case border, new SR SK3): step 2's same verb "
                             "left +2 'Wire has loose ends.' items (diag_c162_a1_2_facts.md), step 3's left none (diag_c163_a2_2_facts.md:31); not "
                             "decidable offline - the step-4 scratch measures it",
                      "delobj": "delete_object of an object that still carries a wire in the sim pre-state (PD399(a): w23519 keeps its source t8494 and "
                                "sinks t23450 / t23241 / t7606; the next row wire_remove_loose_ends w23519 removes the stub): whether LabVIEW leaves a "
                                "loose-end item at step end is outside tools/elrule.py's classes (L / C / SR / A); the step-4 scratch measures it"}}
sys.exit(LB.el(CFG))
