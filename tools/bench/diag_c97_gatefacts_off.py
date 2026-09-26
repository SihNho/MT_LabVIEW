"""Card 97-1 OFFLINE part (B, B', A-offline). No LabVIEW, no COM. Input: tools/bench/par1359_95_graph.json
(D1_s1_copy.vi md5 3e3d23ce...). Prior art used: f1359_consumers_96.json (96-3 trace), diag_c94c_f7911.json (94-3
tunnel reads), tools/bench/main_vi_node_labels.json (OpNodeLabels_v0 sweep 2026-09-14, other VI of same lineage).

PREDICTION CONTRACT: G1 graph md5 == 3e3d23cefd3a334001aa9d6156bf1aee; G2 body 7911 has >=1 node on the 11363 path
and >=1 node on the 9227 path; G3 every #1359 tunnel of diag_c94c appears with frame_diagram 7911 on its inner side;
G4 #8741's array input wire == 9227's inner wire (8811) iff 96-3 is right (reported either way, not a gate);
G5 terminal table has exactly one row for term 8323.
Writes tools/bench/f1359_gate_facts_97_offline.json. Ends with RESULT line.
"""
import json, collections, sys
sys.path.insert(0, 'tools')
g = json.load(open('tools/bench/par1359_95_graph.json'))
T = g['terminals']; O = g['objs']
OBJ = {o['uid']: o for o in O}
IDX = {o['uid']: i for i, o in enumerate(O)}
gates = []
def gate(name, ok, det):
    gates.append([name, bool(ok), det]); print('GATE', name, 'PASS' if ok else 'FAIL', det)

gate('G1 md5', g['md5'] == '3e3d23cefd3a334001aa9d6156bf1aee', g['md5'])
by_wire = collections.defaultdict(list); by_owner = collections.defaultdict(list)
for t in T:
    if t['wire_uid']: by_wire[t['wire_uid']].append(t)
    by_owner[t['owner_uid']].append(t)

BODY = 7911
tun = json.load(open('tools/bench/diag_c94c_f7911.json'))['tunnels']
TUN = set(int(k) for k in tun) | {7922}
body_terms = [t for t in T if t['frame_diagram'] == BODY]
body_nodes = sorted(set(t['owner_uid'] for t in body_terms) - TUN)
inner_tun = sorted(set(t['owner_uid'] for t in body_terms) & TUN)
gate('G3 tunnels inner on 7911', set(inner_tun) >= (TUN - {7922}), 'inner-side tunnels %s' % inner_tun)
# nested diagrams inside 7911? any body node that is a structure-ish owner class
nested = [(u, by_owner[u][0]['owner_class']) for u in body_nodes
          if by_owner[u][0]['owner_class'] in ('Tunnel', 'SelectorTunnel', 'LoopTunnel', 'FlatSequenceOuterTunnel',
                                               'LeftShiftRegister', 'RightShiftRegister')]
print('NESTED-STRUCTURE TERMS ON 7911', nested)

def srcs_of_node(u):
    """sources feeding the input terminals of node u that sit on BODY"""
    out = []
    for t in by_owner[u]:
        if t['is_source'] or not t['wire_uid'] or t['frame_diagram'] != BODY: continue
        for s in by_wire[t['wire_uid']]:
            if s['is_source'] and s is not t: out.append((s['owner_uid'], s['term_name'], s['term_uid'], t['term_name'], t['term_uid'], t['wire_uid']))
    return out

def back(start_tunnel):
    seen = set(); stack = []
    for t in by_owner[start_tunnel]:
        if t['frame_diagram'] == BODY and not t['is_source'] and t['wire_uid']:
            for s in by_wire[t['wire_uid']]:
                if s['is_source']: stack.append(s['owner_uid'])
    while stack:
        u = stack.pop()
        if u in seen: continue
        seen.add(u)
        if u in TUN: continue           # stop at input tunnels
        for s in srcs_of_node(u): stack.append(s[0])
    return seen

R11 = back(11363); R92 = back(9227)
gate('G2 both paths non-empty', R11 - TUN and R92 - TUN, '11363:%d 9227:%d' % (len(R11 - TUN), len(R92 - TUN)))

def desc(u):
    o = OBJ.get(u, {}); ts = by_owner[u]
    return {'uid': u, 'class': ts[0]['owner_class'] if ts else o.get('class'), 'pos': o.get('pos'),
            'terms': [(t['term_name'], 'out' if t['is_source'] else 'in', t['wire_uid']) for t in ts]}

