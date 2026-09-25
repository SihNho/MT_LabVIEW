"""l2a1_q81 - card 81-5 read-only query (no LabVIEW): who is #9703 'x' (new PB row of sim_l2a1_81b), base vs end state."""
import json, collections, os, sys, glob
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.getcwd()))
import vigraph as V, jev_candidates as JC                                          # noqa: E402
g = json.load(open('l2a1_graph_k_80.json')); F = json.load(open('l2a1_facts_80.json'))
plan = json.load(open('sim/l2a1/plan_l2a1.json'))
last = json.load(open(os.path.join('..', '..', plan['steps'][-1]['file']['path']) if not os.path.isabs(plan['steps'][-1]['file']['path']) else plan['steps'][-1]['file']['path']))['state'] if 'steps' in plan else None
print('plan keys', list(plan.keys())[:12])
def show(T, tag):
    byw = collections.defaultdict(list)
    for r in T:
        if r['wire_uid']: byw[r['wire_uid']].append(r)
    for r in [r for r in T if V.node_of(r) == 9703]:
        print(tag, r['term_uid'], r['term_name'], r['owner_class'], r['is_source'], r['wire_uid'], r['frame_diagram'],
              [(x['term_uid'], V.node_of(x), x['owner_class'], x['term_class'], x['is_source'], x['frame_diagram']) for x in byw.get(r['wire_uid'], []) if x is not r])
show(g['terminals'], 'BASE')
S1 = JC.load(JC.S1_KEY)
for k, a, b, _i in S1['edges']:
    if k == 'wire' and V.key_parts(b)[0] == 9703:
        print('S1 edge', a, '->', b)
if last: show(last['terminals'], 'END')
print("RESULT {\"schema\":\"result-line/1\",\"status\":\"PASS\",\"gates\":{\"pass\":0,\"fail\":0},\"first_fail\":null,\"artefacts\":[]}")
