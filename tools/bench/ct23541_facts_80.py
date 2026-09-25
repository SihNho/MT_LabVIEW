r"""ct23541_facts_80 - card 80-7 V5 (plan PD180(c)). OFFLINE, no LabVIEW: D1_k's terminal/object census as read live by
l2a1_facts_80 (tools/bench/l2a1_graph_k_80.json, md5 field = D1_k 6cf5b077...), owners from l2a1_facts_80.json, node labels
from main_vi_node_labels.json (the ORIGINAL's labels - uids created later have none).
PREDICTION: #23541 is a ControlTerminal labelled 'index' on diagram #639 (WhileLoop #637), sink of w23556 from #10757
'element' (the only writer); its readers are Locals only; no other ControlTerminal is labelled 'index'; no Property
node / control-reference constant is bound to it (implicit property nodes carry the control's label; any
Property/ControlReferenceConstant whose uid has no original label is listed, since offline it cannot be excluded).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/ct23541_facts_80.log -- py -u tools/bench/ct23541_facts_80.py"""
import collections, json, os, sys                                                  # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))  # noqa: E702
import vigraph as V, jev_candidates as JC, protocol as PR                           # noqa: E401,E402
N, FF = {"pass": 0, "fail": 0}, []


def gate(label, ok, detail=""):
    N["pass" if ok else "fail"] += 1
    if not ok and not FF:
        FF.append(label)
    print("  {0}  {1}{2}".format("PASS" if ok else "FAIL", label, (" | " + str(detail)[:900]) if detail != "" else ""), flush=True)


def fact(x):
    print("  FACT  " + str(x)[:1200], flush=True)


gk = json.load(open(os.path.join(HERE, "l2a1_graph_k_80.json"), encoding="utf-8"))
F = json.load(open(os.path.join(HERE, "l2a1_facts_80.json"), encoding="utf-8"))
O, LAB = dict((int(k), tuple(v)) for k, v in F["owners"].items()), JC.node_labels_default()
T = V.dedupe_rows(gk["terminals"])[0]
CL = dict((int(o["uid"]), o["class"]) for o in gk["objs"])
fact("source {0} md5-field {1}; {2} terminal rows, {3} objects".format(gk["vi"], gk["md5"], len(T), len(CL)))


def loop_of(d):
    for _n in range(14):
        c, u = O.get(d, ("?", 0))
        if c in ("WhileLoop", "ForLoop"):
            return "{0}#{1}".format(c, u)
        if not u or c not in V.STRUCT_OWNER:
            return "top(D{0}:{1})".format(d, c)
        d = O.get(u, ("?", 0))[1]
    return "?"


WI = collections.defaultdict(list)
for r in T:
    WI[r["wire_uid"]].append(r)
ct = [r for r in T if r["term_uid"] == 23541]
gate("C1 #23541 is one ControlTerminal row (census class {0})".format(CL.get(23541)), len(ct) == 1 and ct[0]["term_class"] == "ControlTerminal" and CL.get(23541) == "ControlTerminal", ct)
r = ct[0]; lab = r["term_name"]                                                     # noqa: E702
fact("C1 label {0!r}; {1} (is_source {2}); owner {3} #{4}; diagram {5}; loop {6}".format(lab, "INDICATOR" if not r["is_source"] else "CONTROL",
     r["is_source"], r["owner_class"], r["owner_uid"], r["frame_diagram"], loop_of(int(r["frame_diagram"]))))
ends = [(x["owner_uid"], x["owner_class"], x["term_name"], "SRC" if x["is_source"] else "SNK", loop_of(int(x["frame_diagram"] or 0))) for x in WI[r["wire_uid"]] if x is not r]
fact("C2 wire w{0} ends: {1}".format(r["wire_uid"], ends))
same = [x for x in T if x.get("term_class") == "ControlTerminal" and x["term_name"] == lab]
gate("C2 exactly one writer: w23556 from #10757 'element' (IndexArray), and no other ControlTerminal labelled {0!r}".format(lab),
     r["wire_uid"] == 23556 and not r["is_source"] and [(e[0], e[2], e[3]) for e in ends] == [(10757, "element", "SRC")] and len(same) == 1,
     {"same_label": [(x["term_uid"], x["frame_diagram"]) for x in same]})
loc = collections.defaultdict(list)
for x in T:
    if x["owner_class"] in ("Local", "Global") and x["term_name"] == lab:
        loc[(x["owner_uid"], x["owner_class"])].append(x)
for (u, c), rs in sorted(loc.items()):
    for x in rs:
        fe = [(e["owner_uid"], e["owner_class"], e["term_name"]) for e in WI[x["wire_uid"]] if e is not x] if x["wire_uid"] else []
        fact("C3 {0} #{1} {2} w{3} diagram {4} loop {5} -> {6}".format(c, u, "READ" if x["is_source"] else "WRITE", x["wire_uid"], x["frame_diagram"], loop_of(int(x["frame_diagram"] or 0)), fe))
wl = [x for rs in loc.values() for x in rs if not x["is_source"]]
gate("C3 no Local/Global WRITES label {0!r}; readers = {1} Local(s)".format(lab, sum(1 for rs in loc.values() for x in rs if x["is_source"])), not wl, [(x["owner_uid"], x["wire_uid"]) for x in wl])
refc = sorted(u for u, c in CL.items() if c in ("Property", "Invoke", "ControlReferenceConstant"))
bylab = [u for u in refc if (LAB.get(u) or "").strip() == lab]
nolab = [(u, CL[u]) for u in refc if u not in LAB]
for u in nolab:
    rs = [x for x in T if x["owner_uid"] == u]
    fact("C4 unlabelled {0} #{1} (uid not in the original's labels): terms {2}".format(CL[u], u, [(x["term_name"], x["is_source"], x["wire_uid"]) for x in rs][:6]))
gate("C4 no Property/Invoke/ControlReferenceConstant carries label {0!r} ({1} such objects; {2} without an original label)".format(lab, len(refc), len(nolab)),
     not bylab, bylab)
print("=== ct23541_facts_80: {0} pass / {1} fail".format(N["pass"], N["fail"]))
print(PR.result_line(PR.make_result(N["pass"], N["fail"], FF[0] if FF else None)))
sys.exit(1 if N["fail"] else 0)
