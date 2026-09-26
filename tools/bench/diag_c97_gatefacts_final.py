"""Card 97-1: assemble tools/bench/f1359_gate_facts_97.json from the offline graph (par1359_95_graph.json), the offline
B tables (f1359_gate_facts_97_offline.json) and the COM label read (diag_c97_gatefacts.json). No LabVIEW.
PREDICTION CONTRACT: G1 all three inputs load; G2 every Local's terminal names exclude 'Force (pN) vs Extension'."""
import json, collections, sys
sys.path.insert(0, 'tools')
g = json.load(open('tools/bench/par1359_95_graph.json'))
off = json.load(open('tools/bench/f1359_gate_facts_97_offline.json'))
com = json.load(open('tools/bench/diag_c97_gatefacts.json'))
T = g['terminals']; bo = collections.defaultdict(list); bw = collections.defaultdict(list)
for t in T:
    bo[t['owner_uid']].append(t)
    if t['wire_uid']: bw[t['wire_uid']].append(t)
gates = [['G1 inputs load', True, '']]
locs = {}
for o in g['objs']:
    if o['class'] == 'Local':
        locs[o['uid']] = sorted(set((t['term_name'], 'out' if t['is_source'] else 'in', t['wire_uid'], t['frame_diagram']) for t in bo[o['uid']]))
bad = [u for u, ts in locs.items() if any('Force (pN) vs Extension' in x[0] for x in ts)]
gates.append(['G2 no Local names the indicator', not bad, bad])
for u, ts in locs.items(): print('LOCAL', u, ts)
A = {
 'indicator': {'panel_uid': 8038, 'terminal_uid': 8323, 'terminal_owner_diagram': 639, 'terminal_owner_of_639': 'WhileLoop#637 (COM owner_of)',
               'in_wire': 10908, 'source': 'BuildArray #11261 appended array', 'sinks': 'none (indicator terminal is a sink)'},
 'linked_objects': [{'uid': 10313, 'class': 'Invoke', 'method': 'Reinit To Dflt', 'link': 'implicit (Node.Label = indicator name, COM 2026-09-26)',
                     'owner_diagram': 3628, 'owner_diagram_owner': 'FlatSequenceFrame (uid not readable, OpOwnerChain 1055 limit)',
                     'reads_or_writes': 'WRITE (method re-initialises the indicator to default)', 'terminals_wired': 0, 'sinks': []}],
 'not_linked': {'ControlReferenceConstant': 21, 'Local': 8, 'Global': 7, 'Property': 106, 'EventStructure': 2,
                'note': 'labels of all 145 read by COM; only #10313 carries the name; Locals label = VI file name, their terminal names below'},
 'locals_terminals': {str(k): v for k, v in locs.items()},
 'event_structures': {'10153': 'on #637 body region (pos 2730,1145); data nodes 10764/32083/32194 expose only Source',
                      '15544': 'pos -12145,1112; data nodes 15599 (Type,Time), 15628 (Source,Type,Time,CtlRef,Coords)',
                      'registration_sources': 'NOT READ (no op reads event specifiers)'},
 'verdict': 'NON-DISPLAY READER OF #8323: no',
}
out = {'task': '97-1', 'vi': g['vi'], 'md5': g['md5'], 'level': 'STRUCTURAL (offline graph + one read-only COM label sweep)',
       'A': A, 'B_rows': off['rows_B'], 'B_cross': off['cross_B'], 'B_src_8741': off['src_8741'],
       'com_hits': com.get('hits'), 'com_gates': com.get('gates'), 'gates': gates}
json.dump(out, open('tools/bench/f1359_gate_facts_97.json', 'w'), indent=1, default=str)
from protocol import result_line, make_result
n = sum(1 for x in gates if x[1])
print(result_line(make_result(n, len(gates) - n, next((x[0] for x in gates if not x[1]), None),
                              [{'path': 'tools/bench/f1359_gate_facts_97.json'}])))
