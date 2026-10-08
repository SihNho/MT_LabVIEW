# ---
# labview: none
# hardware: none
# ---
r"""diag_c147_a1_1_t2626 - card 147-a1-1 step 4 (OFFLINE, no LabVIEW; PD352(d) s06 licence evidence): the terminals of Build Array #2626 at
the end of P4 session 5, read from the session-5 graph file named by tools/bench/diag_c147_a1_1_graph.json `graph` (path + md5). COPIED from
tools/bench/diag_c146_a1_4_t2626.py (md5 3edad010, card input) with ONLY the graph-record name changed. Every terminal row whose owner_uid == 2626
(inputs and output, wired or not), term_name, term_class, is_source, wire_uid and the other end(s) of a wired one; compared with the s04 graph
graph_ring_p4s04_20261007_223245.json (094ba298). The graph read carries no LabVIEW data-type field: TYPE = terminal class + name as read.
PREDICTION: G graph md5 == the graph script's record; R #2626 has >= 1 output row and >= 1 input row; S04 s04 graph md5 094ba298.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c147_a1_1_t2626.log -- py -u tools/bench/diag_c147_a1_1_t2626.py"""
import hashlib, json, os, sys                                                               # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


rec = (json.load(open(os.path.join(B, "diag_c147_a1_1_graph.json"), encoding="utf-8")).get("graph") or {})
gp = os.path.join(ROOT, rec.get("path", ""))
gate("G graph file md5 == the graph script's record", os.path.isfile(gp) and md5(gp) == rec.get("md5"), rec)
S04 = os.path.join(B, "graph_ring_p4s04_20261007_223245.json")
gate("S04 s04 graph md5 094ba298", md5(S04) == "094ba298ba7b2c1d69f92c84d8ecb626", md5(S04))


def table(path):
    gr = json.load(open(path, encoding="utf-8"))
    T = gr["terminals"]
    byw = {}
    for r in T:
        if r.get("wire_uid"):
            byw.setdefault(int(r["wire_uid"]), []).append(r)
    rows = []
    for r in sorted((r for r in T if int(r.get("owner_uid") or 0) == 2626), key=lambda r: (r["is_source"] is False, int(r["term_uid"]))):
        w = int(r.get("wire_uid") or 0)
        far = ["#{0} {1} '{2}' t{3}".format(o["owner_uid"], o["owner_class"], o["term_name"], o["term_uid"])
               for o in byw.get(w, []) if int(o["owner_uid"]) != 2626] if w else []
        rows.append({"term_uid": int(r["term_uid"]), "dir": "output" if r["is_source"] else "input", "term_name": r["term_name"],
                     "term_class": r.get("term_class"), "wire_uid": w, "other_end": far, "frame_diagram": r.get("frame_diagram")})
    obj = [o for o in gr["objs"] if int(o["uid"]) == 2626]
    return rows, obj


new, nobj = table(gp)
old, _ = table(S04)
gate("R #2626 has >= 1 output row and >= 1 input row in the s05 graph", any(r["dir"] == "output" for r in new) and any(r["dir"] == "input" for r in new), len(new))
print("FACT #2626 object {0}".format(nobj), flush=True)
print("TABLE term_uid | dir | term_name | term_class | wire_uid | other end | (s04: name / wire)", flush=True)
om = dict((r["term_uid"], r) for r in old)
for r in new:
    o = om.get(r["term_uid"], {})
    print("ROW {0} | {1} | {2} | {3} | {4} | {5} | s04 {6!r} / {7}".format(r["term_uid"], r["dir"], r["term_name"], r["term_class"], r["wire_uid"],
                                                                           "; ".join(r["other_end"]) or "-", o.get("term_name"), o.get("wire_uid")), flush=True)
print("FACT s04 term_uids not in s05: {0}; s05 term_uids not in s04: {1}".format(sorted(set(om) - set(r["term_uid"] for r in new)),
                                                                                 sorted(set(r["term_uid"] for r in new) - set(om))), flush=True)
print("FACT data type: not a field of the graph read (wiki_build.read_live terminal rows) - UNREAD", flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [{"path": rec.get("path"), "md5": rec.get("md5")}])), flush=True)
sys.exit(1 if G["fail"] else 0)
