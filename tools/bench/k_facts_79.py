"""k_facts_79 - Stage K facts for kernel #5058 on D1_s4_loop17.vi. Pure Python over on-disk JSONs; no LabVIEW, no model.
Found before writing: c73_l7r_facts.py (same shape), vigraph (not needed: a wire index suffices), protocol.result_line.
No D1_s4_loop17 graph/wiki is on disk: S4 = S3 graph (graph_s3_loop15_20260924.json) + the L7 edits (L7-1a moved #376,
L7-R deleted w3957 w1899 w4337 w5073 w5274 w1397 w5056, moved #3052 #3453; stage_d1_l7_r_r2.log:39-58). F4 checks that
no #5058 row touches those edits. Facts only; no row-mode decision.
Prediction: 16 terminals, 13 wired (== build_d1_v0 cut uid 5058 == d1_rewire_sources rows uid 5058); 0 L7 overlaps."""
import json, hashlib, collections, sys
sys.path.insert(0, 'tools'); import protocol
J = lambda p: json.load(open(p, encoding='utf-8'))
M = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
P3, PW = 'tools/bench/graph_s3_loop15_20260924.json', 'docs/wiki/subvi/D1_s1_copy.json'
BED = r'C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_s4_loop17.vi'
S3, W, B, RW, SP = J(P3), J(PW), J('tools/bench/build_d1_v0.json'), J('tools/bench/d1_rewire_sources.json'), J('tools/bench/split_rows_l2l7.json')
G = {'pass': 0, 'fail': 0, 'first': None}
def gate(ok, lab):
    G['pass' if ok else 'fail'] += 1
    if not ok and not G['first']: G['first'] = lab
    print(' %s %s' % ('PASS' if ok else 'FAIL', lab))
print('F4 bed md5', M(BED), '| S3 graph file md5', M(P3), 'vi-md5', S3['md5'], '| S1 wiki file md5', M(PW), 'vi-md5', W['md5'])
gate(M(BED) == '4b621946492da3d2fbb96b6053e715ec', 'bed md5 == card')
T3 = S3['terminals']; WI = collections.defaultdict(list); OW = collections.defaultdict(list)
for i, r in enumerate(T3): WI[r['wire_uid']].append(i); OW[r['owner_uid']].append(i)
W1 = {r['term_uid']: r for r in W['terminals'] if r['owner_uid'] == 5058}
GR = {'A': {5540, 9647, 10247, 10445, 10950, 17289, 10969, 10757}, 'B': {1359, 2222, 2626, 6104, 8885, 9833, 11261, 29874},
      'C': {10686}, 'W': {376, 3052, 3453}}; TUN = {}
for r in SP['rows']:                                    # structure tunnels (P1) belong to their structure's group
    for g, s in GR.items():
        pt = (r.get('p1_tunnel') or {}).get('tunnel_uid')
        if r['uid'] in s and pt: s.add(pt); TUN[pt] = r['uid']
GR['K'] = {5058}
print('group sets incl. P1 tunnels', {g: len(s) for g, s in GR.items()}, 'sample p1_tunnel', SP['rows'][0].get('p1_tunnel'))
SRP = {1147: 1142, 5796: 5805, 119: 2972, 7311: 11001, 15: 51, 24: 1108}; SRU = set(SRP) | set(SRP.values())
L7W = {4517, 1397, 5274, 3268, 3957, 1899, 4337, 5073, 5056}; L7N = {376, 3052, 3453}
def tag(r):
    u, c, d = r['owner_uid'], r['owner_class'] or '', r.get('frame_diagram')
    for g, s in GR.items():
        if u in s: return 'group %s%s' % (g, ' (tunnel of #%d, P1)' % TUN[u] if u in TUN else '')
    if u in SRU: return '#637 SR (PD149) ' + ('1.2' if u not in (15, 51, 24, 1108) else '1.7')
    if 'Constant' in c: return 'constant'
    if u == 637 or c == 'Diagram': return '#637 loop terminal'
    if d == 686: return 'top-level #686'
    if d == 639: return '1.1-stays (639)'
    return 'diagram %s' % d
def ends(i):
    r = T3[i]; return [j for j in WI[r['wire_uid']] if j != i] if r['wire_uid'] else []
def fmt(j):
    r = T3[j]; return {'uid': r['owner_uid'], 'class': r['owner_class'], 'term': r['term_name'], 'dir': 'OUT' if r['is_source'] else 'IN',
                       'diagram': r.get('frame_diagram'), 'tag': tag(r), 'cite': 'graph_s3 terminals[%d]' % j}
def via(j):
    """one hop through a tunnel/SR/FSIT owner: its other-face terminals and what they connect to"""
    r = T3[j]; c = r['owner_class'] or ''
    if not any(k in c for k in ('Tunnel', 'Shift', 'Left', 'Right')): return None
    out = []
    for k in OW[r['owner_uid']]:
        if k == j or T3[k]['wire_uid'] in (0, r['wire_uid']): continue
        out.append({'face_wire': T3[k]['wire_uid'], 'face_diagram': T3[k].get('frame_diagram'), 'ends': [fmt(x) for x in ends(k)]})
    return {'tunnel': r['owner_uid'], 'class': c, 'outer': out}
