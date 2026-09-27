r"""facts_c108b - card 108-2 F1 (PD221(d)), OFFLINE, no LabVIEW: what #10886 is and does with rows 10382.x / 11529.x, and the
S1 sources those two rows must re-make (rule 1a), read from graph files only.
INPUTS: argv[1] = the graph (default: newest tools/bench/graph_l2a2_*.json, else graph_l2a1_bed_20260927.json); the S1 wiki
graph docs/wiki/subvi/D1_s1_copy.json; labels tools/bench/main_vi_node_labels.json (jev_candidates.node_labels_default).
PRIOR ART: diag_c107b_bedgraph.py (graph loading), ct23541_facts_80.py (wire-partner reads). No new op.
PREDICTION (from docs/camera-acquisition-facts.md:266-272): #10886 is a Compound Arithmetic in 1.1 whose inputs include 10382's
and 11529's outputs; downstream reaches NOT #10285 -> Property #1469 ('Fix to a Certain Pattern' write), which the #10407 autofocus
case (motor) reads. Rows printed as FACT lines; gates only on file presence / the prediction.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/facts_c108b.log -- py -u tools/bench/facts_c108b.py"""
import collections, glob, json, os, sys                                              # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P, jev_candidates as JC                                            # noqa: E402
gates = []
STOP = ("Property", "Invoke", "ControlTerminal", "Local", "Global", "SubVI", "PolySubVI", "ExpressVI")


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)


def load(p):
    return json.load(open(p, encoding="utf-8"))


def main():
    gp = sys.argv[1] if len(sys.argv) > 1 else (sorted(glob.glob(os.path.join(HERE, "graph_l2a2_*.json"))) or [os.path.join(HERE, "graph_l2a1_bed_20260927.json")])[-1]
    G, S1 = load(gp), load(os.path.join(JC.WIKI, JC.S1_KEY + ".json"))
    lab = JC.node_labels_default()
    print("  FACT graph {0} (vi {1} md5 {2}); S1 {3}".format(gp, G["vi"], G["md5"], JC.S1_KEY), flush=True)
    for name, T, objs in (("CUR", G["terminals"], G["objs"]), ("S1", S1["terminals"], None)):
        cls = dict((int(o["uid"]), o["class"]) for o in (objs or []))
        byw = collections.defaultdict(list)
        for r in T:
            if r["wire_uid"]:
                byw[r["wire_uid"]].append(r)
        own = collections.defaultdict(list)
        for r in T:
            own[r["owner_uid"]].append(r)

        def show(r):
            return "#{0}({1} {2!r}) t{3} {4!r} {5} w{6} diag {7}".format(r["owner_uid"], r["owner_class"], lab.get(r["owner_uid"], ""), r["term_uid"],
                                                                     r["term_name"], "SRC" if r["is_source"] else "SNK", r["wire_uid"], r["frame_diagram"])

        def partners(r):
            return [x for x in byw.get(r["wire_uid"], []) if x["term_uid"] != r["term_uid"]] if r["wire_uid"] else []
        for u in (10886, 10382, 11529, 9647, 11336, 10445, 10285, 1469, 23541, 23523):
            for r in own.get(u, []):
                print("  FACT {0} NODE {1} class {2} :: {3} <-> {4}".format(name, u, cls.get(u, r["owner_class"]), show(r), [show(x) for x in partners(r)]), flush=True)
        if name == "S1":
            for u in (10382, 11529):
                for r in own.get(u, []):
                    if r["term_name"] == "x" and not r["is_source"]:
                        src = [x for x in partners(r) if x["is_source"]]
                        print("  FACT S1 EDGE {0}.x <- {1}".format(u, [show(x) for x in src]), flush=True)
                        gate("S1 {0}.x has exactly one source".format(u), len(src) == 1, [show(x) for x in src])
        # downstream walk from #10886's outputs to the first STOP-class node (or depth 8)
        seen, q, chain = set(), [(10886, 0)], []
        while q:
            u, d = q.pop(0)
            if u in seen or d > 8:
                continue
            seen.add(u)
            for r in own.get(u, []):
                if not r["is_source"]:
                    continue
                for x in partners(r):
                    if x["is_source"]:
                        continue
                    chain.append((d, show(r), show(x)))
                    nxt = x["owner_uid"]
                    if x["owner_class"] in STOP:
                        continue
                    if x["owner_class"] in JC.TREE_OWNERS:                        # a tunnel: continue from its other face(s)
                        q.append((nxt, d + 1))
                    else:
                        q.append((nxt, d + 1))
        for d, a, b in chain:
            print("  FACT {0} DOWNSTREAM d{1} {2} -> {3}".format(name, d, a, b), flush=True)
        if name == "CUR":
            gate("CUR #10886 is present with >= 2 input rows", len([r for r in own.get(10886, []) if not r["is_source"]]) >= 2, len(own.get(10886, [])))
    n = sum(1 for _l, ok in gates if ok)
    ff = next((lb for lb, ok in gates if not ok), None)
    print(P.result_line(P.make_result(n, len(gates) - n, ff, artefacts=[])), flush=True)
    return 0 if ff is None else 1


if __name__ == "__main__":
    sys.exit(main())
