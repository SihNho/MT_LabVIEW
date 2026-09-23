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
    """Every node uid reachable from `starts` (node-level, forward).

    Polymorphic since step 4: a graph from `build4()` carries `out`/`in` (TERMINAL-level) instead of
    `adj`, and is walked by `reach4()`. The step-3 callers (`wiki_build.io_paths`) are untouched.
    """
    if "adj" not in graph:
        return reach4(graph, starts)
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


# =====================================================================================================
# STEP 4 - THE FULL GRAPH: terminal-level edges, frame-exact tunnels, `Shift Registers[]` pairing,
# a diff keyed by (owner uid, terminal name), and a rule-1a `computation_diff`.
# `docs/connectivity-map-plan.md` step 4. Everything ABOVE this line is the step-3 walker and is
# UNCHANGED (wiki_build.py calls build/io_paths/fp_terminals and must keep working).
#
# A TERMINAL KEY is "<owner node uid>|<terminal leaf class>|<terminal name>|<ordinal>" - Pre-decided 137
# (node uid + terminal name), never a wire uid, which is transient. The ordinal is the rank of the
# terminal's OWN uid inside the group sharing (node, class, name), so it is stable while uids are.
#
# EDGE KINDS
#   wire   a wire's source terminal -> each of its sink terminals.        EXACT (the machine's rows)
#   thru   inside ONE owner object, every sink terminal -> every source terminal. EXACT for a tunnel
#          (a LoopTunnel/SelectorTunnel is ONE object owning its outer and its per-frame inner
#          terminals - measured, diag_wiki_probe2.log) and an OVER-approximation for a function or
#          subVI. DERIVED from the terminal list, so `diff` ignores it.
#   sr     RightShiftRegister -> its LeftShiftRegister: written this iteration, read the next.
#   fs     FlatSequenceOuterTunnel <-> FlatSequenceInnerTunnel, per FRAME (the two-object model).
#   local  a Local that WRITES -> every Local that READS the same label, and -> that control's own
#   global front-panel terminal node (same for Global, by name).
# =====================================================================================================

TUNNEL_OWNER = ("LoopTunnel", "Tunnel", "SelectorTunnel", "FlatSequenceOuterTunnel",
                "FlatSequenceInnerTunnel", "LeftShiftRegister", "RightShiftRegister")
DIAGRAM_OWNER = ("Diagram", "TopLevelDiagram", "FlatSequenceFrame")
STRUCT_OWNER = ("ForLoop", "WhileLoop", "TimedLoop", "CaseStructure", "FlatSequence", "Sequence",
                "EventStructure", "CycleSchedule")
# ASSUMPTION A (judgement, chat 2026-09-23) - what "scheduling" MEANS for the rule-1a diff. It is an
# ASSUMPTION: the plan's OPEN A is still open and the user has not ruled on it.
SCHED_OWNER = set(TUNNEL_OWNER) | set(DIAGRAM_OWNER) | set(STRUCT_OWNER) | {"Local", "Global"}
WAIT_LABEL = ("wait", "tick count", "time delay", "millisecond", "timer")


def _k(node, cls, name, ordinal):
    return "{0}|{1}|{2}|{3}".format(node, cls, name, ordinal)


def key_parts(key):
    node, cls, rest = key.split("|", 2)
    name, ordinal = rest.rsplit("|", 1)
    return int(node), cls, name, int(ordinal)


def show(key):
    node, cls, name, ordinal = key_parts(key)
    return "#{0} {1} {2}{3}".format(node, cls, repr(name) if name else "(unnamed)",
                                    "" if ordinal == 0 else " [{0}]".format(ordinal))


