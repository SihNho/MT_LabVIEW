r"""diag_c110_terms - card 110-1 P3 OFFLINE: every terminal row of the listed owners (argv[2:], or the B1/B2/B3 row owners) with its wire
partners, pos of each object, and the #637/#10170 shift-register tables. No LabVIEW.
    py tools/bgrun.py --material --max-min 3 --log <log> -- py -u tools/bench/diag_c110_terms.py <graph.json> [uid ...]"""
import collections, json, os, sys                                                   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P                                                                # noqa: E402
GR = json.load(open(sys.argv[1], encoding="utf-8"))
OWN = [int(x) for x in sys.argv[2:]] or [2451, 7091, 9833, 6104, 8885, 10004, 30135, 11363, 11261, 8323, 29172, 28786, 403, 2276, 9306,
                                         6132, 28170, 31051, 29091, 31137, 30896, 9906, 6404, 9050, 5058, 2765, 2626, 9227, 9087, 29616,
                                         29911, 9018, 9025, 29505, 29512, 8953, 28124, 27605, 28343, 28370, 5426, 5556, 5129, 5328, 2992,
                                         3176, 1147, 1359, 29874, 2222, 10170, 23166, 637]
T = GR["terminals"]
OBJ = dict((int(o["uid"]), o) for o in GR["objs"])
bw = collections.defaultdict(list)
for r in T:
    if r.get("wire_uid"):
        bw[int(r["wire_uid"])].append(r)
for u in OWN:
    o = OBJ.get(u, {})
    print("OBJ #{0} {1} owner {2} pos {3}".format(u, o.get("class"), o.get("owner"), o.get("pos")), flush=True)
    for r in T:
        if int(r["owner_uid"]) == u or (int(r["term_uid"]) == u and o.get("class") in ("ControlTerminal", None)):
            w = int(r["wire_uid"] or 0)
            parts = [(int(q["owner_uid"]), q["term_uid"], q["term_name"], q["term_class"], int(q["frame_diagram"] or 0), q.get("is_source")) for q in bw.get(w, []) if q is not r]
            print("   t{0} {1!r} {2} src={3} fd={4} w{5} -> {6}".format(r["term_uid"], r["term_name"], r["term_class"], r.get("is_source"), r.get("frame_diagram"), w, parts), flush=True)
OW = GR.get("owners") or {}
for u in OWN:                                                                       # owner chain up to the top diagram
    ch, v = [], u
    while str(v) in OW and len(ch) < 12:
        ch.append(tuple(OW[str(v)]))
        v = OW[str(v)][1]
        if not v:
            break
    ch and print("CHAIN #{0}: {1}".format(u, ch), flush=True)
for lp in GR.get("loops") or []:
    if int(lp.get("loop_uid") or 0) in (637, 10170):
        print("LOOP {0}".format(json.dumps(lp)[:2500]), flush=True)
print(P.result_line(P.make_result(1, 0, None)), flush=True)
