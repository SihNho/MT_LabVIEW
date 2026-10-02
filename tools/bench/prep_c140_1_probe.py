"""prep_c140_1_probe - card 140-1 read-only condensed print of diag_c140_1_sessions.json (no LabVIEW)."""
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'tools/bench/diag_c140_1_sessions.json'), encoding='utf-8'))
for b in d['step1_binds']:
    print('S1B', b['op'], b['id'], b['kind'], b['classes'], b['interval'], b['first_use'], b['first_use_op'], b['binder'][:40])
print('S1 reads', d['merge']['step1_reads'])
for g in d['merge']['step1_groups']:
    print('S1G', g['read'], g['binds'], g['ambiguous'])
print('V14 reads', len(d['merge']['v14_reads']), d['merge']['v14_reads'])
for g in d['merge']['v14_groups']:
    if g['ambiguous']:
        print('V14G amb', g['read'], g['binds'], g['ambiguous'])
for t in ('table_A', 'table_B'):
    for r in d[t]:
        if r['uses_cut']:
            print(t, r['session'], 'uses_cut', r['uses_cut'][:8])
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":0,"fail":0},"first_fail":null,"artefacts":[]}')
