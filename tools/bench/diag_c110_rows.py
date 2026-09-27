r"""diag_c110_rows - card 110-1 P1/P2 OFFLINE reader (no LabVIEW): on a bed graph JSON, print the group-B objects' classes and owners,
every wire touching a B terminal with its partners, and the ControlTerminals whose label names #30117/#4580 with their writers/readers.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c110_rows.log -- py -u tools/bench/diag_c110_rows.py <graph.json>"""
import collections, json, os, sys                                                   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P                                                                # noqa: E402
GR = json.load(open(sys.argv[1], encoding="utf-8"))
B = [1359, 2222, 2626, 6104, 8885, 9833, 11261, 29874]
EXTRA = [403, 9306, 28170, 29091, 47, 9289, 28148, 28996, 8323, 28786, 8038, 30117, 4580, 10068, 5119, 11608, 29240, 5058, 376,
         9018, 9025, 29505, 29512, 8953, 28124, 27605, 5426, 5556, 2276, 9087, 9227, 11363, 29911, 8476]
T = GR["terminals"]
OBJ = dict((int(o["uid"]), o) for o in GR["objs"])
OWN = GR.get("owners") or {}
print("ROW KEYS", sorted(T[0].keys()), flush=True)
print("OBJ KEYS", sorted(GR["objs"][0].keys()), flush=True)
by_wire = collections.defaultdict(list)
for r in T:
    if r.get("wire_uid"):
        by_wire[int(r["wire_uid"])].append(r)
for u in B + EXTRA:
    o = OBJ.get(u, {})
    rows = [r for r in T if int(r["owner_uid"]) == u or int(r["term_uid"]) == u]
    print("OBJ #{0} class {1} owner {2} label {3!r} rows {4}".format(u, o.get("class"), OWN.get(str(u)), o.get("label"), len(rows)), flush=True)
closure = set(B)
for u in B:                                                                         # rows owned by B nodes or on their tunnels
    for r in T:
        if int(r["owner_uid"]) != u:
            continue
        w = int(r["wire_uid"] or 0)
        parts = [(int(q["owner_uid"]), q["owner_class"], q["term_name"], int(q["frame_diagram"] or 0), q.get("is_source")) for q in by_wire.get(w, []) if q is not r]
        print("  B #{0} t{1} {2!r} src={3} fd={4} w{5} -> {6}".format(u, r["term_uid"], r["term_name"], r.get("is_source"), r.get("frame_diagram"), w, parts), flush=True)
for lb in ("Trans Pos (mm)", "Rot pos (deg)", "Z/dZ", "Correction Factor"):
    for r in T:
        if r.get("term_name") == lb:
            w = int(r["wire_uid"] or 0)
            parts = [(int(q["owner_uid"]), q["owner_class"], q["term_name"], int(q["frame_diagram"] or 0), q.get("is_source")) for q in by_wire.get(w, []) if q is not r]
            print("LABEL {0!r}: owner #{1} {2} t{3} src={4} fd={5} w{6} -> {7}".format(lb, r["owner_uid"], r["owner_class"], r["term_uid"], r.get("is_source"), r.get("frame_diagram"), w, parts), flush=True)
print(P.result_line(P.make_result(1, 0, None)), flush=True)
