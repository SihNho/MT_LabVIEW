# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-3-4.md
# ---
r"""prep_c164_a3_4_el - card 164-3-4 (OFFLINE, json only): the PREDICTED step-4-end Error List of P5-2 step 4 on the re-made plan
plan_ring_p5s02d.json 725cd68e (J in the P4 delete form + K3 = A53..A71) -> tools/bench/errorlist_predicted_D1_ring_p5s02d_end.json,
item by item from the 53-item expected file of the 564d8cbe bed (errorlist_expected_D1_ring_p5s02c_20261010_125755.json 26d45c71,
NOT edited). Inputs only; the flow is prep_c164_a2_3_lib.el (called, not copied).
PREDICTION CONTRACT: M0 pins; B compare(read 53, file) 0/0; CL cleared rows each tied to an A53..A71 action; ST stale = the rows whose
clears_by names an action outside this plan (K3f / K4f, step 5); R elrule new items attributed; U = the 2 register_end_case_border
groups (A66 t_k3o, A69 t_k3i) + each delete_object row whose sim pre-state still carries a wire (A56 do_23501: w23519, kept, cleaned
by A57 rle_23519); F / PC / W (the file's own entries accepted by errorlist_check.compare).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c164_a3_4_el.log -- py -u tools/bench/prep_c164_a3_4_el.py"""
import os, sys                                                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep_c164_a2_3_lib as LB                                                             # noqa: E402
B = LB.B
PLAN, SESS = os.path.join(B, "plan_ring_p5s02d.json"), os.path.join(B, "prep_c164_a3_1_session.json")
EXPF = os.path.join(B, "errorlist_expected_D1_ring_p5s02c_20261010_125755.json")
GRAPH = os.path.join(B, "graph_ring_p5s02c_20261010_131658.json")
CFG = {"PLAN": PLAN, "SESS": SESS, "EXPF": EXPF, "OUT": os.path.join(B, "errorlist_predicted_D1_ring_p5s02d_end.json"),
       "PINS": {EXPF: "26d45c71", PLAN: "725cd68e", SESS: "2aeaef24", GRAPH: "3d5196ab"}, "A0": 53, "N_REB": 2,
       "STEP_TXT": "P5-2 step 4, groups J (P4 delete form) + K3 A53..A71", "CARD": "164-3-4 (docs/d1/ring-p5c.md PD397(d), PD398, PD399)",
       "MAKER": "tools/bench/prep_c164_a3_4_el.py", "ELR_SPAN": "step_00 -> step_19 of tools/bench/sim/ring_p5s02d",
       "UNPRED_WHY": {"reb": "connect_term_uid register_end_case_border (tunnel + register face through the case border, new SR SK3): step 2's same verb "
                             "left +2 'Wire has loose ends.' items (diag_c162_a1_2_facts.md), step 3's left none (diag_c163_a2_2_facts.md:31); not "
                             "decidable offline - the step-4 scratch measures it",
                      "delobj": "delete_object of an object that still carries a wire in the sim pre-state (PD399(a): w23519 keeps its source t8494 and "
                                "sinks t23450 / t23241 / t7606; the next row wire_remove_loose_ends w23519 removes the stub): whether LabVIEW leaves a "
                                "loose-end item at step end is outside tools/elrule.py's classes (L / C / SR / A); the step-4 scratch measures it"}}
sys.exit(LB.el(CFG))
