"""Card 97-1 OFFLINE part 5. No LabVIEW. #1114 (WLC function sub.vi) outputs and their sinks; whether w8319 feeds
anything besides #11576; the #8323 panel object id; ControlTerminal 8476 (Exp Baseline) other sinks.
PREDICTION CONTRACT: G1 w8319 has exactly one source (#1114)."""
import json, collections, sys
sys.path.insert(0, 'tools')
g = json.load(open('tools/bench/par1359_95_graph.json'))
T = g['terminals']
lab = {}
for d, lst in json.load(open('tools/bench/main_vi_node_labels.json'))['diagrams'].items():
    for n in lst: lab[n['uid']] = n['label']
bw = collections.defaultdict(list); bo = collections.defaultdict(list)
for t in T:
    if t['wire_uid']: bw[t['wire_uid']].append(t)
    bo[t['owner_uid']].append(t)
for u in (1114,):
    print('NODE', u, lab.get(u))
    for t in bo[u]:
        oth = [(s['owner_uid'], s['owner_class'], s['term_name'].replace('\n', '|')[:24], lab.get(s['owner_uid']), s['frame_diagram'])
               for s in bw.get(t['wire_uid'], []) if s['is_source'] != t['is_source']] if t['wire_uid'] else []
        print('  %-3s %-26s w%-6s -> %s' % ('out' if t['is_source'] else 'in', t['term_name'].replace('\n', '|')[:26], t['wire_uid'], oth))
for w in (8319, 7931):
    print('WIRE', w, [(s['owner_uid'], s['owner_class'], s['term_name'], s['is_source'], s['frame_diagram']) for s in bw[w]])
srcs = [s for s in bw[8319] if s['is_source']]
from protocol import result_line, make_result
ok = len(srcs) == 1 and srcs[0]['owner_uid'] == 1114
print(result_line(make_result(int(ok), int(not ok), None if ok else 'G1 w8319 sources', [])))
