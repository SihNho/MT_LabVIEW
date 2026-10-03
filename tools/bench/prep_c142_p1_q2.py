r"""prep_c142_p1_q2 - card 142-P1 (OFFLINE, read-only). Which fields the s01 graph JSON carries per terminal/object (is there a
LabVIEW TYPE field?), and the rows of the bed endpoints v17's non-repair actions name. Existing: vigraph.py helpers (node_of,
node_class) - used here; no type reader exists in the plan files (KEYS listing in prep_c142_p1_q1.log has no type key).
PREDICTION CONTRACT: M0 graph md5 == f697a0b2...; graph has 'terminals' and 'objs'.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c142_p1_q2.log -- py -u tools/bench/prep_c142_p1_q2.py"""
import collections, hashlib, json, os, sys                                                   # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
GR = os.path.join(B, "graph_ring_p4s01_20261002_234419.json")
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:600]), flush=True)


m = hashlib.md5(open(GR, "rb").read()).hexdigest()
gate("M0 graph md5", m == "f697a0b21c3bdb481207318812a0adad", m)
g = json.load(open(GR, encoding="utf-8"))
gate("K graph keys", "terminals" in g and "objs" in g, sorted(g.keys()))
print("GRAPH keys", sorted(g.keys()))
for k, v in g.items():
    if not isinstance(v, (list, dict)):
        print("SCALAR", k, str(v)[:200])
T = g["terminals"]
print("TERM keys", sorted(set(k for r in T for k in r)))
print("TERM sample", json.dumps(T[0])[:500])
print("OBJ keys", sorted(set(k for o in g["objs"] if isinstance(o, dict) for k in o)))
print("OBJ sample", json.dumps(g["objs"][0])[:500])
want = [5058, 2626, 9503, 10068, 29240, 10177, 29777, 8936, 28844, 28809, 27373, 5119, 642, 10170, 10969, 3173, 9519, 23792, 23508,
        10757, 2765, 25240, 10850, 25344, 25339, 11336, 25382, 25371, 25573, 9227, 10544, 9603, 29616, 25582, 25545, 9647, 10465, 25557,
        29048, 29265, 29316, 29095, 29312, 29380, 29264, 29313, 28413, 29408, 29411]
byown = collections.defaultdict(list)
for r in T:
    byown[r.get("owner_uid")].append(r)
for u in want:
    rows = byown.get(u, [])
    o = next((x for x in g["objs"] if isinstance(x, dict) and x.get("uid") == u), None)
    print("NODE #{0} obj {1} | rows {2}".format(u, json.dumps(o)[:200] if o else None, len(rows)))
    for r in rows:
        print("   ", json.dumps(dict((k, v) for k, v in r.items()))[:300])
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
