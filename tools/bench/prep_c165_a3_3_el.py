# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_165-3-3.md
# ---
r"""prep_c165_a3_3_el - card 165-3-3 (OFFLINE, json only): the PREDICTED step-5-end Error List on plan fd23974e -> errorlist_predicted_D1_ring_p5s02e_end.json,
from the expected file c74200f2 (errorlist_expected_D1_ring_p5s02d_20261010_152518.json, NOT edited). Inputs only; the flow is prep_c164_a2_3_lib.el
(called), CFG of prep_c164_a3_6_el.py with the step-5 plan / session / expected file. Before the call it PRINTS (facts only, no verdict change) every
expected row whose clears_by names an action of THIS plan (the step-4 stale rows A70 w_k3f / A80 w_k4f) with the lib's verdict: CLEARED (its object
uid is named by an action) or STANDING (uid not named; the lib keeps it).
PREDICTION CONTRACT: CL 4 cleared (items 6 / 7 / 8 / 50: uids 10362, 5204, 10404, 25232); ST 0 stale; U 2 reb groups (t_k4o, t_k4i); compare B / F / W 0/0.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c165_a3_3_el.log -- py -u tools/bench/prep_c165_a3_3_el.py"""
import os, sys                                                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep_c164_a2_3_lib as LB                                                             # noqa: E402
B, J = LB.B, LB.J
PLAN, SESS = os.path.join(B, "plan_ring_p5s02e.json"), os.path.join(B, "prep_c165_a3_2_session.json")
EXPF = os.path.join(B, "errorlist_expected_D1_ring_p5s02d_20261010_152518.json")
GRAPH = os.path.join(B, "graph_ring_p5s02d_20261010_154830.json")
A0 = 72
P = J(PLAN)
AID = dict((a["id"], A0 + n) for n, a in enumerate(P["actions"]))
TOUCH = dict((u, a["id"]) for a in P["actions"] for u in LB.base_uids(a))
for r in J(EXPF)["expected"]:
    nm = str(((r.get("clears_by") or {}).get("action")) or "")
    if nm and nm.split()[-1] in AID:
        ou = (r.get("object") or {}).get("uid")
        hit = ou is not None and int(ou) in TOUCH
        print("FACT NAMED item {0} {1} uid {2} clears_by '{3}' (now A{4} {5}) -> {6}".format(
            r.get("item"), r.get("class"), ou, nm, AID[nm.split()[-1]], nm.split()[-1],
            "CLEARED by A{0} {1} (uid named)".format(AID[TOUCH[int(ou)]], TOUCH[int(ou)]) if hit else
            "STANDING (uid not named by any action of this plan; lib el keeps the row)"), flush=True)
CFG = {"PLAN": PLAN, "SESS": SESS, "EXPF": EXPF, "OUT": os.path.join(B, "errorlist_predicted_D1_ring_p5s02e_end.json"),
       "PINS": {EXPF: "c74200f2", PLAN: "fd23974e", GRAPH: "2a5fa0c4"}, "A0": A0, "N_REB": 2,
       "STEP_TXT": "P5-2 step 5, groups K3f + K4 + K4f A72..A84", "CARD": "165-3-3 (docs/d1/ring-p5c.md PD400, PD401, PD402)",
       "MAKER": "tools/bench/prep_c165_a3_3_el.py", "ELR_SPAN": "step_00 -> step_13 of tools/bench/sim/ring_p5s02e",
       "UNPRED_WHY": {"reb": "connect_term_uid register_end_case_border (tunnel + register face through the case border, new SR SK4): step 2's same verb "
                             "left +2 'Wire has loose ends.' items (diag_c162_a1_2_facts.md), step 3's left none (diag_c163_a2_2_facts.md:31); not "
                             "decidable offline - the step-5 scratch measures it",
                      "delobj": "no delete_object row in this plan"}}
sys.exit(LB.el(CFG))
