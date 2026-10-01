"""card 130-5 read-only peek: top-level keys of stageplan JSONs (no LabVIEW). RESULT line at end."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for f in sys.argv[1:]:
    p = json.load(open(f, encoding='utf-8'))
    print(f, list(p.keys()))
    for k, v in p.items():
        if k not in ('actions', 'decisions'):
            print('  ', k, str(v)[:400])
    print('  actions', len(p.get('actions') or []), 'decisions', len(p.get('decisions') or []))
import protocol as P
print(P.result_line(P.make_result(1, 0, None)))
