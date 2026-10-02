r"""prep_c141_1_census - card 141-1 (offline, read-only): the 5 bed slot-write nodes (#27928 #28916 #29048 #29265 #29316) on
the P3b-2b bed graph graph_ring_p3b2b_20261002_133824.json: every terminal row, and for each wire every other endpoint (owner,
class, term, frame, source/sink), so the repair rows of v16 are derived from the graph (PD323(a)). Also the p3b plan actions that
made each node and its wires, and every v15 action that names one of these uids / wires.
PREDICTION: each node 4 rows (array, output array, index, new element/subarray), all wired; w28367 shared by #29048/#29265/#29316.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c141_1_census.log -- py -u tools/bench/prep_c141_1_census.py"""
import json, os, sys                                                                     # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
J = lambda p: json.load(open(os.path.join(B, p), encoding="utf-8"))                     # noqa: E731
gr = J("graph_ring_p3b2b_20261002_133824.json")
T = gr["terminals"]
NODES = [27928, 28916, 29048, 29265, 29316]
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:600]), flush=True)


print("graph keys", sorted(gr.keys()))
objs = dict((int(o["uid"]), o) for o in gr.get("objs") or gr.get("objects") or [])
allw = {}
for r in T:
    if r.get("wire_uid"):
        allw.setdefault(int(r["wire_uid"]), []).append(r)
for u in NODES:
    rows = [r for r in T if r["owner_uid"] == u]
    print("NODE #{0} obj {1} | {2} rows".format(u, objs.get(u), len(rows)))
    for r in rows:
        w = r.get("wire_uid")
        print("  ROW t{0} {1!r} src={2} cls={3} frame={4} wire={5}".format(r["term_uid"], r["term_name"], r["is_source"], r["term_class"],
                                                                          r["frame_diagram"], w))
        for o in allw.get(int(w or 0), []):
            if o is r:
                continue
            print("      OTHER #{0} {1} t{2} {3!r} src={4} tcls={5} frame={6}".format(o["owner_uid"], o["owner_class"], o["term_uid"],
                                                                                    o["term_name"], o["is_source"], o["term_class"], o["frame_diagram"]))
    gate("N{0} 4 rows all wired".format(u), len(rows) == 4 and all(r.get("wire_uid") for r in rows), len(rows))
sh = [r["owner_uid"] for r in allw.get(28367, []) if not r["is_source"]]
gate("W w28367 sinks include #29048 #29265 #29316", set([29048, 29265, 29316]) <= set(sh), sh)
print("fs_tunnel_pairs n", len(gr.get("fs_tunnel_pairs") or []))
for pn in ("plan_ring_p3b1.json", "plan_ring_p3b2a.json", "plan_ring_p3b2b.json"):
    p = J(pn)
    for a in p["actions"]:
        s = json.dumps(a)
        if "ras" in a["id"] or "_r_" in a["id"] or "IAN" in s:
            print("P3B", pn, json.dumps(a)[:400])
v15 = J("plan_ring_p4_v15.json")
ws = set(int(r["wire_uid"]) for u in NODES for r in T if r["owner_uid"] == u and r.get("wire_uid"))
for k, a in enumerate(v15["actions"], 1):
    s = json.dumps(a)
    hit = [u for u in NODES if str(u) in s] + [w for w in ws if str(w) in s]
    if hit:
        print("V15", k, a["id"], hit, s[:300])
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