print('\n== F1/F2 #5058 terminals (S3 order = index); bed wire = S3 wire (F4)')
rows, touch = [], []
cut = {c[1]: (k, c) for k, c in enumerate(B['cut']) if c[0] == 5058}
rw = {r['i']: (k, r) for k, r in enumerate(RW['rows']) if r['uid'] == 5058}
for t, i in enumerate(OW[5058]):
    r = T3[i]; s1 = W1.get(r['term_uid'], {})
    e = ends(i); row = {'t': t, 'name': r['term_name'], 'dir': 'OUT' if r['is_source'] else 'IN', 'term_uid': r['term_uid'],
                        'bed_wire': r['wire_uid'], 's1_wire': s1.get('wire_uid'), 'cite': 'graph_s3 terminals[%d]' % i,
                        'other': [fmt(j) for j in e], 'via': [v for v in (via(j) for j in e) if v]}
    row['cut'] = 'build_d1_v0 cut[%d]' % cut[t][0] if t in cut else None
    row['rw'] = ('d1_rewire_sources rows[%d] %s' % (rw[t][0], rw[t][1]['action'])) if t in rw else None
    ws = {r['wire_uid']} | {o['face_wire'] for v in row['via'] for o in v['outer']}
    us = {o['uid'] for o in row['other']} | {x['uid'] for v in row['via'] for o in v['outer'] for x in o['ends']}
    if ws & L7W or us & L7N: touch.append((t, sorted(ws & L7W), sorted(us & L7N)))
    rows.append(row)
    print(' t%-2d %-3s %-30r w%-6s S1 w%-6s %s | %s | %s' % (t, row['dir'], r['term_name'], r['wire_uid'], row['s1_wire'], row['cite'], row['cut'], row['rw']))
    for o in row['other']: print('      -> #%s %s %r d%s [%s] (%s)' % (o['uid'], o['class'], o['term'], o['diagram'], o['tag'], o['cite']))
    for v in row['via']:
        for o in v['outer']:
            print('      via %s #%s face w%s d%s: %s' % (v['class'], v['tunnel'], o['face_wire'], o['face_diagram'],
                  ['#%s %s %r d%s [%s]' % (x['uid'], x['class'], x['term'], x['diagram'], x['tag']) for x in o['ends']] or 'no ends'))
gate(len(rows) == 16, 'F1 16 terminals on #5058 (%d)' % len(rows))
gate(sum(1 for r in rows if r['bed_wire']) == 13, 'F1 13 wired')
gate(not touch, 'F4 no #5058 row (incl. one tunnel hop) touches an L7 wire/node: %s' % touch)
print('\n== F3 1.2 SR pairs (PD149): left read by / right fed by (graph_s3)')
f3 = {}
for rt, lf in list(SRP.items())[:4]:
    rd = [fmt(j) for i in OW[lf] if T3[i]['is_source'] and T3[i]['wire_uid'] for j in ends(i)]
    fd = [fmt(j) for i in OW[rt] if not T3[i]['is_source'] and T3[i]['wire_uid'] for j in ends(i)]
    ini = [fmt(j) for i in OW[lf] if not T3[i]['is_source'] and T3[i]['wire_uid'] for j in ends(i)]
    f3['%d/%d' % (rt, lf)] = {'left_read_by': rd, 'right_fed_by': fd, 'left_init': ini}
    print(' #%s/#%s left->%s\n      right<-%s\n      init<-%s' % (rt, lf, [(o['uid'], o['term'], o['tag']) for o in rd],
          [(o['uid'], o['term'], o['tag']) for o in fd], [(o['uid'], o['term'], o['tag']) for o in ini]))
print('\n== F5 cross-check vs build_d1_v0 cut / d1_rewire_sources')
dis = []
for r in rows:
    t = r['t']
    if r['bed_wire'] and t not in cut: dis.append('t%d wired on S3 but absent from cut' % t)
    if t in cut and (cut[t][1][2], cut[t][1][4], not cut[t][1][3]) != (r['name'], r['bed_wire'], r['dir'] == 'IN'):
        dis.append('t%d cut %s vs S3 %r w%s' % (t, cut[t][1], r['name'], r['bed_wire']))
    if t in rw:
        x = rw[t][1]; oe = {o['uid'] for o in x['other_ends']}; me = {o['uid'] for o in r['other']}
        if (x['name'], x['wire']) != (r['name'], r['bed_wire']): dis.append('t%d rewire name/wire %r w%s' % (t, x['name'], x['wire']))
        me |= {TUN[u] for u in me if u in TUN}          # a structure is addressed on the bed by its P1 tunnel
        if oe - me: dis.append('t%d rewire other_ends %s not on S3 wire (S3 has %s)' % (t, sorted(oe - me), sorted(me)))
    if r['s1_wire'] != r['bed_wire']: dis.append('t%d S1 w%s != S3 w%s' % (t, r['s1_wire'], r['bed_wire']))
for d in dis: print(' DIS', d)
gate(set(cut) == set(rw), 'F5 cut and rewire_sources index sets equal (%d/%d)' % (len(cut), len(rw)))
print('\n== F6 docs/stage-simulator-plan.md:40,69,91: plan = tools/bench/plan_<stage>.json (+ sim steps tools/bench/sim/<stage>/step_NN_<action>.json); '
      'launch gate needs dry + pre-run PASS records in tools/bench/prerun_records.jsonl (py tools/stage_prerun.py --dry|--prerun <plan.json>)')
out = {'bed': BED, 'bed_md5': M(BED), 'graph': P3, 'graph_file_md5': M(P3), 'wiki_file_md5': M(PW), 'l7_overlap': touch,
       'rows': rows, 'f3': f3, 'f5_disagreements': dis}
json.dump(out, open('tools/bench/k_facts_79.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(protocol.result_line(protocol.make_result(G['pass'], G['fail'], G['first'],
      [{'path': 'tools/bench/k_facts_79.json', 'md5': M('tools/bench/k_facts_79.json')}])))
