r"""diag_c125_loose - card 125-2 STEP A.2 (brief_125-2.md, PD251(c)): OFFLINE, no LabVIEW. Every wire of the P3a graph with fewer
than one source + one sink among its terminal rows ("loose end"), diffed against the P2b graph; for each NEW one: uid, the
terminals it IS connected to (node uid/class, terminal name/class), its diagram, and the plan_ring_p3a row that made it (from the
stage log's STEPX lines: bound symbolic ids -> real uids, plus the CONNECT/OP lines naming terminal uids).
PREDICTION: exactly one new loose-end wire (Error List 55 = P2b 54 + 1 `Wire has loose ends`, result_124-8).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c125_loose.log -- py -u tools/bench/diag_c125_loose.py"""
import json, os, re, sys                                                                     # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                                              # noqa: E402
P3A = os.path.join(HERE, "graph_ring_p3a_20261001_190155.json")
P2B = os.path.join(HERE, "graph_ring_p2b_20261001_154542.json")
SLOG = os.path.join(HERE, "stage_d1_ring_p3a.log")


def loose(gr):
    T, W = gr["terminals"], set(int(o["uid"]) for o in gr["objs"] if o["class"] == "Wire")
    by = {}
    for r in T:
        w = int(r.get("wire_uid") or 0)
        if w:
            by.setdefault(w, []).append(r)
    out = {}
    for w in W | set(by):
        rs = by.get(w, [])
        ns, nk = sum(1 for r in rs if r["is_source"]), sum(1 for r in rs if not r["is_source"])
        if ns < 1 or nk < 1:
            out[w] = {"n_src": ns, "n_sink": nk, "in_objs": w in W, "ends": [{k: r.get(k) for k in ("term_uid", "term_name", "is_source", "owner_uid",
                      "owner_class", "frame_diagram", "term_class")} for r in rs]}
    return out, by


def main():
    g3, g2 = json.load(open(P3A, encoding="utf-8")), json.load(open(P2B, encoding="utf-8"))
    l3, by3 = loose(g3)
    l2, _b = loose(g2)
    w2 = set(int(o["uid"]) for o in g2["objs"] if o["class"] == "Wire")
    new = dict((w, v) for w, v in l3.items() if w not in l2)
    print("FACT loose-end wires: P3a {0}, P2b {1}; in P3a not loose in P2b: {2}; of those, wire uid absent from P2b: {3}".format(
        len(l3), len(l2), sorted(new), sorted(w for w in new if w not in w2)))
    lines = open(SLOG, encoding="utf-8", errors="replace").read().splitlines()
    rows, bound = [], {}
    for ln in lines:
        m = re.search(r"STEPX\s+(\d+)\s+(\S+)\s+acts \[([^\]]*)\] ids (\[[^\]]*\]) bound (\{[^}]*\}) diff", ln)
        if m:
            b = eval(m.group(5), {})                                                         # noqa: S307 - our own log's dict repr
            rows.append({"k": int(m.group(1)), "op": m.group(2), "ids": eval(m.group(4), {}), "bound": b, "line": lines.index(ln) + 1})
            bound.update(b)
    for w, v in sorted(new.items()):
        mention = [i + 1 for i, ln in enumerate(lines) if re.search(r"\b{0}\b".format(w), ln)]
        own = set(int(e["owner_uid"]) for e in v["ends"]) | set(int(e["term_uid"]) for e in v["ends"])
        made = [r for r in rows if own & set(int(x) for x in r["bound"].values())]
        ctx = []
        for e in v["ends"]:
            nr = [r for r in g3["terminals"] if int(r["owner_uid"]) == int(e["owner_uid"])]
            ctx.append({"owner": e["owner_uid"], "terms": [(r["term_uid"], r["term_name"], r["is_source"], r["wire_uid"]) for r in nr]})
        print("NEWLOOSE {0}".format(json.dumps({"wire": w, "in_p2b_wires": w in w2, **v, "owner_terms": ctx, "stage_log_lines": mention[:12],
                                                "plan_rows_binding_an_end": [(r["k"], r["op"], r["ids"], r["bound"]) for r in made]}, default=str)))
    _l, by2 = loose(g2)
    w3 = set(int(o["uid"]) for o in g3["objs"] if o["class"] == "Wire")
    key = lambda rs: sorted((int(r["term_uid"]), bool(r["is_source"])) for r in rs)              # noqa: E731
    for w in sorted(w3 - w2):
        print("NEWWIRE {0}".format(json.dumps({"wire": w, "ends": [(r["term_uid"], r["term_name"], r["is_source"], r["owner_uid"], r["owner_class"],
                                                r["frame_diagram"]) for r in by3.get(w, [])]}, default=str)))
    for w in sorted(w3 & w2):
        if key(by3.get(w, [])) != key(by2.get(w, [])):
            print("CHANGEDWIRE {0}".format(json.dumps({"wire": w, "p2b": key(by2.get(w, [])), "p3a": key(by3.get(w, []))})))
    print("FACT wires lost P2b->P3a: {0}".format(sorted(w2 - w3)))
    ok = len(new) == 1
    print("{0}  P1 exactly one new loose-end wire in P3a vs P2b  n={1}".format("PASS" if ok else "FAIL", len(new)))
    print(protocol.result_line({"status": "PASS" if ok else "FAIL", "gates": {"pass": int(ok), "fail": int(not ok)},
                                "first_fail": None if ok else "P1 n={0}".format(len(new)), "artefacts": []}))


if __name__ == "__main__":
    main()
