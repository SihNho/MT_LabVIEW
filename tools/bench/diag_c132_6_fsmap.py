"""card 132-6 diag (offline, read-only): FS frame map in the provisional base vs the real P3b-1 graph."""
import json
d = json.load(open('tools/bench/sim/ring_p3b2_base_provisional.json', encoding='utf-8'))
print('prov keys', list(d.keys()))
for k in ('fs_frames', 'fs_tunnels', 'case_frames', 'sym'):
    print('prov', k, json.dumps(d.get(k))[:900])
o = d.get('owners') or {}
print('prov owners n', len(o), {k: v for k, v in o.items() if k.startswith('-')})
g = json.load(open('tools/bench/graph_ring_p3b1_20261002_073225.json', encoding='utf-8'))
print('real keys', list(g.keys()))
o = g.get('owners') or {}
print('real owners n', len(o), {k: o.get(k) for k in ('27641', '32464', '27722')})
objs = [x for x in g.get('objs') or [] if isinstance(x, dict) and x.get('uid') in (27641, 32464, 27722)]
print('real objs', objs)
fsobjs = [x for x in g.get('objs') or [] if isinstance(x, dict) and x.get('class') in ('FlatSequence', 'FlatSequenceStructure')]
print('real FS objs', fsobjs[:5])