def build4(terms, objs=None, loops=None, labels=None, fs_pairs=None):
    """The full terminal-level graph. `terms` = OpAllTerms_v1 rows (the 7th column `frame_diagram` is
    REQUIRED for frame-exact sequence tunnels), each tagged with `term_class` (leaf class, from
    `objs`). `objs` = the GObject census (positions). `loops` = [{loop_uid, right_uids}] read from
    `Loop.Shift Registers[]` - the exact membership the pairing is VALIDATED against.
    `fs_pairs` = the wiki's `fs_tunnel_pairs` (STEP 4b: both faces of every flat-sequence tunnel READ by
    uid). When given, FS edges come from it EXACTLY; when absent, the step-4 heuristic runs."""
    pos, leaf = {}, {}
    for o in (objs or []):
        pos[int(o["uid"])] = tuple(o["pos"])
        leaf[int(o["uid"])] = o["class"]
    rows = []
    for r in terms:
        r = dict(r)
        if not r.get("term_class"):
            r["term_class"] = leaf.get(r["term_uid"], "")
        r["node"] = node_of(r)
        rows.append(r)

    groups = collections.defaultdict(list)
    for r in rows:
        groups[(r["node"], r["term_class"], r["term_name"])].append(r)
    for g_rows in groups.values():
        for i, r in enumerate(sorted(g_rows, key=lambda x: x["term_uid"])):
            r["key"] = _k(r["node"], r["term_class"], r["term_name"], i)

    cls, by_node, by_key = {}, collections.defaultdict(list), {}
    for r in rows:
        cls.setdefault(r["node"], node_class(r))
        by_node[r["node"]].append(r)
        by_key[r["key"]] = r

    edges, flags = [], []

    # --- 1 WIRE ---------------------------------------------------------------------------------
    by_wire = collections.defaultdict(list)
    for r in rows:
        if r["wire_uid"]:
            by_wire[r["wire_uid"]].append(r)
    for wire_uid in sorted(by_wire):
        w = by_wire[wire_uid]
        src = [r for r in w if r["is_source"]]
        snk = [r for r in w if not r["is_source"]]
        if len(src) != 1 or not snk:
            flags.append({"wire_uid": wire_uid, "n_src": len(src), "n_sink": len(snk),
                          "src": [r["key"] for r in src], "sink": [r["key"] for r in snk]})
        for a in src:
            for b in snk:
                edges.append(("wire", a["key"], b["key"], wire_uid))

    # --- 2 THRU (derived; `diff` ignores it) -----------------------------------------------------
    n_thru = 0
    for node, rs in by_node.items():
        if cls.get(node) in DIAGRAM_OWNER or cls.get(node) == FP_CLASS:
            continue                      # a diagram is not a data path; an FP terminal has one side
        if fs_pairs and cls.get(node) == FS_IN:
            continue                      # 4b: the traverse's OWNER for an FSIT row is wrong for half of
            #                               them (4 rows under one uid of a physical pair, 2 of them not
            #                               faces at all) - the exact `fs` edge below replaces `thru` here
        ins = [r for r in rs if not r["is_source"]]
        outs = [r for r in rs if r["is_source"]]
        for a in ins:
            for b in outs:
                edges.append(("thru", a["key"], b["key"], 0))
                n_thru += 1

    method = {"wire_edges": sum(1 for e in edges if e[0] == "wire"), "thru_edges": n_thru,
              "assumption_A": "scheduling = tunnels, shift registers, structures, diagrams, "
                              "Local/Global, Wait/timing labels (SCHED_OWNER)"}

    # --- 3 SHIFT REGISTERS ------------------------------------------------------------------------
    def body_diagram(node):
        """The diagram a tunnel-ish object's INNER terminal sits on (OpAllTerms_v1's 7th column)."""
        for r in by_node.get(node, ()):
            if "Inner" in (r["term_class"] or "") and r.get("frame_diagram"):
                return int(r["frame_diagram"])
        return 0

    rights = [u for u, c in cls.items() if c == SR_R]
    lefts = [u for u, c in cls.items() if c == SR_L]
    by_body = collections.defaultdict(lambda: ([], []))
    for u in rights:
        by_body[body_diagram(u)][0].append(u)
    for u in lefts:
        by_body[body_diagram(u)][1].append(u)
    # MACHINE PAIRS FIRST (cycle 68, 2026-09-24): `loops[i]["left_of"]` = {str(right uid): [left uid, ...]},
    # each list the RightShiftRegister's own `Left Registers[]` (gscript.shift_reg_left, OpShiftRegs_v1).
    # Keyed by uid, NOT parallel to `right_uids`, because stagekit.live_graph filters/appends right_uids.
    # Equal-TOP alone MIS-paired M4b: the new left #23796 shares TOP 2826 with #23880
    # (tools/bench/q_m4a_diffuid.log:94-99). TOP remains only for rights the machine table does not cover.
    machine, sr_mismatch = {}, []
    for L in (loops or []):
        for r, ls in (L.get("left_of") or {}).items():
            if not ls or int(r) not in cls:
                continue                     # unread, or a right retired from this file (live_graph filtering)
            ls = [ls] if isinstance(ls, int) else list(ls)
            ok = [int(x) for x in ls if cls.get(int(x)) == SR_L]
            if ok and len(ok) == len(ls):
                machine[int(r)] = ok
            else:
                sr_mismatch.append({"right": int(r), "left_uids": ls})
    sr_pairs, sr_unpaired = [], []
    for u, ls in sorted(machine.items()):
        for v in ls:
            sr_pairs.append((u, v))
    n_machine = len(sr_pairs)
    claimed = {v for ls in machine.values() for v in ls}
    for d, (rr, ll) in by_body.items():
        free = [v for v in ll if v not in claimed]
        for u in sorted([x for x in rr if x not in machine], key=lambda x: pos.get(x, (0, 0))[1]):
            same_y = [v for v in free if pos.get(v, (1, 1))[1] == pos.get(u, (0, 0))[1]]
            if len(same_y) != 1:
                sr_unpaired.append({"right": u, "body": d, "candidates": same_y})
                continue
            free.remove(same_y[0])
            sr_pairs.append((u, same_y[0]))
    for u, v in sr_pairs:
        for a in by_node[u]:
            if a["is_source"]:
                continue                                 # the body WRITES into the right register
            for b in by_node[v]:
                if b["is_source"]:                       # and READS it from the left one next round
                    edges.append(("sr", a["key"], b["key"], 0))
    prop = None
    if loops:
        want = set()
        for L in loops:
            want |= set(int(x) for x in L["right_uids"])
        mine = set(rights)
        split = [L["loop_uid"] for L in loops
                 if len({body_diagram(int(u)) for u in L["right_uids"]}) > 1]
        prop = {"from_shift_registers_property": len(want), "from_census": len(mine),
                "equal": want == mine, "only_in_property": sorted(want - mine)[:6],
                "only_in_census": sorted(mine - want)[:6],
                "loops_split_across_body_diagrams": split}
    method["sr"] = {"right": len(rights), "left": len(lefts), "paired": len(sr_pairs),
                    "paired_machine": n_machine, "paired_top": len(sr_pairs) - n_machine,
                    "machine_mismatch": sr_mismatch,
                    "unpaired": sr_unpaired, "shift_registers_property": prop,
                    "rule": "MACHINE (loops[].left_of = RightShiftRegister.Left Registers[]) where given; "
                            "else same loop BODY DIAGRAM (frame_diagram of the inner terminal) + equal TOP"}

    # --- 4 FLAT-SEQUENCE TUNNELS, per FRAME --------------------------------------------------------
    # MEASURED 2026-09-23 on D1_s1_copy, and it is NOT what the step-3 note assumed:
    #   * an FS tunnel's terminals have leaf class `Terminal`, NOT Outer/InnerTerminal (so the
    #     inner-terminal test used for shift registers cannot identify them);
    #   * ONE FS tunnel object carries terminals on SEVERAL frames - outer #14430 on frames
    #     {13236, 14435}, inner #14007 on {13236, 14037, 14435} - each with its own wire;
    #   * only 22 of 114 wired outer terminals share a wire with an inner object, so a wire alone does
    #     NOT join the two objects in general.
    # RULE: an outer and an inner tunnel at the SAME TOP that appear on a COMMON FRAME are the two
    # halves of one tunnel; inside that frame the source terminal feeds the sink terminal.
    def frames_of(node):
        return set(int(r["frame_diagram"]) for r in by_node.get(node, ()) if r.get("frame_diagram"))

    outers = [u for u, c in cls.items() if c == FS_OUT]
    inners = [u for u, c in cls.items() if c == FS_IN]
    if fs_pairs:
        # STEP 4b - EXACT, from the machine (tools/bench/diag_fstunnel_pairs.log, 14/0 on S1):
        #   * FSOT: OuterTerminal + InnerTerminal == the two rows the traverse gives that FSOT (58/58);
        #   * FSIT: Left + Right, on DIFFERENT frames (518/518); every PHYSICAL inner tunnel is TWO FSIT
        #     uids reporting the same two faces swapped (259 pairs), and the traverse files all four
        #     rows of the pair under ONE of the two uids - two faces plus two NON-face terminals
        #     (frame_diagram mostly the TopLevelDiagram) joined only to each other by one wire.
        # EDGE: one `fs` edge per physical tunnel, its SINK face -> its SOURCE face. info = "faces:<uid>"
        # (the rule that made it; the heuristic's edges carry the frame uid instead).
        by_term = dict((r["term_uid"], r) for r in rows)
        done, fs_edges, unpaired, n_out, n_in = set(), 0, [], 0, 0
        for p in fs_pairs:
            a, b = by_term.get(p.get("term_a")), by_term.get(p.get("term_b"))
            ok = bool(a and b and not p.get("err_a") and not p.get("err_b") and
                      a["is_source"] != b["is_source"])
            if not ok:
                unpaired.append(p["uid"])
                continue
            if p["class"] == FS_OUT:
                n_out += 1
            else:
                n_in += 1
            phys = frozenset((a["term_uid"], b["term_uid"]))
            if phys in done:
                continue
            done.add(phys)
            src, snk = (a, b) if a["is_source"] else (b, a)
            edges.append(("fs", snk["key"], src["key"], "faces:{0}".format(p["uid"])))
            fs_edges += 1
        faces = set()
        for p in fs_pairs:
            faces |= {p.get("term_a"), p.get("term_b")}
        phantom = sum(1 for r in rows if r["owner_class"] == FS_IN and r["term_uid"] not in faces)
        method["fs_tunnel"] = {"rule": "machine faces (wiki fs_tunnel_pairs: OuterTerminal/InnerTerminal, "
                                       "LeftTerm/RightTerm read by uid); sink face -> source face",
                               "outer": len(outers), "outer_paired": n_out,
                               "inner_uids": len([p for p in fs_pairs if p["class"] == FS_IN]),
                               "inner_paired_uids": n_in, "physical_tunnels": len(done),
                               "edges": fs_edges, "unpaired_uids": unpaired[:20],
                               "unpaired_outer": sum(1 for p in fs_pairs if p["class"] == FS_OUT
                                                     and p["uid"] in unpaired),
                               "fsit_nonface_rows_isolated": phantom,
                               "fsit_thru_suppressed": True}
        outers = []                       # the heuristic below is the FALLBACK only
    in_by_y = collections.defaultdict(list)
    for u in inners:
        in_by_y[round(pos.get(u, (0, -10 ** 9))[1])].append(u)
    fs_pairs, fs_edges, fs_unpaired = [], 0, []
    for u in outers:
        fu = frames_of(u)
        hit = False
        for v in in_by_y.get(round(pos.get(u, (0, 10 ** 9))[1]), []):
            shared = fu & frames_of(v)
            if not shared:
                continue
            hit = True
            fs_pairs.append((u, v))
            for f in shared:
                for a in by_node[u]:
                    for b in by_node[v]:
                        if int(a.get("frame_diagram") or 0) != f or \
                                int(b.get("frame_diagram") or 0) != f or \
                                a["is_source"] == b["is_source"]:
                            continue
                        src, snk = (a, b) if a["is_source"] else (b, a)
                        edges.append(("fs", src["key"], snk["key"], f))
                        fs_edges += 1
        if not hit:
            fs_unpaired.append(u)
    if "fs_tunnel" not in method:         # the fallback's own record (the exact rule wrote its own)
        method["fs_tunnel"] = {"outer": len(outers), "inner": len(inners), "pairs": len(fs_pairs),
                               "edges": fs_edges, "unpaired_outer": len(fs_unpaired),
                               "rule": "HEURISTIC fallback (no fs_tunnel_pairs): equal TOP + a COMMON frame "
                                       "(frame_diagram); source -> sink inside that frame"}

    # --- 5 LOCAL / GLOBAL ---------------------------------------------------------------------------
    fp_by_label = collections.defaultdict(list)
    for r in rows:
        if r["term_class"] == FP_CLASS:
            fp_by_label[r["term_name"]].append(r)
    for kind in ("Local", "Global"):
        n = 0
        by_name = collections.defaultdict(lambda: ([], []))
        for r in rows:
            if r["owner_class"] == kind:
                by_name[r["term_name"]][0 if r["is_source"] else 1].append(r)
        for name, pair in by_name.items():
            readers, writers = pair
            targets = list(readers)
            fp = fp_by_label.get(name, ())
            if kind == "Local":
                # a Local WRITE also updates the control, whose own diagram terminal is a source
                targets += [x for x in fp if x["is_source"]]
            for w in writers:
                for rd in targets:
                    if rd["node"] != w["node"]:
                        edges.append((kind.lower(), w["key"], rd["key"], 0))
                        n += 1
            # ... and the mirror, which the step-3 rule MISSED and `computation_diff` caught on the
            # bed: an INDICATOR written by a wire (its front-panel terminal is a SINK) is read back by
            # every Local READ of the same label. M3a's re-wiring uses exactly that relay, and without
            # this edge #9703's input looked unsourced (tools/bench/vigraph_check.log, run 1).
            if kind == "Local":
                for ind in [x for x in fp if not x["is_source"]]:
                    for rd in readers:
                        edges.append((kind.lower(), ind["key"], rd["key"], 0))
                        n += 1
        method[kind.lower()] = n

    out_e, in_e = collections.defaultdict(list), collections.defaultdict(list)
    for kind, a, b, info in edges:
        out_e[a].append((kind, b, info))
        in_e[b].append((kind, a, info))
    lab = dict((int(u), t) for u, t in (labels or {}).items())
    return {"cls": cls, "rows": by_key, "by_node": dict(by_node), "edges": edges,
            "out": dict(out_e), "in": dict(in_e), "pos": pos, "labels": lab,
            "flags": flags, "method": method, "nodes": sorted(cls), "n_terminals": len(rows)}


