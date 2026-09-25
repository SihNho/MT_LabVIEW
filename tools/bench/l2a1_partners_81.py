r"""l2a1_partners_81 - card 81-3 R4/R5. OFFLINE, no LabVIEW. Facts on the five #639 partners that 81-2 found with no
decided mechanism (#10382 #11529 #17272 #10739 #10929) and the writers/readers of indicator #17272, in the shape of
ct23541_facts_80.py (PD181(c) for #23541).
PRIOR ART: ct23541_facts_80.py (census/owner/Local/Property scan, reused as-is), l2a1_facts_80.py (loop_of, closure);
data l2a1_graph_k_80.json (live D1_k read, md5-field 6cf5b077...), l2a1_facts_80.json owners, build_d1_v0.json moved/cut,
plan docs/d1-loop12-17-split-plan.md section 1/2 groups. No new op.
PREDICTION (contract): P1 each of the 5 uids owns >= 1 terminal row in the census; P2 each has a class; P3 #17272 is
one ControlTerminal row. Ownership / reader results are REPORTED as FACTS, not gated (card: measure, do not decide).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/l2a1_partners_81.log -- py -u tools/bench/l2a1_partners_81.py"""
import collections, json, os, sys                                                  # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))  # noqa: E702
import vigraph as V, jev_candidates as JC, protocol as PR                           # noqa: E401,E402
N, FF = {"pass": 0, "fail": 0}, []
UIDS = [10382, 11529, 17272, 10739, 10929]
GROUPS = {"A": [5540, 9647, 10247, 10445, 10950, 17289, 10969, 10757], "A+ct": [17487, 5634, 23541],
          "B": [1359, 2222, 2626, 6104, 8885, 9833, 11261, 29874], "C": [10686], "W": [376], "K": [5058]}


def gate(label, ok, detail=""):
    N["pass" if ok else "fail"] += 1
    if not ok and not FF:
        FF.append(label)
    print("  {0}  {1}{2}".format("PASS" if ok else "FAIL", label, (" | " + str(detail)[:900]) if detail != "" else ""), flush=True)


def fact(x):
    print("  FACT  " + str(x)[:1200], flush=True)


gk = json.load(open(os.path.join(HERE, "l2a1_graph_k_80.json"), encoding="utf-8"))
F = json.load(open(os.path.join(HERE, "l2a1_facts_80.json"), encoding="utf-8"))
BD = json.load(open(os.path.join(HERE, "build_d1_v0.json"), encoding="utf-8"))
O, LAB = dict((int(k), tuple(v)) for k, v in F["owners"].items()), JC.node_labels_default()
T = V.dedupe_rows(gk["terminals"])[0]
CL = dict((int(o["uid"]), o["class"]) for o in gk["objs"])
MOVED = dict((int(u), sect) for sect, u, _b in BD["moved"])
CUTW = collections.defaultdict(list)
for c in BD["cut"]:
    CUTW[c[4]].append((c[0], c[1], c[2]))
fact("source {0} md5-field {1}; {2} rows, {3} objects, {4} owners, {5} moved, {6} cut".format(
    gk["vi"], gk["md5"], len(T), len(CL), len(O), len(MOVED), len(BD["cut"])))
WI, BY = collections.defaultdict(list), collections.defaultdict(list)
for r in T:
    WI[r["wire_uid"]].append(r); BY[V.node_of(r)].append(r)                       # noqa: E702


def chain(d):
    out = []
    for _n in range(14):
        c, u = O.get(d, ("?", 0))
        out.append((d, c, u))
        if not u or c not in V.STRUCT_OWNER:
            break
        d = O.get(u, ("?", 0))[1]
    return out


def loop_of(d):
    for d2, c, u in chain(d):
        if c in ("WhileLoop", "ForLoop"):
            return "{0}#{1}".format(c, u)
    return "top/?"


def group_of(u):
    return [g for g, us in GROUPS.items() if u in us]


