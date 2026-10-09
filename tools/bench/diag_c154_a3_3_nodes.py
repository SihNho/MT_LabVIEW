# ---
# labview: none
# hardware: none
# ---
r"""diag_c154_a3_3_nodes - card 154-a3-3b step 6 (OFFLINE, no LabVIEW): from the P5-1a graph json (argv[1], written by diag_c154_a3_3_graph.py)
print the rows of the NEW nodes (the 8 made uids of diag_c154_a3_3_graph_plan.json edits.made + the tunnels / SR bound in the scratch log:
t_el #31000, sr_n #30996/#31004, t_ci #31175, t_co #31186), the new Case #30726's frames (owners) and selector row, and the unwired rows of the
13 owners that hold the prefix's 19 declared open (node, term) pairs (diag_c154_a3_2b_facts.md:15-17). Row form == diag_c152_b3_1_fs.py show()
(owner, POSITION index via addrcheck.pos_table, owner class, term class, name, term uid, wire uid, is_source, frame).
Replaces the copy of diag_c152_b3_1_fs.py (FS #29721 rows, not asked in this step). READ-ONLY, record only.
PREDICTION: every made / bound uid has >= 1 row; case #30726 has 2 frames owned by it; >= 1 declared-open owner row unwired.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c154_a3_3_nodes.log -- py -u tools/bench/diag_c154_a3_3_nodes.py <graph json>"""
import json, os, sys                                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import addrcheck as AC                                                                      # noqa: E402
gr = json.load(open(os.path.join(ROOT, sys.argv[1]), encoding="utf-8"))
PL = json.load(open(os.path.join(ROOT, "tools", "bench", "diag_c154_a3_3_graph_plan.json"), encoding="utf-8"))
MADE = dict((int(k), v) for k, v in PL["edits"]["made"].items())
BOUND = {31000: "t_el tunnel", 30996: "sr_n SR (L/R)", 31004: "sr_n SR (L/R)", 31175: "t_ci tunnel", 31186: "t_co tunnel",
         30897: "case #30726 selector (c_case bound -20)"}
# 1st run (log segment 1) FAILED gate N: CaseStructure #30726 owns no terminal row (its selector is Tunnel #30897) and ControlTerminal #31071
# is a row of Diagram #4866 with term_uid 31071. Fix: a node's rows = owner_uid == u OR term_uid == u; the case is not a row owner (its
# selector #30897 is listed instead); the selector's outer wire source is printed.
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
     infr == cf and srcs == [(29724, 29900)], (infr, srcs))     # added after archive/peer/2026-10-09-c154-a3-3b-nodes.md:78
gate("C case #{0} has 2 frames owned by it".format(CASE), len(cf) == 2, cf)
op = []
for u in DECL:
    for r in sorted(byo.get(u, []), key=key):
        if not r.get("wire_uid"):
            op.append((u, r.get("term_name")))
            show("decl-open", r)
print("FACT declared-open owners: {0} unwired rows {1}".format(len(op), op), flush=True)
gate("O >= 1 declared-open owner row unwired", bool(op), len(op))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
