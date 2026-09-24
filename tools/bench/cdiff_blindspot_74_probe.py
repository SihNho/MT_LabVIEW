"""cdiff_blindspot_74 probe 2: offline read of the bed dumps' row shapes. No LabVIEW."""
import json, os, sys
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(B))
import protocol as P  # noqa: E402
for p in ['opmodels/bed_s4_loop17.json', 'opmodels/bed_l7_1a.json', 'opmodels/bed_s3_loop15.json',
          'graph_s3_loop15_20260924.json', 'opmodels/bed_s4_map.json', 'opmodels_read_map.json', 'opmodels_read_bed.json']:
    d = json.load(open(os.path.join(B, p), encoding='utf-8'))
    print("==", p, list(d)[:30] if isinstance(d, dict) else type(d))
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                print("   ", k, len(v), sorted(v[0].keys()))
            elif not isinstance(v, (list, dict)):
                print("   ", k, repr(v)[:120])
            else:
                print("   ", k, type(v).__name__, len(v))
    s = json.dumps(d)
    print("   mentions 060431:", "060431" in s, " D1_s4_loop17.vi:", "D1_s4_loop17.vi" in s)
print(P.result_line(P.make_result(1, 0)))
