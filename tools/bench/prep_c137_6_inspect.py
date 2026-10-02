"""Card 137-6 read-only inspection: v6 rollback actions 115-158 in full; graph facts on #10465 and the reseed flag. No LabVIEW."""
import json
p = json.load(open('tools/bench/plan_ring_p4_v6.json'))
for i in list(range(115, 125)) + list(range(139, 159)):
    print(i, json.dumps(p['actions'][i - 1]))
g = json.load(open('tools/bench/graph_ring_p3b2b_20261002_133824.json'))
O = {o['uid']: o for o in g['objs']}
def chain(u):
    out = []
    while u in O:
        o = O[u]; out.append((u, o['class']));
        if not o.get('owner'): break
        u = o['owner']
    return out
for u in (10465, 10453, 10459, 25557, 9647, 23166):
    print('OBJ', u, json.dumps(O.get(u)), 'chain', chain(u))
print('OWNERS', {k: v for k, v in g['owners'].items() if k in ('10465', '10453', '10459', '25557', '23166')})
for r in g['terminals']:
    if 'reseed' in (r.get('term_name') or '') or r['owner_uid'] in (10453, 10459):
        print('T', json.dumps(r))
for lp in g['loops']:
    if lp.get('loop_uid') in (10170, 639, 637):
        print('LOOP', json.dumps(lp)[:300])
