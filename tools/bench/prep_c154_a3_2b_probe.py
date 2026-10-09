# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_154-a3-2b.md
# ---
r"""prep_c154_a3_2b_probe - card 154-a3-2b: read-only key census of the inputs the P5-1a pred/recipes copy from (no LabVIEW, json only).
PREDICTION CONTRACT: prints keys only; RESULT 1/0.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c154_a3_2b_probe.log -- py -u tools/bench/prep_c154_a3_2b_probe.py"""
import json, os, sys                                                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
J = lambda n: json.load(open(os.path.join(B, n), encoding="utf-8"))                          # noqa: E731
sh = lambda d: dict((k, (v if not isinstance(v, (list, dict)) else type(v).__name__ + str(len(v)))) for k, v in d.items())   # noqa: E731
g = J("graph_ring_p4s09_20261009_062044.json")
print("GRAPH", sh(g))
p = J("plan_ring_p4_s09v18_pred.json")
print("PRED09 keys", list(p))
print("PRED09", p["census"], p["census_overall"], p["census_unpredicted"], p["graph"], p["bed"], p["bed_md5"])
print("PRED09 errorlist keys", list(p["errorlist"]), "memory_pred", sh(p["memory_pred"]))
q = J("plan_ring_p5s01.json")
print("P5 keys", list(q), "base", q["base"])
print("P5 finalized", sh(q["finalized"]))
print("P5 fz base", q["finalized"]["base"], "plan_in", q["finalized"]["plan_in"])
s9 = J("plan_ring_p4_s09v18.json")
print("S09 finalized", sh(s9["finalized"]), "base", s9["finalized"]["base"])
e = J("errorlist_expected_D1_ring_p4s09_20261009_060515.json")
print("ELEXP", sh(e))
ss = J("prep_c152_b2_1_session.json")
print("SESS09", sh(ss))
print(protocol.result_line(protocol.make_result(1, 0, None, [])), flush=True)
