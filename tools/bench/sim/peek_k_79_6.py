import json, collections, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
print({k: (type(v).__name__, len(v) if hasattr(v, '__len__') else v) for k, v in d.items()})
print('finalized', json.dumps(d.get('finalized'))[:600])
print('final', json.dumps(d.get('final'))[:800])
print(collections.Counter(a.get('kind') or a.get('action') or a.get('op') or a.get('verb') for a in d['actions']))
for a in d['actions'][:3]:
    print(json.dumps(a)[:400])
print(sorted(set(k for a in d['actions'] for k in a)))
print('open_rows', json.dumps(d.get('open_rows'))[:300])
