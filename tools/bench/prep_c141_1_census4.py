r"""prep_c141_1_census4 - card 141-1 (offline, read-only): every v15 create action with a `prim` (prim, class, donor) and the
label main_vi_node_labels.json gives a `$work` donor uid; the file's shape.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c141_1_census4.log -- py -u tools/bench/prep_c141_1_census4.py"""
import collections, json, os, sys                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
J = lambda p: json.load(open(os.path.join(B, p), encoding="utf-8"))                     # noqa: E731
L = J("main_vi_node_labels.json")
print("labels type", type(L).__name__, (list(L.keys())[:5] if isinstance(L, dict) else L[:3]))
if isinstance(L, dict):
    for k in list(L.keys())[:3]:
        print("  key", k, json.dumps(L[k])[:300])
c = collections.Counter()
for k, a in enumerate(J("plan_ring_p4_v15.json")["actions"], 1):
    if a["op"] == "create" and a.get("prim"):
        dn = a.get("donor") or {}
        c[(a["prim"], a.get("class"), os.path.basename(str(dn.get("donor"))), dn.get("uid"))] += 1
for k, v in sorted(c.items(), key=str):
    print("PRIM", v, k)
print(protocol.result_line(protocol.make_result(1, 0, None, [])), flush=True)
