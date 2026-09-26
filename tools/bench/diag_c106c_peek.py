"""Card 106-3 scratch reader: offline JSON peeks (no LabVIEW)."""
import json, os, sys
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, 'tools')
what = sys.argv[1] if len(sys.argv) > 1 else 'plan'
if what == 'plan':
    for pp in ('tools/bench/sim/disp/plan_disp.json', 'tools/bench/sim/disp/fixture_c106c_plan_disp_r7.json'):
        P = json.load(open(pp, encoding='utf-8'))
        print('==', pp, 'keys', sorted(P))
        print('context', json.dumps(P.get('context'))[:800])
        print('open_rows', len(P.get('open_rows') or []))
        for r in P.get('open_rows') or []:
            print('   ', r.get('node'), repr(r.get('term')), r.get('class'), str(r.get('why'))[:60])
        fz = P.get('finalized') or {}
        print('finalized keys', sorted(fz), 'base', fz.get('base'), 'match', fz.get('open_rows_match'))
        import stagexec as SX
        ops = SX.compile_plan(P)
        for k, o in enumerate(ops, 1):
            if o['kind'] == 'create' or k >= 38:
                a = P['actions'][o['acts'][0] - 1]
                rt = None
                try:
                    rt = SX.create_route(a) if a.get('op') == 'create' else None
                except Exception as e:
                    rt = 'ERR ' + str(e)
                print('  op', k, o['kind'], o['acts'], a.get('id'), a.get('class'), 'route', rt)
elif what == 'json':
    d = json.load(open(sys.argv[2], encoding='utf-8'))
    for k in sys.argv[3:]:
        d = d[int(k)] if isinstance(d, list) else d[k]
    print(json.dumps(d, indent=0, default=str)[:6000])
elif what == 'keys':
    d = json.load(open(sys.argv[2], encoding='utf-8'))
    for k in sys.argv[3:]:
        d = d[int(k)] if isinstance(d, list) else d[k]
    print(type(d).__name__, sorted(d) if isinstance(d, dict) else len(d))
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":0,"fail":0}}')
