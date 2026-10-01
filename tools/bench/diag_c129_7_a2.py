"""diag_c129_7_a2 - offline (card 129-7): source attributes of every measured FS-border crossing source uid,
from tools/bench/graph_ring_p3a_20261001_190155.json. No LabVIEW. No gates (fact dump)."""
import json
R = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop"
g = json.load(open(R + r"\tools\bench\graph_ring_p3a_20261001_190155.json"))
T = g['terminals']; O = {o['uid']: o for o in g['objs']}
by_term = {}
for t in T:
    by_term.setdefault(t['term_uid'], []).append(t)
by_wire = {}
for t in T:
    by_wire.setdefault(t.get('wire_uid'), []).append(t)
SRC = [6897, 644, 23289, 27373, 27401]
for s in SRC:
    rows = by_term.get(s, [])
    print('SRC', s, 'rows', len(rows))
    for r in rows:
        print('   ', r)
        ow = O.get(r['owner_uid']); print('    owner obj', ow)
        net = by_wire.get(r.get('wire_uid'), [])
        print('    net', r.get('wire_uid'), 'terms', len(net))
        for n in net:
            print('       ', n['term_uid'], repr(n['term_name']), 'src' if n['is_source'] else 'snk', n['owner_class'], n['owner_uid'], 'frame', n.get('frame_diagram'))
    if not rows:
        print('    obj?', O.get(s))
# objects' other keys
print('OBJ keys', sorted({k for o in g['objs'] for k in o}))
print('TERM keys', sorted({k for t in T for k in t}))
# any object with a label/name field equal to 'current image number'
for o in g['objs']:
    if 'current image number' in json.dumps(o):
        print('OBJ CIN', o)
cnt = {}
for t in T:
    if t['term_name'] == 'current image number':
        cnt.setdefault(t['owner_class'], []).append((t['term_uid'], t['owner_uid'], t['is_source'], t.get('wire_uid'), t.get('frame_diagram')))
for k, v in cnt.items():
    print('TERM CIN', k, len(v), v[:12])
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":0,"fail":0},"first_fail":null,"artefacts":[]}')
