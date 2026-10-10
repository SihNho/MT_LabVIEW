# ---
# labview: none
# hardware: none
# ---
r"""Card 159-a3-1 probe: print the SHAPE of the two graph jsons (keys, counts, a sample row per list) so the attribution
script reads the right fields. Offline, read-only. PREDICTION: both files load; each has terminals + objs lists.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P  # noqa: E402

G = {"p52a": "graph_ring_p5s02a_20261010_032547.json", "p51": "graph_ring_p5s01_20261009_125622.json"}
ok = 0
for k, f in G.items():
    d = json.load(open(os.path.join(HERE, f), encoding="utf-8"))
    print("==", k, f)
    for key, v in d.items():
        if isinstance(v, list):
            print("  list", key, len(v), json.dumps(v[0])[:400] if v else "")
        elif isinstance(v, dict):
            ks = list(v.keys())
            print("  dict", key, len(ks), ks[:8], json.dumps(v[ks[0]])[:300] if ks else "")
        else:
            print("  val ", key, str(v)[:200])
    cls = {}
    for o in d.get("objs") or []:
        cls[o.get("class")] = cls.get(o.get("class"), 0) + 1
    print("  obj classes", sorted(cls.items(), key=lambda x: -x[1])[:40])
    ok += 1 if d.get("terminals") and d.get("objs") else 0
print(P.result_line({"status": "PASS" if ok == 2 else "FAIL", "gates": {"pass": ok, "fail": 2 - ok}, "first_fail": None,
                     "artefacts": []}))
