r"""diag_c91_t0_tunnels_offline - card 91-1 (A): PD197(h) tunnel sites, READ OFFLINE from the S1 wiki (no LabVIEW).

For every step-3 node that sits inside a For body or a case frame (Median #30306 in For body #29894; Median #29009 and
FIR #28233 in For body #7911; plot Z #6085 in case frame #2235; plot dZ #5696 in case frame #2265; circle #16788 and
text #16827 in For body #16621 inside case frame #16303), find the ENCLOSING structure's OUTPUT tunnels whose outer
terminal sits on the holding While body (#639 or #15266) and carries a wire. The stamp branches that wire (PD197(h):
"the ENCLOSING structure's output-tunnel wire on the While body").

FOUND FIRST (nothing new built): diag_c90_t0_sites_offline.py's wiki access (jev_candidates.load(S1_KEY): rec["terminals"]
rows owner_uid/owner_class/frame_diagram/wire_uid/is_source/term_class; rec["wires"] with n_sink; graph_objs for the
Diagram traverse index; diagram_tree from tunnel faces). TREE_OWNERS = LoopTunnel/Tunnel/SelectorTunnel/SRs.

PREDICTION CONTRACT: T1 each of the 7 nodes resolves to >= 1 output tunnel on its holding While body; T2 every chosen
wire is on #639 or #15266 (frame_diagram of the outer terminal == holding body) with n_sink >= 1; T3 for each node at
least one chosen tunnel is fed (directly or through nodes inside the structure) by that node's outputs, i.e. the
tunnel measures the node's completion; T4 the chosen wires are distinct from the 8 While-body site wires; T5 rows == 7.
Output: tools/bench/t0_tunnel_sites_s1.json. RESULT line last (C6).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c91_t0_tunnels_offline.log -- py -u tools/bench/diag_c91_t0_tunnels_offline.py
"""
import collections, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402
import jev_candidates as JC  # noqa: E402

OUT = os.path.join(HERE, "t0_tunnel_sites_s1.json")
# (site id, node uid, label, innermost structure body diagram, holding While body, holding While uid, its Diagram index)
NODES = [(3, 30306, "Median #30306", 29894, 639, 637, 43), (4, 29009, "Median #29009", 7911, 639, 637, 43),
         (5, 28233, "FIR #28233", 7911, 639, 637, 43), (6, 6085, "plot Z #6085", 2235, 639, 637, 43),
         (7, 5696, "plot dZ #5696", 2265, 639, 637, 43), (16, 16788, "circle #16788", 16621, 15266, 15173, 99),
         (17, 16827, "text #16827", 16621, 15266, 15173, 99)]
WHILE_SITE_WIRES = {3268, 5859, 541, 19372, 19465, 19468, 19429, 34066}
P, F, facts = [], [], []


def gate(label, ok, detail=""):
    (P if ok else F).append(label); print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, detail), flush=True)


G = JC.load(JC.S1_KEY)
rec, objs, by_node, tree = G["wiki"], G["objs"], G["by_node"], G["tree"]
diag_objs = [o for o in json.load(open(JC._newest("graph_objs_s1_*.json"), encoding="utf-8"))["objects"] if o["class"] in ("Diagram", "TopLevelDiagram")]
diag_index = {int(o["uid"]): i for i, o in enumerate(diag_objs)}
terms = rec["terminals"]
wires = {int(w["wire_uid"]): w for w in rec["wires"]}
print("  SCHEMA terminal row keys %r" % sorted(terms[0].keys()), flush=True)
print("  SCHEMA wire row keys %r" % sorted(next(iter(wires.values())).keys()), flush=True)
by_term = {int(r["term_uid"]): r for r in terms}
# wire -> source terminal rows / sink terminal rows (from the terminal table itself; wires[] n_sink cross-checks it)
w_src, w_sink = collections.defaultdict(list), collections.defaultdict(list)
for r in terms:
    if r.get("wire_uid"):
        (w_src if r["is_source"] else w_sink)[int(r["wire_uid"])].append(r)
# structure tunnels: owner uid -> rows, only tree owners
tunnels = collections.defaultdict(list)
for r in terms:
    if r["owner_class"] in JC.TREE_OWNERS:
        tunnels[int(r["owner_uid"])].append(r)


def frames_between(inner, holding):
    """Every diagram from `inner` up to (excluding) `holding` along the tunnel tree - the structures a stamp must clear."""
    ch = JC._ancestors(tree, inner)
    return ch[:ch.index(holding)] if holding in ch else None


