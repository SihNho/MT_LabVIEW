"""prep_c138_p1_q - card 138-P1 read-only query of a plan json (no LabVIEW): top-level keys, op counts, actions matching args."""
import json
import os
import sys
from collections import Counter
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
P = os.environ.get("QPLAN", "tools/bench/plan_ring_p4_v8.json")
v = json.load(open(os.path.join(R, P), encoding='utf-8'))
for k in v:
    if k != 'actions':
        print("TOP", k, json.dumps(v[k])[:900])
print(Counter(a['op'] for a in v['actions']))
pat = sys.argv[1:]
for i, a in enumerate(v['actions'], 1):
    s = json.dumps(a)
    if any(p.lower() in s.lower() for p in pat):
        print(i, s[:900])
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
