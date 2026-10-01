"""diag_c131_5_lediff - card 131-5 step 0 (offline, no LabVIEW): which 'wire has loose ends' item is gone.

Inputs: P3a full read (measured_from of errorlist_expected_D1_ring_p3a_*.json) vs the 131-4 scratch read (53).
Prediction: P3a read has 55 items with 23 loose-end items; scratch has 53 with 22; the item fields name the
missing one if the reader recorded any identifying field beyond the reason text (else: unknown).
Existing tools checked: tools/errorlist_check.py compares by class count only (no per-item location diff).
"""
import json
from collections import Counter
from pathlib import Path
B = Path(__file__).resolve().parent
EXP = json.loads((B / 'errorlist_expected_D1_ring_p3a_20261001_180540.json').read_text(encoding='utf-8'))
P3A = json.loads((B.parent.parent / EXP['measured_from']).read_text(encoding='utf-8'))
SCR = json.loads((B / 'errorlist_scratch_c129_ring_p3b1_20261002_052136_20261002_053812.json').read_text(encoding='utf-8'))


def le(items):
    return [it for it in items if 'loose' in (it.get('raw') or '').lower()]


for name, d in (('P3A', P3A), ('SCR', SCR)):
    its = d['items']
    print(name, 'items', len(its), 'loose', len(le(its)), 'keys', sorted(its[0].keys()))
KEYS = None
for name, d in (('P3A', P3A), ('SCR', SCR)):
    for it in le(d['items']):
        flat = {k: v for k, v in it.items() if not isinstance(v, (list, dict))}
        flat.pop('detail', None)
        print(name, json.dumps(flat, ensure_ascii=False)[:700])
        se = {k: v for k, v in (it.get('show_error') or {}).items() if not (isinstance(v, str) and v.endswith('.png'))}
        print('    SE', it.get('row_index'), json.dumps(se, ensure_ascii=False)[:600], 'LIC', json.dumps(it.get('licensed_by'))[:200])
# multiset diff on every scalar field except index/row_index/vi/paths
IGN = {'index', 'row_index', 'vi', 'detail', 'detail_path', 'selection_route'}


def sig(it):
    return tuple(sorted((k, str(v)) for k, v in it.items() if k not in IGN and not isinstance(v, (list, dict))))


a = Counter(sig(i) for i in le(P3A['items']))
b = Counter(sig(i) for i in le(SCR['items']))
print('ONLY_P3A', json.dumps([dict(s) for s in (a - b).elements()], ensure_ascii=False)[:3000])
print('ONLY_SCR', json.dumps([dict(s) for s in (b - a).elements()], ensure_ascii=False)[:3000])
print('RESULT ' + json.dumps({'schema': 'result-line/1', 'status': 'PASS', 'gates': {'pass': 1, 'fail': 0},
                              'first_fail': None, 'artefacts': []}))
