# ---
# labview: none
# hardware: none
# ---
"""Card 154-a1-2: list top-level keys and sample rows of the stored graph jsons (offline, read-only).
Prior art: diag_c153_a1_1_census*.py read the same s09 json; this only prints its shape.
Prediction: each file parses as JSON; prints keys, samples; ends with a RESULT line."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import protocol
s1 = json.loads((ROOT / "docs/wiki/subvi/D1_s1_copy.json").read_text(encoding="utf-8"))
gs = s1["graph_summary"]
for k, v in gs.items():
    if isinstance(v, list):
        print("S1 gs", k, "list", len(v), json.dumps(v[:2])[:400])
    elif isinstance(v, dict):
        ks = list(v)[:3]
        print("S1 gs", k, "dict", len(v), json.dumps({x: v[x] for x in ks})[:400])
    else:
        print("S1 gs", k, repr(v)[:200])
s9 = json.loads((ROOT / "tools/bench/graph_ring_p4s09_20261009_062044.json").read_text(encoding="utf-8"))
names = [o for o in s9["objs"] if o.get("uid") in (644, 2136, 1114, 10068, 29240, 6859, 30240, 3045, 2213, 12195, 637, 639)]
for o in names:
    print("S9 obj", json.dumps(o)[:300])
print("S9 objs keys union", sorted({k for o in s9["objs"] for k in o}))
print("S9 owners sample", json.dumps({k: s9["owners"][k] for k in list(s9["owners"])[:3]})[:400])
print("S9 loops sample", json.dumps(s9["loops"][1])[:400])
print("S9 fs_measured", json.dumps(s9["fs_measured"])[:600])
print("S1 call_sites", json.dumps(s1["call_sites_in_main"])[:300])
print(protocol.result_line({"status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None, "artefacts": []}))
