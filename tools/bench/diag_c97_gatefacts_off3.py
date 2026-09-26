"""Card 97-1 OFFLINE part 3. No LabVIEW. Event Data Nodes (10764, 32083, 32194, 15599, 15628) and event structures
10153/15544: terminal names, frame diagrams, sinks; Bundler #11608 (2nd input of BuildArray #11261) backward chain on
diagram 639 and its other sinks; #10068 Q&R chain to tunnel 10177.
PREDICTION CONTRACT: G1 each event data node has >=1 terminal row; G2 #11608 has a source-terminal row.
"""
import json, collections, sys
sys.path.insert(0, 'tools')
g = json.load(open('tools/bench/par1359_95_graph.json'))
T = g['terminals']; O = g['objs']; OBJ = {o['uid']: o for o in O}
lab = {}
for d, lst in json.load(open('tools/bench/main_vi_node_labels.json'))['diagrams'].items():
    for n in lst: lab[n['uid']] = n['label']
bw = collections.defaultdict(list); bo = collections.defaultdict(list)
for t in T:
    if t['wire_uid']: bw[t['wire_uid']].append(t)
    bo[t['owner_uid']].append(t)
gates = []
def gate(n, ok, d): gates.append([n, bool(ok), d]); print('GATE', n, 'PASS' if ok else 'FAIL', d)
def peers(w, src):
    return [(s['owner_uid'], s['owner_class'], s['term_name'], lab.get(s['owner_uid']), s['frame_diagram']) for s in bw.get(w, []) if s['is_source'] == src]
EDN = [10764, 32083, 32194, 15599, 15628]
for u in EDN + [10153, 15544]:
    print('EV', u, OBJ.get(u), lab.get(u))
    for t in bo[u]:
        print('    ', t['term_name'].replace('\n', '|'), 'out' if t['is_source'] else 'in', t['wire_uid'], t['frame_diagram'],
              peers(t['wire_uid'], not t['is_source']) if t['wire_uid'] else '')
gate('G1 edn rows', all(bo[u] for u in EDN), [len(bo[u]) for u in EDN])
# Bundler 11608 backward on its diagram, one level + its outputs
def back(u, depth=0, seen=None):
    seen = seen if seen is not None else set()
    if u in seen or depth > 12: return seen
    seen.add(u)
    for t in bo[u]:
        if not t['is_source'] and t['wire_uid']:
            for s in bw[t['wire_uid']]:
                if s['is_source']: back(s['owner_uid'], depth + 1, seen)
    return seen
B = back(11608)
gate('G2 11608 rows', bo[11608], len(bo[11608]))
for u in sorted(B):
    ts = bo[u]; cls = ts[0]['owner_class'] if ts else OBJ.get(u, {}).get('class')
    outs = [(t['term_name'][:20], t['wire_uid'], [(p[0], p[1], p[2][:20]) for p in peers(t['wire_uid'], False)]) for t in ts if t['is_source'] and t['wire_uid']]
    print('B11608', u, cls, lab.get(u), sorted(set(t['frame_diagram'] for t in ts)), outs[:3])
print('10068 terms', [(t['term_name'], t['is_source'], t['wire_uid'], peers(t['wire_uid'], not t['is_source'])) for t in bo[10068]])
print('29240 terms', [(t['term_name'], t['is_source'], t['wire_uid'], peers(t['wire_uid'], not t['is_source'])) for t in bo[29240]])
from protocol import result_line, make_result
n = sum(x[1] for x in gates)
print(result_line(make_result(n, len(gates) - n, next((x[0] for x in gates if not x[1]), None), [])))
