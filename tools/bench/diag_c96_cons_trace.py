"""Card 96-3 - OFFLINE, read-only consumer trace of ForLoop #1359's outputs in D1_s1_copy.vi. No LabVIEW, no COM.

Existing tools checked first: tools/bench/par1359_95_graph.json (card 95-2: wiki terminals + graph_objs objects,
same md5 as the VI) already holds every terminal with its wire and frame diagram, and the objects in LabVIEW
pre-order; result_94-3 gave the tunnel map. No existing tracer walks sinks through structures, so this one does,
using the graph's own edge rules (graph_summary.edge_method: node pass-through all-in -> all-out; SR pairing by
equal TOP; FS tunnel pairing by equal TOP).

PREDICTION CONTRACT (gates):
 G1 VI md5 on disk == graph md5 (3e3d23ce...) -> graph describes the file.
 G2 #1359 out tunnels are exactly 9227 and 11363 (result_94-3 facts).
 G3 tunnel 9227 outer wire 9215 reaches RightShiftRegister #9018 (result_94-3).
 G4 every #1359 outer terminal sits on diagram 639 (no case between #1359 and #637's body).
 G5 diagram tree consistent: every tunnel's inner diagrams have the tunnel's outer diagram as parent (0 mismatches).
 G6 trace terminates (bounded, visited set) and every reached sink is classified.
 G7 (added after review archive/peer/2026-09-26-c96-cons-trace-g2.md) no Diagram without an owner structure;
    2235 -> case 2222, 3292 -> case 3191, case 2222 has 2 frames. G3 also asserts SR 9018 pairs only with 9025.
 Run 1 FAILED G2/G4 (tunnels positioned by their outer side); fixes per that review, s.1-3, s.5.
Outputs: tools/bench/f1359_consumers_96.json (+ printed table). Ends with a RESULT line.
"""
import json, os, sys, hashlib, collections
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import protocol

HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(HERE, 'par1359_95_graph.json')
WIKI = os.path.join(HERE, '..', '..', 'docs', 'wiki', 'subvi', 'D1_s1_copy.json')
OUT = os.path.join(HERE, 'f1359_consumers_96.json')
VI = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_s1_copy.vi"
d = json.load(open(G, encoding='utf-8'))
wiki = json.load(open(WIKI, encoding='utf-8'))
gates = []
def gate(name, ok, detail):
    gates.append((name, bool(ok), detail)); print('GATE', name, 'PASS' if ok else 'FAIL', detail)

md5 = hashlib.md5(open(VI, 'rb').read()).hexdigest()
gate('G1 md5', md5 == d['md5'], '%s vs %s' % (md5, d['md5']))

objs = d['objs']; obj = {o['uid']: o for o in objs}
terms = d['terminals']; term = {t['term_uid']: t for t in terms}
by_owner = collections.defaultdict(list); by_wire = collections.defaultdict(list)
for t in terms:
    by_owner[t['owner_uid']].append(t)
    if t['wire_uid']:
        by_wire[t['wire_uid']].append(t)
subvi = {c['node_uid']: c['subvi_name'] for c in wiki['graph_summary'].get('subvi_calls', [])} if isinstance(wiki['graph_summary'].get('subvi_calls'), list) else {}
if not subvi:
    subvi = {c['node_uid']: c['subvi_name'] for c in d['graph_summary']['subvi_calls']}
TUN = {'LoopTunnel', 'Tunnel', 'SelectorTunnel', 'FlatSequenceInnerTunnel', 'FlatSequenceOuterTunnel'}
STRUCT = {'ForLoop', 'WhileLoop', 'CaseStructure', 'FlatSequence', 'Sequence', 'EventStructure'}
TERMCLS = {'Terminal', 'InnerTerminal', 'OuterTerminal', 'ParameterTerminal', 'OverridableParameterTerminal'}

