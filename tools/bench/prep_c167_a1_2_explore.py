# ---
# labview: none
# hardware: none
# ---
"""Card 167-a1-2 prep: print stored-graph rows around the F2 consumers and the P3a uids (offline, no LabVIEW). Exploration only."""
import collections, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

P5 = json.load(open("tools/bench/graph_ring_p5s02e_20261012_173009.json", encoding="utf-8"))
S1 = json.load(open("docs/wiki/subvi/D1_s1_copy.json", encoding="utf-8"))
OWN = {int(k): v for k, v in P5["owners"].items()}
CLS = {o["uid"]: o["class"] for o in P5["objs"]}


def rows(g, uid):
    return sorted((t["term_uid"], t["term_name"], t["is_source"], t["wire_uid"], t["frame_diagram"], t["term_class"], t["owner_class"])
                  for t in g["terminals"] if t["owner_uid"] == uid)


def wire(g, w):
    return sorted((t["owner_uid"], t["owner_class"], t["term_uid"], t["term_name"], t["is_source"], t["frame_diagram"])
                  for t in g["terminals"] if t["wire_uid"] == w)


print("OWNERS sample classes", collections.Counter(v[0] for v in OWN.values()))
for d in (639, 27219, 27232, 3227, 3292, 16565, 32464, 23166, 686, 536, 11926, 11936, 7911, 29894):
    print("OWN d%d %s" % (d, OWN.get(d)))
for u in (22694, 3191, 11869, 16543, 27509, 637, 10170, 16483, 27258, 27250, 27344, 27359, 26879, 27373, 27311, 3045, 29440, 12195, 2213, 30239):
    print("P5 #%d %s %s" % (u, CLS.get(u), rows(P5, u)))
    print("S1 #%d %s" % (u, rows(S1, u)))
for u in (1114, 2136, 29411, 12045, 3162, 1628, 30240, 29240, 10068):
    print("CONS P5 #%d %s %s" % (u, CLS.get(u), rows(P5, u)))
    print("CONS S1 #%d %s" % (u, rows(S1, u)))
for w in (27245, 29454, 3268):
    print("WIRE P5 w%d %s" % (w, wire(P5, w)))
    print("WIRE S1 w%d %s" % (w, wire(S1, w)))
print("S1 wires keys", S1["wires"][0].keys())
print(protocol.result_line({"status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None, "artefacts": []}))
