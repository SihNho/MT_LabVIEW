r"""jev_candidates.py - connectivity-map plan STEP 5, part A: EVERY legal terminal pair for an intent row.

PYTHON ONLY, NO JUDGEMENT, NO MODEL, NO LabVIEW (Pre-decided 134/136, docs/connectivity-map-plan.md). Given an
intent row {src, dst, hints, scope, replace} it lists every (source terminal, sink terminal) pair that the HARD
FACTS allow, with no ranking and no truncation. The hints are carried through for Jev (tools/jev_pairs.py) and
are NEVER used to filter here - filtering by a name is ranking, and ranking is Jev's.

HARD FACTS (each one a column the caller can print):
  direction   src terminal is_source == True, dst terminal is_source == False                      (filter)
  sink free   dst terminal wire_uid == 0, OR its wire has NO source terminal (a severed half-wire -
              `vigraph` flags n_src == 0), OR the intent says replace=True                         (filter)
  scope       the two terminals' frame_diagram (OpAllTerms_v1 7th column) related in the DIAGRAM TREE:
              same | nested (ancestor/descendant) | cousins (common ancestor) | exclusive (two frames of
              ONE case structure - never both executed) | unknown (the tree does not connect them)
              `exclusive` is the only scope that is FILTERED; `unknown` is kept and marked            (filter)
  type        only where the wiki has one; every wiki `type` read so far is "" -> "unknown"       (column)
  cycle       dst node already reaches src node through the graph (vigraph.reach4, an OVER-approx)  (column)

DIAGRAM TREE: built from the single-object tunnels (LoopTunnel / Tunnel / SelectorTunnel / Left|Right
ShiftRegister): their OuterTerminal sits on the PARENT diagram, every InnerTerminal on a CHILD (frame) diagram,
measured on the bed (tools/bench/vigraph_check.log; #11263 outer on 23058, inners on 10417/10423). A structure
with no such tunnel does not appear in the tree -> `unknown`. Flat-sequence frames are not added (their tunnels
are two objects and vigraph pairs only 23 of 58 outers - the step-4 KNOWN LIMIT).

NODE RESOLUTION (an intent end may be): an int uid of a graph node; {"structure": uid} = every terminal owned by
that structure's border tunnels (HEURISTIC, named in the output: the tunnel group sharing inner frames that has a
member at the structure's own left x); {"subvi": "<name fragment>"} = every SubVI call node whose wiki
`subvi_calls` name matches.

PRIOR ART CHECKED (2026-09-23): tools/vigraph.py (build4/terminals/reach4/effective_sources - used, not edited;
a parallel session edits it), tools/bench/diag_vigraph_check.py (its `load()` shape is copied, not imported,
because that module pins today's DATE), tools/jev_rowcheck.py (checks a planned row, does not enumerate),
tools/allterms.py (the reader). Nothing in the tree enumerated candidate pairs before this file.

    import jev_candidates as JC
    G = JC.load("D1_s3b_m3a3b_rowD_20260922_161040")
    rows = JC.candidates(G, {"src": 4344, "dst": 48, "dst_hint": "VISA resource name", "replace": True})
"""
import collections
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(HERE, "bench")
WIKI = os.path.join(ROOT, "docs", "wiki", "subvi")
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import vigraph as V  # noqa: E402

BED_KEY = "D1_s3b_m3a3b_rowD_20260922_161040"
S1_KEY = "D1_s1_copy"
TREE_OWNERS = ("LoopTunnel", "Tunnel", "SelectorTunnel", "LeftShiftRegister", "RightShiftRegister")


def _newest(pattern):
    hits = sorted(glob.glob(os.path.join(BENCH, pattern)))
    return hits[-1] if hits else None


def node_labels_default():
    labels = {}
    p = os.path.join(BENCH, "main_vi_node_labels.json")
    if os.path.exists(p):
        for _d, rows in json.load(open(p, encoding="utf-8")).get("diagrams", {}).items():
            for x in rows:
                labels[int(x["uid"])] = x.get("label", "")
    return labels


def load(key, fs=True):
    """The step-4 graph of one wiki VI, built exactly as tools/bench/diag_vigraph_check.py builds it
    (wiki terminals + the newest graph_objs/graph_loops census + main_vi_node_labels), plus the wiki record.
    fs=True (2026-09-23, step 5b): the wiki's STEP-4b `fs_tunnel_pairs` are passed to build4, so flat-sequence
    edges are the EXACT machine faces; before this the loader silently built the step-4 HEURISTIC fs edges
    (measured by tools/bench/bench_map_20260923/a4_units.py: R1/R2 sequence-crossing paths 0/2 without them)."""
    rec = json.load(open(os.path.join(WIKI, key + ".json"), encoding="utf-8"))
    tag = "s1" if key == S1_KEY else "bed"
    objs_p, loops_p = _newest("graph_objs_{0}_*.json".format(tag)), _newest("graph_loops_{0}_*.json".format(tag))
    objs = json.load(open(objs_p, encoding="utf-8"))["objects"] if objs_p else []
    loops = json.load(open(loops_p, encoding="utf-8"))["loops"] if loops_p else None
    return from_parts(rec, objs, loops, node_labels_default(), rec.get("fs_tunnel_pairs") if fs else None, key)