# ---- diagram tree from the pre-order -------------------------------------------------------------
diag_parent = {}          # inner diagram -> outer diagram, from tunnels
for owner, ts in by_owner.items():
    if obj.get(owner, {}).get('class') in ('LoopTunnel', 'Tunnel', 'SelectorTunnel'):
        outer = [t['frame_diagram'] for t in ts if t['term_class'] == 'OuterTerminal']
        inner = [t['frame_diagram'] for t in ts if t['term_class'] == 'InnerTerminal']
        if outer:
            for i in inner:
                diag_parent.setdefault(i, outer[0])
def obj_diag(u):
    ts = by_owner.get(u)
    if ts:
        outer = [t['frame_diagram'] for t in ts if t['term_class'] == 'OuterTerminal']
        return outer[0] if outer else ts[0]['frame_diagram']
    if obj.get(u, {}).get('class') == 'Wire' and by_wire.get(u):
        return by_wire[u][0]['frame_diagram']
    return None
diag_owner = {}; struct_parent = {}; struct_diags = collections.defaultdict(list); tunnel_struct = {}
stack = []; cur = None; TOP = None
def pop_to(X):
    """Pop only when X is known: top-level clears; a diagram of a stacked structure pops to it; unknown X leaves
    the stack alone (peer 2026-09-26-c96-cons-trace-g2 s.1: an unknown X used to empty the stack)."""
    global stack
    if X == TOP:
        stack = []; return True
    if any(X in struct_diags[s] for s in stack):
        while X not in struct_diags[stack[-1]]:
            stack.pop()
        return True
    return False
def struct_outer_diag(i):
    """A structure has no own terminals: its parent diagram = frame of the outer-side objects listed right after it
    (OuterTerminal objects / FlatSequenceOuterTunnel), else diag_parent of its first Diagram."""
    for o in objs[i + 1:]:
        if o['class'] == 'OuterTerminal' and o['uid'] in term:
            return term[o['uid']]['frame_diagram']
        if o['class'] == 'FlatSequenceOuterTunnel' and by_owner.get(o['uid']):
            return by_owner[o['uid']][0]['frame_diagram']
        if o['class'] in ('Diagram', 'TopLevelDiagram'):
            return diag_parent.get(o['uid'])
    return None
for i, o in enumerate(objs):
    u, c = o['uid'], o['class']
    if c in TERMCLS:
        continue
    if c == 'TopLevelDiagram':
        cur = TOP = u; diag_owner[u] = None; continue
    if c == 'Diagram':
        P = diag_parent.get(u)
        if P is not None:
            cands = [k for k, s in enumerate(stack) if struct_parent[s] == P]
            if cands:
                del stack[cands[-1] + 1:]
        S = stack[-1] if stack else None
        diag_owner[u] = S; struct_diags[S].append(u); cur = u; continue
    if c in STRUCT:
        P = struct_outer_diag(i)
        if P is not None and pop_to(P):
            cur = P
        struct_parent[u] = cur; stack.append(u); continue
    X = obj_diag(u)
    if c in ('LoopTunnel', 'Tunnel', 'SelectorTunnel'):
        # pre-order lists a tunnel under its structure's frame: position it by the INNER side, the listed frame
        # first when it is one of them (peer s.2: a case tunnel has one InnerTerminal per frame)
        inn = [t['frame_diagram'] for t in by_owner.get(u, []) if t['term_class'] == 'InnerTerminal']
        X = cur if cur in inn else (inn[0] if inn else X)
    if X is not None and X != cur and pop_to(X):
        cur = X
    if c in TUN:
        tunnel_struct[u] = diag_owner.get(cur)
mism = sum(1 for i, p in diag_parent.items() if diag_owner.get(i) is not None and struct_parent.get(diag_owner[i]) != p)
gate('G5 tree', mism == 0, 'tunnel parent mismatches %d over %d inner diagrams' % (mism, len(diag_parent)))
none_d = [o['uid'] for o in objs if o['class'] == 'Diagram' and diag_owner.get(o['uid']) is None]
g7 = (not none_d and diag_owner.get(2235) == 2222 and diag_owner.get(3292) == 3191 and len(struct_diags[2222]) == 2)
gate('G7 owners', g7, 'owner-None diagrams %d %s; 2235->%s 3292->%s frames(2222)=%d' % (
    len(none_d), none_d[:10], diag_owner.get(2235), diag_owner.get(3292), len(struct_diags[2222])))
