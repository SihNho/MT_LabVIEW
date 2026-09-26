"""card 103-4 offline query (no LabVIEW): compiled display-stage ops + the Part-A binding JSON shape."""
import json, os, sys
T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, T); os.chdir(T)
import stagexec as SX
P = json.load(open('bench/sim/disp/plan_disp.json', encoding='utf-8'))
ops = SX.compile_plan(P)
A = P['actions']
for k, o in enumerate(ops, 1):
    print(k, o['kind'], o['acts'], [A[n-1].get('id') for n in o['acts']], {x: y for x, y in o.items() if x not in ('kind', 'acts')})
print(list(P.keys()))
d = json.load(open('bench/stage_d1_dispA.json', encoding='utf-8'))
print(list(d.keys()))
pa = d.get('partA')
if pa:
    print({k: (v if not isinstance(v, (dict, list)) else (type(v).__name__, len(v))) for k, v in pa.items()})
    print(json.dumps(pa.get('bind'))[:1500]); print(pa.get('loop_of')); print(json.dumps(pa.get('sym_real'))[:800])
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":0,"fail":0},"first_fail":null,"artefacts":[]}')
