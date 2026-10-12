# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_168-a1-1.md
# ---
r"""diag_c168_a1_1_ba - card 168-a1-1 steps 2-4 (OFFLINE, stored graph json only; no LabVIEW, no VI opened).

Found before writing: the stored graphs carry the OpAllTerms rows (`terminals`: term_uid, term_name, is_source, wire_uid, owner_uid,
owner_class, frame_diagram, term_class), the GObject census (`objs`), `owners` (diagram/structure -> [owner class, owner uid]) and
`fs_tunnel_pairs` (prep_c167_a1_1_graphlib.read_graph:59-61). The terminal-level graph and its walks are vigraph's: dedupe_rows,
build4 (the stored-graph call of stagesim.load_s1:2464), terminals, reach4, path. No second graph parser is written here; this script
only lists rows and asks vigraph for edges. The graph stores NO terminal data type, so every type column is the word `unread`.

census(gr)       -> every BuildArray node (objs class BuildArray U rows owner_class BuildArray): container chain, each terminal with its
                    wire, its source (or `none`) and its sinks, `has_unwired_input`.   Called twice (7815af09 before RBW, c5531708 after).
downstream(gr)   -> every key reachable from #11261 t11267 through vigraph.build4 edges (wire/thru/sr/fs/local), the leaves, the quoted
                    chain to each leaf, and a class per sink from the definitions in brief_168-a1-1.md step 3.
delete_pred(gr)  -> wires still attached to #11261 and the Wire-object count after deleting it.
PREDICTION CONTRACT (from prep_c167_a1_3_explore.log:44-47,60-61 and p6_rbw_deleted.md:35):
  P1 graph md5s 7815af09 / c5531708;  P2 #11261 t11270 and t11273 have no source in BOTH graphs;  P3 every #2626 input wired in 7815af09;
  P4 #11261 t11267 carries w25618 -> #23166 t8323 in 7815af09 and no wire in c5531708;  P5 Wire objects in c5531708 == 2066.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c168_a1_1_ba.log -- py -u tools/bench/diag_c168_a1_1_ba.py"""
import collections, json, os, sys                                                           # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench")):
    _p in sys.path or sys.path.insert(0, _p)                                                # noqa: E701
import vigraph as V                                                                         # noqa: E402
import prep_c156_a1_1_lib as L                                                              # noqa: E402

GRAPHS = [("before", "tools/bench/graph_ring_p5s02e_20261012_173009.json", "7815af09"),
          ("after", "tools/bench/graph_ring_p6rbw_20261012_191349.json", "c5531708")]
NODE, T_OUT, T_IN = 11261, 11267, (11270, 11273)
OUT_JSON, OUT_MD = "tools/bench/p6_buildarray.json", "tools/bench/p6_buildarray.md"
SAVE_WORDS = ("write", "save", "file", "tdms", "spreadsheet")
CONTROL_WORDS = ("motor", "stage", "piezo", "camera", "imaq", "stop", "selector", "case")


def first_index(gr):
    """{term_uid: index of its FIRST row in gr['terminals']} - the json path used as the row citation."""
    out = {}
    for i, r in enumerate(gr["terminals"]):
        out.setdefault(r["term_uid"], i)
    return out


def chain_up(gr, diag):
    """Container chain of a diagram uid up to the top, from gr['owners'] (+ objs classes): ['#d Diagram', '#s WhileLoop', ...]."""
    ocls = dict((int(o["uid"]), o["class"]) for o in gr["objs"])
    own, out, u, seen = gr.get("owners") or {}, [], int(diag or 0), set()
    while u and u not in seen:
        seen.add(u)
        out.append("#{0} {1}".format(u, ocls.get(u, "?")))
        v = own.get(str(u))
        if not v or not int(v[1] or 0):
            break
        u = int(v[1])
    return out


def cite(gr_path, idx, uid):
    return "{0}:terminals[{1}]".format(os.path.basename(gr_path), idx.get(uid, "?"))


