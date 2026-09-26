"""Card 97-1 OFFLINE part 4. No LabVIEW. One-hop terminal dump of the #11608 branch (11576, 11608) and of #8566/#28083
inputs; prediction: G1 #11576 has exactly one wired input terminal."""
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
def hop(u):
    for t in bo[u]:
        other = [(s['owner_uid'], s['owner_class'], s['term_name'].replace('\n', '|'), lab.get(s['owner_uid']), s['frame_diagram'])
                 for s in bw.get(t['wire_uid'], []) if s['is_source'] != t['is_source']] if t['wire_uid'] else []
        print('  %s %-3s %-28s w%-6s -> %s' % (u, 'out' if t['is_source'] else 'in', t['term_name'].replace('\n', '|')[:28], t['wire_uid'], other))
for u in (11576, 11608, 8566, 28083, 9087, 10004, 10177, 9503, 28370, 31051, 31137):
    print('NODE', u, lab.get(u)); hop(u)
ins = [t for t in bo[11576] if not t['is_source'] and t['wire_uid']]
from protocol import result_line, make_result
ok = len(ins) == 1
print(result_line(make_result(int(ok), int(not ok), None if ok else 'G1 11576 inputs %d' % len(ins), [])))
