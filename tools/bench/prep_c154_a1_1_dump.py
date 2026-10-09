# ---
# labview: none
# hardware: none
# ---
"""card 154-a1-1: print the actions of donor plans (read-only json dump). Usage: py prep_c154_a1_1_dump.py <plan.json> [...]"""
import json
import sys

for f in sys.argv[1:]:
    try:
        p = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        print(f, e)
        continue
    print("=====", f, p.get("stage"), len(p.get("actions", [])), "base", p.get("base"))
    print("goal:", str(p.get("goal", ""))[:400])
    print("keys:", list(p.keys()))
    for i, a in enumerate(p.get("actions", []), 1):
        print(i, json.dumps(a)[:400])
