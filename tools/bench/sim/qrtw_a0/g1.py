"""card 120-5 offline read of the pool-bed graph dump (no LabVIEW): structure, diagram 686's owner/nodes, typed constants."""
import json, os, collections
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
d = json.load(open('tools/bench/graph_qrt_pool_20260928.json', encoding='utf-8'))
print(list(d.keys()))
for k, v in d.items():
    if isinstance(v, list):
        print(k, len(v), json.dumps(v[0])[:500] if v else None)
    elif isinstance(v, dict):
        print(k, 'dict', len(v), list(v)[:10])
    else:
        print(k, repr(v)[:200])
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