def is_scheduling(G, node):
    """ASSUMPTION A. A node is SCHEDULING when its class is a tunnel / shift register / structure /
    diagram / Local / Global, or its label is a Wait-or-timing primitive."""
    if G["cls"].get(node) in SCHED_OWNER:
        return True
    text = (G["labels"].get(node) or "").lower()
    return any(w in text for w in WAIT_LABEL)


def transparent(G, key):
    """ASSUMPTION A, at TERMINAL level: is this terminal a scheduling RELAY to walk through?

    A scheduling node always is. A front-panel terminal is transparent only when it is WRITTEN on the
    diagram and read back - the `indicator -> Local -> tunnel` relay M3a uses. A control that nothing
    writes is a real SOURCE and the collapse stops there."""
    node = key_parts(key)[0]
    if is_scheduling(G, node):
        return True
    return G["cls"].get(node) == FP_CLASS and bool(G["in"].get(key))


def terminals(G, node=None, name=None, term_uid=None, is_source=None, cls=None):
    """Terminal KEYS matching the filter - the addressing helper the queries below take."""
    out = []
    for key, r in G["rows"].items():
        if node is not None and r["node"] != node:
            continue
        if term_uid is not None and r["term_uid"] != term_uid:
            continue
        if name is not None and r["term_name"] != name:
            continue
        if cls is not None and r["term_class"] != cls:
            continue
        if is_source is not None and bool(r["is_source"]) != bool(is_source):
            continue
        out.append(key)
    return sorted(out)


