# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c165_p5s02e_scratch.log:141
# ---
r"""diag_c165_a3_4_reads - card 165-3-4 (OFFLINE, read-only, no LabVIEW): the brief's PD401(b) / PD402 reads (brief_165-3-4.md deltas 5, 7):
per stub-delete + connect pair (dw_10362 + w_k3f on face t8776; dw_25232 + w_k4f on face t24342): the face's wire in the base graph
graph_ring_p5s02d_20261010_154830.json (2a5fa0c4), in the sim step after the delete and at the sim end (sim/ring_p5s02e step_01 / step_12 /
step_13), in the scratch run's op result (diag_c165_p5s02e_scratch.json ops: connect_term_uid wire_uid / broken) and in the ADOPTED graph
(argv[1]); the real net of each face (source + sinks) versus the stagesim prediction (K3f: w31792 src t31815 on OK3 #31803; K4f: OK4 outer net);
the stub wires' rows; and beside them the re-ended old wires w4337 / w9636 (term_identity.new ∩ base, diag_c165_a3_4_mkgraph.log) base vs adopted.
COPY-SHAPE of diag_c164_a3_5_reads.py (prints rows only, no verdict, no edit); keys and graphs changed, sim / op reads added.
PREDICTION: prints; RESULT PASS when every file loads.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c165_a3_4_reads.log -- py -u tools/bench/diag_c165_a3_4_reads.py <adopted graph json>"""
import json, os, sys                                                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
J = lambda p: json.load(open(os.path.join(B, p), encoding="utf-8"))                          # noqa: E731
GR = {"base": "graph_ring_p5s02d_20261010_154830.json", "adopted": os.path.basename(sys.argv[1])}
SIM = {"sim01": os.path.join("sim", "ring_p5s02e", "step_01_delete_wire.json"), "sim12": os.path.join("sim", "ring_p5s02e", "step_12_delete_wire.json"),
       "sim13": os.path.join("sim", "ring_p5s02e", "step_13_wire.json")}
KEYS = ("term_uid", "term_name", "owner_uid", "owner_class", "wire_uid", "is_source", "term_class", "frame_diagram")
FACES = (8776, 24342)
n = 0


def rows_of(T, pred):
    return [dict((k, r.get(k)) for k in KEYS if k in r) for r in T if pred(r)]


def net(T, w):
    src = sorted(int(r["term_uid"]) for r in T if int(r.get("wire_uid") or 0) == w and r.get("is_source"))
    snk = sorted(int(r["term_uid"]) for r in T if int(r.get("wire_uid") or 0) == w and not r.get("is_source"))
    own = dict((int(r["term_uid"]), (r.get("owner_uid"), r.get("owner_class"), r.get("term_class"))) for r in T if int(r.get("wire_uid") or 0) == w)
    return {"wire": w, "sources": src, "sinks": snk, "owners": own}


for tag, f in list(GR.items()) + list(SIM.items()):
    p = os.path.join(B, f)
    if not os.path.exists(p):
        print("FACT {0} {1}: MISSING".format(tag, f), flush=True)
        continue
    g = J(f)
    T = g.get("terminals") or (g.get("graph") or {}).get("terminals") or []
    n += 1
    print("FACT {0} {1}: {2} rows".format(tag, f, len(T)), flush=True)
    for t in FACES:
        fr = rows_of(T, lambda r: int(r.get("term_uid") or 0) == t)
        print("ROW {0} face t{1}: {2}".format(tag, t, fr), flush=True)
        for w in sorted(set(int(r.get("wire_uid") or 0) for r in fr) - {0}):
            print("NET {0} face t{1} on {2}".format(tag, t, net(T, w)), flush=True)
    for w in (10362, 25232, 4337, 9636):
        rr = rows_of(T, lambda r: int(r.get("wire_uid") or 0) == w)
        print("FACT {0} w{1}: {2} rows {3}".format(tag, w, len(rr), rr), flush=True)
    if tag in GR:
        objs = dict((int(o["uid"]), o) for o in g["objs"])
        for u in (31803, 31847, 31855, 31812, 31817, 31824, 5204, 10404):
            o = objs.get(u)
            print("OBJ {0} #{1}: {2} | terms {3}".format(tag, u, None if o is None else (o.get("class"), o.get("owner")),
                  [(r.get("term_uid"), r.get("term_class"), r.get("wire_uid"), r.get("is_source")) for r in T if int(r.get("owner_uid") or 0) == u]), flush=True)
ops = J("diag_c165_p5s02e_scratch.json")
n += 1


def walk(o, acc):
    if isinstance(o, dict):
        if o.get("verb") in ("connect_term_uid", "delete_wire") and "detail" in o:
            acc.append((o.get("verb"), o.get("detail"), o.get("err"), dict((k, (o.get("result") or {}).get(k)) for k in ("wire_uid", "broken", "sink_echo",
                        "src_echo")) if isinstance(o.get("result"), dict) else o.get("result")))
        for v in o.values():
            walk(v, acc)
    elif isinstance(o, list):
        for v in o:
            walk(v, acc)
    return acc


for x in walk(ops, []):
    print("OPRESULT {0}".format(x), flush=True)
print(protocol.result_line(protocol.make_result(n, 0, None, [])), flush=True)
