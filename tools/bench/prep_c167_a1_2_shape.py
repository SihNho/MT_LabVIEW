# ---
# labview: none
# hardware: none
# ---
"""Card 167-a1-2 prep: print the key shape of the two stored graphs (P5 final, S1) - offline read only, no LabVIEW."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

for p in ["tools/bench/graph_ring_p5s02e_20261012_173009.json", "docs/wiki/subvi/D1_s1_copy.json"]:
    g = json.load(open(p, encoding="utf-8"))
    print(p, list(g.keys()))
    for k, v in g.items():
        if isinstance(v, list):
            print("  ", k, len(v), json.dumps(v[0])[:400] if v else "")
        elif isinstance(v, dict):
            print("  ", k, "dict", len(v), json.dumps(list(v.items())[:3])[:600])
        else:
            print("  ", k, str(v)[:100])
print(protocol.result_line({"status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None, "artefacts": []}))