def census(gr, gr_path):
    """Every BuildArray node with its terminals, wires, sources/sinks. Pure."""
    rows, rec = V.dedupe_rows(gr["terminals"])
    idx = first_index(gr)
    by_wire = collections.defaultdict(list)
    for r in rows:
        r["wire_uid"] and by_wire[r["wire_uid"]].append(r)                                 # noqa: E701
    uids = sorted(set(int(o["uid"]) for o in gr["objs"] if o["class"] == "BuildArray") |
                  set(int(r["owner_uid"]) for r in rows if r["owner_class"] == "BuildArray"))
    in_objs = set(int(o["uid"]) for o in gr["objs"] if o["class"] == "BuildArray")
    out = []
    for u in uids:
        ts = sorted((r for r in rows if r["owner_uid"] == u), key=lambda r: r["term_uid"])
        diags = sorted(set(int(r.get("frame_diagram") or 0) for r in ts))
        terms = []
        for r in ts:
            w = int(r["wire_uid"] or 0)
            others = [x for x in by_wire.get(w, []) if x["term_uid"] != r["term_uid"]]
            peer = lambda x: {"term_uid": x["term_uid"], "term_name": x["term_name"], "owner_uid": x["owner_uid"],   # noqa: E731
                              "owner_class": x["owner_class"], "term_class": x.get("term_class"), "row": cite(gr_path, idx, x["term_uid"])}
            t = {"term_uid": r["term_uid"], "term_name": r["term_name"], "dir": "output" if r["is_source"] else "input",
                 "wire_uid": w, "type": "unread", "row": cite(gr_path, idx, r["term_uid"])}
            if r["is_source"]:
                t["sinks"] = [peer(x) for x in others if not x["is_source"]]
            else:
                src = [peer(x) for x in others if x["is_source"]]
                t["source"] = src if src else "none"
                t["wire_without_source_row"] = bool(w and not src)
            terms.append(t)
        ins = [t for t in terms if t["dir"] == "input"]
        out.append({"uid": u, "in_objs": u in in_objs, "n_terminal_rows": len(ts), "frame_diagrams": diags,
                    "container": chain_up(gr, diags[0]) if diags else [], "terminals": terms,
                    "n_inputs": len(ins), "has_unwired_input": any(t["source"] == "none" for t in ins),
                    "output_sinks": sum(len(t.get("sinks") or []) for t in terms if t["dir"] == "output")})
    return {"nodes": out, "dedupe": rec}


def graph4(gr):
    return V.build4(gr["terminals"], gr.get("objs"), gr.get("loops"), {}, gr.get("fs_tunnel_pairs"))


def step(G, key, gr_path, idx):
    r = G["rows"][key]
    return {"key": key, "term_uid": r["term_uid"], "term_name": r["term_name"], "owner_uid": r["owner_uid"], "owner_class": r["owner_class"],
            "term_class": r.get("term_class"), "node_class": G["cls"].get(r["node"]), "is_source": bool(r["is_source"]),
            "wire_uid": int(r["wire_uid"] or 0), "row": cite(gr_path, idx, r["term_uid"])}


def sink_class(st, has_out):
    """The brief's step-3 class of ONE reached terminal (definitions in brief_168-a1-1.md:31-33)."""
    nm = (st["term_name"] or "").lower() + " " + (st["owner_class"] or "").lower()
    if st["term_class"] == V.FP_CLASS and not st["is_source"] and not has_out:
        return "display-only"
    if st["term_class"] == V.FP_CLASS and not st["is_source"]:
        return "indicator-with-outflow"
    if any(w in nm for w in SAVE_WORDS):
        return "save"
    if any(w in nm for w in CONTROL_WORDS):
        return "control"
    return "compute"


