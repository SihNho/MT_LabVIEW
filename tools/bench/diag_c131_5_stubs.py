"""diag_c131_5_stubs - card 131-5 step 0b (offline, no LabVIEW): which one-sided wires (stubs) does P3b-1 retire?

The Error List items carry no uid (show_error.uid_route 'none', errorlist_scratch_c129_..._053812.json), so the
missing loose end is located from the GRAPH: a wire whose terminals are all sources (or all sinks) in the P3a base
graph (graph_ring_p3a_20261001_190155.json, the base the plan was finalized on) but not in the simulated end state
(sim/ring_p3b1/step_31_*.json). Prediction: base has >= 1 stub; the set retired by P3b-1 contains w27378 (row
p3b_rle_w27378) and, if PD273(a)'s mechanism holds, ONE more wire on a net a P3b-1 row touches.
"""
import json
from collections import defaultdict
from pathlib import Path
B = Path(__file__).resolve().parent
BASE = B / 'graph_ring_p3a_20261001_190155.json'
END = sorted((B / 'sim' / 'ring_p3b1').glob('step_31_*.json'))[0]


def stubs(path):
    g = json.loads(path.read_text(encoding='utf-8'))
    terms = g.get('terminals') or (g.get('state') or {}).get('terminals')
    w = defaultdict(lambda: [0, 0, []])
    for t in terms:
        wu = t.get('wire_uid')
        if wu in (None, 0, -1):
            continue
        w[wu][0 if t.get('is_source') else 1] += 1
        w[wu][2].append((t.get('term_uid'), t.get('term_name'), t.get('owner_uid'), t.get('owner_class'), bool(t.get('is_source'))))
    one = {k: v for k, v in w.items() if v[0] == 0 or v[1] == 0}
    return g, w, one


gb, wb, sb = stubs(BASE)
ge, we, se = stubs(END)
print('BASE', BASE.name, 'wires', len(wb), 'one-sided', len(sb))
print('END ', END.name, 'wires', len(we), 'one-sided', len(se))
gone = sorted(set(sb) - set(se))
new = sorted(set(se) - set(sb))
for k in gone:
    print('RETIRED w%s src/snk %d/%d in_end=%s end_src/snk=%s terms=%s' % (
        k, sb[k][0], sb[k][1], k in we, (we[k][0], we[k][1]) if k in we else None, sb[k][2][:4]))
for k in new:
    print('NEW     w%s src/snk %d/%d terms=%s' % (k, se[k][0], se[k][1], se[k][2][:4]))
# card 132-1 (retrospective-cycle131 finding 3b): PASS now depends on the docstring's prediction (:5-7), checked here;
# it printed PASS unconditionally before (the measured retired set was [3040], without w27378).
checks = [('S1 base has >= 1 one-sided wire', len(sb) >= 1),
          ('S2 the retired set contains w27378 (row p3b_rle_w27378)', 27378 in gone)]
for nm, ok in checks:
    print('%s  %s  retired=%s' % ('PASS' if ok else 'FAIL', nm, gone))
nf = sum(1 for _n, ok in checks if not ok)
print('RESULT ' + json.dumps({'schema': 'result-line/1', 'status': 'FAIL' if nf else 'PASS',
                              'gates': {'pass': len(checks) - nf, 'fail': nf},
                              'first_fail': next((n for n, ok in checks if not ok), None), 'artefacts': []}))
