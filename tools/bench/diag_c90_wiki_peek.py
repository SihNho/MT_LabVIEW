"""diag_c90_wiki_peek - read-only peek (no LabVIEW): FlatSequence structures vs the gap frames #686/#3121/#15041 and the 3 While loops."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
objs = json.load(open(os.path.join(ROOT, "tools/bench/graph_objs_s1_20260923.json"), encoding="utf-8"))["objects"]
d = {o["uid"]: o for o in objs}
print("FlatSequence/Sequence structures (uid, pos, owner class):")
for o in objs:
    if o["class"] in ("FlatSequence", "Sequence"):
        print("  ", o["uid"], o["pos"], o["owner"])
print("gap frames:", [(u, d[u]["pos"], d[u]["owner"]) for u in (686, 3121, 15041)])
print("While loops:", [(o["uid"], o["pos"], o["owner"]) for o in objs if o["class"] == "WhileLoop"])
print("While bodies:", [(u, d[u]["pos"]) for u in (25392, 639, 15266)])
print("frames of the top-level FS #681 by y-band 102..140:", [(o["uid"], o["pos"]) for o in objs if o["class"] == "Diagram" and o["owner"] == "FlatSequenceFrame" and 100 <= o["pos"][1] <= 140])