def downstream(gr, gr_path):
    """Every terminal reachable from #11261 t11267, the leaves, the chain to each, the class per sink and overall."""
    G, idx = graph4(gr), first_index(gr)
    starts = V.terminals(G, term_uid=T_OUT)
    reached = sorted(V.reach4(G, starts)) if starts else []
    leaves = [k for k in reached if not G["out"].get(k)]
    sinks = []
    for k in leaves:
        p = V.path(G, starts[0], k)
        kinds = []
        for a, b in zip(p, p[1:]):
            kinds.append(next((e[0] for e in G["out"].get(a, ()) if e[1] == b), "?"))
        st = step(G, k, gr_path, idx)
        sinks.append({"leaf": st, "class": sink_class(st, bool(G["out"].get(k))),
                      "chain": [step(G, x, gr_path, idx) for x in p], "edge_kinds": kinds})
    allc = [sink_class(step(G, k, gr_path, idx), bool(G["out"].get(k))) for k in reached]
    rows = list(G["rows"].values())
    lab = None
    if leaves:
        lab = G["rows"][leaves[0]]["term_name"]
    same_label = [{"term_uid": r["term_uid"], "owner_uid": r["owner_uid"], "owner_class": r["owner_class"], "is_source": bool(r["is_source"]),
                   "term_class": r.get("term_class"), "wire_uid": int(r["wire_uid"] or 0), "row": cite(gr_path, idx, r["term_uid"])}
                  for r in rows if lab is not None and r["term_name"] == lab]
    over = ("none-reached" if not reached else "display-only" if set(allc) == {"display-only"} else
            "/".join(sorted(set(c for c in allc if c != "display-only"))))
    return {"start_keys": starts, "n_reached": len(reached), "reached": [step(G, k, gr_path, idx) for k in reached],
            "class_of_each_reached": allc, "sinks": sinks, "overall": over, "leaf_label_rows": same_label,
            "graph_method": {"wire_edges": G["method"]["wire_edges"], "local": G["method"].get("local"), "global": G["method"].get("global"),
                             "fs_tunnel": {k: G["method"]["fs_tunnel"].get(k) for k in ("rule", "edges")}}}


def node_terms(gr, gr_path, uid):
    rows, _ = V.dedupe_rows(gr["terminals"])
    idx = first_index(gr)
    by_wire = collections.defaultdict(list)
    for r in rows:
        r["wire_uid"] and by_wire[r["wire_uid"]].append(r)                                 # noqa: E701
    out = []
    for r in sorted((r for r in rows if r["owner_uid"] == uid), key=lambda r: r["term_uid"]):
        w = int(r["wire_uid"] or 0)
        out.append({"term_uid": r["term_uid"], "term_name": r["term_name"], "is_source": bool(r["is_source"]), "wire_uid": w,
                    "row": cite(gr_path, idx, r["term_uid"]),
                    "other_ends": [{"term_uid": x["term_uid"], "term_name": x["term_name"], "owner_uid": x["owner_uid"],
                                    "owner_class": x["owner_class"], "term_class": x.get("term_class"), "is_source": bool(x["is_source"]),
                                    "row": cite(gr_path, idx, x["term_uid"])}
                                   for x in by_wire.get(w, []) if x["term_uid"] != r["term_uid"]]})
    return out


def wire_objs(gr):
    return sum(1 for o in gr["objs"] if o["class"] == "Wire")


