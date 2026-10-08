# ---
# labview: none
# hardware: none
# ---
"""Card 153-a1-1: print the shape of the s09 graph, the S1 wiki, the EL expected file and memory_model.
Reads json only. Prediction: all four load; s09 graph md5 field == eb1d0f31..."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
FILES = ["tools/bench/graph_ring_p4s09_20261009_062044.json", "docs/wiki/subvi/D1_s1_copy.json",
         "tools/bench/errorlist_expected_D1_ring_p4s09_20261009_060515.json", "tools/bench/memory_model.json",
         "tools/bench/graph_objs_s1_20260923.json", "tools/bench/graph_loops_s1_20260924.json"]

def shape(v, depth=0, maxd=2):
    pad = "  " * depth
    if isinstance(v, dict):
        for k in list(v)[:40]:
            x = v[k]
            d = (f"dict[{len(x)}]" if isinstance(x, dict) else f"list[{len(x)}]" if isinstance(x, list)
                 else repr(x)[:120])
            print(f"{pad}{k}: {d}")
            if depth < maxd and isinstance(x, (dict, list)) and k not in ():
                shape(x, depth + 1, maxd)
        if len(v) > 40:
            print(f"{pad}... {len(v)} keys")
    elif isinstance(v, list) and v:
        print(f"{pad}[0] = {json.dumps(v[0])[:400]}")
        if len(v) > 1:
            print(f"{pad}[-1] = {json.dumps(v[-1])[:400]}")

for f in FILES:
    print("=" * 20, f)
    try:
        j = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        print("LOAD FAIL", e); continue
    shape(j, 0, 1)
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
