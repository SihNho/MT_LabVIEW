"""Read-only peek at the offline graph JSON structure (card 97-1). No LabVIEW, no COM."""
import json, collections
g = json.load(open('tools/bench/par1359_95_graph.json'))
print(json.dumps(g['graph_summary'])[:3000])
T = g['terminals']; O = g['objs']
keys = collections.Counter(k for t in T for k in t)
print('term keys', keys)
okeys = collections.Counter(k for o in O for k in o)
print('obj keys', okeys)
cls = collections.Counter(o['class'] for o in O)
print('obj classes', cls.most_common())
tcls = collections.Counter(t['owner_class'] for t in T)
print('term owner classes', tcls.most_common())
# anything mentioning 8323
for t in T:
    if t['owner_uid'] == 8323 or t['term_uid'] == 8323:
        print('T8323', t)
for i, o in enumerate(O):
    if o['uid'] in (8323, 1359, 637, 639, 7911, 11261, 11363, 25380, 686):
        print('O', i, o)
