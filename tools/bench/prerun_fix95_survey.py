"""prerun_fix95_survey - read-only census of graph_*.json shapes (card 95-1). Offline, no LabVIEW."""
import glob, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
for p in sorted(glob.glob('tools/bench/graph_*.json') + glob.glob('tools/bench/sim/*/graph_*.json')):
    h = open(p, encoding='utf-8', errors='replace').read(800)
    m = re.search(r'"md5"\s*:\s*"([0-9a-f]{32})"', h)
    if not m:
        continue
    try:
        d = json.load(open(p, encoding='utf-8'))
    except Exception as e:
        print(m.group(1)[:8], p, 'ERR', e)
        continue
    ks = sorted(d) if isinstance(d, dict) else type(d).__name__
    print(m.group(1)[:8], int(os.path.getmtime(p)), p, ks)
d = json.load(open('tools/bench/graph_s1_20260924.json', encoding='utf-8'))
print('S1 method', d['method'])
print('S1 note', d['note'])
print('S1 flags', d['flags'][:3])
print('S1 edges', d['edges'][:2])
print('S1 cls', list(d['cls'].items())[:3])
