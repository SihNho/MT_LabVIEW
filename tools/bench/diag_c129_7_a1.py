"""diag_c129_7_a1 - offline: inspect graph file structure + diag_c126_4_fs.log lines 53/57 (card 129-7). No LabVIEW.
Prediction: prints keys; no gates."""
import json, sys
R = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop"
g = json.load(open(R + r"\tools\bench\graph_ring_p3a_20261001_190155.json"))
print(type(g))
if isinstance(g, dict):
    for k, v in g.items():
        print(k, type(v).__name__, len(v) if hasattr(v, '__len__') else v)
        if isinstance(v, list) and v:
            print('   sample', json.dumps(v[0])[:400])
        if isinstance(v, dict) and v:
            kk = next(iter(v)); print('   sample', kk, json.dumps(v[kk])[:400])
for ln in (53, 57):
    s = open(R + r"\tools\bench\diag_c126_4_fs.log", encoding='utf-8', errors='replace').read().splitlines()[ln-1]
    print(ln, s[:2500])
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":0,"fail":0},"first_fail":null,"artefacts":[]}')
