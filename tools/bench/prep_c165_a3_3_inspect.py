# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_165-3-3.md
# ---
r"""prep_c165_a3_3_inspect - card 165-3-3 (OFFLINE, read-only): print the step-5 plan rows, the 165-3-2 session keys / compile, the expected Error
List c74200f2 rows that name w_k3f / w_k4f or a uid this plan touches, so the CFGs of the step-5 drivers are filled from files. Prints only.
PREDICTION: 13 actions A72..A84; session compile 9 ops.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c165_a3_3_inspect.log -- py -u tools/bench/prep_c165_a3_3_inspect.py"""
import json, os, sys                                                                        # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep_c164_a2_3_lib as LB                                                             # noqa: E402
B, J = LB.B, LB.J
p = J(os.path.join(B, "plan_ring_p5s02e.json"))
print("KEYS", list(p.keys()))
for n, a in enumerate(p["actions"], 1):
    print("ACT", n, json.dumps(a)[:400])
fz = p["finalized"]
print("FZ keys", list(fz.keys()))
print("FZ base", fz["base"], "plan_in", fz.get("plan_in"))
print("STEPFILES", [(x["n"], x["path"]) for x in fz["step_files"]])
s = J(os.path.join(B, "prep_c165_a3_2_session.json"))
print("SESS keys", list(s.keys()))
print("SESS compile", s.get("compile"))
print("SESS x10", s.get("x10"), "start", s.get("start_mb"), s.get("start"))
print("SESS frame_map", s.get("frame_map"))
print("SESS plan", s.get("plan"), "actions", s.get("actions"))
ex = J(os.path.join(B, "errorlist_expected_D1_ring_p5s02d_20261010_152518.json"))
print("EX keys", list(ex.keys()), "total", ex.get("total"), "measured_from", ex.get("measured_from"))
AID = set(a["id"] for a in p["actions"])
TOUCH = set(u for a in p["actions"] for u in LB.base_uids(a))
for r in ex["expected"]:
    cb = r.get("clears_by") or {}
    ou = (r.get("object") or {}).get("uid")
    print("EXROW item {0} class {1} uid {2} count {3} clears_by {4} touched {5} stale {6}".format(
        r.get("item"), r.get("class"), ou, r.get("count"), json.dumps(cb)[:160], ou is not None and int(ou) in TOUCH, LB.is_stale(r, AID)))
pd = J(os.path.join(B, "prep_c165_a3_2_pd401b.json"))
print("PD401B", json.dumps(pd)[:1500])
print("RESULT {\"schema\":\"result-line/1\",\"status\":\"PASS\",\"gates\":{\"pass\":1,\"fail\":0},\"first_fail\":null,\"artefacts\":[]}")
