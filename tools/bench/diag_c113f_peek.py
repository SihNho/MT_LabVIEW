"""diag_c113f_peek - card 113-4, OFFLINE read of the L2-B2b plan files (no LabVIEW)."""
import json, os
os.chdir(r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop")
p = json.load(open('tools/bench/plan_l2b2b_in.json', encoding='utf-8'))
print(list(p.keys()))
for a in p['actions']:
    print(json.dumps(a)[:400])
print('OPEN', len(p['open_rows']))
for r in p['open_rows']:
    print(json.dumps(r)[:250])
f = json.load(open('tools/bench/plan_l2b2b.json', encoding='utf-8'))
print(list(f.keys())); print(list(f['finalized'].keys()))
print(json.dumps(f['finalized']['plan_in']))
print('FIN open_rows', len(f['open_rows']))
d = json.load(open('tools/bench/plan_l2b2b_d4.json', encoding='utf-8'))
print({k: (v if k != 'scope_nodes' else len(v)) for k, v in d.items()})
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":0,"fail":0},"first_fail":null,"artefacts":[]}')
