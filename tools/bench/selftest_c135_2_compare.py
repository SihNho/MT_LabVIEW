r"""selftest_c135_2_compare - card 135-2 pass 2: the re-annotated strict compare (launch_p3b2_resume_c135_compare.py). OFFLINE.
Fixtures are copies of the REAL reference read graph_ring_p3b2a_fs_20261002_102553.json (b885fa4a), edited in memory only.
PREDICTION: T1 ref vs ref EQUAL; T2 annotation-only (status stripped from one copy's borders) EQUAL with the new compare and
DIFFERENT with the old (the 135-1 failure reproduced); T3..T9 each real difference DIFFERENT naming its field: a stored border's
non-annotation field, a border tunnel face moved to another frame, a terminal uid, a wire uid, an FS frame order, an obj class,
a dropped terminal-row field. 9/0.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_c135_2_compare.log -- py -u tools/bench/selftest_c135_2_compare.py"""
import copy, json, os, sys                                                         # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(B))
sys.path.insert(0, B)
import protocol as P                                                               # noqa: E402
import launch_p3b2_resume_c135_compare as CMP                                      # noqa: E402
import launch_p3b2_c135 as C135                                                    # noqa: E402
REF = json.load(open(os.path.join(B, "graph_ring_p3b2a_fs_20261002_102553.json"), encoding="utf-8"))
ok = []


def gate(n, c, d=""):
    ok.append((n, bool(c)))
    print("  {0}  {1}  {2}".format("PASS" if c else "FAIL", n, json.dumps(d, default=str)[:400]), flush=True)


def cur():
    g, _ch = CMP.reannotate(REF)            # the reference as the CURRENT reader would have written it
    return g


eq, d, ch = CMP.compare(REF, REF)
gate("T1 ref vs ref EQUAL", eq, d)
a = cur()
stripped = copy.deepcopy(a)
n = 0
for b in stripped["fs_measured"]["borders"].values():
    n += b.pop("status", None) is not None
eq, d, ch = CMP.compare(a, stripped)
eq_old, d_old = C135.compare(a, stripped)
gate("T2 annotation-only ({0} borders) EQUAL new / DIFFERENT old".format(n), n > 0 and eq and not eq_old and list(d_old) == ["borders"], [d, list(d_old)])


def differs(label, mut, field):
    g = copy.deepcopy(a)
    mut(g)
    eq, d, _c = CMP.compare(g, a)
    gate(label, not eq and field in d, list(d))


bk = next(k for k, v in a["fs_measured"]["borders"].items() if v.get("fs") is not None)
differs("T3 stored border field changed -> DIFFERENT (reannotation)", lambda g: g["fs_measured"]["borders"][bk].update(frame=-1), "reannotation")
oface = a["fs_measured"]["borders"][bk]["outer_face"]


def move_face(g):
    r = next(r for r in g["terminals"] if int(r["term_uid"]) == oface)
    r["frame_diagram"] = int(r.get("frame_diagram") or 0) + 1


differs("T4 border tunnel face on another diagram -> DIFFERENT (borders)", move_face, "borders")
differs("T5 terminal uid -> DIFFERENT (terminals)", lambda g: g["terminals"][0].update(term_uid=int(g["terminals"][0]["term_uid"]) + 999999), "terminals")
wr = next(i for i, r in enumerate(a["terminals"]) if r.get("wire_uid"))
differs("T6 wire uid -> DIFFERENT (wires)", lambda g: g["terminals"][wr].update(wire_uid=int(g["terminals"][wr]["wire_uid"]) + 999999), "wires")
fk = next(k for k, v in a["fs_measured"]["fs_frames"].items() if len(v) > 1)
differs("T7 FS frame order -> DIFFERENT (fs_frames)", lambda g: g["fs_measured"]["fs_frames"][fk].reverse(), "fs_frames")
differs("T8 obj class -> DIFFERENT (node_classes)", lambda g: g["objs"][0].update({"class": "X"}), "node_classes")
differs("T9 dropped terminal-row field -> DIFFERENT (terminals)", lambda g: g["terminals"][0].pop("term_name", None), "terminals")
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None))), flush=True)
sys.exit(1 if nf else 0)
