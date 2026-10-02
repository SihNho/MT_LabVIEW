"""Card 140-4 census (offline, read-only, no LabVIEW): array-write nodes in the ring bed, intended vs real.
Existing tools checked: tools/bench/prep_c140_4_probe.py (structure only); no existing census of labels vs plan prims.
Inputs: graph_ring_p3b2b_20261002_133824.json (bed md5 395118775a...), main_vi_node_labels.json (labels of the original copy).
Prediction contract: (G1) the 6 created ring array-write uids 27928/28916/29048/29265/29316 are in the bed graph with 4 terminals
each (29489 is scratch-only, expected ABSENT); (G2) every 'Replace Array Subset' uid in main_vi_node_labels.json is in the bed
graph; (G3) labels file has >=1 'Insert Into Array' and >=1 'Replace Array Subset'."""
import json, os, sys, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from protocol import result_line
B = os.path.dirname(os.path.abspath(__file__))
g = json.load(open(os.path.join(B, 'graph_ring_p3b2b_20261002_133824.json'), encoding='utf-8'))
labtxt = open(os.path.join(B, 'main_vi_node_labels.json'), encoding='utf-8').read().splitlines()
# labels: uid line followed by label line
lab = {}
for i, ln in enumerate(labtxt):
    m = re.search(r'"uid": (\d+)', ln)
    if m and i + 1 < len(labtxt):
        m2 = re.search(r'"label": "(.*)"', labtxt[i + 1])
        if m2:
            lab.setdefault(int(m.group(1)), (m2.group(1), i + 2))
terms = {}
for t in g['terminals']:
    terms.setdefault(t['owner_uid'], []).append(t)
objs = {o['uid']: o for o in g['objs']}
gp, gf = 0, 0
def show(uid, tag):
    ts = terms.get(uid, [])
    o = objs.get(uid)
    l = lab.get(uid)
    print('NODE %s #%d class=%s labelsfile=%s frame=%s nterm=%d' % (tag, uid, o and o['class'], l and ('%r @main_vi_node_labels.json:%d' % l),
          ts and ts[0]['frame_diagram'], len(ts)))
    for t in ts:
        print('   T %-24s src=%-5s term=%d wire=%s' % (repr(t['term_name']), t['is_source'], t['term_uid'], t['wire_uid']))
    return len(ts)
print('== G1 created ring array-write nodes in bed graph')
for u, aid in [(27928, 'p3b_ras_num3'), (28916, 'p3b_ras_num1'), (29048, 'p3b_ras_transpos'), (29265, 'p3b_ras_rotpos'),
               (29316, 'p3b_ras_frameidx'), (29489, 'p4_ras_bufdiff(scratch)')]:
    n = show(u, aid)
    ok = (n == 0) if u == 29489 else (n == 4)
    gp += ok; gf += (not ok)
    print('GATE G1 %s #%d nterm=%d %s' % (aid, u, n, 'PASS' if ok else 'FAIL'))
print('== G2 labels-file Replace Array Subset / Insert Into Array nodes in bed graph')
ras = sorted(u for u, (l, _) in lab.items() if l == 'Replace Array Subset')
iia = sorted(u for u, (l, _) in lab.items() if l == 'Insert Into Array')
print('RAS uids', len(ras), ras)
print('IIA uids', len(iia), iia)
miss = []
for u in ras + iia:
    n = show(u, lab[u][0])
    if n == 0:
        miss.append(u)
print('NOT IN BED GRAPH', miss)
ok = not [u for u in ras if u in miss]
gp += ok; gf += (not ok)
print('GATE G2 RAS all in bed graph %s' % ('PASS' if ok else 'FAIL'))
ok = len(ras) >= 1 and len(iia) >= 1
gp += ok; gf += (not ok)
print('GATE G3 labels file has both prims %s' % ('PASS' if ok else 'FAIL'))
# RAS terminal-name census
names = {}
for u in ras:
    names.setdefault(tuple(sorted(t['term_name'] for t in terms.get(u, []))), []).append(u)
for k, v in names.items():
    print('RAS-TERMSET %s -> %s' % (list(k), v))
names = {}
for u in iia:
    names.setdefault(tuple(sorted(t['term_name'] for t in terms.get(u, []))), []).append(u)
for k, v in names.items():
    print('IIA-TERMSET %s -> %s' % (list(k), v))
print(result_line({'status': 'PASS' if gf == 0 else 'FAIL', 'gates': {'pass': gp, 'fail': gf},
                   'first_fail': None if gf == 0 else 'see GATE lines', 'artefacts': []}))
