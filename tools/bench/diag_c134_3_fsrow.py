"""Card 134-3 step 1 (offline, no LabVIEW): where does graph_ring_p3b2a_fs_20261002_102553.json hold
FS 27509's node row, and on which diagram was it read?  Prediction: the top-level keys are listed; every
occurrence of uid 27509 is printed as (json path, value excerpt); no inference is made.
Reuse check: tools/bench/diag_c134_1_graph.py reads graphs for borders, not for one uid's path."""
import json, sys
G = 'tools/bench/graph_ring_p3b2a_fs_20261002_102553.json'
TARGETS = [int(a) for a in sys.argv[1:]] or [27509]
g = json.load(open(G, encoding='utf-8'))
print('TOP', {k: (type(v).__name__, len(v) if hasattr(v, '__len__') else v) for k, v in g.items()})
hits = []
def walk(x, path):
    if isinstance(x, dict):
        if any(isinstance(v, (int, str)) and str(v) in map(str, TARGETS) for v in x.values()):
            hits.append((path, x))
        for k, v in x.items():
            if str(k) in map(str, TARGETS):
                hits.append((path + [k], v))
            walk(v, path + [k])
    elif isinstance(x, list):
        if any(isinstance(e, (int, str)) and str(e) in map(str, TARGETS) for e in x):
            hits.append((path, x))
        for i, v in enumerate(x):
            walk(v, path + [i])
walk(g, [])
for p, v in hits[:80]:
    s = json.dumps(v)
    print('HIT', '/'.join(map(str, p)), s[:300])
print('NHITS', len(hits))
print('RESULT ' + json.dumps({"schema": "result-line/1", "status": "PASS", "gates": {"pass": 1, "fail": 0},
      "first_fail": None, "artefacts": []}))
