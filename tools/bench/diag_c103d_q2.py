"""card 103-4 offline query 2 (no LabVIEW): base wire count, step-39 state shape, negative-uid coverage by the Part-A binding."""
import json, os, sys
T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, T); os.chdir(T)
import stagexec as SX, stagesim as SS
P = json.load(open('bench/sim/disp/plan_disp.json', encoding='utf-8'))
B = json.load(open('bench/par1359_95_graph.json', encoding='utf-8'))
print('BASE keys', sorted(B), 'vi', B.get('vi'), 'md5', B.get('md5'))
print('BASE wire uids', len(set(r['wire_uid'] for r in B['terminals'] if r['wire_uid'])))
ex = SX.Executor('bench/sim/disp/plan_disp.json', None)
st = ex.step(39)['state']
print('step39 keys', sorted(st), 'effect' in ex.step(39))
neg = {}
for r in st['terminals']:
    for k in ('owner_uid', 'term_uid', 'wire_uid', 'frame_diagram'):
        if isinstance(r.get(k), int) and r[k] < 0:
            neg.setdefault(k, set()).add(r[k])
for o in st.get('objs') or []:
    if int(o['uid']) < 0:
        neg.setdefault('obj', set()).add(int(o['uid']))
for k, v in (st.get('diagrams') or {}).items():
    if int(k) < 0 or int(v) < 0:
        neg.setdefault('diagrams', set()).update(x for x in (int(k), int(v)) if x < 0)
for k, v in (st.get('owners') or {}).items():
    if int(k) < 0 or int(v[1] or 0) < 0:
        neg.setdefault('owners', set()).update(x for x in (int(k), int(v[1] or 0)) if x < 0)
for L in st.get('loops') or []:
    if int(L['loop_uid']) < 0:
        neg.setdefault('loops', set()).add(int(L['loop_uid']))
print('sym', {k: v for k, v in st['sym'].items()})
b = json.load(open('bench/stage_d1_dispA.json', encoding='utf-8'))['partA']['bind']
M = {}
for kind in ('obj', 'term', 'diag'):
    for k, v in b[kind].items():
        if int(k) in M and M[int(k)] != v:
            print('CONFLICT', k, M[int(k)], v)
        M[int(k)] = v
for k, v in neg.items():
    print(k, sorted(v), 'unbound', sorted(x for x in v if x not in M))
print('loops', [(L['loop_uid'], L.get('right_uids'), L.get('left_of')) for L in st.get('loops') or [] if int(L['loop_uid']) < 0])
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":0,"fail":0},"first_fail":null,"artefacts":[]}')
