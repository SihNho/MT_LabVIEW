import json, sys
p = r"G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/wiki/subvi/D1_s1_copy.json"
d = json.load(open(p, encoding="utf-8"))
print("KEYS", list(d.keys()))
T = d.get("terminals", [])
print("NTERM", len(T), T[0] if T else None)
for u in (22692, 15403):
    rows = [r for r in T if int(r.get("owner_uid") or 0) == u]
    print("NODE", u, "rows", len(rows))
    for r in rows:
        print("   ", r)
# diagram index -> uid: try objs / diagrams keys
for k in ("diagrams", "objs", "objects", "owners"):
    if k in d:
        v = d[k]
        print(k, type(v).__name__, (list(v.items())[:3] if isinstance(v, dict) else v[:3]))
gs = d.get("graph_summary", {})
print("GS KEYS", list(gs.keys()) if isinstance(gs, dict) else type(gs))
# wire 3268 / i-terminal rows for loop 637
for w in (3268, 19372, 34066):
    print("WIRE", w, [ (r.get("term_uid"), r.get("owner_uid"), r.get("owner_class"), r.get("term_name"), r.get("is_source"), r.get("frame_diagram")) for r in T if int(r.get("wire_uid") or 0) == w])
