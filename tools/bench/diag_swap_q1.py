"""diag_swap_q1 - card 75-4 offline look-up (no LabVIEW): where #6810 sits in the S1 wiki; RESULT line at end."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P  # noqa: E402
os.chdir(ROOT)
W = json.load(open('docs/wiki/subvi/D1_s1_copy.json', encoding='utf-8'))
print(list(W.keys()))
for k, v in W.items():
    if isinstance(v, list) and v and isinstance(v[0], dict) and any(6810 in (x.get('node_uid'), x.get('uid')) for x in v):
        print(k, len(v), [x for x in v if 6810 in (x.get('node_uid'), x.get('uid'))])
print([o for o in json.load(open('tools/bench/graph_objs_s1_20260923.json', encoding='utf-8'))['objects'] if o['uid'] == 6810])
print([t for t in W['terminals'] if t['owner_uid'] == 6810])
print(P.result_line(P.make_result(1, 0, None)))
