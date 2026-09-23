"""c73 L7-R probe0 - structure census of the on-disk graph/wiki JSONs. No LabVIEW. Read-only.
Prediction: every file loads; prints top-level keys and first-element shapes. Existing: vigraph.py (build4)."""
import json, sys
FILES = ['tools/bench/graph_s1_20260924.json', 'tools/bench/graph_s3_loop15_20260924.json',
         'docs/wiki/subvi/D1_s1_copy.json', 'tools/bench/stage_d1_l7_1b.json',
         'tools/bench/graph_loops_s1_20260924.json', 'tools/bench/stage_d1_l7_1a.json']
for f in FILES:
    d = json.load(open(f, encoding='utf-8'))
    print('==', f, type(d).__name__, (list(d)[:40] if isinstance(d, dict) else len(d)))
    items = d.items() if isinstance(d, dict) else [('[0]', d[0])]
    for k, v in list(items)[:40]:
        n = len(v) if hasattr(v, '__len__') else ''
        ex = v[0] if isinstance(v, list) and v else (list(v.items())[:2] if isinstance(v, dict) else v)
        print('   ', k, type(v).__name__, n, json.dumps(ex, default=str)[:300])
sys.stdout.flush()