def main():
    gate = L.Gate(fatal_default=False)
    res = {"card": "168-a1-1", "source": "tools/bench/diag_c168_a1_1_ba.py", "graphs": {}, "census": {}, "node_11261": {}, "downstream": {}}
    grs = {}
    for tag, p, pin in GRAPHS:
        m = L.md5(os.path.join(ROOT, p))
        gate("P1 {0} graph {1} md5 {2} vs {3}".format(tag, os.path.basename(p), m, pin), m.startswith(pin), "equal" if m.startswith(pin) else "UNEQUAL")
        grs[tag] = json.load(open(os.path.join(ROOT, p), encoding="utf-8"))
        res["graphs"][tag] = {"path": p, "md5": m, "wire_objs": wire_objs(grs[tag]), "n_terminal_rows": len(grs[tag]["terminals"]),
                              "wire_uids_in_rows": len(set(r["wire_uid"] for r in grs[tag]["terminals"] if r["wire_uid"]))}
    for tag, p, _pin in GRAPHS:
        res["census"][tag] = census(grs[tag], p)
        res["node_11261"][tag] = node_terms(grs[tag], p, NODE)
        res["downstream"][tag] = downstream(grs[tag], p)
    # side-by-side table
    table = collections.OrderedDict()
    for tag in ("before", "after"):
        for n in res["census"][tag]["nodes"]:
            table.setdefault(n["uid"], {})[tag] = n
    res["table"] = []
    for u, d in table.items():
        row = {"uid": u}
        for tag in ("before", "after"):
            n = d.get(tag)
            row[tag] = None if n is None else {
                "container": n["container"], "has_unwired_input": n["has_unwired_input"], "n_inputs": n["n_inputs"],
                "unwired_inputs": ["t{0} {1!r}".format(t["term_uid"], t["term_name"]) for t in n["terminals"]
                                   if t["dir"] == "input" and t["source"] == "none"],
                "output_sinks": n["output_sinks"]}
        res["table"].append(row)
    for tag in ("before", "after"):
        ns = res["census"][tag]["nodes"]
        res["census"][tag]["with_unwired_input"] = [n["uid"] for n in ns if n["has_unwired_input"]]
        res["census"][tag]["all_inputs_wired"] = [n["uid"] for n in ns if not n["has_unwired_input"]]
        print("FACT {0}: BuildArray nodes {1}; with unwired input {2}; all wired {3}".format(
            tag, len(ns), res["census"][tag]["with_unwired_input"], res["census"][tag]["all_inputs_wired"]), flush=True)
    # P2 / P3 / P4
    for tag in ("before", "after"):
        tt = dict((t["term_uid"], t) for t in res["node_11261"][tag])
        empty = [u for u in T_IN if u in tt and not tt[u]["wire_uid"]]
        gate("P2 {0}: #11261 t11270 'array' and t11273 'element' have no wire/source".format(tag), len(empty) == 2,
             dict((u, (tt[u]["wire_uid"], tt[u]["row"])) for u in T_IN if u in tt))
    b2626 = [n for n in res["census"]["before"]["nodes"] if n["uid"] == 2626]
    gate("P3 before: every #2626 input wired", bool(b2626) and not b2626[0]["has_unwired_input"],
         b2626 and ["t{0} {1!r} <- {2}".format(t["term_uid"], t["term_name"], t["source"] if t["source"] == "none" else
                   ["t{0} #{1} {2}".format(s["term_uid"], s["owner_uid"], s["owner_class"]) for s in t["source"]])
                    for t in b2626[0]["terminals"] if t["dir"] == "input"])
    tb = dict((t["term_uid"], t) for t in res["node_11261"]["before"])
    ta = dict((t["term_uid"], t) for t in res["node_11261"]["after"])
    okb = tb.get(T_OUT, {}).get("wire_uid") == 25618 and [x["term_uid"] for x in tb[T_OUT]["other_ends"]] == [8323]
    gate("P4 before: t11267 w25618 -> t8323 only", okb, tb.get(T_OUT))
    gate("P4 after: t11267 carries no wire", ta.get(T_OUT, {}).get("wire_uid") == 0, ta.get(T_OUT))
    # delete prediction
    att = sorted(set(t["wire_uid"] for t in res["node_11261"]["after"] if t["wire_uid"]))
    wa = res["graphs"]["after"]["wire_objs"]
    res["delete_prediction"] = {"graph": "c5531708", "wires_attached_to_11261": [
        {"wire_uid": t["wire_uid"], "term": t["term_uid"], "other_ends": t["other_ends"]} for t in res["node_11261"]["after"] if t["wire_uid"]],
        "wire_objs_now": wa, "expected_wire_objs_after_delete": wa - len(att),
        "basis": "objs class Wire count of graph_ring_p6rbw_20261012_191349.json minus distinct wire uids on #11261 terminal rows"}
    gate("P5 after: Wire objects == 2066 (brief step 4)", wa == 2066, wa)
    for tag in ("before", "after"):
        d = res["downstream"][tag]
        print("FACT {0}: t11267 reach {1} keys, leaves {2}, overall {3}".format(
            tag, d["n_reached"], [(s["leaf"]["key"], s["class"]) for s in d["sinks"]], d["overall"]), flush=True)
        for s in d["sinks"]:
            print("FACT {0} chain: {1}".format(tag, " -> ".join("t{0} #{1} {2} {3!r} [{4}]".format(
                c["term_uid"], c["owner_uid"], c["node_class"], c["term_name"], c["row"]) for c in s["chain"])), flush=True)
        print("FACT {0}: rows sharing the leaf label: {1}".format(tag, d["leaf_label_rows"]), flush=True)
    print("FACT delete prediction: attached {0}; Wire objs {1} -> expected {2}".format(
        att, wa, res["delete_prediction"]["expected_wire_objs_after_delete"]), flush=True)
    json.dump(res, open(os.path.join(ROOT, OUT_JSON), "w", encoding="utf-8"), indent=1)
    write_md(res)
    arts = [{"path": p, "md5": L.md5(os.path.join(ROOT, p))} for p in (OUT_JSON, OUT_MD)]
    return gate.result(arts)