print('CHECK 7922 terms', [(t['term_uid'], t['term_class'], t['is_source'], t['wire_uid']) for t in by_owner[7922]])

def chain(D):
    """diagram -> list of (structure uid, class, frame index, n frames) from inner to outer."""
    out = []; seen = set()
    while D is not None and D in diag_owner and diag_owner[D] is not None and D not in seen:
        seen.add(D); S = diag_owner[D]
        out.append((S, obj[S]['class'], struct_diags[S].index(D), len(struct_diags[S]), D))
        D = struct_parent.get(S)
    return out
def owner_loop(D):
    for S, cls, fi, nf, dd in chain(D):
        if cls in ('ForLoop', 'WhileLoop'):
            return S
    return None
def case_selector(S):
    """First 'Tunnel' listed after the case's first frame (pre-order) = selector; returns (tunnel, src uid, src class, src term)."""
    first = struct_diags[S][0]; i = next(k for k, o in enumerate(objs) if o['uid'] == first)
    for o in objs[i + 1:]:
        if o['class'] == 'Tunnel' and tunnel_struct.get(o['uid']) == S:
            outer = [t for t in by_owner[o['uid']] if t['term_class'] == 'OuterTerminal']
            if outer and outer[0]['wire_uid']:
                srcs = [t for t in by_wire[outer[0]['wire_uid']] if t['is_source']]
                s = srcs[0] if srcs else None
                return (o['uid'], s and s['owner_uid'], s and s['owner_class'], s and s['term_name'])
            return (o['uid'], None, None, None)
        if o['class'] == 'Diagram' and diag_owner.get(o['uid']) != S and o['uid'] != first:
            pass
    return (None, None, None, None)

# ---- G2/G4: #1359's tunnels -----------------------------------------------------------------------
t1359 = [u for u, s in tunnel_struct.items() if s == 1359]
outs = [u for u in t1359 if any(t['term_class'] == 'OuterTerminal' and t['is_source'] for t in by_owner[u])]
gate('G2 out tunnels', sorted(outs) == [9227, 11363], 'tunnels %s outs %s' % (sorted(t1359), sorted(outs)))
od = sorted({t['frame_diagram'] for u in t1359 for t in by_owner[u] if t['term_class'] == 'OuterTerminal'})
gate('G4 on 639', od == [639], 'outer diagrams %s; chain(639)=%s; chain(7911)=%s' % (od, chain(639), chain(7911)))

# ---- SR pairing (equal TOP) ----------------------------------------------------------------------
def sr_partner(u):
    """graph_summary.edge_method.sr: equal TOP (pos[1]); restricted to the same loop body (inner terminal diagram)."""
    cls = obj[u]['class']; want = 'LeftShiftRegister' if cls == 'RightShiftRegister' else 'RightShiftRegister'
    y = obj[u]['pos'][1]
    body = {t['frame_diagram'] for t in by_owner[u] if t['term_class'] == 'InnerTerminal'}
    return [o['uid'] for o in objs if o['class'] == want and o['pos'][1] == y and
            body & {t['frame_diagram'] for t in by_owner[o['uid']] if t['term_class'] == 'InnerTerminal'}]

# ---- forward trace --------------------------------------------------------------------------------
records = []   # (start, path list of uids, sink uid, kind)
MAXN = 4000
def kind_of(u):
    c = obj.get(u, {}).get('class'); n = subvi.get(u, '')
    if c == 'ControlTerminal': return 'indicator/control terminal'
    if c == 'Local': return 'local variable'
    if c == 'Global': return 'global variable'
    if c == 'ReadWriteFile': return 'FILE WRITE (ReadWriteFile)'
    if c in ('Property', 'Invoke'): return 'property/invoke node'
    if c in ('SubVI', 'PolymorphicSubVI'): return 'subVI ' + n
    if c in ('RightShiftRegister', 'LeftShiftRegister'): return 'shift register'
    return c