def reach_from_node(node_uid, inside):
    """Terminal-level forward reach from node_uid's outputs, walking wires -> sink terminals -> owner node's outputs,
    restricted to owner nodes whose rows sit on diagrams in `inside`. Returns the set of wire uids reached."""
    seen_w, seen_n, todo = set(), set(), [node_uid]
    while todo:
        n = todo.pop()
        if n in seen_n:
            continue
        seen_n.add(n)
        for r in by_node.get(n, []):
            if not r["is_source"] or not r.get("wire_uid"):
                continue
            if r.get("frame_diagram") and int(r["frame_diagram"]) not in inside:
                continue
            w = int(r["wire_uid"]); seen_w.add(w)
            for s in w_sink.get(w, []):
                todo.append(int(s["owner_uid"]))
    return seen_w


rows = []
for site, nu, label, inner, holding, loop_uid, hidx in NODES:
    fb = frames_between(inner, holding)
    facts.append("%s: inner #%d -> holding #%d frames between %r (owners %r)" % (label, inner, holding, fb, [objs.get(d, {}).get("owner") for d in (fb or [])]))
    print("  FACT  " + facts[-1], flush=True)
    outs = []
    if fb:
        outermost = fb[-1]                                  # the structure whose outer face sits on the holding body
        inside = set(fb)
        reached = reach_from_node(nu, inside)
        for tu, trs in tunnels.items():
            inner_rows = [r for r in trs if r["term_class"] == "InnerTerminal" and r.get("frame_diagram") and int(r["frame_diagram"]) in inside]
            outer_rows = [r for r in trs if r["term_class"] == "OuterTerminal" and r.get("frame_diagram") and int(r["frame_diagram"]) == holding and r["is_source"] and r.get("wire_uid")]
            if not inner_rows or not outer_rows:
                continue
            if not any(int(r["frame_diagram"]) == outermost for r in inner_rows):
                continue
            o = outer_rows[0]; w = int(o["wire_uid"])
            fed = any(int(r["wire_uid"] or 0) in reached for r in inner_rows if not r["is_source"])
            outs.append({"tunnel_uid": tu, "tunnel_class": o["owner_class"], "outer_term_uid": int(o["term_uid"]), "outer_frame": holding,
                         "wire_uid": w, "n_sink": wires.get(w, {}).get("n_sink", len(w_sink.get(w, []))),
                         "n_src_rows": len(w_src.get(w, [])), "fed_by_node": fed,
                         "inner_frames": sorted(set(int(r["frame_diagram"]) for r in inner_rows))})
    outs.sort(key=lambda x: (not x["fed_by_node"], x["wire_uid"]))
    chosen = next((x for x in outs if x["fed_by_node"]), outs[0] if outs else None)
    rows.append({"site": site, "node_uid": nu, "label": label, "inner_diagram": inner, "holding_body": holding, "holding_loop": loop_uid,
                 "holding_body_index": hidx, "frames_between": fb, "output_tunnels": outs, "chosen": chosen})
    facts.append("%s: %d output tunnel(s) on #%d: %r; CHOSEN %r" % (label, len(outs), holding, [(x["tunnel_uid"], x["wire_uid"], x["fed_by_node"], x["n_sink"]) for x in outs], (chosen or {}).get("wire_uid")))
    print("  FACT  " + facts[-1], flush=True)
gate("T1 each of the 7 nodes resolves to >= 1 output tunnel on its holding While body", all(r["chosen"] for r in rows), repr([(r["site"], bool(r["chosen"])) for r in rows]))
gate("T2 every chosen wire has its outer terminal on the holding body and n_sink >= 1",
     all(r["chosen"] and r["chosen"]["outer_frame"] == r["holding_body"] and (r["chosen"]["n_sink"] or 0) >= 1 for r in rows))
gate("T3 every chosen tunnel is fed by its node's outputs (measures the node's completion)", all(r["chosen"] and r["chosen"]["fed_by_node"] for r in rows),
     repr([(r["site"], (r["chosen"] or {}).get("fed_by_node")) for r in rows]))
chosen_w = [r["chosen"]["wire_uid"] for r in rows if r["chosen"]]
gate("T4 chosen wires are distinct from the 8 While-body site wires", not (set(chosen_w) & WHILE_SITE_WIRES), repr(sorted(set(chosen_w) & WHILE_SITE_WIRES)))
gate("T5 rows == 7", len(rows) == 7)
facts.append("SHARED wires (two nodes on one tunnel): %r" % [w for w, c in collections.Counter(chosen_w).items() if c > 1])
print("  FACT  " + facts[-1], flush=True)
json.dump({"input": rec.get("file"), "input_md5": rec.get("md5"), "source": "docs/wiki/subvi/D1_s1_copy.json (offline)", "rows": rows,
           "facts": facts, "gates": {"pass": P, "fail": F}}, open(OUT, "w", encoding="utf-8"), indent=1)
print("=== GATES: %d pass / %d fail%s" % (len(P), len(F), ("; failing: " + ", ".join(F)) if F else ""))
print(protocol.result_line(protocol.make_result(len(P), len(F), F[0] if F else None, [{"path": OUT}])))
sys.exit(0 if not F else 1)
