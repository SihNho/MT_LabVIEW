# ---
# labview: none
# hardware: none
# ---
"""p64p2r1_peek - read-only: print parts of p64p2_state.json (the failed cycle's records) / a JSON file's keys."""
import json, os, sys                                                                     # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
f = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "p64p2_state.json")
S = json.load(open(f, encoding="utf-8"))
print("KEYS", list(S.keys()))
for k in sys.argv[2:]:
    v = S
    for p in k.split("."):
        v = v[p]
    if isinstance(v, dict):
        v = dict((kk, vv) for kk, vv in v.items() if kk not in ("edges_set",))
    print(k, json.dumps(v, default=str)[:4000])