def write_md(res):
    o = ["# p6_buildarray - BuildArray census before/after RBW and the #11261 'appended array' path (card 168-a1-1)", "",
         "Source: `tools/bench/diag_c168_a1_1_ba.py` (offline, vigraph over the stored graphs). Data: `tools/bench/p6_buildarray.json`.",
         "Graphs: before = {0} ({1}), after = {2} ({3}). Type column: the graph stores no terminal type -> `unread`.".format(
             res["graphs"]["before"]["path"], res["graphs"]["before"]["md5"][:8], res["graphs"]["after"]["path"], res["graphs"]["after"]["md5"][:8]),
         "", "## 1. Census (every BuildArray node)", "",
         "| uid | container (before) | before: unwired inputs | after: unwired inputs | out sinks b/a |", "|---|---|---|---|---|"]
    for r in res["table"]:
        b, a = r["before"], r["after"]
        o.append("| #{0} | {1} | {2} | {3} | {4}/{5} |".format(
            r["uid"], " < ".join((b or a)["container"][:4]) if (b or a) else "", "absent" if b is None else (", ".join(b["unwired_inputs"]) or "all wired"),
            "absent" if a is None else (", ".join(a["unwired_inputs"]) or "all wired"),
            "-" if b is None else b["output_sinks"], "-" if a is None else a["output_sinks"]))
    for tag in ("before", "after"):
        c = res["census"][tag]
        o += ["", "**{0}**: with an unwired input {1}; all inputs wired {2}.".format(tag, c["with_unwired_input"], c["all_inputs_wired"])]
    o += ["", "### Inputs, per node (after = c5531708)", ""]
    for n in res["census"]["after"]["nodes"]:
        for t in n["terminals"]:
            src = t.get("source")
            o.append("- #{0} t{1} {2!r} {3} w{4} type {5}: {6} [{7}]".format(
                n["uid"], t["term_uid"], t["term_name"], t["dir"], t["wire_uid"], t["type"],
                ("source none" if src == "none" else "source " + "; ".join("t{0} {1!r} #{2} {3}".format(
                    s["term_uid"], s["term_name"], s["owner_uid"], s["owner_class"]) for s in src)) if t["dir"] == "input"
                else "sinks " + ("; ".join("t{0} {1!r} #{2} {3}".format(s["term_uid"], s["term_name"], s["owner_uid"], s["owner_class"])
                                           for s in t["sinks"]) or "none"), t["row"]))
    o += ["", "## 2. #11261 terminals", ""]
    for tag in ("before", "after"):
        for t in res["node_11261"][tag]:
            o.append("- {0}: t{1} {2!r} w{3} -> {4} [{5}]".format(tag, t["term_uid"], t["term_name"], t["wire_uid"],
                     ["t{0} {1!r} #{2} {3}/{4}".format(x["term_uid"], x["term_name"], x["owner_uid"], x["owner_class"], x["term_class"])
                      for x in t["other_ends"]] or "nothing", t["row"]))
    o += ["", "## 3. t11267 downstream (vigraph.build4 + reach4/path)", ""]
    for tag in ("before", "after"):
        d = res["downstream"][tag]
        o.append("- **{0}**: reached {1} terminal(s); overall class **{2}**.".format(tag, d["n_reached"], d["overall"]))
        for s in d["sinks"]:
            o.append("  - leaf class {0}; chain: {1}; edges {2}".format(s["class"], " -> ".join(
                "t{0} #{1} {2} {3!r} [{4}]".format(c["term_uid"], c["owner_uid"], c["node_class"], c["term_name"], c["row"]) for c in s["chain"]),
                s["edge_kinds"]))
        o.append("  - rows with the leaf's label: {0}".format(["t{0} #{1} {2}/{3} src={4} w{5}".format(
            x["term_uid"], x["owner_uid"], x["owner_class"], x["term_class"], x["is_source"], x["wire_uid"]) for x in d["leaf_label_rows"]]))
    dp = res["delete_prediction"]
    o += ["", "## 4. Delete prediction (c5531708)", "",
          "Wires attached to #11261: {0}. Wire objects now {1}; expected after deleting #11261: **{2}** ({3}).".format(
              [w["wire_uid"] for w in dp["wires_attached_to_11261"]] or "none", dp["wire_objs_now"], dp["expected_wire_objs_after_delete"], dp["basis"])]
    open(os.path.join(ROOT, OUT_MD), "w", encoding="utf-8").write("\n".join(o) + "\n")


if __name__ == "__main__":
    sys.exit(main())
