"""Card 90-2 helper: print the cycle-89 panel-leg tables (m8_panelmin_89.json / _89b.json) for the INDEX row."""
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for f in ['tools/bench/m8_panelmin_89.json', 'tools/bench/m8_panelmin_89b.json']:
    d = json.load(open(os.path.join(R, f))); print(f, d.get('card'))
    for r in d['rows']:
        pm = r.get('pm_gates', {})
        print('  ', r['leg'], r['mode'], 'rc', r['rc'], 'secs', r.get('secs'), 'lost', r.get('lost_frames'),
              'frames', r.get('frames_delta'), 'hz', r.get('measured_hz'),
              'pm', sum(1 for v in pm.values() if v is True), '/', len(pm), 'json', r.get('json'))
    print('  top', {k: d[k] for k in d if k not in ('rows', 'pins', 'schema', 'card', 'legs')})
for f in ['tools/bench/m8_panelmin_89.log', 'tools/bench/m8_panelmin_89b.log']:
    ls = open(os.path.join(R, f), errors='replace').read().splitlines()
    print(f, [l for l in ls if 'BGRUN END' in l or 'BGRUN TIMEOUT' in l or l.startswith('RESULT') or 'GATES' in l][-4:])
