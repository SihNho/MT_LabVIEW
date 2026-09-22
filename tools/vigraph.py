r"""vigraph - the block diagram as a NODE-LEVEL graph, in pure Python. No LabVIEW, no model.

`docs/connectivity-map-plan.md` step 4 owns the full graph (frame-indexed tunnels, `Shift Registers[]`
pairing, diff vs the original). THIS FILE IS THE MINIMAL WALKER step 3 needs and step 4 EXTENDS - it is
deliberately an OVER-approximation of reachability, and every approximation is named in `method` so a
caller can print it instead of believing it.

INPUT is exactly what `tools/allterms.py` returns:
    terms  [{term_uid, term_name, is_source, wire_uid, owner_uid, owner_class}]   (read_terms)
    wires  [{wire_uid, src_uid, sink_uid, ..., termless}]                         (join_wires)
    objs   [{uid, class, pos, owner}] from gscript.report_all(vi, <class>)  - OPTIONAL, only used for
           shift-register / flat-sequence-tunnel pairing, which needs POSITIONS.

EDGES, and what each one is worth:
  1 WIRE            src owner node -> every sink owner node. EXACT (it is the wire's own terminal rows).
  2 NODE PASS-THROUGH  every input terminal of a node reaches every output terminal of that node. An
    OVER-approximation for a real function, and EXACT for a single-object tunnel (a LoopTunnel or
    SelectorTunnel carries its outside and inside terminals under ONE uid, so 1+2 already crosses the
    structure border with no extra rule).
  3 SHIFT REGISTER  RightShiftRegister -> LeftShiftRegister, paired by EQUAL y (LabVIEW puts a pair on
    the two edges of the same loop at the same y). HEURISTIC: `method['sr']` reports paired/unpaired.
    Step 4 replaces it with `Loop.Shift Registers[]`.
  4 FLAT SEQUENCE   FlatSequenceOuterTunnel <-> FlatSequenceInnerTunnel, paired by equal y, nearest x.
    Same heuristic, same caveat; `OpTunnels_v0.Inner Terminals[]` is step 4's exact route.
  5 LOCAL / GLOBAL  every `Local` (or `Global`) node that is a SINK reaches every same-named one that is
    a SOURCE. Name-keyed, within ONE VI (cross-VI globals are step 4's).

NOT MODELLED (so `io_paths` is an over-approximation, never an under-one): case-frame selection, error
clusters as control flow, sequence ORDER, and the difference between reading a shift register before and
after it is written. For a WIKI - "which inputs can reach this output" - over-approximating is the safe
direction; for a rule-1a diff it is not, which is why step 4 exists.

    import vigraph
    G = vigraph.build(terms, wires, objs)
    vigraph.reach(G, start_uids)            -> set of node uids
    vigraph.io_paths(G, terms, conpane)     -> {output label: [input labels]}
"""
import collections

# MEASURED, not assumed (`tools/bench/diag_wiki_probe2.log`, 2026-09-23, full row dump of two VIs):
#   * `Traverse('Terminal')` is INCLUSIVE of its subclasses, and a row's LEAF class comes only from a
#     `report_all(vi,'GObject')` join on term_uid. wiki_build puts it on the row as `term_class`.
#   * a FRONT-PANEL terminal has leaf class `ControlTerminal` and its OWNER is the TopLevelDiagram, so
#     every one of them would collapse into ONE graph node if keyed on owner_uid. They are keyed on
#     `term_uid` instead, and are their own nodes.
#   * a LOOP tunnel is ONE object: `LoopTunnel`/`Tunnel` #311 owns BOTH `OuterTerminal` #310 and
#     `InnerTerminal` #313, so rules 1+2 alone already cross a loop border exactly - no tunnel rule needed.
#     A FLAT SEQUENCE tunnel is NOT: outer and inner are separate objects (116 vs 1036 on the D1 bed).
#   * `GObject.Position` is (LEFT, TOP): ForLoop #248 at (90,48) has tunnels at (90,48), (90,162) on its
#     left edge and (284,92) on its right. So a left/right PAIR shares pos[1], which is what rules 3 and 4
#     match on.
FP_CLASS = "ControlTerminal"
SR_R, SR_L = "RightShiftRegister", "LeftShiftRegister"
FS_OUT, FS_IN = "FlatSequenceOuterTunnel", "FlatSequenceInnerTunnel"


def node_of(row):
    """The GRAPH NODE a terminal row belongs to: its owner, except a front-panel terminal, which is its
    own node (its owner is the whole TopLevelDiagram - see the measurement note above)."""
    return row["term_uid"] if row.get("term_class") == FP_CLASS else row["owner_uid"]


def node_class(row):
    return FP_CLASS if row.get("term_class") == FP_CLASS else row["owner_class"]


