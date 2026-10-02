r"""prep_c141_1_census2 - card 141-1 (offline, read-only): how the P3b plans wired the 5 slot-write nodes (every action naming
the aliases RAN3 / RAN1 / RAT1 / RAR1 / RAF1, plus the creates of their sources), and each finalized plan's fs_routes for those
actions; the outer sources of the FS tunnels feeding them (#28395 #29235 #28413 #29243 #29408 #29411) from the bed graph.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c141_1_census2.log -- py -u tools/bench/prep_c141_1_census2.py"""
import json, os, sys                                                                     # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
J = lambda p: json.load(open(os.path.join(B, p), encoding="utf-8"))                     # noqa: E731
AL = {"plan_ring_p3b1.json": ["RAN3"], "plan_ring_p3b2a.json": ["RAN1", "RAT1"], "plan_ring_p3b2b.json": ["RAR1", "RAF1"]}
for pn, als in AL.items():
    p = J(pn)
    A = p["actions"]
    fr = (p.get("finalized") or {}).get("fs_routes") or {}
    ids = dict((a["id"], k) for k, a in enumerate(A, 1))
    for k, a in enumerate(A, 1):
        s = json.dumps(a)
        if any(("new:" + x) in s or a.get("as") == x for x in als):
            print("P", pn, k, json.dumps(a)[:520], "| fs_route", fr.get(str(k)))
            for e in (a.get("src"), a.get("dst")):
                if isinstance(e, str) and e.startswith("new:"):
                    al = e[4:].split(".")[0]
                    src = next((b for b in A if b.get("as") == al), None)
                    if src and src["id"] != a["id"] and not any(x == al for x in als):
                        print("   SRC-CREATE", json.dumps(src)[:400])
gr = J("graph_ring_p3b2b_20261002_133824.json")
T = gr["terminals"]
for t in (28395, 29235, 28413, 29243, 29408, 29411):
    rows = [r for r in T if r["owner_uid"] == t]
    print("TUNNEL #{0}".format(t))
    for r in rows:
        oth = [(o["owner_uid"], o["owner_class"], o["term_uid"], o["term_name"], o["is_source"], o["frame_diagram"]) for o in T
               if r["wire_uid"] and o["wire_uid"] == r["wire_uid"] and o is not r]
        print("  t{0} {1!r} src={2} tcls={3} frame={4} w{5} -> {6}".format(r["term_uid"], r["term_name"], r["is_source"], r["term_class"],
                                                                          r["frame_diagram"], r["wire_uid"], oth))
print("owners 32464", gr["owners"].get("32464"), "27722", gr["owners"].get("27722"), "27641", gr["owners"].get("27641"))
print("fs_measured keys", list((gr.get("fs_measured") or {}).keys())[:10])
print(protocol.result_line(protocol.make_result(1, 0, None, [])), flush=True)
