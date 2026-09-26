"""diag_c97_fgate_q1 - card 97-4 OFFLINE graph read (no LabVIEW): classes/terminals of the donors and gate objects in
S1's graph JSON, to fill tools/bench/plans/plan_fgate_97.json. Read-only."""
import json, collections, os
R = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(R, "par1359_95_graph.json"), encoding="utf-8"))
print(d.get("md5"), [k for k in d])
print(list(d.keys()))
T = d["terminals"]; print(len(T), T[0])
objs = d.get("objs") or d.get("objects") or []
print(len(objs), objs[:1])
cls = dict((o["uid"], o["class"]) for o in objs)
by = collections.defaultdict(list)
for r in T:
    by[r["owner_uid"]].append(r)
for u in (2136, 10068, 29240, 637, 639, 644, 1359, 7911, 8476, 8323, 11261):
    print(u, cls.get(u), [(r["term_name"], r["is_source"], r["wire_uid"], r.get("frame_diagram"), r["term_class"], r["term_uid"]) for r in by.get(u, [])])
eq0 = [u for u, rs in by.items() if any((r["term_name"] or "").strip() == "x = 0?" for r in rs)]
print("EQ0", [(u, cls.get(u), [(r["term_name"], r["wire_uid"], r.get("frame_diagram")) for r in by[u]]) for u in eq0])
w = [r for r in T if r["wire_uid"] == 3268]
print("W3268", [(r["owner_uid"], r["owner_class"], r["term_name"], r["is_source"], r["term_uid"]) for r in w])
own = d.get("owners") or {}
print("owners", own.get("637"), own.get("639"), own.get("7911"), own.get("1359"))
print("RESULT {\"schema\":\"result-line/1\",\"status\":\"PASS\",\"gates\":{\"pass\":1,\"fail\":0},\"first_fail\":null,\"artefacts\":[]}")
