"""Card 97-1 OFFLINE part 2 (A detail). No LabVIEW. For every Property/Invoke/ControlReferenceConstant/Local/Global/
EventStructure of D1_s1_copy (par1359_95_graph.json): its 09-14 label, whether its `reference` input is wired and from
what; every 'Register'/'Event'/'Reference' label in the 09-14 sweep; owner-chain of diagram 3628 by position.
Also: the owner-7911 terminals split, w3268 sinks, #28180 callee.
PREDICTION CONTRACT: G1 every candidate has a 09-14 label (145/145); G2 exactly one implicit label names #8323's control.
"""
import json, collections, sys
sys.path.insert(0, 'tools')
g = json.load(open('tools/bench/par1359_95_graph.json'))
T = g['terminals']; O = g['objs']; OBJ = {o['uid']: o for o in O}
by_wire = collections.defaultdict(list); by_owner = collections.defaultdict(list)
for t in T:
    if t['wire_uid']: by_wire[t['wire_uid']].append(t)
    by_owner[t['owner_uid']].append(t)
lab = {}; diag_of_lab = {}
L = json.load(open('tools/bench/main_vi_node_labels.json'))
for d, lst in L['diagrams'].items():
    for n in lst: lab[n['uid']] = n['label']; diag_of_lab[n['uid']] = d
print('09-14 sweep vi:', L['vi'], 'keys', list(L.keys()))
gates = []
def gate(n, ok, det): gates.append([n, bool(ok), det]); print('GATE', n, 'PASS' if ok else 'FAIL', det)
C = [o for o in O if o['class'] in ('Property', 'Invoke', 'ControlReferenceConstant', 'Local', 'Global', 'EventStructure')]
gate('G1 all labelled', all(o['uid'] in lab for o in C), '%d/%d' % (sum(o['uid'] in lab for o in C), len(C)))
def src(w):
    return [(s['owner_uid'], s['owner_class'], s['term_name'], lab.get(s['owner_uid'])) for s in by_wire.get(w, []) if s['is_source']]
def sinks(w):
    return [(s['owner_uid'], s['owner_class'], s['term_name'], lab.get(s['owner_uid'])) for s in by_wire.get(w, []) if not s['is_source']]
for o in C:
    u = o['uid']; ts = by_owner[u]
    ref = [t for t in ts if t['term_name'] == 'reference' and not t['is_source']]
    refw = ref[0]['wire_uid'] if ref else None
    outs = [(t['term_name'], t['wire_uid'], sinks(t['wire_uid'])) for t in ts if t['is_source'] and t['wire_uid']]
    print('CAND', u, o['class'], repr(lab.get(u)), 'diag', sorted(set(t['frame_diagram'] for t in ts)),
          'refwire', refw, src(refw) if refw else '', '| outs', outs[:4])
hits = [o['uid'] for o in C if lab.get(o['uid'], '').startswith('Force (pN) vs Extension')]
gate('G2 one implicit hit', len(hits) == 1, hits)
print('LABELS with Register/Event/Reference/Force:', [(u, l, diag_of_lab[u]) for u, l in lab.items()
      if any(k in l for k in ('Register', 'Event', 'Reference', 'Force', 'Ctl Ref', 'VI Server'))])
# diagram 3628 and its owner by position
for u in (3628, 10313):
    o = OBJ[u]; i = O.index(o)
    print('OBJ', u, o, 'preorder idx', i)
d = OBJ[3628]['pos']
near = sorted(((abs(o['pos'][0] - d[0]) + abs(o['pos'][1] - d[1]), o['uid'], o['class']) for o in O
               if o['class'] in ('CaseStructure', 'FlatSequence', 'Sequence', 'ForLoop', 'WhileLoop', 'EventStructure', 'FlatSequenceFrame')))[:4]
print('STRUCT nearest to diag 3628 pos', d, near)
print('09-14 diagram index of 10313:', diag_of_lab.get(10313), 'siblings:', [(n['uid'], n['label']) for n in L['diagrams'][diag_of_lab[10313]]])
# owner-7911 terminals
print('OWNER 7911 TERMS', [(t['term_uid'], t['term_name'], t['is_source'], t['wire_uid'], t['term_class'], OBJ.get(t['term_uid'], {}).get('pos')) for t in by_owner[7911]])
print('OBJ 1359 pos', OBJ[1359]['pos'])
print('W3268 sinks', sinks(3268), 'src', src(3268))
print('28180 label', lab.get(28180), [c for c in g['graph_summary']['subvi_calls'] if c['node_uid'] in (28180, 28233, 29009, 28083)])
print('11261 terms', [(t['term_name'], t['is_source'], t['wire_uid'], sinks(t['wire_uid']) if t['is_source'] else src(t['wire_uid'])) for t in by_owner[11261]])
print('w10908 all', by_wire[10908])
json.dump({'candidates': [{'uid': o['uid'], 'class': o['class'], 'label_0914': lab.get(o['uid'])} for o in C], 'hits': hits,
           'gates': gates}, open('tools/bench/f1359_gate_facts_97_offline2.json', 'w'), indent=1)
from protocol import result_line, make_result
np_ = sum(x[1] for x in gates)
print(result_line(make_result(np_, len(gates) - np_, next((x[0] for x in gates if not x[1]), None),
                              [{'path': 'tools/bench/f1359_gate_facts_97_offline2.json'}])))
