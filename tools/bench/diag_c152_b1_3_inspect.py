# ---
# labview: none
# hardware: none
# ---
"""card 152-b1-3 offline read: LoopTunnel #30179 terminal rows, its nets, owners of its diagrams, objs rows, in the derived
s08 graph (graph_ring_p4s08_20261009_033522_fsowner.json, e26b4d90). JSON read only; no LabVIEW.
PRIOR ART: diag_c152_b1_1_graph4.log read the same graph through LabVIEW; this only re-reads the saved JSON for the rule's fields.
PREDICTION: 2 LoopTunnel faces named 'min slot'; inner face's diagram owned by WhileLoop #16483; inner net source a SubVI."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import protocol
g = json.load(open(os.path.join(HERE, "graph_ring_p4s08_20261009_033522_fsowner.json"), encoding="utf-8"))
print("keys", list(g.keys()))
T = g["terminals"]
lt = [r for r in T if r["owner_uid"] == 30179]
for r in lt:
    print("LT", r)
inner_src = []
for r in lt:
    if r["wire_uid"]:
        for q in T:
            if q["wire_uid"] == r["wire_uid"] and q["term_uid"] != r["term_uid"]:
                print("  net", r["wire_uid"], q)
                if q["is_source"]:
                    inner_src.append(q["owner_class"])
    print("owner of diag", r["frame_diagram"], (g.get("owners") or {}).get(str(r["frame_diagram"])))
print("objs", [o for o in g["objs"] if o.get("uid") in (30179, 16483)])
ok1 = len(lt) == 2 and all(r["term_name"] == "min slot" for r in lt)
ok2 = "SubVI" in inner_src
first = None if ok1 and ok2 else ("G1 two faces 'min slot'" if not ok1 else "G2 inner source SubVI")
print(protocol.result_line(protocol.make_result(int(ok1) + int(ok2), 2 - int(ok1) - int(ok2), first)))