def wire_terminals(G, wire_uid):
    return sorted(k for k, r in G["rows"].items() if r["wire_uid"] == wire_uid)


def reach4(G, starts, kinds=None):
    """Every terminal key reachable DOWNSTREAM of `starts` (terminal keys, or node uids)."""
    stack = []
    for s in starts:
        stack.extend(terminals(G, node=s) if isinstance(s, int) else [s])
    seen = set()
    while stack:
        cur = stack.pop()
        for kind, nxt, _i in G["out"].get(cur, ()):
            if kinds and kind not in kinds:
                continue
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


def sources_of(G, sink, kinds=None, collapse=False):
    """Every terminal key UPSTREAM of `sink`. `collapse=True` returns only COMPUTATION terminals,
    walking THROUGH scheduling relays (tunnels, shift registers, Locals) - the rule-1a question
    'where does this input's value really come from'."""
    starts = list(sink) if isinstance(sink, (list, tuple, set)) else [sink]
    stack, seen, out = list(starts), set(starts), set()
    while stack:
        cur = stack.pop()
        for kind, prev, _i in G["in"].get(cur, ()):
            if kinds and kind not in kinds:
                continue
            if prev in seen:
                continue
            seen.add(prev)
            sched = transparent(G, prev)
            if not collapse or not sched:
                out.add(prev)
            if sched or not collapse:
                stack.append(prev)
    return out


