r"""c125_5_fsscan - card 125-5 OFFLINE (no LabVIEW): list the P3a bed graph's FlatSequence objects with what sits inside them,
so a near-empty FS can be chosen as a struct_copy donor if needed. Read-only on graph_ring_p3a_20261001_190155.json.
PREDICTION: the graph JSON parses; >= 1 FlatSequence listed. Prints one RESULT line.
    py tools/bgrun.py --material --max-min 1 --log tools/bench/c125_5_fsscan.log -- py -u tools/bench/c125_5_fsscan.py"""
import collections, json, os, sys                                                           # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                                        # noqa: E402
d = json.load(open(os.path.join(HERE, "graph_ring_p3a_20261001_190155.json"), encoding="utf-8"))
objs = d["objs"]
cls = dict((o["uid"], o["class"]) for o in objs)
own = dict((o["uid"], o["owner"]) for o in objs)
print("owner value samples", collections.Counter(type(o["owner"]).__name__ for o in objs), [o for o in objs if o["class"] == "Diagram"][:3])
fss = [o for o in objs if o["class"] == "FlatSequence"]
print("FlatSequence count", len(fss), "sample", fss[:2])
# frame diagrams of an FS: diagrams that hold the inner faces of that FS's inner tunnels (terminals.frame_diagram)
tun_owner = {}
for o in objs:
    if o["class"] in ("FlatSequenceInnerTunnel", "FlatSequenceOuterTunnel"):
        tun_owner[o["uid"]] = o["owner"]
fd = collections.defaultdict(set)
for t in d["terminals"]:
    if t["owner_class"] == "FlatSequenceInnerTunnel":
        fd[tun_owner.get(t["owner_uid"])].add(t["frame_diagram"])
inside = collections.Counter(o["owner"] for o in objs)
for f in fss:
    u = f["uid"]
    print("FS", u, "owner", f["owner"], "pos", f["pos"], "tunnels", sum(1 for k, v in tun_owner.items() if str(v) == str(u) or v == u),
          "frame diagrams via tunnels", sorted(fd.get(u, []) or fd.get(str(u), [])))
print(P.result_line(P.make_result(1 if fss else 0, 0 if fss else 1, None if fss else "no FlatSequence", [])))