def trace(start_term):
    """BFS over (source terminal) -> sinks; returns dict node uid -> (parent node uid, via wire)."""
    seen = {}; q = collections.deque([(start_term, None)]); n = 0; srhits = []
    while q and n < MAXN:
        st, par = q.popleft(); n += 1
        w = term[st]['wire_uid']
        if not w: continue
        for sk in by_wire[w]:
            if sk['is_source']: continue
            u = sk['owner_uid']
            if sk['owner_class'] in ('Diagram', 'TopLevelDiagram'):
                # a front-panel terminal on a diagram: the terminal itself is the sink, never expand the diagram
                key = ('FP', sk['term_uid'])
                if key not in seen:
                    seen[key] = (par, w, sk['term_uid'], sk['term_name'])
                continue
            if u in seen: continue
            seen[u] = (par, w, sk['term_uid'], sk['term_name'])
            c = obj.get(u, {}).get('class', sk['owner_class'])
            nxt = [t for t in by_owner[u] if t['is_source']]
            if c == 'RightShiftRegister':
                srhits.append(u)
                for p in sr_partner(u):
                    if p not in seen:
                        seen[p] = (u, None, None, 'next-iteration')
                        nxt += [t for t in by_owner[p] if t['is_source']]
            if c == 'FlatSequenceOuterTunnel':
                pass  # rare on this path; reported if reached
            for t in nxt:
                q.append((t['term_uid'], u))
    return seen, n, srhits

def path_of(seen, k):
    out = []; guard = 0
    while k is not None and guard < 200:
        out.append(k[1] if isinstance(k, tuple) else k)
        k = seen.get(k, (None,))[0]; guard += 1
    return list(reversed(out))
srp = {o['uid']: sr_partner(o['uid']) for o in objs if o['class'] == 'RightShiftRegister'}
print('CHECK SR pairing: right SRs %d, with exactly 1 partner %d, others %s' % (
    len(srp), sum(1 for v in srp.values() if len(v) == 1), {k: v for k, v in srp.items() if len(v) != 1}))
result = {'task': '96-3', 'vi': VI, 'md5': md5, 'tunnels': {}, 'no_vi_was_run': True, 'level': 'STRUCTURAL (offline graph)'}
for tun in (9227, 11363):
    inner = [t for t in by_owner[tun] if t['term_class'] == 'InnerTerminal'][0]
    srcs = [t for t in by_wire[inner['wire_uid']] if t['is_source']]
    src_desc = [(s['owner_uid'], s['owner_class'], s['term_name']) for s in srcs]
    outer = [t for t in by_owner[tun] if t['term_class'] == 'OuterTerminal'][0]
    seen, n, srhits = trace(outer['term_uid'])
    rows = []
    for u, (par, w, tu, tn) in seen.items():
        if isinstance(u, tuple):
            D = term[tu]['frame_diagram']
            fpk = ('front-panel terminal (indicator)' if term[tu]['term_class'] == 'ControlTerminal'
                   else 'loop/unresolved diagram terminal (class Terminal; e.g. while-loop stop terminal)')
            rows.append({'uid': tu, 'class': 'FPTerminal', 'kind': fpk, 'label': tn, 'path': path_of(seen, u),
                         'in_term': tu, 'from': par, 'wire': w, 'diagram': D, 'owner_loop': owner_loop(D),
                         'cases': [{'case': S, 'frame_index': fi, 'n_frames': nf, 'frame_diagram': dd,
                                    'selector_src': case_selector(S)[1], 'selector_src_class': case_selector(S)[2],
                                    'selector_src_term': case_selector(S)[3], 'selector_tunnel': case_selector(S)[0]}
                                   for S, cls, fi, nf, dd in chain(D) if cls == 'CaseStructure'],
                         'terminal': True})
            continue
        D = obj_diag(u)
        ch = chain(D) if D else []
        cases = []
        for S, cls, fi, nf, dd in ch:
            if cls == 'CaseStructure':
                sel = case_selector(S)
                cases.append({'case': S, 'frame_index': fi, 'n_frames': nf, 'frame_diagram': dd,
                              'selector_tunnel': sel[0], 'selector_src': sel[1], 'selector_src_class': sel[2],
                              'selector_src_term': sel[3]})
        rows.append({'uid': u, 'class': obj.get(u, {}).get('class'), 'kind': kind_of(u), 'label': subvi.get(u) or tn,
                     'path': path_of(seen, u),
                     'in_term': tu, 'from': par, 'wire': w, 'diagram': D, 'owner_loop': owner_loop(D) if D else None,
                     'cases': cases,
                     'terminal': not any(t['is_source'] and t['wire_uid'] for t in by_owner[u])})
    result['tunnels'][tun] = {'inner_src': src_desc, 'outer_wire': outer['wire_uid'], 'visited': n,
                              'sr_hits': srhits, 'reached': rows}
    print('TUNNEL', tun, 'inner<-', src_desc, 'outer wire', outer['wire_uid'], 'reached', len(rows), 'nodes, SR', srhits)
    for r in sorted(rows, key=lambda r: (r['class'] or '')):
        if r['class'] in ('Wire',): continue
        cs = ';'.join('case%s f%d/%d sel<-%s(%s)' % (c['case'], c['frame_index'], c['n_frames'], c['selector_src'],
                                                    c['selector_src_class']) for c in r['cases'])
        print('  REACH %6s %-24s %-38s loop=%s diag=%s from=%s %s%s' % (r['uid'], r['class'], str(r['label'])[:38],
              r['owner_loop'], r['diagram'], r['from'], cs, (' SINK path=' + '>'.join(map(str, r['path']))) if r['terminal'] else ''))
