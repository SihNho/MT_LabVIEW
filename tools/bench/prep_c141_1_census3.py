r"""prep_c141_1_census3 - card 141-1 (offline, read-only): action id/op/of lists of the P3b-2a/2b plans and v15 #1..#40; the
fs_border_entries the simulator derives from the bed graph for the 5 slot-write frames; the v15 meta session table keys.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c141_1_census3.log -- py -u tools/bench/prep_c141_1_census3.py"""
import json, os, sys                                                                     # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
J = lambda p: json.load(open(os.path.join(B, p), encoding="utf-8"))                     # noqa: E731
for pn in ("plan_ring_p3b2a.json", "plan_ring_p3b2b.json"):
    for k, a in enumerate(J(pn)["actions"], 1):
        print("A", pn, k, a["id"], a["op"], a.get("of") or "", a.get("wire_uid") or "")
v15 = J("plan_ring_p4_v15.json")
for k, a in enumerate(v15["actions"][:45], 1):
    print("V15", k, a["id"], a["op"], a.get("of") or "", json.dumps(a.get("src"))[:60] if a.get("src") else "", json.dumps(a.get("dst"))[:60] if a.get("dst") else "")
gr = J("graph_ring_p3b2b_20261002_133824.json")
m = SS.fs_measured_state(gr)
for k, v in sorted(m["fs_border_entries"].items()):
    if k.endswith(("|32464", "|27722", "|27641")):
        print("ENTRY", k, v)
for u in (28395, 29235, 28413, 29243, 29408, 29411):
    print("BORDER", u, m["borders"].get(u))
meta = J("plan_ring_p4_v15_meta.json")
print("META keys", list(meta.keys()))
print("META", json.dumps({k: v for k, v in meta.items() if k != "actions"})[:3000])
print("META actions[:3]", json.dumps(meta["actions"][:3])[:800])
print(protocol.result_line(protocol.make_result(1, 0, None, [])), flush=True)
