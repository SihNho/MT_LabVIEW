# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c164_a3_5_graph.log:304
# ---
r"""diag_c164_a3_5_reads - card 164-3-5 (OFFLINE, read-only, no LabVIEW): the brief's PD399(a) reads on the adopted step-4 graph
graph_ring_p5s02d_20261010_154830.json (w23460 rows; w23519 sinks vs the stagesim prediction {t23450, t23241, t7606}) and, beside them, the
recorded rows of the uid the graph read's E5 gate found present (#23501, diag_c164_a3_5_graph.log:304), in the base graph (p5s02c 3d5196ab) and in
the adopted graph. Prints rows only; no verdict, no edit. New file (no earlier reader of these keys found: grep "w23519" tools/bench/*.py gave only
prep_c164_a3_4_pd399.py, which reads the PLAN's sim, not a graph json).
PREDICTION: prints; RESULT PASS when both graphs load.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c164_a3_5_reads.log -- py -u tools/bench/diag_c164_a3_5_reads.py"""
import json, os, sys                                                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
GR = {"base": "graph_ring_p5s02c_20261010_131658.json", "adopted": "graph_ring_p5s02d_20261010_154830.json"}
KEYS = ("term_uid", "term_name", "owner_uid", "owner_class", "wire_uid", "direction", "term_class")
n = 0
for tag, f in GR.items():
    g = json.load(open(os.path.join(B, f), encoding="utf-8"))
    n += 1
    objs = dict((int(o["uid"]), o) for o in g["objs"])
    T = g["terminals"]
    print("FACT {0} {1}: {2} rows, {3} objs".format(tag, f, len(T), len(objs)), flush=True)
    for u in (23501, 23042):
        o = objs.get(u)
        print("FACT {0} obj #{1}: {2}".format(tag, u, None if o is None else dict((k, o.get(k)) for k in ("class", "owner", "owner_uid", "label", "name") if k in o)), flush=True)
        for r in T:
            if int(r.get("owner_uid") or 0) == u or int(r.get("term_uid") or 0) == u:
                print("ROW {0} owner/term #{1}: {2}".format(tag, u, dict((k, r.get(k)) for k in KEYS if k in r)), flush=True)
    for w in (23460, 23519):
        rows = [r for r in T if int(r.get("wire_uid") or 0) == w]
        print("FACT {0} w{1}: {2} rows".format(tag, w, len(rows)), flush=True)
        for r in rows:
            print("ROW {0} w{1}: {2}".format(tag, w, dict((k, r.get(k)) for k in KEYS if k in r)), flush=True)
print(protocol.result_line(protocol.make_result(n, 2 - n, None if n == 2 else "graph load", [])), flush=True)
