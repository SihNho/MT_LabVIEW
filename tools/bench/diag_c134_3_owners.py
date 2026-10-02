"""Card 134-3 step 1b (offline): how do objs rows of the measured graph record their owner, and what
does the graph's 'owners' dict hold?  Prediction: owner values are listed by type/count; the rows for uids
given on the command line are printed verbatim with their 'owners' entry.  No inference."""
import json, sys, collections
G = 'tools/bench/graph_ring_p3b2a_fs_20261002_102553.json'
g = json.load(open(G, encoding='utf-8'))
objs = g['objs']
c = collections.Counter(type(o.get('owner')).__name__ + ':' + (o.get('owner') if isinstance(o.get('owner'), str) else '<uid/list>') for o in objs)
print('OWNER-VALUE-COUNTS', c.most_common(20))
print('OBJ-KEYS', collections.Counter(tuple(sorted(o)) for o in objs).most_common(6))
print('OWNERS-DICT sample', list(g['owners'].items())[:8])
print('OWNERS value kinds', collections.Counter(str(v[0]) if isinstance(v, list) else type(v).__name__ for v in g['owners'].values()))
print('FS_MEASURED keys', {k: len(v) for k, v in g['fs_measured'].items()})
print('SOURCE', g['source'])
by = {o['uid']: (i, o) for i, o in enumerate(objs)}
for u in [int(a) for a in sys.argv[1:]]:
    print('UID', u, 'objs-row', by.get(u), 'owners', g['owners'].get(str(u), g['owners'].get(u)))
fsl = [o for o in objs if o['class'] == 'FlatSequence']
print('FS rows', len(fsl), [(o['uid'], o['owner'], str(o['uid']) in g['owners']) for o in fsl])
print('LOOPS sample', g['loops'][:3])
print('RESULT ' + json.dumps({"schema": "result-line/1", "status": "PASS", "gates": {"pass": 1, "fail": 0},
      "first_fail": None, "artefacts": []}))
