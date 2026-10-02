import json, os
os.chdir(r"G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop")
p = json.load(open('tools/bench/plan_ring_p4_v15.json', encoding='utf-8'))
print([k for k in p])
print(json.dumps(p['base']), p.get('context'), p.get('stage'))
A = p['actions']
for i, a in enumerate(A[:20], 1):
    print(i, json.dumps(a)[:500])
for i, a in enumerate(A, 1):
    if 'ras' in a['id'] or a.get('prim') == 'Replace Array Subset' or a['op'] in ('delete_object',):
        print('RAS', i, json.dumps(a)[:1200])
print(json.dumps(p['finalized'], default=str)[:2500])
ops = sorted(set(a['op'] for a in A))
print(ops)
