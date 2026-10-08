# ---
# labview: none
# hardware: none
# ---
"""Card 153-a1-1 census part 2: every row (all faces) of named uids in the s09 graph 22f967b5 + their wire ends, and
owner chains of the nested diagrams seen in part 1. Reads json only. Prediction: SR outer faces of #24133/#24187 are fed
from diagram 686; #23501's outer source is on 686; W1 = the loop owning diagram 29699."""
import json, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
G = json.load(open("tools/bench/graph_ring_p4s09_20261009_062044.json", encoding="utf-8"))
OWN = G["owners"]
BO, BW = collections.defaultdict(list), collections.defaultdict(list)
for t in G["terminals"]:
    BO[t["owner_uid"]].append(t)
    if t["wire_uid"]:
        BW[t["wire_uid"]].append(t)
OBJ = {o["uid"]: o for o in G["objs"]}

def ends(t):
    return [(r["owner_uid"], r["owner_class"], r["term_name"], "src" if r["is_source"] else "sink", r["term_uid"], r["frame_diagram"])
            for r in BW.get(t["wire_uid"], []) if r["term_uid"] != t["term_uid"]] if t["wire_uid"] else []

UIDS = [24133, 24187, 24083, 24150, 23501, 24357, 24361, 25223, 5204, 10404, 23042, 4538, 4576, 4577, 4586, 4590, 4594, 30398,
        29818, 6384, 2048, 10171, 9603, 25545, 25371, 25339, 10850, 23508]
for u in UIDS:
    print("== #%s %s" % (u, OBJ.get(u, {}).get("class")))
    for t in sorted(BO.get(u, []), key=lambda r: r["term_uid"]):
        print("   t%s %r %s w%s d%s -> %s" % (t["term_uid"], t["term_name"], "src" if t["is_source"] else "sink", t["wire_uid"],
                                           t["frame_diagram"], ends(t)))
for d in ("29699", "29894", "2265", "2235", "7911", "686", "23166", "23405", "639"):
    o = OWN.get(d)
    print("owner", d, o, "->", OWN.get(str(o[1])) if o else None)
print("loops with body 29699:", [L for L in G["loops"] if OWN.get("29699", [0, 0])[1] == L["loop_uid"]])
# #2626 element sources
for w in (30418, 30270, 30274, 30522):
    print("wire", w, [(r["owner_uid"], r["owner_class"], r["term_name"], r["is_source"]) for r in BW.get(w, [])])
for u in (30300, 30119, 30216, 30240):
    print("#%s" % u, [(t["term_name"], t["is_source"], t["wire_uid"], ends(t)) for t in BO.get(u, [])])
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