def build(terms, wires, objs=None):
    """{adj, nodes, cls, method} - a directed node-uid graph. Pure; no LabVIEW, no mutation of the input."""
    adj = collections.defaultdict(set)
    cls = {}
    for r in terms:
        cls.setdefault(node_of(r), node_class(r))
    method = {"wires": 0, "pass_through": "all inputs -> all outputs of the same node"}

    # 1 WIRE. Rebuilt from the terminal rows rather than from `wires`, because join_wires keeps only the
    #   FIRST source and FIRST sink while a wire may have several sinks (n_sink up to 2+ on the bed).
    by_wire = collections.defaultdict(list)
    for r in terms:
        if r["wire_uid"]:
            by_wire[r["wire_uid"]].append(r)
    for wire_uid, rows in by_wire.items():
        srcs = [node_of(r) for r in rows if r["is_source"]]
        snks = [node_of(r) for r in rows if not r["is_source"]]
        for a in srcs:
            for b in snks:
                if a != b:
                    adj[a].add(b)
                    method["wires"] += 1

    # 3/4 need positions, which only a GObject census carries.
    pos = {}
    for o in (objs or []):
        try:
            pos[int(o["uid"])] = tuple(o["pos"])
        except Exception:                                                          # noqa: BLE001
            pass

    def pair_by_y(a_cls, b_cls):
        a = [u for u, c in cls.items() if c == a_cls and u in pos]
        b = [u for u, c in cls.items() if c == b_cls and u in pos]
        by_y = collections.defaultdict(list)
        for u in b:
            by_y[round(pos[u][1])].append(u)      # pos = (LEFT, TOP); a left/right pair shares TOP
        out, missed = [], 0
        for u in a:
            cand = by_y.get(round(pos[u][1]), [])
            if not cand:
                missed += 1
                continue
            for v in cand:
                out.append((u, v))
        return out, missed, len(a)

    sr_pairs, sr_missed, sr_n = pair_by_y(SR_R, SR_L)
    for r, l in sr_pairs:
        adj[r].add(l)
    method["sr"] = {"right": sr_n, "paired": len(sr_pairs), "unpaired_right": sr_missed,
                    "rule": "equal TOP (pos[1]); step 4 replaces with Shift Registers[]"}

    fs_pairs, fs_missed, fs_n = pair_by_y(FS_OUT, FS_IN)
    for o, i in fs_pairs:
        adj[o].add(i)
        adj[i].add(o)
    method["fs_tunnel"] = {"outer": fs_n, "paired": len(fs_pairs), "unpaired_outer": fs_missed,
                           "rule": "equal TOP (pos[1]); step 4 replaces with Inner Terminals[]"}

    # 5 LOCAL / GLOBAL by name.
    for kind in ("Local", "Global"):
        by_name = collections.defaultdict(lambda: ([], []))
        for r in terms:
            if r["owner_class"] == kind:
                by_name[r["term_name"]][0 if r["is_source"] else 1].append(r["owner_uid"])
        # `by_name` values are (sources=readers, sinks=writers): a Local that is a SOURCE is a READ.
        n = 0
        for _name, (readers, writers) in by_name.items():
            for w in writers:
                for rd in readers:
                    if w != rd:
                        adj[w].add(rd)
                        n += 1
        method[kind.lower()] = n

    nodes = set(cls) | set(adj) | {v for s in adj.values() for v in s}
    return {"adj": {k: sorted(v) for k, v in adj.items()}, "nodes": sorted(nodes), "cls": cls,
            "method": method}


def reach(graph, starts):
    """Every node uid reachable from `starts` (node-level, forward)."""
    adj, seen, stack = graph["adj"], set(), list(starts)
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        stack.extend(adj.get(u, ()))
    return seen


def fp_terminals(terms):
    """The VI's own front-panel control/indicator terminals: leaf class `ControlTerminal`.

    [{term_uid, label, direction}] - 'input' for a CONTROL (a source on the diagram), 'output' for an
    INDICATOR (a sink). Measured: 4 on `rect coord from center.vi` and they are exactly its 4 connector
    pane terminals (`tools/bench/diag_wiki_probe2.log`).
    """
    return [{"term_uid": r["term_uid"], "label": r["term_name"],
             "direction": "output" if not r["is_source"] else "input"}
            for r in terms if r.get("term_class") == FP_CLASS]


def io_paths(graph, terms, labels_in=None, labels_out=None):
    """{output label: [input labels that can reach it]} over the front-panel terminals.

    `labels_in`/`labels_out` restrict the answer to the CONNECTOR PANE (pass the conpane table's labels);
    omit them for every front-panel control/indicator. A terminal object on the diagram IS its own node
    (its owner is the Diagram), so the walk starts and ends on `term_uid`.
    """
    fps = fp_terminals(terms)
    ins = [t for t in fps if t["direction"] == "input" and (labels_in is None or t["label"] in labels_in)]
    outs = [t for t in fps if t["direction"] == "output" and (labels_out is None or t["label"] in labels_out)]
    out_uids = {}
    for t in outs:
        out_uids.setdefault(t["term_uid"], t["label"])
    result = collections.defaultdict(set)
    for t in ins:
        for uid in reach(graph, [t["term_uid"]]):
            if uid in out_uids:
                result[out_uids[uid]].add(t["label"])
    return dict((k, sorted(v)) for k, v in result.items())
