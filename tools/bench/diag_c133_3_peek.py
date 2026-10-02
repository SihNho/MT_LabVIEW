r"""diag_c133_3_peek - card 133-3 (OFFLINE, read-only): list the 39 actions of plan_ring_p3b2.json (04204133) with their
compiled op kinds, the finalized keys, and the meter lines cited for the X10 start term. No LabVIEW. PREDICTION: 39 actions,
39 ops; the cited lines carry 561.8 / 567.7 / 584.1 MB.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c133_3_peek.log -- py -u tools/bench/diag_c133_3_peek.py"""
import json, os, sys                                                                 # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, stagexec as SX                                                 # noqa: E402,E401
p = json.load(open(os.path.join(B, "plan_ring_p3b2.json"), encoding="utf-8"))
ops = SX.compile_plan(p)
k2op = dict((n, (k, o["kind"])) for k, o in enumerate(ops, 1) for n in o["acts"])
for k, a in enumerate(p["actions"], 1):
    print(k, k2op.get(k), a["op"], a["id"], a.get("as", ""), a.get("class", ""), str(a.get("diagram", ""))[:12],
          str(a.get("src", ""))[:50], str(a.get("dst", ""))[:50], a.get("of", ""), flush=True)
fz = p["finalized"]
print("FINALIZED keys", sorted(fz), "route", (fz.get("route_check") or {}).get("status"), "base", p.get("base"), flush=True)
print("FS_ROUTES", json.dumps(fz.get("fs_routes"))[:1500], flush=True)
for f, lines in (("stage_d1_ring_p3b1.log", (41, 42, 43)), ("diag_c132_2_graph_p3b1.log", (23, 24, 25))):
    L = open(os.path.join(B, f), encoding="utf-8", errors="replace").read().splitlines()
    for n in lines:
        print("CITE {0}:{1}: {2}".format(f, n, L[n - 1][:220]), flush=True)
print(P.result_line(P.make_result(1 if len(ops) == 39 else 0, 0 if len(ops) == 39 else 1, None, [])), flush=True)
