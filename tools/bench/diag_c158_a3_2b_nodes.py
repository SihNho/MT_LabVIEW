# ---
# labview: none
# hardware: none
# ---
r"""diag_c158_a3_2b_nodes - card 158-a3-2b (OFFLINE, no LabVIEW): from the P5-2a graph json (argv[1], written by diag_c158_a3_2b_graph.py) print the
rows the step-2 plan is built on (brief_156-a2-1.md:45-48): the refnum SR sr_q7 on 1.7 (#31347/#31352, diag_c158_p5s02a_scratch.log:67), Dequeue #31262
and Release #31266 with their terminals, the timeout constant #31448, the new Case #31308 (frames / selector #31485/#31506/#31517, tunnels #31447,
#31546, #31557, nodes inside), the owners of #376 / #3052 / #3453, loop 1.7 (#23041) condition terminal source, and the open terminals of these
nodes. The 1.7 counter SR is a STEP-2 action (plan_ring_p5s02r_in.json A41 sr_c7) - not in this file. Row form = diag_c155_a3_2_nodes.py show()
(5f445a0b, card 155-a3-2), copied (6 lines); the selection of uids is new.
PREDICTION: every bound uid has >= 1 row; Case #31308 owns 2 frames; #376 / #3052 / #3453 sit on one of those frames; Dequeue 'queue' wired from sr_q7.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c158_a3_2b_nodes.log -- py -u tools/bench/diag_c158_a3_2b_nodes.py <graph json>"""
import json, os, sys                                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import addrcheck as AC                                                                      # noqa: E402
gr = json.load(open(os.path.join(ROOT, sys.argv[1]), encoding="utf-8"))
BOUND = {31347: "sr_q7 SR (L/R)", 31352: "sr_q7 SR (L/R)", 31262: "Dequeue Element c_deq", 31266: "Release Queue c_rel", 31448: "timeout const c_tmo",
         31447: "t_el7 case tunnel", 31546: "t_in1 case tunnel", 31557: "t_in2 case tunnel", 31485: "c_case7 bound -31", 31506: "c_case7 bound -29",
         31517: "c_case7 bound -30", 376: "#376 save trace", 3052: "#3052 refnum const", 3453: "#3453 file progress", 31258: "Obtain Queue (P5-1a)"}
CASE, LOOP17 = 31308, 23041
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


rows = gr.get("terminals") or []
pos = AC.pos_table(rows)
own = gr.get("owners") or {}
cls = dict((int(o["uid"]), o["class"]) for o in gr.get("objs") or [])


def show(tag, r):
    k = pos.get(r["term_uid"])
    print("ROW {0} | owner #{1} | index {2} | {3} | {4} | name {5!r} | term #{6} | wire {7} | src {8} | frame {9}".format(
        tag, r.get("owner_uid"), k[1] if k else None, r.get("owner_class"), r.get("term_class"), r.get("term_name"), r.get("term_uid"),
        r.get("wire_uid"), bool(r.get("is_source")), r.get("frame_diagram")), flush=True)


byo = {}
for r in rows:
    byo.setdefault(int(r["owner_uid"]), []).append(r)
key = lambda r: pos.get(r["term_uid"], (0, 0))[1]                                           # noqa: E731


def src_of(r):
    return [s for s in rows if r.get("wire_uid") and s.get("wire_uid") == r["wire_uid"] and s.get("is_source")]


missing, opens = [], []
for u in sorted(BOUND):
    rs = sorted(byo.get(u, []), key=key)
    op = [r.get("term_name") for r in rs if not r.get("wire_uid")]
    opens += [(u, n) for n in op]
    print("NODE #{0} {1} class {2}: {3} rows, open {4}; frames {5}".format(u, BOUND[u], cls.get(u), len(rs), op,
                                                                            sorted(set(str(r.get("frame_diagram")) for r in rs))), flush=True)
    missing += [] if (rs or cls.get(u) == "Diagram") else [u]
    for r in rs:
        show("n{0}".format(u), r)
gate("N every bound uid (not a frame Diagram) has >= 1 terminal row", not missing, missing)
cf = sorted(int(k) for k, v in own.items() if list(v) == ["CaseStructure", CASE])
print("FACT case #{0} frames (owned by it): {1}; case obj {2}".format(CASE, cf, [o for o in gr.get("objs") or [] if int(o["uid"]) == CASE]), flush=True)
gate("C case #{0} owns 2 frames".format(CASE), len(cf) == 2, cf)
fr = dict((u, sorted(set(int(r["frame_diagram"]) for r in byo.get(u, []) if r.get("frame_diagram") not in (None, "")))) for u in (376, 3052, 3453))
print("FACT #376/#3052/#3453 diagrams {0}".format(fr), flush=True)
gate("F #376 / #3052 / #3453 each sit on one frame of case #{0}".format(CASE), all(len(v) == 1 and v[0] in cf for v in fr.values()), fr)
dq = [r for r in byo.get(31262, []) if (r.get("term_name") or "").strip().lower() == "queue"]
dqs = [(int(s["owner_uid"]), int(s["term_uid"])) for r in dq for s in src_of(r)]
for r in dq:
    show("deq-queue", r)
print("FACT Dequeue 'queue' source {0}".format(dqs), flush=True)
gate("Q Dequeue #31262 'queue' wired; its source owned by sr_q7 (#31347 or #31352)", len(dqs) == 1 and dqs[0][0] in (31347, 31352), dqs)
for r in sorted(byo.get(LOOP17, []), key=key):
    show("loop17", r)
    for s in src_of(r):
        show("loop17-src", s)
print("FACT open rows of the bound nodes: {0} {1}".format(len(opens), opens), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
