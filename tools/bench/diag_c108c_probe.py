"""c108c probe: print the shape of the input JSON files (offline, no LabVIEW)."""
import json, sys
ROOT = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop"
for f in sys.argv[1:]:
    g = json.load(open(ROOT + "\\" + f, encoding="utf-8"))
    print("=== ", f, type(g).__name__)
    if isinstance(g, dict):
        for k, v in g.items():
            if isinstance(v, list):
                print(" ", k, "list", len(v), json.dumps(v[0])[:300] if v else "")
            elif isinstance(v, dict):
                items = list(v.items())[:2]
                print(" ", k, "dict", len(v), json.dumps(items)[:300])
            else:
                print(" ", k, repr(v)[:200])
    else:
        print(" list", len(g), json.dumps(g[0])[:300])