def from_parts(rec, objs, loops, labels, fs_pairs, key):
    """The same graph from parts already in memory (a LIVE read of a scratch VI: `rec` needs `terminals` and,
    for the subVI-name map, `graph_summary.subvi_calls`)."""
    G = V.build4(rec["terminals"], objs, loops, labels, fs_pairs)
    G["wiki"] = rec
    G["key"] = key
    G["objs"] = dict((int(o["uid"]), o) for o in objs)
    G["tree"] = diagram_tree(G)
    G["subvi_name"] = dict((int(c["node_uid"]), c["subvi_name"])
                           for c in rec.get("graph_summary", {}).get("subvi_calls", []))
    G["halfwire_nosrc"] = set(int(f["wire_uid"]) for f in G["flags"] if f["n_src"] == 0)
    G["_reach"] = {}
    return G


def diagram_tree(G):
    """{parent: {child: parent}, exclusive: {frame: frozenset(sibling frames of the same case)}}."""
    parent, votes, exclusive = {}, collections.defaultdict(collections.Counter), {}
    for node, rows in G["by_node"].items():
        if G["cls"].get(node) not in TREE_OWNERS:
            continue
        outer = [int(r["frame_diagram"]) for r in rows if r["term_class"] == "OuterTerminal" and r.get("frame_diagram")]
        inner = set(int(r["frame_diagram"]) for r in rows if r["term_class"] == "InnerTerminal" and r.get("frame_diagram"))
        for o in outer:
            for i in inner:
                if i != o:
                    votes[i][o] += 1
        if G["cls"].get(node) in ("SelectorTunnel", "Tunnel") and len(inner) > 1:
            for i in inner:
                exclusive[i] = frozenset(inner - {i}) | exclusive.get(i, frozenset())
    for child, c in votes.items():
        parent[child] = c.most_common(1)[0][0]
    return {"parent": parent, "exclusive": exclusive}


def _ancestors(tree, d):
    out, seen = [d], {d}
    while d in tree["parent"]:
        d = tree["parent"][d]
        if d in seen:
            break
        seen.add(d)
        out.append(d)
    return out


def scope(G, da, db):
    """(relation, borders) between two diagrams. borders = structure borders a wire would cross."""
    if not da or not db:
        return "unknown", None
    if da == db:
        return "same", 0
    t = G["tree"]
    if db in t["exclusive"].get(da, ()):
        return "exclusive", None
    aa, ab = _ancestors(t, da), _ancestors(t, db)
    if db in aa:
        return "nested", aa.index(db)
    if da in ab:
        return "nested", ab.index(da)
    common = [x for x in aa if x in set(ab)]
    if not common:
        return "unknown", None
    lca = common[0]
    ca, cb = aa[aa.index(lca) - 1], ab[ab.index(lca) - 1]
    if cb in t["exclusive"].get(ca, ()):
        return "exclusive", None
    return "cousins", aa.index(lca) + ab.index(lca)


def structure_terminals(G, struct_uid):
    """HEURISTIC: the border-tunnel group of a structure = tunnels sharing inner frames, the group chosen by a
    member at the structure's own left x. Returns (node uids, method string)."""
    so = G["objs"].get(int(struct_uid))
    if not so:
        return [], "structure uid not in the GObject census"
    groups = collections.defaultdict(set)
    for node, rows in G["by_node"].items():
        if G["cls"].get(node) not in ("SelectorTunnel", "Tunnel", "LoopTunnel", "LeftShiftRegister",
                                     "RightShiftRegister"):
            continue
        inner = frozenset(int(r["frame_diagram"]) for r in rows
                          if r["term_class"] == "InnerTerminal" and r.get("frame_diagram"))
        if inner:
            groups[inner].add(node)
    x, y = so["pos"][0], so["pos"][1]
    for inner, nodes in groups.items():
        if any(G["pos"].get(n, (None, None))[0] == x and G["pos"].get(n, (0, -1))[1] >= y for n in nodes):
            return sorted(nodes), "heuristic: tunnel group (inner frames {0}) with a member at left x={1}".format(
                sorted(inner), x)
    return [], "heuristic found no tunnel at the structure's left x"


def resolve(G, end):
    """An intent end -> ([node uids], method)."""
    if isinstance(end, int):
        return [end], "uid"
    if isinstance(end, dict) and "structure" in end:
        return structure_terminals(G, end["structure"])
    if isinstance(end, dict) and "subvi" in end:
        frag = end["subvi"].lower()
        return sorted(u for u, n in G["subvi_name"].items() if frag in n.lower()), "wiki subvi_calls name match"
    if isinstance(end, dict) and "nodes" in end:
        return [int(u) for u in end["nodes"]], "explicit node list"
    return [], "unresolvable end {0!r}".format(end)