rows = []
for u in body_nodes:
    a, b = u in R11, u in R92
    rows.append(dict(desc(u), set='both' if a and b else '11363-only' if a else '9227-only' if b else 'neither'))
for u in inner_tun:
    a, b = u in R11, u in R92
    rows.append(dict(desc(u), set=('both' if a and b else '11363-only' if a else '9227-only' if b else 'neither'), tunnel=True,
                     index_mode=tun.get(str(u), {}).get('tun', {}).get('index_mode')))
S = {r['uid']: r['set'] for r in rows}
cross = []
for w, ts in by_wire.items():
    srcs = [t for t in ts if t['is_source']]; sinks = [t for t in ts if not t['is_source'] and t['frame_diagram'] == BODY]
    for s in srcs:
        for k in sinks:
            a, b = S.get(s['owner_uid']), S.get(k['owner_uid'])
            if a and b and a != b:
                cross.append({'wire': w, 'src': '%d:%s' % (s['owner_uid'], s['term_name']), 'src_set': a,
                              'sink': '%d:%s' % (k['owner_uid'], k['term_name']), 'sink_set': b})
for r in rows: print('ROW', r['set'], r['uid'], r['class'], [x for x in r['terms']][:8], 'TUN' if r.get('tunnel') else '')
for c in cross: print('CROSS', c)
# 8741 input
s8741 = srcs_of_node(8741)
print('8741 SOURCES', s8741)
inner9227 = [t['wire_uid'] for t in by_owner[9227] if t['frame_diagram'] == BODY]
print('9227 inner wire', inner9227, '8634 terms', [(t['term_name'], t['is_source'], t['wire_uid']) for t in by_owner[8634]])
# B': 8323 terminal, 11261 owner diagram
t8323 = [t for t in T if t['term_uid'] == 8323]
gate('G5 one row for term 8323', len(t8323) == 1, t8323)
t11261 = sorted(set(t['frame_diagram'] for t in by_owner[11261]))
t1359out = sorted(set((t['owner_uid'], t['frame_diagram']) for t in T if t['owner_uid'] in TUN and t['frame_diagram'] != BODY))
print('11261 frame diagrams', t11261, '| tunnel outer diagrams', t1359out)
print('OBJ 637/639/644', [OBJ.get(u) for u in (637, 639, 644)], [(t['term_uid'], t['term_name'], t['is_source'], t['wire_uid'], t['owner_uid'], t['owner_class'], t['frame_diagram']) for t in T if t['term_uid'] == 644 or t['owner_uid'] == 644])
# A offline: every Property/Invoke/ControlReferenceConstant/Local/Global/EventStructure, with labels from the 09-14 sweep
lab = {}
for d, lst in json.load(open('tools/bench/main_vi_node_labels.json'))['diagrams'].items():
    for n in lst: lab[n['uid']] = (d, n['label'])
cand = [o for o in O if o['class'] in ('Property', 'Invoke', 'ControlReferenceConstant', 'Local', 'Global', 'EventStructure')]
A = []
for o in cand:
    L = lab.get(o['uid'])
    fd = sorted(set(t['frame_diagram'] for t in by_owner[o['uid']]))
    A.append({'uid': o['uid'], 'class': o['class'], 'label_0914': L[1] if L else None, 'frame_diagram': fd,
              'terms': [(t['term_name'], 'out' if t['is_source'] else 'in', t['wire_uid']) for t in by_owner[o['uid']]]})
nolab = [a['uid'] for a in A if a['label_0914'] is None]
hits = [a for a in A if a['label_0914'] and 'Force (pN) vs Extension' in a['label_0914']]
print('A candidates', len(A), 'unlabelled in 09-14 sweep', len(nolab), nolab)
for h in hits: print('A HIT', h)
json.dump({'md5': g['md5'], 'rows_B': rows, 'cross_B': cross, 'src_8741': s8741, 'inner9227': inner9227,
           'term8323': t8323, 'diag11261': t11261, 'A_candidates': A, 'A_hits_0914': hits, 'A_unlabelled': nolab,
           'gates': gates}, open('tools/bench/f1359_gate_facts_97_offline.json', 'w'), indent=1)
from protocol import result_line, make_result
npass = sum(1 for x in gates if x[1]); nfail = len(gates) - npass
print(result_line(make_result(npass, nfail, next((x[0] for x in gates if not x[1]), None),
                              [{'path': 'tools/bench/f1359_gate_facts_97_offline.json'}])))
