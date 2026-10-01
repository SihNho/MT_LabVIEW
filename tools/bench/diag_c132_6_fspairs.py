"""card 132-6 diag (offline, read-only): fs_tunnel_pairs of the real P3b-1 graph vs the provisional base's fs_pairs."""
import json
d = json.load(open('tools/bench/sim/ring_p3b2_base_provisional.json', encoding='utf-8'))
g = json.load(open('tools/bench/graph_ring_p3b1_20261002_073225.json', encoding='utf-8'))
pp, rp = d.get('fs_pairs') or [], g.get('fs_tunnel_pairs') or []
print('prov fs_pairs', len(pp), 'real fs_tunnel_pairs', len(rp))
print('prov negative', [p for p in pp if isinstance(p.get('uid'), int) and p['uid'] < 0])
print('real FSIT classes', sorted(set(p.get('class') for p in rp)))
print('real pairs on 28333', [p for p in rp if p.get('uid') == 28333])
pu = set(p.get('uid') for p in pp if isinstance(p.get('uid'), int) and p['uid'] > 0)
ru = set(p.get('uid') for p in rp)
print('pos uids only prov', sorted(pu - ru)[:20], 'only real', sorted(ru - pu)[:20])
