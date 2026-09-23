"""q_c69_peek - offline, no LabVIEW: print the shape of the two row-list files and the bed loop table."""
import json, os
B = os.path.dirname(os.path.abspath(__file__))
v0 = json.load(open(os.path.join(B, "build_d1_v0.json"), encoding="utf-8"))
print("v0 keys", list(v0.keys())[:30])
print("moved", json.dumps(v0.get("moved"))[:600])
c = v0.get("cut")
print("cut type", type(c).__name__, len(c)); print("cut[0:3]", json.dumps(c[:3])[:600])
rs = json.load(open(os.path.join(B, "d1_rewire_sources.json"), encoding="utf-8"))
print("rs type", type(rs).__name__, list(rs.keys())[:20] if isinstance(rs, dict) else len(rs))
for k, v in (rs.items() if isinstance(rs, dict) else []):
    print(" rs", k, type(v).__name__, json.dumps(v)[:500])
L = json.load(open(os.path.join(B, "graph_loops_m4b_20260924.json"), encoding="utf-8"))
print("loops md5", L.get("md5"), "unread", L.get("unread_rights"))
for x in L["loops"]:
    print(" ", x["class"], x["index"], x["loop_uid"], x["right_uids"], x["left_of"])