gate('G3 9227->9018', 9018 in {r['uid'] for r in result['tunnels'][9227]['reached']} and sr_partner(9018) == [9025],
     'reached SR set %s; partner(9018)=%s' % (result['tunnels'][9227]['sr_hits'], sr_partner(9018)))
allr = {r['uid'] for t in result['tunnels'].values() for r in t['reached']}
k5058 = 5058 in allr
fw = [u for u in allr if obj.get(u, {}).get('class') == 'ReadWriteFile' or 'save' in (subvi.get(u) or '').lower() or 'write' in (subvi.get(u) or '').lower() or 'tdms' in (subvi.get(u) or '').lower()]
motor = [u for u in allr if any(k in (subvi.get(u) or '').lower() for k in ('motor', 'setcommand', 'visa', 'serial', 'asi', 'pi ', 'move', 'mag', 'rot'))]
print('FACT kernel5058_reached', k5058, '| file-write-like reached', [(u, subvi.get(u) or obj.get(u, {}).get('class')) for u in fw],
      '| motor/instrument-like reached', [(u, subvi.get(u)) for u in motor])
result['kernel_5058_reached'] = k5058; result['file_write_reached'] = fw; result['motor_like_reached'] = motor
# where the history input comes from: SR 9025 (left) / 9018 (right)
for sr in (9025, 9018):
    ts = by_owner[sr]
    info = []
    for t in ts:
        others = [(o['owner_uid'], o['owner_class'], o['term_name']) for o in by_wire[t['wire_uid']] if o['term_uid'] != t['term_uid']] if t['wire_uid'] else []
        info.append({'term': t['term_uid'], 'src': t['is_source'], 'class': t['term_class'], 'diag': t['frame_diagram'], 'wire': t['wire_uid'], 'peers': others})
    result['sr_%d' % sr] = info
    print('SR', sr, json.dumps(info))
gate('G6 trace bounded', all(t['visited'] < MAXN for t in result['tunnels'].values()), 'visited %s' % [t['visited'] for t in result['tunnels'].values()])
result['gates'] = gates
json.dump(result, open(OUT, 'w', encoding='utf-8'), indent=1, default=str)
npass = sum(1 for g in gates if g[1]); nfail = len(gates) - npass
ff = next((g[0] + ': ' + g[2] for g in gates if not g[1]), None)
art = [{'path': 'tools/bench/f1359_consumers_96.json', 'md5': hashlib.md5(open(OUT, 'rb').read()).hexdigest()}]
print(protocol.result_line(protocol.make_result(npass, nfail, ff, art)))
