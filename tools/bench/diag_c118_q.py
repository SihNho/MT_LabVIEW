r"""diag_c118_q - card 118-1 offline query helper (no LabVIEW): print graph rows for owner uids.
   py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c118_q.log -- py -u tools/bench/diag_c118_q.py <graph.json> <uid,uid,...>"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol as P  # noqa: E402
G = json.load(open(sys.argv[1], encoding='utf-8'))
print({k: (len(v) if hasattr(v, '__len__') else v) for k, v in G.items()})
U = [int(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else []
for u in U:
    print("== uid", u)
    for r in G['terminals']:
        if int(r['owner_uid']) == u:
            print(" T", r)
    for o in G['objs']:
        if int(o['uid']) == u:
            print(" O", o)
W = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else []
for w in W:
    print("== wire", w)
    for r in G['terminals']:
        if int(r['wire_uid'] or 0) == w:
            print(" T", r, [o for o in G['objs'] if int(o['uid']) == int(r['owner_uid'])][:1])
D = [int(x) for x in sys.argv[4].split(',')] if len(sys.argv) > 4 else []
for d in D:
    own = sorted(set((int(r['owner_uid']), r['owner_class']) for r in G['terminals'] if int(r['frame_diagram'] or 0) == d))
    print("== diagram", d, "owners with rows:", own)
    print("   objs:", [o for o in G['objs'] if int(o['uid']) == d])
if len(sys.argv) > 5:
    for o in G['owners'][:3] if isinstance(G['owners'], list) else list(G['owners'].items())[:3]:
        print("owners sample", o)
    for L in G['loops'][:2]:
        print("loops sample", L)
print("sample term", G['terminals'][0]); print("sample obj", G['objs'][0])
print(P.result_line(P.make_result(1, 0, None)))