def path(G, a, b, kinds=None):
    """One shortest terminal path a -> b as a list of terminal keys, or [] if there is none."""
    starts = terminals(G, node=a) if isinstance(a, int) else [a]
    goal = set(terminals(G, node=b) if isinstance(b, int) else [b])
    prev, queue = {}, collections.deque()
    for s in starts:
        prev[s] = None
        queue.append(s)
    while queue:
        cur = queue.popleft()
        if cur in goal:
            out, node = [], cur
            while node is not None:
                out.append(node)
                node = prev[node]
            return list(reversed(out))
        for kind, nxt, _i in G["out"].get(cur, ()):
            if kinds and kind not in kinds:
                continue
            if nxt not in prev:
                prev[nxt] = cur
                queue.append(nxt)
    return []


DIFF_KINDS = ("wire", "sr", "fs", "local", "global")


def diff(A, B, kinds=DIFF_KINDS):
    """Edges added / removed / changed between two graphs, keyed by (owner uid, terminal name) and
    never by wire uid (Pre-decided 137). `thru` is DERIVED from the terminal list and is excluded;
    terminal and node additions are reported separately so nothing hides inside a derived edge.

    changed_sinks = a sink terminal present in BOTH graphs whose set of incoming sources differs."""
    def eset(G):
        return set((k, a, b) for k, a, b, _i in G["edges"] if k in kinds)

    ea, eb = eset(A), eset(B)
    srcs = {}
    for tag, G in (("a", A), ("b", B)):
        d = collections.defaultdict(set)
        for k, a, b, _i in G["edges"]:
            if k in kinds:
                d[b].add((k, a))
        srcs[tag] = d
    changed = []
    for key in set(A["rows"]) & set(B["rows"]):
        x, y = srcs["a"].get(key, set()), srcs["b"].get(key, set())
        if x != y:
            changed.append({"sink": key, "before": sorted(a for _k, a in x),
                            "after": sorted(a for _k, a in y)})
    fl = {}
    for tag, G in (("a", A), ("b", B)):
        fl[tag] = dict((f["wire_uid"], f) for f in G["flags"])
    return {
        "edges_removed": sorted(ea - eb), "edges_added": sorted(eb - ea),
        "changed_sinks": sorted(changed, key=lambda r: r["sink"]),
        "nodes_removed": sorted(set(A["cls"]) - set(B["cls"])),
        "nodes_added": sorted(set(B["cls"]) - set(A["cls"])),
        "terminals_removed": sorted(set(A["rows"]) - set(B["rows"])),
        "terminals_added": sorted(set(B["rows"]) - set(A["rows"])),
        "half_wires_only_in_a": sorted(set(fl["a"]) - set(fl["b"])),
        "half_wires_only_in_b": sorted(set(fl["b"]) - set(fl["a"])),
        "counts": {"edges_removed": len(ea - eb), "edges_added": len(eb - ea),
                   "changed_sinks": len(changed)},
    }


