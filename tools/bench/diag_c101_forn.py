r"""diag_c101_forn - card 101-3, after stage_d1_disp_r3.log:69 (op 3 create For: real new objects {'Tunnel': 1} owner
#23403, sim {}). Pure Python, no LabVIEW. READ what a For loop's count terminal (N) looks like in S1's read
(par1359_95_graph.json): every row with owner_class 'Tunnel', its frame diagram, name, direction, wire, term_class, and
which structure that frame's owner is (s1_owners.json); plus what stage_d1_disp.json (run r3) recorded for op 3.
PREDICTION (to be measured, not assumed): each S1 ForLoop (#1359 body 7911, #27489 body 27537) has exactly one
'Tunnel'-owned row on its PARENT diagram, unnamed, a sink (N). Reported whatever it is.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c101_forn.log -- py -u tools/bench/diag_c101_forn.py"""
import collections, json, os, sys                                                   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P                                                               # noqa: E402
J = lambda p: json.load(open(os.path.join(HERE, p), encoding="utf-8"))             # noqa: E731
G, O = J("par1359_95_graph.json"), J("sim/disp/s1_owners.json")["owners"]
objs = dict((int(o["uid"]), o) for o in G["objs"])
rows = dict(((r["term_uid"], r["owner_uid"]), r) for r in G["terminals"]).values()
tun = collections.defaultdict(list)
for r in rows:
    if r["owner_class"] == "Tunnel":
        tun[r["owner_uid"]].append(r)
print("  FACT Tunnel-class owners in S1: {0}".format(len(tun)), flush=True)
fl = sorted(int(u) for k, (c, u) in O.items() if c == "ForLoop" for u in [u])
bodies = dict((int(k), (c, int(u))) for k, (c, u) in O.items())
for tu, rs in sorted(tun.items()):
    fd = int(rs[0]["frame_diagram"] or 0)
    print("  FACT Tunnel #{0} obj {1} frame {2} (frame owner {3}) rows {4}".format(
        tu, {k: v for k, v in objs.get(tu, {}).items() if k != "uid"}, fd, bodies.get(fd),
        [(r["term_uid"], r["term_name"], r["is_source"], r["wire_uid"], r["term_class"]) for r in rs]), flush=True)
print("  FACT ForLoops (owners of bodies): {0}".format(sorted(set(fl))), flush=True)
for L in sorted(set(fl)):
    print("  FACT ForLoop #{0} obj {1}; owner {2}".format(L, {k: v for k, v in objs.get(L, {}).items() if k != "uid"}, O.get(str(L))), flush=True)
try:
    R = J("stage_d1_disp.json")
    for rec in R.get("stagexec") or []:
        if rec.get("k") in (3,):
            print("  FACT r3 op3 record: {0}".format(json.dumps(rec, default=str)[:1500]), flush=True)
except (OSError, ValueError) as e:
    print("  FACT stage_d1_disp.json unreadable: {0}".format(e), flush=True)
print(P.result_line(P.make_result(1, 0, None)), flush=True)