for u in UIDS:
    rs = BY[u]
    gate("P1 #{0} owns >= 1 terminal row".format(u), bool(rs), len(rs))
    gate("P2 #{0} has a class".format(u), u in CL or bool(rs), CL.get(u))
    fds = sorted(set(int(r.get("frame_diagram") or 0) for r in rs))
    enc = sorted(set(x for d in fds for _d, _c, x in chain(d) if x in MOVED))
    fact("R4 #{0} class {1} label {2!r} diagrams {3} chain {4} loop {5} | moved-set {6} | plan group {7} | enclosing moved {8}".format(
        u, CL.get(u) or (V.node_class(rs[0]) if rs else "?"), LAB.get(u), fds, [chain(d) for d in fds][:2],
        [loop_of(d) for d in fds], MOVED.get(u), group_of(u), [(x, MOVED[x], group_of(x)) for x in enc]))
    for r in rs:
        ends = [(V.node_of(e), V.node_class(e), e["term_name"], "SRC" if e["is_source"] else "SNK",
                 group_of(V.node_of(e)), MOVED.get(V.node_of(e))) for e in WI[r["wire_uid"]] if e is not r] if r["wire_uid"] else []
        fact("   t{0} {1!r} {2} w{3} F{4} -> {5} | build_d1_v0 cut rows on this wire {6}".format(
            r["term_uid"], r["term_name"], "OUT" if r["is_source"] else "IN", r["wire_uid"], r.get("frame_diagram"), ends,
            CUTW.get(r["wire_uid"], [])))

# R5 #17272 writers / readers (ct23541_facts_80.py C1-C4 applied to #17272)
ct = [r for r in T if r["term_uid"] == 17272]
gate("P3 #17272 is one ControlTerminal row", len(ct) == 1 and ct[0]["term_class"] == "ControlTerminal", ct)
if ct:
    r = ct[0]; lab = r["term_name"]                                                 # noqa: E702
    fact("R5 C1 #17272 label {0!r} {1} owner {2} #{3} diagram {4} loop {5}".format(lab, "INDICATOR" if not r["is_source"] else "CONTROL",
         r["owner_class"], r["owner_uid"], r["frame_diagram"], loop_of(int(r["frame_diagram"] or 0))))
    fact("R5 C2 wire w{0} ends {1}".format(r["wire_uid"], [(x["owner_uid"], x["owner_class"], x["term_name"], "SRC" if x["is_source"] else "SNK")
                                             for x in WI[r["wire_uid"]] if x is not r]))
    same = [(x["term_uid"], x["frame_diagram"]) for x in T if x.get("term_class") == "ControlTerminal" and x["term_name"] == lab]
    fact("R5 C2 ControlTerminals labelled {0!r}: {1}".format(lab, same))
    loc = [x for x in T if x["owner_class"] in ("Local", "Global") and x["term_name"] == lab]
    for x in loc:
        fe = [(e["owner_uid"], e["owner_class"], e["term_name"]) for e in WI[x["wire_uid"]] if e is not x] if x["wire_uid"] else []
        fact("R5 C3 {0} #{1} {2} w{3} diagram {4} loop {5} -> {6}".format(x["owner_class"], x["owner_uid"], "READ" if x["is_source"] else "WRITE",
             x["wire_uid"], x["frame_diagram"], loop_of(int(x["frame_diagram"] or 0)), fe))
    fact("R5 C3 Local/Global rows labelled {0!r}: {1} (writes {2})".format(lab, len(loc), sum(1 for x in loc if not x["is_source"])))
    refc = sorted(u for u, c in CL.items() if c in ("Property", "Invoke", "ControlReferenceConstant"))
    bylab = [(u, CL[u]) for u in refc if (LAB.get(u) or "").strip() == lab]
    for u, c in bylab:
        fact("R5 C4 {0} #{1} labelled {2!r}: terms {3}".format(c, u, lab, [(x["term_name"], "OUT" if x["is_source"] else "IN", x["wire_uid"],
             x.get("frame_diagram"), [(e["owner_uid"], e["term_name"]) for e in WI[x["wire_uid"]] if e is not x] if x["wire_uid"] else [])
             for x in BY[u]]))
    fact("R5 C4 Property/Invoke/CtlRef objects labelled {0!r}: {1} of {2} (unlabelled {3})".format(
        lab, bylab, len(refc), sum(1 for u in refc if u not in LAB)))
print("=== l2a1_partners_81: {0} pass / {1} fail".format(N["pass"], N["fail"]))
print(PR.result_line(PR.make_result(N["pass"], N["fail"], FF[0] if FF else None)))
sys.exit(1 if N["fail"] else 0)
