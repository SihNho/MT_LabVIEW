"""read-only peek at plan json files (card 114-1). usage: py tools/bench/diag_c114_peek.py <json> [keys...]"""
import json
import sys

f = sys.argv[1]
d = json.load(open(f, encoding="utf-8"))
keys = sys.argv[2:] or list(d.keys())
print("=====", f, list(d.keys()) if isinstance(d, dict) else type(d))
for k in keys:
    v = d.get(k)
    if isinstance(v, list):
        print(" ", k, "n=", len(v))
        for x in v:
            print("    ", json.dumps(x)[:500])
    else:
        print(" ", k, json.dumps(v)[:1500])
