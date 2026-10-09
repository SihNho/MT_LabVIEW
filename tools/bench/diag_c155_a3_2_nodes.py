# ---
# labview: none
# hardware: none
# ---
r"""diag_c155_a3_2_nodes - card 155-a3-2 (OFFLINE, no LabVIEW): from the P5-1 graph json (argv[1], written by diag_c155_a3_2_graph.py) print the rows of
the NEW / BOUND nodes of the P5-1b scratch (diag_c155_p5s01b_scratch.log:95-147: Local c_lw #31213, sr_q L/R #31222/#31225 on loop #10170,
SelectorTunnels t_qi #31257 / t_qo #31293 on Case #30726) plus the P5-1a nodes the P5-1b rows wire to (Obtain #31258, Enqueue #30756, selector
Tunnel #30897, Count SR #31004/#30996, case tunnels #31000/#31175/#31186), the Case #30726 frames, the wired rows on frame #30914, the Enqueue
'queue' terminal's source, and the unwired rows of the 13 declared-open owners of P5-1a. COPIED from tools/bench/diag_c154_a3_3_nodes.py
(90ee6233, card 154-a3-3b, ran 4/0) with ids changed (plan json, BOUND map) and three record steps added (F frame #30914 rows, Q Enqueue
'queue' source, the 8 new wires' rows). Changed lines: 5-14, 20, 22-24, 88-110. Row form unchanged.
PREDICTION: every made / bound uid has >= 1 row; case #30726 has 2 frames owned by it; selector source #29724 t29900 (unchanged from P5-1a);
Enqueue 'queue' wired, its source on SelectorTunnel #31257 (plan w_qi_enq); every new wire uid has a row.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c155_a3_2_nodes.log -- py -u tools/bench/diag_c155_a3_2_nodes.py <graph json>"""
import json, os, sys                                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import addrcheck as AC                                                                      # noqa: E402
gr = json.load(open(os.path.join(ROOT, sys.argv[1]), encoding="utf-8"))
PL = json.load(open(os.path.join(ROOT, "tools", "bench", "diag_c155_a3_2_graph_plan.json"), encoding="utf-8"))
MADE = dict((int(k), v) for k, v in PL["edits"]["made"].items())
BOUND = {31222: "sr_q SR (L/R)", 31225: "sr_q SR (L/R)", 31257: "t_qi SelectorTunnel", 31293: "t_qo SelectorTunnel", 31258: "Obtain Queue (P5-1a)",
         30756: "Enqueue Element (P5-1a)", 31004: "sr_n SR (P5-1a)", 30996: "sr_n SR (P5-1a)", 31000: "t_el tunnel (P5-1a)",
         31175: "t_ci tunnel (P5-1a)", 31186: "t_co tunnel (P5-1a)", 30897: "case #30726 selector (P5-1a)"}
CASE = 30726
DECL = [10068, 10150, 10382, 10757, 11261, 11529, 2626, 28083, 29240, 29625, 376, 5058, 8634]
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
missing = []
for r in rows:
    if int(r["term_uid"]) in MADE and int(r["owner_uid"]) != int(r["term_uid"]):
        byo.setdefault(int(r["term_uid"]), []).append(r)
for u in sorted((set(MADE) - {CASE}) | set(BOUND)):
    rs = sorted(byo.get(u, []), key=key)
    print("NODE #{0} {1} class {2}: {3} rows, open {4}".format(u, MADE.get(u) or BOUND.get(u), cls.get(u), len(rs),
                                                               [r.get("term_name") for r in rs if not r.get("wire_uid")]), flush=True)
    missing += [] if rs else [u]
    for r in rs:
        show("new", r)
gate("N every made / bound uid has >= 1 terminal row", not missing, missing)
cf = sorted(int(k) for k, v in own.items() if list(v) == ["CaseStructure", CASE])
print("FACT case #{0} frames (owned by it): {1}; case obj {2}".format(CASE, cf, [o for o in gr.get("objs") or [] if int(o["uid"]) == CASE]), flush=True)
srcs = []
for r in byo.get(30897, []):
    if r.get("wire_uid") and r.get("term_class") == "OuterTerminal":
        for s in rows:
            if s.get("wire_uid") == r["wire_uid"] and s.get("is_source"):
                show("selector-src", s)
                srcs.append((int(s["owner_uid"]), int(s["term_uid"])))
infr = sorted(int(r["frame_diagram"]) for r in byo.get(30897, []) if r.get("term_class") == "InnerTerminal")
gate("S selector #30897 inner rows on the case's frames {0} and its outer wire's source is #29724 t29900 (brief_154-a3-3.md:21)".format(cf),
     infr == cf and srcs == [(29724, 29900)], (infr, srcs))
gate("C case #{0} has 2 frames owned by it".format(CASE), len(cf) == 2, cf)
op = []
for u in DECL:
    for r in sorted(byo.get(u, []), key=key):
        if not r.get("wire_uid"):
            op.append((u, r.get("term_name")))
            show("decl-open", r)
print("FACT declared-open owners: {0} unwired rows {1}".format(len(op), op), flush=True)
gate("O >= 1 declared-open owner row unwired", bool(op), len(op))
f0 = [r for r in rows if str(r.get("frame_diagram")) == "30914"]
for r in sorted(f0, key=lambda r: (int(r["owner_uid"]), key(r))):
    show("frame30914", r)
print("FACT frame #30914 rows {0}, wired {1}, unwired {2}".format(len(f0), sum(1 for r in f0 if r.get("wire_uid")),
                                                                 [(r.get("owner_uid"), r.get("term_name")) for r in f0 if not r.get("wire_uid")]), flush=True)
qsrc = []
for r in byo.get(30756, []):
    if (r.get("term_name") or "").strip().lower() == "queue":
        show("enq-queue", r)
        for s in rows:
            if r.get("wire_uid") and s.get("wire_uid") == r["wire_uid"] and s.get("is_source"):
                show("enq-queue-src", s)
                qsrc.append((int(s["owner_uid"]), int(s["term_uid"])))
gate("Q Enqueue #30756 'queue' wired; its source is owned by SelectorTunnel #31257 (plan w_qi_enq)", len(qsrc) == 1 and qsrc[0][0] == 31257, qsrc)
nw = [int(w) for w in PL["edits"]["new_wires"]]
for w in nw:
    for r in rows:
        if r.get("wire_uid") and int(r["wire_uid"]) == w:
            show("newwire{0}".format(w), r)
nwm = [w for w in nw if not any(r.get("wire_uid") and int(r["wire_uid"]) == w for r in rows)]
gate("W every new wire uid {0} has >= 1 row".format(nw), not nwm, nwm)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