def effective_sources(G, key, memo=None):
    """The COMPUTATION terminals whose value reaches `key` through scheduling relays only.
    An empty set means the input is UNSOURCED (severed, or only reachable through an uninitialised
    register). A shift register is a cycle, so the walk carries its own visited set."""
    if memo is None:
        memo = {}
    if key in memo:
        return memo[key]
    out, stack, seen = set(), [key], {key}
    while stack:
        cur = stack.pop()
        for _kind, prev, _i in G["in"].get(cur, ()):
            if prev in seen:
                continue
            seen.add(prev)
            if transparent(G, prev):
                stack.append(prev)
            else:
                out.add(prev)
    memo[key] = out
    return out


def computation_diff(A, B):
    """ASSUMPTION A's rule-1a question: for every COMPUTATION node (subVI, primitive, constant,
    front-panel terminal), is every input fed by the SAME computation source in both graphs once
    scheduling relays are collapsed? Returns exactly the rows where it is not."""
    ma, mb = {}, {}
    rows, added, removed = [], [], []
    ca = set(n for n in A["cls"] if not is_scheduling(A, n))
    cb = set(n for n in B["cls"] if not is_scheduling(B, n))
    for n in sorted(ca - cb):
        removed.append({"node": n, "class": A["cls"][n]})
    for n in sorted(cb - ca):
        added.append({"node": n, "class": B["cls"][n]})
    for n in sorted(ca & cb):
        sinks = set(terminals(A, node=n, is_source=False)) | set(terminals(B, node=n, is_source=False))
        for key in sorted(sinks):
            sa = effective_sources(A, key, ma) if key in A["rows"] else None
            sb = effective_sources(B, key, mb) if key in B["rows"] else None
            if sa == sb:
                continue
            rows.append({"node": n, "class": A["cls"].get(n) or B["cls"].get(n), "sink": key,
                         "before": None if sa is None else sorted(sa),
                         "after": None if sb is None else sorted(sb)})
    return {"rows": rows, "computation_nodes_added": added, "computation_nodes_removed": removed,
            "n_computation_nodes": len(ca & cb),
            "assumption": "A (SCHED_OWNER) - judgement 2026-09-23, awaiting the user (plan OPEN A)"}
