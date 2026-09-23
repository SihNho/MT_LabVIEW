"""c73 L7-R facts (M1-M4) - pure Python over on-disk JSONs, no LabVIEW, no model.
Found before writing: tools/vigraph.py build4/terminals/reach4/path/sources_of/effective_sources; the S1 wiki
(docs/wiki/subvi/D1_s1_copy.json), S1 objs (graph_objs_s1_20260923.json) and loops (graph_loops_s1_20260924.json),
S3 terms+objs (graph_s3_loop15_20260924.json). No L7-1 graph exists on disk: L7-1 = S3 + the L7-1a/b edits named in
tools/bench/stage_d1_l7_1b_r3.log:206,346 (#376 moved to diagram 23405; tunnels 3644/2294/5096 deleted).
Prediction: all files load; #376 has 9+ terminals; M3 prints a path list or 'none'."""
import json, collections, sys
sys.path.insert(0, 'tools')
import vigraph as V
J = lambda p: json.load(open(p, encoding='utf-8'))
W = J('docs/wiki/subvi/D1_s1_copy.json'); O1 = J('tools/bench/graph_objs_s1_20260923.json')
L1 = J('tools/bench/graph_loops_s1_20260924.json'); S3 = J('tools/bench/graph_s3_loop15_20260924.json')
print('md5 wiki', W['md5'], 'objs', O1['md5'], 'loops', L1['md5'], 'S3', S3['md5'])
G1 = V.build4(W['terminals'], O1['objects'], L1['loops'], None, W['fs_tunnel_pairs'])
G3 = V.build4(S3['terminals'], S3['objs'], None, None, None)
print('G1 method', {k: v for k, v in G1['method'].items() if k != 'assumption_A'})

def dtree(terms):
    """diagram parent map from tunnel-ish nodes: inner-terminal frame_diagram -> outer-terminal frame_diagram"""
    by = collections.defaultdict(list)
    for r in terms: by[r['owner_uid']].append(r)
    par, owner = {}, {}
    for u, rs in by.items():
        inn = [r['frame_diagram'] for r in rs if 'Inner' in (r.get('term_class') or '') and r.get('frame_diagram')]
        out = [r['frame_diagram'] for r in rs if 'Outer' in (r.get('term_class') or '') and r.get('frame_diagram')]
        if inn and out and inn[0] != out[0]:
            par.setdefault(inn[0], out[0]); owner.setdefault(inn[0], (u, rs[0]['owner_class']))
    return by, par, owner
LOOPBODY = {639: '1.1 #637 body', 23405: '1.7 #23041 body', 536: 'TOP'}
def chain(par, d):
    out = []
    while d and len(out) < 12:
        out.append('%s%s' % (d, '(' + LOOPBODY[d] + ')' if d in LOOPBODY else '')); d = par.get(d)
    return '>'.join(out)
BY1, PAR1, _ = dtree(W['terminals']); BY3, PAR3, _ = dtree(S3['terminals'])
def diag(by, u):
    ds = sorted(set(r['frame_diagram'] for r in by.get(u, []) if r.get('frame_diagram')))
    return ds
def where(u):
    d1, d3 = diag(BY1, u), diag(BY3, u)
    l7 = [23405] if u == 376 else d3
    return 'S1 %s | S3 %s | L7-1 %s' % ([chain(PAR1, d) for d in d1], [chain(PAR3, d) for d in d3],
                                         [chain(PAR3, d) for d in l7] + (['(moved by L7-1a)'] if u == 376 else []))
def srcs(G, key):
    return [(a, w) for k, a, b, w in G['edges'] if b == key and k != 'thru']
def sinks(G, key):
    return [(b, w, k) for k, a, b, w in G['edges'] if a == key and k != 'thru']

print('\n== M1 CDIFF rows (log 338-345)')
CD = [(376, 'current frame data array in'), (376, 'saved file refnum'), (2048, 'array'), (2048, 'length'),
      (3453, 'file progress'), (6384, 'actual # data points'), (6384, 'error in'), (6384, 'file # to append')]
for n, t in CD:
    for key in V.terminals(G1, node=n, name=t, is_source=False):
        for a, w in srcs(G1, key):
            print(' M1 sink %-45s <- %-45s wire %s' % (key, a, w))
            print('    src  #%s %s' % (V.key_parts(a)[0], where(V.key_parts(a)[0])))
            print('    sink #%s %s' % (n, where(n)))
        eff = V.effective_sources(G1, key)
        print('    effective(collapsed) S1:', sorted(eff))

print('\n== M2 nodes')
for n in (2048, 6384, 3453, 1929, 5020, 376):
    print(' M2 #%s class S1=%s S3=%s | %s' % (n, G1['cls'].get(n), G3['cls'].get(n), where(n)))
    for key in V.terminals(G1, node=n):
        r = G1['rows'][key]
        if r['is_source']:
            cs = sinks(G1, key)
            print('   OUT %-50s w%-6s -> %s' % (key, r['wire_uid'], [(b, 'diag' + str(diag(BY1, V.key_parts(b)[0]))) for b, w, k in cs]))
        else:
            print('   IN  %-50s w%-6s <- %s eff=%s' % (key, r['wire_uid'], [a for a, w in srcs(G1, key)],
                                                  sorted(V.effective_sources(G1, key))))
    for key in V.terminals(G3, node=n):
        r = G3['rows'][key]
        print('   S3 %s %-50s w%s %s' % ('OUT' if r['is_source'] else 'IN ', key, r['wire_uid'],
              [b for b, w, k in sinks(G3, key)] if r['is_source'] else [a for a, w in srcs(G3, key)]))

print('\n== M3 feedback #376 outputs -> #376 inputs (S1, all edge kinds incl thru/sr)')
outs = V.terminals(G1, node=376, is_source=True); ins = set(V.terminals(G1, node=376, is_source=False))
R = V.reach4(G1, outs)
hit = sorted(ins & R)
print(' M3 reached inputs:', hit if hit else 'none')
for h in hit:
    best = None
    for o in outs:
        p = V.path(G1, o, h)
        if p and (best is None or len(p) < len(best)): best = p
    print(' M3 path to', h, ':', ' -> '.join(best or []))
    kinds = collections.Counter()
    for a, b in zip(best, best[1:]):
        kinds.update(k for k, x, y, w in G1['edges'] if x == a and y == b)
    print('    edge kinds on path', dict(kinds))
R2 = V.reach4(G1, outs, kinds=('wire', 'thru'))
print(' M3 reached inputs WITHOUT sr/fs/local/global edges:', sorted(ins & R2) or 'none')
for via in (2048, 6384, 3453):
    vk = V.terminals(G1, node=via, is_source=True)
    Rv = V.reach4(G1, vk)
    print(' M3 from #%s outputs reach #376 inputs:' % via, sorted(ins & Rv) or 'none')

print('\n== M4 #376 inputs, index = order in the S1 wiki terminal list')
i = 0
for r in W['terminals']:
    if r['owner_uid'] == 376:
        key = [k for k, x in G1['rows'].items() if x['term_uid'] == r['term_uid']][0]
        s = srcs(G1, key) if not r['is_source'] else []
        print(' M4 t%-2d %s %-34s w%-6s src=%s' % (i, 'OUT' if r['is_source'] else 'IN ', r['term_name'], r['wire_uid'], s))
        for a, w in s:
            u = V.key_parts(a)[0]
            print('       src #%s cls=%s %s; collapsed=%s' % (u, G1['cls'].get(u), where(u), sorted(V.effective_sources(G1, key))))
        i += 1
