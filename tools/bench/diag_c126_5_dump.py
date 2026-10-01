r"""diag_c126_5_dump - card 126-5, OFFLINE read-only: dump the P3a plan actions compactly (no LabVIEW, no COM).
Prediction: prints the 25 P3a actions and the top-level keys; ends with a RESULT line."""
import json, os, sys
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(B))
import protocol as P  # noqa: E402
p = json.load(open(os.path.join(B, 'plan_ring_p3a.json'), encoding='utf-8'))
print([k for k in p])
for a in p['actions']:
    print(json.dumps({k: v for k, v in a.items() if k not in ('why', 'donor')}))
for k in p:
    if k != 'actions':
        print(k, json.dumps(p[k])[:1500])
print(P.result_line(P.make_result(1, 0, None)))