def sink_state(G, r):
    w = r["wire_uid"]
    if not w:
        return "free"
    if w in G["halfwire_nosrc"]:
        return "half-wire"
    return "occupied"


TUNNEL_CLS = ("SelectorTunnel", "Tunnel", "LoopTunnel")


def cut_input_tunnel(G, node):
    """FACT RULE (judgement 2026-09-23 16:xx, measured by bench 5b B run 2): a Selector/Loop tunnel whose OUTER
    terminal reads as a SINK (is_source False = an input tunnel) with wire_uid 0 has had its outer feed cut; its
    INNER terminals then read as SINKS only because the damage removed their source - they are never a
    restoration target, so they are excluded as sinks."""
    if G["cls"].get(node) not in TUNNEL_CLS:
        return False
    outer = [G["rows"][k] for k in V.terminals(G, node=node) if G["rows"][k]["term_class"] == "OuterTerminal"]
    return bool(outer) and all((not r["is_source"]) and not r["wire_uid"] for r in outer)


def _reaches(G, a_node, b_node):
    if a_node not in G["_reach"]:
        G["_reach"][a_node] = set(V.key_parts(k)[0] for k in V.reach4(G, [a_node]))
    return b_node in G["_reach"][a_node]


def term_row(G, key):
    r = G["rows"][key]
    return {"key": key, "uid": r["node"], "term": r["term_name"], "term_uid": r["term_uid"],
            "term_class": r["term_class"], "owner_class": G["cls"].get(r["node"]),
            "diagram": int(r.get("frame_diagram") or 0), "wire_uid": r["wire_uid"],
            "subvi": G["subvi_name"].get(r["node"])}


def candidates(G, intent):
    """Every legal pair for ONE intent row. Returns {intent, resolved, pairs:[...], excluded:{reason: n}}."""
    srcs, m_src = resolve(G, intent["src"])
    dsts, m_dst = resolve(G, intent["dst"])
    replace = bool(intent.get("replace"))
    excluded = collections.Counter()
    pairs = []
    s_keys = [k for u in srcs for k in V.terminals(G, node=u, is_source=True)]
    d_keys = [k for u in dsts for k in V.terminals(G, node=u, is_source=False)]
    for sk in s_keys:
        s = term_row(G, sk)
        for dk in d_keys:
            d = term_row(G, dk)
            if s["uid"] == d["uid"]:
                excluded["same node"] += 1
                continue
            if d["term_class"] == "InnerTerminal" and cut_input_tunnel(G, d["uid"]):
                excluded["inner terminal of an input tunnel whose outer feed is cut"] += 1
                continue
            st = sink_state(G, G["rows"][dk])
            if st == "occupied" and not replace:
                excluded["sink occupied"] += 1
                continue
            rel, borders = scope(G, s["diagram"], d["diagram"])
            if rel == "exclusive":
                excluded["exclusive case frames"] += 1
                continue
            pairs.append({"row_key": {"src_uid": s["uid"], "src_term": s["term"], "src_term_class": s["term_class"],
                                      "dst_uid": d["uid"], "dst_term": d["term"], "dst_term_class": d["term_class"]},
                          "src": s, "dst": d, "sink_state": st, "scope": rel, "borders": borders,
                          "type": "unknown (wiki type column empty)",
                          "cycle_overapprox": _reaches(G, d["uid"], s["uid"])})
    return {"intent": intent, "resolved": {"src": srcs, "src_method": m_src, "dst": dsts, "dst_method": m_dst},
            "n_src_terms": len(s_keys), "n_dst_terms": len(d_keys), "pairs": pairs, "excluded": dict(excluded)}


def map_key(G, key_other, G_other):
    """The key in G of a terminal named by `key_other` in another graph (Pre-decided 137: node uid + terminal
    name). Falls back to node uid + terminal class + direction when the name changed and that is unique -
    measured: LeftShiftRegister #4344's inner terminal is 'VISA out' in S1 and 'Outgoing Handle' in the bed."""
    if key_other in G["rows"]:
        return key_other, "same key"
    r = G_other["rows"][key_other]
    hits = [k for k in V.terminals(G, node=r["node"], cls=r["term_class"], is_source=r["is_source"])]
    if len(hits) == 1:
        return hits[0], "renamed: {0!r} -> {1!r}".format(r["term_name"], G["rows"][hits[0]]["term_name"])
    return None, "no unique match ({0} hits)".format(len(hits))


if __name__ == "__main__":
    G = load(BED_KEY)
    for it in ({"src": 4344, "dst": 48, "replace": True}, {"src": 23499, "dst": {"structure": 10407}}):
        c = candidates(G, it)
        print(json.dumps({k: v for k, v in c.items() if k != "pairs"}), len(c["pairs"]))
