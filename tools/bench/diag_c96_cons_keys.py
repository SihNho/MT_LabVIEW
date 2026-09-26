"""Card 96-3, offline, read-only: where do tunnels, wires and case frames sit in the objs pre-order?
Prediction: tunnel 9227 / 11363 objects appear somewhere after ForLoop 1359; wires appear per diagram.
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import protocol
G = os.path.join(os.path.dirname(__file__), 'par1359_95_graph.json')
d = json.load(open(G, encoding='utf-8'))
objs = d['objs']
idx = {o['uid']: i for i, o in enumerate(objs)}
for u in (9227, 11363, 9087, 8811, 11374, 9215, 11352, 637, 639, 1359, 7911):
    i = idx.get(u)
    print('IDX', u, i, objs[i]['class'] if i is not None else None)
i = idx[7911]
print('7911 tail', [(o['uid'], o['class']) for o in objs[i:i + 400] if o['class'] not in ('Terminal', 'ParameterTerminal', 'OverridableParameterTerminal')][:120])
# first case structure after 637
j = next(k for k in range(idx[639], len(objs)) if objs[k]['class'] == 'CaseStructure')
print('CASE@', objs[j]['uid'], [(o['uid'], o['class']) for o in objs[j:j + 40]])
print(protocol.result_line(protocol.make_result(1, 0)))
