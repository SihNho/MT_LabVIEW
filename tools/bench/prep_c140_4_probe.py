"""Card 140-4 probe: print the structure of the bed graph JSON (offline, read-only, no LabVIEW).
Prediction: graph has a node table or terminal table keyed by owner_uid; prints top-level keys and first rows."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
B = os.path.dirname(os.path.abspath(__file__))
g = json.load(open(os.path.join(B, 'graph_ring_p3b2b_20261002_133824.json'), encoding='utf-8'))
print('KEYS', list(g.keys()))
for k, v in g.items():
    if isinstance(v, list) and v:
        print('LIST', k, len(v), json.dumps(v[0])[:400])
    elif isinstance(v, dict):
        ks = list(v.keys())
        print('DICT', k, len(ks), ks[:8], json.dumps(v[ks[0]])[:300] if ks else '')
    else:
        print('SCAL', k, str(v)[:200])
for k, v in g.items():
    if isinstance(v, list):
        for r in v:
            s = json.dumps(r)
            if any(str(u) in s for u in ('29265', '29316', '29157')):
                print('HIT', k, s[:500])
from protocol import result_line
print(result_line({'status': 'PASS', 'gates': {'pass': 1, 'fail': 0}, 'first_fail': None, 'artefacts': []}))
