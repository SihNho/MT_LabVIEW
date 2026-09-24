r"""stagesim - the STAGE SIMULATOR core (docs/stage-simulator-plan.md "The method" steps 2 and 4; card chat-S2).
PURE PYTHON on tools/vigraph.py. No LabVIEW, no COM, no model, no Jev: it applies a stage plan (stageplan/1,
docs/protocol/stageplan.json) ACTION BY ACTION to the graph JSON and decides nothing.

    py tools/stagesim.py simulate <plan.json> <graph.json> [--out-root DIR] [--plan-out DIR]
    py tools/stagesim.py selftest

WHAT EXISTED FIRST (checked 2026-09-24 before writing): tools/vigraph.py (build4 / terminals / effective_sources /
computation_diff / diff - used, NOT edited); tools/jev_candidates.py (from_parts, diagram_tree, scope, term_row,
map_key, chain_terminals = RULE-CHAIN-S1 - used, not edited); tools/stagekit.py uid_edges (copied as `uid_edges`
below, because importing stagekit pulls the LabVIEW fleet in); tools/stage_prerun.py (dry run + pre-run of a RECIPE
with COM stubbed - says itself "no op-effect models yet: build order step 3/4"; this file is step 4);
tools/bench/l7_1_predict.py, l7_r_predict.py (hand-written per-stage predictions - what this generalises).
No simulator and no plan schema existed.

GRAPH STATE (one step file = one state): the raw tables vigraph.build4 reads - `terminals` (OpAllTerms_v1 rows),
`objs` (GObject census), `loops` (Shift Registers[] table), `fs_pairs` - plus `sym` {symbolic id: internal uid}
and `diagrams` {body: parent} for structures the plan touched. Objects the plan CREATES get NEGATIVE internal
uids (terminals and wires too); the plan names them only by symbolic id (new:SR1R, new:T1 ...), so the plan never
carries a uid that does not exist yet. Every action reads the PREVIOUS STEP FILE from disk, not an in-memory copy.

OP EFFECT MODELS: tools/bench/opmodels/<op>.json (card chat-S1) when present - its `sim` object overrides the
provisional parameters below and the step records `model_source: measured:<file>@<md5>`; otherwise the PROVISIONAL
rule (the plan table's op, with the log line it rests on) is used and recorded as `provisional`. A measured model
file WITHOUT a `sim` object is recorded as `measured-file-present-no-sim-params` and the provisional rule runs -
never silently.

MOVE: the cut set = every wire with terminals both inside and outside the moved set. The RECONNECT TABLE maps each
cut terminal to its S1 partner(s) (direct S1 wire partner and the collapsed computation partner). A cut row whose
terminal is on an S1 iteration chain is tagged RULE-CHAIN-S1 (jev_candidates) and is NOT a candidate; any other
cut row that must cross a structure border has more than one legal mechanism (tunnel / indexing tunnel / shift
register) and goes to `candidates.json` in the jev_candidates shape. The simulator decides none of them.

FINALIZE: the last step's graph vs S1 `computation_diff` == 0 rows, no failed action, no undecided `decide`
action => `plan_<stage>.json` is written with `final: true` and the md5s of base, plan and last step; otherwise it
is written with `final: false` and `first_divergent` = the earliest step from which every remaining row stays.
"""
import collections
import copy
import glob
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(HERE, "bench")
SIM_ROOT = os.path.join(BENCH, "sim")
OPMODEL_DIR = os.path.join(BENCH, "opmodels")
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import vigraph as V            # noqa: E402
import jev_candidates as JC    # noqa: E402
import protocol                # noqa: E402

TUN1 = ("LoopTunnel", "Tunnel")                     # single-object tunnels whose outer can flip direction
DROP_WHEN_UNWIRED = ("LoopTunnel", "Tunnel")
SR_CLS = ("RightShiftRegister", "LeftShiftRegister")

# The plan table's ops with the provisional rule each one runs until chat-S1's measured model lands.
PROVISIONAL = {
    "move_in": {"params": {"cut_clears": "moved", "tunnel_flip": True},
                "evidence": "tools/bench/diag_c71_l7_1a_tunnels.log (TERM 2043/5050 is_source True->False, FLAG w4337/w5073 "
                            "n_src 0 after move_in #376); tools/bench/stage_d1_l7_1b_r3.log:207-214 (#376's cut terminals read "
                            "wire=0)",
                "gaps": ["SR pair names reset on a cut (15/51 -> '' but 24/1108 kept 'error out') NOT modelled: names only, "
                         "computation_diff collapses registers", "the junk Invoke node each op leaves is NOT modelled "
                                                                     "(stagekit.junk_purge deletes it)"]},
    "add_shift_reg": {"params": {"names": ""},
                      "evidence": "tools/bench/stage_d1_l7_1a.json l7_1a.sr (a Right+Left pair per call); "
                                  "jev_candidates.rule_chain_s1 docstring (new register terminals unnamed)",
                      "gaps": ["an error-cluster register's outer later reads 'error out' (l7_r_prediction.json s1map) - "
                               "name propagation on wiring not modelled"]},
    "tunnel": {"params": {},
               "evidence": "tools/bench/stage_d1_l7_r_r2.log PC3 (connect_nested_v1 made exactly one LoopTunnel per border)",
               "gaps": ["LabVIEW picks direction from the wiring; the plan states `dir`"]},
    "delete_wire": {"params": {"drop_unwired_tunnel": True},
                    "evidence": "tools/bench/stage_d1_l7_r.json ops: delete_object LoopTunnel #1929/#5020 -> False "
                                "(already gone) after their inner+outer wires were deleted",
                    "gaps": []},
    "delete_object": {"params": {"sr_pair": True},
                      "evidence": "tools/bench/stage_d1_l7_r.json ops: delete RightShiftRegister #15 True, then "
                                  "LeftShiftRegister #51 False (gone with its pair); same for #24/#1108",
                      "gaps": []},
    "wire": {"params": {"same_diagram": True, "detach_sourceless_sink": True},
             "evidence": "stage_d1_l7_1b_r3.log connect_from_wire results `UID 2` = the EXISTING wire (4969, 3543): a sink "
                         "wired to an already-wired source joins that wire",
             "gaps": ["a sink on a sourceless half-wire is detached from it (not measured)"]},
    "remove_bad_wires": {"params": {},
                         "evidence": "vigraph.build4 flags (a wire with n_src != 1 or no sink); stage_d1_l7_r_r2.log "
                                     "'RBW removed no live uid edge'",
                         "gaps": ["LabVIEW may also delete dangling tunnels on RBW - not modelled"]},
    "create": {"params": {}, "evidence": "plan-declared terminal list (no measurement yet)",
               "gaps": ["terminal list must come from an op model or the subVI wiki"]},
    "decide": {"params": {}, "evidence": "never applied - listed as a candidate row", "gaps": []},
}
MODEL_ALIASES = {"wire": ("wire", "connect_from_wire", "wire_sr", "connect_nested", "connect"),
                 "tunnel": ("tunnel", "tunnel_create", "create_tunnel"),
                 "create": ("create", "const_create", "primitive_create", "create_const", "create_primitive")}
MECHANISMS_ACROSS = ["tunnel", "tunnel_indexing", "shift_register"]


class SimError(Exception):
    """An action that cannot be applied: an unaddressable/ambiguous terminal, an occupied sink, a cross-diagram
    wire. The simulation STOPS at it, exactly where a real stage would."""


def md5_file(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _j(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _rel(p):
    try:
        return os.path.relpath(p, ROOT).replace("\\", "/")
    except ValueError:
        return p


def _abs(p):
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


# ------------------------------------------------------------------------------------------------ op models
def load_models(model_dir=OPMODEL_DIR):
    out = {}
    for p in sorted(glob.glob(os.path.join(model_dir, "*.json"))):
        try:
            d = _j(p)
        except Exception as e:                                                       # noqa: BLE001
            out[os.path.splitext(os.path.basename(p))[0]] = {"path": p, "md5": None, "data": None, "error": str(e)}
            continue
        name = d.get("op") if isinstance(d, dict) and isinstance(d.get("op"), str) else \
            os.path.splitext(os.path.basename(p))[0]
        out[name] = {"path": p, "md5": md5_file(p), "data": d}
    return out


def model_for(op, models):
    """(params, source string, evidence, gaps) for one op."""
    base = PROVISIONAL[op]
    params = dict(base["params"])
    for name in MODEL_ALIASES.get(op, (op,)):
        m = models.get(name)
        if not m:
            continue
        src = "{0}:{1}@{2}".format("measured", _rel(m["path"]), m.get("md5"))
        sim = (m.get("data") or {}).get("sim") if isinstance(m.get("data"), dict) else None
        if isinstance(sim, dict):
            params.update(sim)
            return params, src, "opmodel file", []
        return params, "measured-file-present-no-sim-params:{0}@{1} (provisional rule ran)".format(
            _rel(m["path"]), m.get("md5")), base["evidence"], base["gaps"]
    return params, "provisional", base["evidence"], base["gaps"]


# ------------------------------------------------------------------------------------------------ state
def base_state(graph, context=None):
    ctx = context or {}
    st = {"terminals": [dict(r) for r in graph["terminals"]], "objs": [dict(o) for o in graph.get("objs") or []],
          "loops": copy.deepcopy(graph.get("loops")), "fs_pairs": copy.deepcopy(graph.get("fs_tunnel_pairs")),
          "graph_summary": graph.get("graph_summary") or {}, "sym": {}, "diagrams": {}, "neg": 0,
          "removed_nodes": [], "vi": graph.get("vi"), "md5": graph.get("md5")}
    if ctx.get("loops"):
        st["loops"] = _j(_abs(ctx["loops"]["path"]))["loops"]
    if ctx.get("fs_pairs_wiki"):
        w = _j(_abs(ctx["fs_pairs_wiki"]["path"]))
        st["fs_pairs"] = w.get("fs_tunnel_pairs")
        st["graph_summary"] = w.get("graph_summary") or st["graph_summary"]
    for r in st["terminals"]:
        r.setdefault("term_class", "")
    return st


def new_uid(st):
    st["neg"] -= 1
    return st["neg"]


def node_rows(st, uid):
    return [r for r in st["terminals"] if V.node_of(r) == uid]


def wire_rows(st, w):
    return [r for r in st["terminals"] if w and r["wire_uid"] == w]


def has_source(st, w):
    return any(r["is_source"] for r in wire_rows(st, w))


def obj_class(st, uid):
    for o in st["objs"]:
        if int(o["uid"]) == uid:
            return o["class"]
    for r in st["terminals"]:
        if V.node_of(r) == uid:
            return V.node_class(r)
    return None


def resolve_uid(st, ref):
    if isinstance(ref, int):
        return ref
    if isinstance(ref, str) and ref.startswith("new:"):
        if ref not in st["sym"]:
            raise SimError("symbolic id {0} is not created by any earlier action of this plan".format(ref))
        return st["sym"][ref]
    try:
        return int(ref)
    except (TypeError, ValueError):
        raise SimError("unaddressable uid reference {0!r}".format(ref))


def parse_addr(a):
    if isinstance(a, dict):
        return dict(a)
    if not isinstance(a, str) or "." not in a:
        raise SimError("address {0!r} is not '<uid>.<terminal>' / 'new:<kind><n>.<terminal>'".format(a))
    head, term = a.split(".", 1)
    return {"uid": head, "term": term}


def resolve_addr(st, a, want_source):
    """The ONE terminal row an address names. Selector order: term_uid, then name; `inner`/`outer` (or `side`)
    pick the tunnel/register face by class when no terminal carries that name. Exactly one row or SimError -
    this is the plan-time addressability check (a wire-walked uid lookup failing mid-run was stage_d1_l7_1b_r2)."""
    a = parse_addr(a)
    uid = resolve_uid(st, a["uid"])
    rows = node_rows(st, uid)
    if not rows:
        raise SimError("#{0} ({1}) owns no terminal in the current graph".format(uid, a["uid"]))
    if a.get("term_uid") is not None:
        rows = [r for r in rows if r["term_uid"] == a["term_uid"]]
    side = a.get("side")
    if a.get("term") is not None:
        named = [r for r in rows if r["term_name"] == a["term"]]
        if not named and a["term"] in ("inner", "outer"):
            side = a["term"]
        else:
            rows = named
    if side:
        rows = [r for r in rows if r["term_class"] == ("InnerTerminal" if side == "inner" else "OuterTerminal")]
    rows = [r for r in rows if bool(r["is_source"]) == bool(want_source)]
    uniq = dict(((r["term_uid"], r["term_class"], r["frame_diagram"]), r) for r in rows)
    if len(uniq) != 1:
        raise SimError("address {0} ({1}) resolves to {2} {3} terminal(s): {4}".format(
            a, uid, len(uniq), "source" if want_source else "sink",
            sorted((r["term_uid"], r["term_name"], r["term_class"]) for r in uniq.values())[:6]))
    return list(uniq.values())[0]


def graph(st, labels=None):
    rec = {"terminals": st["terminals"], "graph_summary": st.get("graph_summary") or {}}
    G = JC.from_parts(rec, st["objs"], st["loops"], labels if labels is not None else {}, st.get("fs_pairs"), "sim")
    for body, parent in st["diagrams"].items():
        G["tree"]["parent"].setdefault(int(body), int(parent))
    return G


# ------------------------------------------------------------------------------------------------ S1 helpers
def effective_consumers(G, key):
    """The COMPUTATION sink terminals `key`'s value reaches through scheduling relays only (forward twin of
    vigraph.effective_sources)."""
    out, stack, seen = set(), [key], {key}
    while stack:
        cur = stack.pop()
        for _k, nxt, _i in G["out"].get(cur, ()):
            if nxt in seen:
                continue
            seen.add(nxt)
            if V.transparent(G, nxt):
                stack.append(nxt)
            else:
                out.add(nxt)
    return out


def s1_partner(S1, G, key):
    k1, how = JC.map_key(S1, key, G)
    if not k1:
        return {"s1_key": None, "how": how, "direct": [], "effective": []}
    r = S1["rows"][k1]
    if r["is_source"]:
        direct = sorted(b for kind, b, _i in S1["out"].get(k1, ()) if kind == "wire")
        eff = sorted(effective_consumers(S1, k1))
    else:
        direct = sorted(a for kind, a, _i in S1["in"].get(k1, ()) if kind == "wire")
        eff = sorted(V.effective_sources(S1, k1))
    return {"s1_key": k1, "how": how, "direct": direct, "effective": eff}


# ------------------------------------------------------------------------------------------------ ops
def _flip_orphaned_output_tunnels(st, wires):
    """PROVISIONAL (diag_c71_l7_1a_tunnels.log TERM 2043/5050): an output LoopTunnel/Tunnel whose INNER sink is left
    on a wire with no source reads its OUTER terminal as a sink afterwards. Repeated to a fixpoint."""
    flipped, todo = [], set(w for w in wires if w)
    while todo:
        w = todo.pop()
        if has_source(st, w):
            continue
        for r in wire_rows(st, w):
            if r["is_source"] or r["term_class"] != "InnerTerminal" or r["owner_class"] not in TUN1:
                continue
            for o in node_rows(st, r["owner_uid"]):
                if o["term_class"] == "OuterTerminal" and o["is_source"]:
                    o["is_source"] = False
                    flipped.append({"tunnel": r["owner_uid"], "outer_term_uid": o["term_uid"], "wire": o["wire_uid"]})
                    todo.add(o["wire_uid"])
    return flipped


def op_move_in(st, a, P, S1, labels):
    moved = set(resolve_uid(st, u) for u in a["nodes"])
    dest = int(a["dest_diagram"])
    G0 = graph(st, labels)
    inside = [r for r in st["terminals"] if V.node_of(r) in moved]
    if not inside:
        raise SimError("move_in: none of {0} owns a terminal".format(sorted(moved)))
    by_w = collections.defaultdict(lambda: ([], []))
    for r in st["terminals"]:
        if r["wire_uid"]:
            by_w[r["wire_uid"]][0 if V.node_of(r) in moved else 1].append(r)
    cut = dict((w, v) for w, v in by_w.items() if v[0] and v[1])
    key_of = dict(((r["term_uid"], r["term_class"], r["frame_diagram"]), k) for k, r in G0["rows"].items())
    kk = lambda r: key_of.get((r["term_uid"], r["term_class"], r["frame_diagram"]))       # noqa: E731
    chains = JC.chain_terminals(S1, moved) if S1 is not None else set()
    table = []
    for w in sorted(cut):
        ins, outs = cut[w]
        for side, rows, other in (("moved", ins, outs), ("outside", outs, ins)):
            for r in rows:
                k = kk(r)
                table.append({"cut_wire": w, "side": side, "key": k, "term_uid": r["term_uid"],
                              "is_source": bool(r["is_source"]), "partners_now": sorted(kk(x) or "" for x in other),
                              "chain": (V.node_of(r), r["term_name"]) in chains,
                              "s1": s1_partner(S1, G0, k) if (S1 is not None and k) else None})
    # apply
    for r in inside:
        r["frame_diagram"] = dest
    cleared = []
    for w, (ins, outs) in cut.items():
        victims = ins if P.get("cut_clears", "moved") == "moved" else outs
        for r in victims:
            r["wire_uid"] = 0
            cleared.append(r["term_uid"])
    flipped = _flip_orphaned_output_tunnels(st, cut.keys()) if P.get("tunnel_flip", True) else []
    # candidates: moved-side rows that must cross a border and are not RULE-CHAIN-S1
    G1 = graph(st, labels)
    key1 = dict(((r["term_uid"], r["term_class"]), k) for k, r in G1["rows"].items())
    cands, rule_rows = [], []
    for row in table:
        if row["side"] != "moved":
            continue
        r_new = next((r for r in inside if r["term_uid"] == row["term_uid"]), None)
        k_new = key1.get((row["term_uid"], r_new["term_class"])) if r_new else None
        for pk in row["partners_now"]:
            pr = G0["rows"].get(pk)
            if not pr:
                continue
            rel, borders = JC.scope(G1, dest, int(pr.get("frame_diagram") or 0))
            mech = ["wire"] if rel == "same" else (MECHANISMS_ACROSS if rel in ("nested", "cousins") else ["unknown"])
            if row["chain"]:
                rule_rows.append({"key": row["key"], "partner": pk, "decided_by": JC.RULE_CHAIN_S1,
                                  "mechanism": "shift_register"})
                continue
            if len(mech) < 2:
                rule_rows.append({"key": row["key"], "partner": pk, "decided_by": "single-mechanism",
                                  "mechanism": mech[0], "scope": rel})
                continue
            src_k, dst_k = (k_new, pk) if row["is_source"] else (pk, k_new)
            G_for = lambda key: G1 if key in G1["rows"] else G0                           # noqa: E731
            pairs = []
            for m in mech:
                s = JC.term_row(G_for(src_k), src_k) if src_k else None
                d = JC.term_row(G_for(dst_k), dst_k) if dst_k else None
                pairs.append({"row_key": {"src_uid": s and s["uid"], "src_term": s and s["term"],
                                          "src_term_class": s and s["term_class"], "dst_uid": d and d["uid"],
                                          "dst_term": d and d["term"], "dst_term_class": d and d["term_class"]},
                              "src": s, "dst": d, "sink_state": "cut", "scope": rel, "borders": borders,
                              "type": "unknown (wiki type column empty)", "cycle_overapprox": None, "mechanism": m})
            cands.append({"intent": {"src": pairs[0]["row_key"]["src_uid"], "dst": pairs[0]["row_key"]["dst_uid"],
                                     "from": "stagesim move_in cut", "cut_wire": row["cut_wire"],
                                     "s1_partner": row["s1"]},
                          "resolved": {"src": [pairs[0]["row_key"]["src_uid"]], "src_method": "cut set",
                                       "dst": [pairs[0]["row_key"]["dst_uid"]], "dst_method": "cut set"},
                          "n_src_terms": 1, "n_dst_terms": 1, "pairs": pairs, "excluded": {}})
    return {"moved": sorted(moved), "dest_diagram": dest, "cut_set": sorted(cut), "n_cut": len(cut),
            "reconnect": table, "cleared_term_uids": sorted(cleared), "tunnel_flips": flipped,
            "rule_rows": rule_rows}, cands


def _parent_of(st, body, a, labels):
    if a.get("parent") is not None:
        return int(a["parent"])
    if str(body) in st["diagrams"] or body in st["diagrams"]:
        return int(st["diagrams"].get(str(body), st["diagrams"].get(body)))
    p = graph(st, labels)["tree"]["parent"].get(body)
    if p is None:
        raise SimError("the parent diagram of body #{0} is unknown (give `parent`)".format(body))
    return int(p)


def _new_obj(st, cls, owner, y=0):
    u = new_uid(st)
    st["objs"].append({"uid": u, "class": cls, "pos": [0, y], "owner": owner})
    return u


def _new_term(st, owner, owner_class, term_class, is_source, diagram, name=""):
    t = new_uid(st)
    st["terminals"].append({"term_uid": t, "term_name": name, "is_source": bool(is_source), "wire_uid": 0,
                            "owner_uid": owner, "owner_class": owner_class, "frame_diagram": diagram,
                            "term_class": term_class})
    return t


def _sym(st, name, uid):
    key = "new:" + name
    if key in st["sym"]:
        raise SimError("symbolic id {0} is created twice".format(key))
    st["sym"][key] = uid
    return key


def op_add_shift_reg(st, a, P, S1, labels):
    loop, body = int(a["loop"]), int(a["body"])
    parent = _parent_of(st, body, a, labels)
    y = -len(st["sym"]) - 1
    R, L = _new_obj(st, "RightShiftRegister", "WhileLoop", y), _new_obj(st, "LeftShiftRegister", "WhileLoop", y)
    nm = P.get("names", "")
    terms = {"R.inner": _new_term(st, R, "RightShiftRegister", "InnerTerminal", False, body, nm),
             "R.outer": _new_term(st, R, "RightShiftRegister", "OuterTerminal", True, parent, nm),
             "L.outer": _new_term(st, L, "LeftShiftRegister", "OuterTerminal", False, parent, nm),
             "L.inner": _new_term(st, L, "LeftShiftRegister", "InnerTerminal", True, body, nm)}
    if st["loops"] is None:
        st["loops"] = []
    ent = next((x for x in st["loops"] if int(x["loop_uid"]) == loop), None)
    if ent is None:
        ent = {"loop_uid": loop, "right_uids": [], "left_of": {}}
        st["loops"].append(ent)
    ent["right_uids"] = list(ent.get("right_uids") or []) + [R]
    ent.setdefault("left_of", {})[str(R)] = [L]
    st["diagrams"][str(body)] = parent
    name = a.get("as") or "SR{0}".format(-R)
    return {"right": _sym(st, name + "R", R), "left": _sym(st, name + "L", L), "loop": loop, "body": body,
            "parent": parent, "terms": terms}, []


def op_tunnel(st, a, P, S1, labels):
    loop, body = int(a["loop"]), int(a["body"])
    parent = _parent_of(st, body, a, labels)
    T = _new_obj(st, "LoopTunnel", "WhileLoop")
    din = a.get("dir", "in") == "in"
    o = _new_term(st, T, "LoopTunnel", "OuterTerminal", not din, parent)
    i = _new_term(st, T, "LoopTunnel", "InnerTerminal", din, body)
    for x in st["objs"]:
        if x["uid"] == T:
            x["indexing"] = bool(a.get("indexing"))
    st["diagrams"][str(body)] = parent
    return {"tunnel": _sym(st, a.get("as") or "T{0}".format(-T), T), "loop": loop, "dir": a.get("dir", "in"),
            "indexing": bool(a.get("indexing")), "outer": o, "inner": i, "body": body, "parent": parent}, []


def _drop_node(st, uid):
    n0 = len(st["terminals"])
    st["terminals"] = [r for r in st["terminals"] if V.node_of(r) != uid]
    st["objs"] = [o for o in st["objs"] if int(o["uid"]) != uid]
    for L in st["loops"] or []:
        L["right_uids"] = [u for u in L.get("right_uids") or [] if int(u) != uid]
        lo = L.get("left_of") or {}
        lo.pop(str(uid), None)
        for k in list(lo):
            lo[k] = [x for x in (lo[k] if isinstance(lo[k], list) else [lo[k]]) if int(x) != uid]
    st["removed_nodes"].append(uid)
    return n0 - len(st["terminals"])


def op_delete_wire(st, a, P, S1, labels):
    if a.get("wire_uid") is not None:
        w = int(a["wire_uid"])
    else:
        at = parse_addr(a["at"])
        uid = resolve_uid(st, at["uid"])
        rs = [r for r in node_rows(st, uid) if (at.get("term") is None or r["term_name"] == at["term"]) and
              (at.get("term_uid") is None or r["term_uid"] == at["term_uid"]) and r["wire_uid"]]
        ws = sorted(set(r["wire_uid"] for r in rs))
        if len(ws) != 1:
            raise SimError("delete_wire at {0}: {1} wire(s) {2}".format(a["at"], len(ws), ws))
        w = ws[0]
    rows = wire_rows(st, w)
    if not rows:
        raise SimError("delete_wire: wire {0} is not in the current graph".format(w))
    owners = set(r["owner_uid"] for r in rows)
    for r in rows:
        r["wire_uid"] = 0
    dropped = []
    if P.get("drop_unwired_tunnel", True):
        for u in sorted(owners):
            rs = node_rows(st, u)
            if rs and rs[0]["owner_class"] in DROP_WHEN_UNWIRED and not any(r["wire_uid"] for r in rs):
                _drop_node(st, u)
                dropped.append(u)
    return {"wire": w, "n_terminals": len(rows), "auto_removed_tunnels": dropped}, []


def op_delete_object(st, a, P, S1, labels):
    uid = resolve_uid(st, a["uid"])
    cls = obj_class(st, uid)
    if cls is None:
        if a.get("missing_ok"):                  # the real op answers False on an absent uid (stage_d1_l7_r.json)
            return {"deleted": [], "already_absent": uid}, []
        raise SimError("delete_object: #{0} is not in the current graph".format(uid))
    gone = [uid]
    if P.get("sr_pair", True) and cls in SR_CLS:
        for L in st["loops"] or []:
            for r, ls in (L.get("left_of") or {}).items():
                ls = ls if isinstance(ls, list) else [ls]
                if int(r) == uid:
                    gone += [int(x) for x in ls]
                elif uid in [int(x) for x in ls]:
                    gone.append(int(r))
    out = {}
    for u in dict.fromkeys(gone):
        if obj_class(st, u) is not None:
            out[u] = _drop_node(st, u)
    return {"deleted": sorted(out), "class": cls, "terminals_removed": sum(out.values())}, []


def op_wire(st, a, P, S1, labels):
    s = resolve_addr(st, a["src"], True)
    d = resolve_addr(st, a["dst"], False)
    if P.get("same_diagram", True) and int(s["frame_diagram"] or 0) != int(d["frame_diagram"] or 0):
        raise SimError("wire {0} -> {1}: source on diagram {2}, sink on diagram {3} - a border needs a tunnel/"
                       "register action first".format(a["src"], a["dst"], s["frame_diagram"], d["frame_diagram"]))
    detached = None
    if d["wire_uid"]:
        if has_source(st, d["wire_uid"]):
            raise SimError("wire {0} -> {1}: the sink is occupied by wire {2}, which has a source".format(
                a["src"], a["dst"], d["wire_uid"]))
        if not P.get("detach_sourceless_sink", True):
            raise SimError("wire: sink on a sourceless half-wire {0}".format(d["wire_uid"]))
        detached = d["wire_uid"]
        d["wire_uid"] = 0
    if s["wire_uid"]:
        w, how = s["wire_uid"], "branch"
    else:
        w, how = new_uid(st), "new"
        s["wire_uid"] = w
    d["wire_uid"] = w
    return {"wire": w, "how": how, "src_term_uid": s["term_uid"], "dst_term_uid": d["term_uid"],
            "detached_from": detached}, []


def op_remove_bad_wires(st, a, P, S1, labels):
    by_w = collections.defaultdict(list)
    for r in st["terminals"]:
        if r["wire_uid"]:
            by_w[r["wire_uid"]].append(r)
    bad = []
    for w, rows in by_w.items():
        n_src = sum(1 for r in rows if r["is_source"])
        if n_src != 1 or n_src == len(rows):
            bad.append(w)
            for r in rows:
                r["wire_uid"] = 0
    return {"removed_wires": sorted(bad)}, []


def op_create(st, a, P, S1, labels):
    cls, dg = a["class"], int(a["diagram"])
    u = _new_obj(st, cls, "Diagram")
    ts = [_new_term(st, u, cls, t.get("term_class") or "Terminal", t["is_source"], dg, t["name"])
          for t in a.get("terminals") or []]
    return {"node": _sym(st, a.get("as") or "N{0}".format(-u), u), "class": cls, "terminals": ts}, []


def op_decide(st, a, P, S1, labels):
    c = {"intent": dict(a.get("row") or {}, from_="stagesim decide", options=a["options"]),
         "resolved": {}, "pairs": [{"row_key": (a.get("row") or {}).get("row_key"), "mechanism": m}
                                   for m in a["options"]], "excluded": {}, "undecided": True}
    return {"undecided": True, "options": a["options"]}, [c]


OPS = {"move_in": op_move_in, "add_shift_reg": op_add_shift_reg, "tunnel": op_tunnel, "delete_wire": op_delete_wire,
       "delete_object": op_delete_object, "wire": op_wire, "remove_bad_wires": op_remove_bad_wires,
       "create": op_create, "decide": op_decide}


# ------------------------------------------------------------------------------------------------ compare
def uid_edges(G, kinds=("wire", "fs")):
    """stagekit.uid_edges, copied (importing stagekit pulls the LabVIEW fleet in)."""
    out = set()
    for k, a, b, _i in G["edges"]:
        if k in kinds:
            out.add((k, V.key_parts(a)[0], int((G["rows"].get(a) or {}).get("term_uid") or 0),
                     V.key_parts(b)[0], int((G["rows"].get(b) or {}).get("term_uid") or 0)))
    return out


def canon(edges, base_nodes, cls_of):
    """Edges with every NEW object named by its class only ('NEW:<class>', terminal '*') - comparison up to
    new-uid naming. `cls_of(uid)` gives the class of a non-base node."""
    out = collections.Counter()
    for k, na, ta, nb, tb in edges:
        a = (na, ta) if na in base_nodes else ("NEW:{0}".format(cls_of(na)), "*")
        b = (nb, tb) if nb in base_nodes else ("NEW:{0}".format(cls_of(nb)), "*")
        out[(k,) + a + b] += 1
    return out


def canon_diff(ca, cb):
    only_a, only_b = ca - cb, cb - ca
    return {"only_sim": sorted(only_a.elements(), key=repr), "only_ref": sorted(only_b.elements(), key=repr),
            "n": sum(only_a.values()) + sum(only_b.values())}


def cdiff_keys(cd):
    return sorted(set(r["sink"] for r in cd["rows"]))


# ------------------------------------------------------------------------------------------------ simulate
def load_s1(plan):
    ctx = plan.get("context") or {}
    if ctx.get("s1_graph"):
        g = _j(_abs(ctx["s1_graph"]["path"]))
        return V.build4(g["terminals"], g.get("objs"), g.get("loops"), {}, g.get("fs_tunnel_pairs"))
    if ctx.get("s1_key"):
        return JC.load(ctx["s1_key"])
    return None


def simulate(plan_path, graph_path, out_root=SIM_ROOT, plan_out_dir=BENCH, model_dir=OPMODEL_DIR, labels=None,
             log=print):
    plan = _j(plan_path)
    ok, why = protocol.validate_obj(plan)
    if not ok:
        raise SimError("plan does not validate against stageplan/1: " + why)
    stage = plan["stage"]
    out_dir = os.path.join(out_root, stage)
    os.makedirs(out_dir, exist_ok=True)
    for old in glob.glob(os.path.join(out_dir, "step_*.json")):
        os.remove(old)
    models = load_models(model_dir)
    S1 = load_s1(plan)
    st = base_state(_j(graph_path), plan.get("context"))
    base_nodes = set(V.node_of(r) for r in st["terminals"])
    labels = labels if labels is not None else {}
    steps, all_cands, cls_new = [], [], {}

    def write_step(n, name, action, effect, src, prev, err=None):
        p = os.path.join(out_dir, "step_{0:02d}_{1}.json".format(n, name))
        rec = {"schema": "stagesim-step/1", "stage": stage, "n": n, "action": action, "model_source": src,
               "prev": prev, "effect": effect, "error": err, "state": st}
        with open(p, "w", encoding="utf-8") as f:
            json.dump(rec, f, separators=(",", ":"), default=str)
        return {"path": p, "md5": md5_file(p)}

    prev = write_step(0, "base", None, {"graph": _rel(graph_path), "graph_md5": md5_file(graph_path)}, "input", None)
    cd0 = V.computation_diff(S1, graph(st, labels)) if S1 is not None else None
    steps.append({"n": 0, "op": "base", "file": prev, "cdiff_rows": cdiff_keys(cd0) if cd0 else None})
    failed = None
    for n, a in enumerate(plan["actions"], 1):
        st = _j(prev["path"])["state"]                         # the next action reads the previous STEP FILE
        P, src, ev, gaps = model_for(a["op"], models)
        t0 = time.time()
        try:
            effect, cands = OPS[a["op"]](st, a, P, S1, labels)
            err = None
        except SimError as e:
            effect, cands, err = None, [], str(e)
        for c in cands:
            c["step"] = n
        all_cands += cands
        for k, u in st["sym"].items():
            cls_new[u] = obj_class(st, u)
        prev = write_step(n, a["op"], a, effect, src, prev, err)
        rec = {"n": n, "op": a["op"], "id": a.get("id"), "checkpoint": a.get("checkpoint"), "file": prev,
               "model_source": src, "model_evidence": ev, "model_gaps": gaps, "error": err,
               "n_candidates": len(cands), "secs": round(time.time() - t0, 2)}
        if effect:
            rec["effect_summary"] = dict((k, v) for k, v in effect.items() if k not in ("reconnect",))
            if "reconnect" in effect:
                rec["reconnect"] = effect["reconnect"]
        if err is None and S1 is not None:
            cd = V.computation_diff(S1, graph(st, labels))
            rec["cdiff_rows"] = cdiff_keys(cd)
            rec["cdiff_detail"] = cd["rows"]
        steps.append(rec)
        log("  STEP {0:02d} {1:<16} {2} cands={3} cdiff={4} {5}".format(
            n, a["op"], "ERROR " + err if err else "ok", len(cands),
            len(rec.get("cdiff_rows") or []) if rec.get("cdiff_rows") is not None else "-", src))
        if err:
            failed = {"n": n, "op": a["op"], "id": a.get("id"), "error": err}
            break
    last = steps[-1]
    end_rows = last.get("cdiff_rows") if not failed else None
    undecided = [c for c in all_cands if c.get("undecided")]
    first_div = None
    if end_rows:
        firsts = []
        for key in end_rows:
            n0 = last["n"]
            for s in reversed(steps):
                if s.get("cdiff_rows") is not None and key in s["cdiff_rows"]:
                    n0 = s["n"]
                else:
                    break
            firsts.append(n0)
        n0 = min(firsts)
        s0 = next(s for s in steps if s["n"] == n0)
        first_div = {"n": n0, "op": s0["op"], "id": s0.get("id"), "rows_from_here": len(end_rows)}
    final = bool(S1 is not None and not failed and end_rows == [] and not undecided)
    cands_path = os.path.join(out_dir, "candidates.json")
    with open(cands_path, "w", encoding="utf-8") as f:
        json.dump({"schema": "stagesim-candidates/1", "stage": stage, "note": "jev_candidates shape; the "
                   "simulator decided none of these", "rows": all_cands}, f, indent=1, default=str)
    summary = {"schema": "stagesim-summary/1", "stage": stage, "plan": {"path": _rel(plan_path),
               "md5": md5_file(plan_path)}, "graph": {"path": _rel(graph_path), "md5": md5_file(graph_path)},
               "s1": (plan.get("context") or {}).get("s1_key") or (plan.get("context") or {}).get("s1_graph"),
               "models_loaded": dict((k, {"path": _rel(v["path"]), "md5": v.get("md5")}) for k, v in models.items()),
               "steps": steps, "failed": failed, "final": final, "end_cdiff_rows": end_rows,
               "first_divergent": first_div, "n_candidates": len(all_cands), "undecided": len(undecided),
               "candidates": {"path": _rel(cands_path), "md5": md5_file(cands_path)}, "sym": st["sym"],
               "new_classes": dict((str(k), v) for k, v in cls_new.items())}
    sp = os.path.join(out_dir, "summary.json")
    with open(sp, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, default=str)
    out_plan = dict(plan)
    out_plan["final"] = final
    out_plan["finalized"] = {"base": {"path": _rel(graph_path), "md5": md5_file(graph_path)},
                             "plan_in": {"path": _rel(plan_path), "md5": md5_file(plan_path)},
                             "last_step": last["file"] and {"path": _rel(last["file"]["path"]),
                                                            "md5": last["file"]["md5"]},
                             "summary": {"path": _rel(sp), "md5": md5_file(sp)},
                             "end_cdiff_rows": end_rows, "failed": failed, "first_divergent": first_div,
                             "undecided": len(undecided), "at": time.strftime("%Y-%m-%d %H:%M:%S")}
    pp = os.path.join(plan_out_dir, "plan_{0}.json".format(stage))
    with open(pp, "w", encoding="utf-8") as f:
        json.dump(out_plan, f, indent=1, default=str)
    summary["plan_out"] = {"path": _rel(pp), "md5": md5_file(pp)}
    summary["summary_path"] = sp
    summary["_state"] = st
    summary["_base_nodes"] = base_nodes
    summary["_S1"] = S1
    return summary


# ------------------------------------------------------------------------------------------------ self-test
def _synthetic():
    """A 2-loop toy: const K (#1) and E (#3), subVI B (#2) inside loop A (#100, body 20), subVI D (#4) outside,
    input tunnel #60, output tunnel #61, register pair #50/#51 carrying B's error chain; empty loop B (#200, body
    30) with one input tunnel #70 so the diagram tree knows its body. Top diagram 10."""
    T = []

    def t(tu, name, src, w, owner, ocls, fd, tc="Terminal"):
        T.append({"term_uid": tu, "term_name": name, "is_source": src, "wire_uid": w, "owner_uid": owner,
                  "owner_class": ocls, "frame_diagram": fd, "term_class": tc})
    t(1001, "v", True, 1, 1, "Constant", 10)
    t(1003, "err", True, 3, 3, "Constant", 10)
    t(1021, "in", False, 2, 2, "SubVI", 20)
    t(1022, "err in", False, 4, 2, "SubVI", 20)
    t(1023, "out", True, 6, 2, "SubVI", 20)
    t(1024, "err out", True, 5, 2, "SubVI", 20)
    t(1041, "x", False, 7, 4, "SubVI", 10)
    t(1042, "y", False, 0, 4, "SubVI", 10)
    t(1601, "v", False, 1, 60, "LoopTunnel", 10, "OuterTerminal")
    t(1602, "v", True, 2, 60, "LoopTunnel", 20, "InnerTerminal")
    t(1611, "out", False, 6, 61, "LoopTunnel", 20, "InnerTerminal")
    t(1612, "out", True, 7, 61, "LoopTunnel", 10, "OuterTerminal")
    t(1501, "err out", False, 5, 50, "RightShiftRegister", 20, "InnerTerminal")
    t(1502, "err out", True, 0, 50, "RightShiftRegister", 10, "OuterTerminal")
    t(1511, "err out", False, 3, 51, "LeftShiftRegister", 10, "OuterTerminal")
    t(1512, "err out", True, 4, 51, "LeftShiftRegister", 20, "InnerTerminal")
    t(1701, "v", False, 1, 70, "LoopTunnel", 10, "OuterTerminal")
    t(1702, "v", True, 0, 70, "LoopTunnel", 30, "InnerTerminal")
    objs = [{"uid": u, "class": c, "pos": [0, y], "owner": "Diagram"} for u, c, y in (
        (10, "TopLevelDiagram", 0), (100, "WhileLoop", 0), (200, "WhileLoop", 0), (1, "Constant", 0),
        (3, "Constant", 0), (2, "SubVI", 0), (4, "SubVI", 0), (60, "LoopTunnel", 5), (61, "LoopTunnel", 6),
        (50, "RightShiftRegister", 7), (51, "LeftShiftRegister", 7), (70, "LoopTunnel", 8))]
    loops = [{"loop_uid": 100, "right_uids": [50], "left_of": {"50": [51]}},
             {"loop_uid": 200, "right_uids": [], "left_of": {}}]
    return {"vi": "synthetic", "md5": None, "terminals": T, "objs": objs, "loops": loops, "fs_tunnel_pairs": None}


def _plan_full(stage, s1_rel):
    return {"schema": "stageplan/1", "stage": stage, "goal": "move B from loop A into loop B",
            "context": {"s1_graph": {"path": s1_rel}},
            "actions": [
                {"op": "move_in", "nodes": [2], "dest_diagram": 30},
                {"op": "add_shift_reg", "loop": 200, "body": 30, "as": "SR1"},
                {"op": "tunnel", "loop": 200, "body": 30, "dir": "in", "as": "T1"},
                {"op": "wire", "src": "1.v", "dst": "new:T1.outer"},
                {"op": "wire", "src": "new:T1.inner", "dst": "2.in"},
                {"op": "wire", "src": "2.err out", "dst": "new:SR1R.inner"},
                {"op": "wire", "src": "new:SR1L.inner", "dst": "2.err in"},
                {"op": "wire", "src": "3.err", "dst": "new:SR1L.outer"},
                {"op": "tunnel", "loop": 200, "body": 30, "dir": "out", "as": "T2"},
                {"op": "wire", "src": "2.out", "dst": "new:T2.inner"},
                {"op": "delete_wire", "wire_uid": 7},
                {"op": "wire", "src": "new:T2.outer", "dst": "4.x"},
                {"op": "delete_object", "uid": 61},
                {"op": "delete_object", "uid": 50},
                {"op": "delete_object", "uid": 60},
                {"op": "remove_bad_wires"}]}


def selftest():
    import tempfile
    tmp = tempfile.mkdtemp(prefix="stagesim_selftest_")
    gates = []

    def gate(label, ok, detail=""):
        gates.append((label, bool(ok)))
        print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)

    base = _synthetic()
    gp = os.path.join(tmp, "graph_base.json")
    with open(gp, "w", encoding="utf-8") as f:
        json.dump(base, f)
    s1p = gp                                            # S1 == the base (the original computation)
    quiet = lambda *_a: None                                                           # noqa: E731
    run = lambda plan, name, **kw: _run_plan(plan, name, gp, tmp, **kw)               # noqa: E731

    # G1-G2 schema
    pf = _plan_full("full", s1p)
    gate("G01 full plan validates as stageplan/1", protocol.validate_obj(pf)[0], protocol.validate_obj(pf)[1])
    bad = dict(pf, actions=[{"op": "teleport"}])
    gate("G02 an unknown op is refused by the schema", not protocol.validate_obj(bad)[0], protocol.validate_obj(bad)[1])

    # full run
    S = run(pf, "full", log=quiet)
    st1 = _j(S["steps"][1]["file"]["path"])
    eff1 = st1["effect"]
    gate("G03 move_in cut set == exactly the 4 wires crossing #2's boundary {2,4,5,6}", eff1["cut_set"] == [2, 4, 5, 6],
         eff1["cut_set"])
    gate("G04 moved node's terminals now sit on the destination diagram 30",
         all(r["frame_diagram"] == 30 for r in st1["state"]["terminals"] if r["owner_uid"] == 2))
    moved_w = [r["wire_uid"] for r in st1["state"]["terminals"] if r["owner_uid"] == 2]
    outside_kept = [r["wire_uid"] for r in st1["state"]["terminals"] if r["term_uid"] in (1602, 1512, 1501, 1611)]
    gate("G05 provisional cut rule: moved-side terminals unwired, outside keep their (half-)wires",
         moved_w == [0, 0, 0, 0] and sorted(outside_kept) == [2, 4, 5, 6], (moved_w, outside_kept))
    gate("G06 orphaned output tunnel #61 flips its outer to a sink (diag_c71 rule)",
         [f["tunnel"] for f in eff1["tunnel_flips"]] == [61], eff1["tunnel_flips"])
    rc = dict(((r["term_uid"], r["side"]), r) for r in eff1["reconnect"])
    gate("G07 reconnect table: #2 'in' -> S1 partner = const #1 'v' (collapsed through tunnel #60)",
         rc[(1021, "moved")]["s1"]["effective"] == ["1|Terminal|v|0"], rc[(1021, "moved")]["s1"])
    gate("G08 reconnect: #2 'out' (source) -> S1 consumer #4 'x'",
         rc[(1023, "moved")]["s1"]["effective"] == ["4|Terminal|x|0"], rc[(1023, "moved")]["s1"])
    gate("G09 the error-chain ends are tagged RULE-CHAIN-S1, not candidates",
         rc[(1022, "moved")]["chain"] and rc[(1024, "moved")]["chain"] and
         all(c["intent"]["cut_wire"] not in (4, 5) for c in _j(os.path.join(tmp, "sim", "full", "candidates.json"))["rows"]))
    cands = _j(os.path.join(tmp, "sim", "full", "candidates.json"))["rows"]
    gate("G10 the 2 non-chain cut rows go to candidates with >=2 mechanisms, jev_candidates shape",
         len(cands) == 2 and all(len(c["pairs"]) >= 2 and {"intent", "resolved", "pairs", "excluded"} <= set(c) and
                                 {"row_key", "src", "dst", "scope"} <= set(c["pairs"][0]) for c in cands),
         [(c["intent"]["cut_wire"], [p["mechanism"] for p in c["pairs"]]) for c in cands])
    st2 = _j(S["steps"][2]["file"]["path"])["state"]
    sr_terms = [r for r in st2["terminals"] if r["owner_uid"] in (st2["sym"]["new:SR1R"], st2["sym"]["new:SR1L"])]
    gate("G11 add_shift_reg: 2 new objects, 4 unnamed terminals, symbolic ids, loop table updated",
         len(sr_terms) == 4 and all(r["term_name"] == "" for r in sr_terms) and
         str(st2["sym"]["new:SR1R"]) in next(L for L in st2["loops"] if L["loop_uid"] == 200)["left_of"],
         st2["sym"])
    st4 = _j(S["steps"][4]["file"]["path"])
    gate("G12 wiring a sink to an already-wired source BRANCHES that wire (T1.outer joins wire 1)",
         st4["effect"]["how"] == "branch" and st4["effect"]["wire"] == 1, st4["effect"])
    st5 = _j(S["steps"][5]["file"]["path"])
    gate("G13 wiring from an unwired source makes a NEW (negative, symbolic) wire", st5["effect"]["how"] == "new" and
         st5["effect"]["wire"] < 0, st5["effect"])
    st14 = _j(S["steps"][14]["file"]["path"])
    gate("G14 delete_object on a RightShiftRegister deletes its Left pair too (stage_d1_l7_r rule)",
         st14["effect"]["deleted"] == [50, 51], st14["effect"])
    gate("G15 full plan: every step applied, end computation_diff(S1) == 0 rows, plan marked final",
         S["failed"] is None and S["end_cdiff_rows"] == [] and S["final"], (S["failed"], S["end_cdiff_rows"]))
    fin = _j(S["plan_out"]["path"])
    gate("G16 finalized plan carries base / plan / last-step / summary md5s",
         fin["final"] and all(len(fin["finalized"][k]["md5"]) == 32 for k in ("base", "plan_in", "last_step", "summary")),
         fin["finalized"].get("last_step"))
    files = sorted(glob.glob(os.path.join(tmp, "sim", "full", "step_*.json")))
    chain_ok = all(_j(files[i])["prev"]["md5"] == md5_file(files[i - 1]) for i in range(1, len(files)))
    gate("G17 one step file per action + base, named step_NN_<op>, each chained to the previous file's md5",
         len(files) == len(pf["actions"]) + 1 and os.path.basename(files[1]) == "step_01_move_in.json" and chain_ok,
         [os.path.basename(x) for x in files[:3]])
    gate("G18 every step records its model source ('provisional' with no opmodels dir)",
         all(s.get("model_source") == "provisional" for s in S["steps"][1:]), S["steps"][1].get("model_source"))

    # divergence
    pd = copy.deepcopy(pf)
    pd["stage"] = "late"
    pd["actions"].append({"op": "delete_wire", "at": {"uid": 2, "term": "in"}})
    S2 = run(pd, "late", log=quiet)
    gate("G19 a late break: not final, first divergent step == the last action (#17 delete_wire)",
         not S2["final"] and S2["first_divergent"] and S2["first_divergent"]["n"] == 17, S2["first_divergent"])
    pe = copy.deepcopy(pf)
    pe["stage"] = "early"
    pe["actions"] = [x for x in pe["actions"] if x.get("dst") != "4.x"]
    S3 = run(pe, "early", log=quiet)
    gate("G20 never reconnecting #4 'x': first divergent step == 1 (move_in), row stays to the end",
         not S3["final"] and S3["first_divergent"]["n"] == 1 and S3["end_cdiff_rows"] == ["4|Terminal|x|0"],
         (S3["first_divergent"], S3["end_cdiff_rows"]))

    # refusals
    po = {"schema": "stageplan/1", "stage": "occupied", "context": {"s1_graph": {"path": s1p}},
          "actions": [{"op": "wire", "src": "1.v", "dst": "4.x"}]}
    S4 = run(po, "occupied", log=quiet)
    gate("G21 wiring into a sink whose wire HAS a source stops the simulation at that step",
         S4["failed"] and S4["failed"]["n"] == 1 and "occupied" in S4["failed"]["error"] and not S4["final"], S4["failed"])
    ps = {"schema": "stageplan/1", "stage": "sym", "context": {"s1_graph": {"path": s1p}},
          "actions": [{"op": "wire", "src": "new:T9.inner", "dst": "4.y"}]}
    S5 = run(ps, "sym", log=quiet)
    gate("G22 a symbolic id used before any action creates it is refused", S5["failed"] and
         "not created" in S5["failed"]["error"], S5["failed"])
    pa = {"schema": "stageplan/1", "stage": "ambig", "context": {"s1_graph": {"path": s1p}},
          "actions": [{"op": "create", "class": "Function", "diagram": 10, "as": "C1",
                       "terminals": [{"name": "a", "is_source": False}, {"name": "a", "is_source": False},
                                     {"name": "r", "is_source": True}]},
                      {"op": "wire", "src": "1.v", "dst": "new:C1.a"}]}
    S6 = run(pa, "ambig", log=quiet)
    gate("G23 an ambiguous terminal name (two sinks 'a') is unaddressable without term_uid",
         S6["failed"] and S6["failed"]["n"] == 2 and "resolves to 2" in S6["failed"]["error"], S6["failed"])
    px = {"schema": "stageplan/1", "stage": "xdiag", "context": {"s1_graph": {"path": s1p}},
          "actions": [{"op": "delete_wire", "wire_uid": 7}, {"op": "wire", "src": "2.out", "dst": "4.x"}]}
    S7 = run(px, "xdiag", log=quiet)
    gate("G24 a plain wire across a structure border (diagram 20 -> 10) is refused", S7["failed"] and
         "border" in S7["failed"]["error"], S7["failed"])
    pu = copy.deepcopy(pf)
    pu["stage"] = "undecided"
    pu["actions"].insert(3, {"op": "decide", "options": ["tunnel", "shift_register"],
                             "row": {"row_key": {"src_uid": 1, "dst_uid": 2}}})
    S8 = run(pu, "undecided", log=quiet)
    gate("G25 a 'decide' row is listed as a candidate, never applied, and blocks finalize",
         S8["undecided"] == 1 and S8["end_cdiff_rows"] == [] and not S8["final"], (S8["undecided"], S8["final"]))
    pw = {"schema": "stageplan/1", "stage": "autodrop", "context": {"s1_graph": {"path": s1p}},
          "actions": [{"op": "delete_wire", "wire_uid": 6}, {"op": "delete_wire", "wire_uid": 7}]}
    S9 = run(pw, "autodrop", log=quiet)
    gate("G26 a LoopTunnel left with no wire after delete_wire is removed (tunnel #61)",
         _j(S9["steps"][2]["file"]["path"])["effect"]["auto_removed_tunnels"] == [61],
         _j(S9["steps"][2]["file"]["path"])["effect"])
    pr = {"schema": "stageplan/1", "stage": "rbw", "context": {"s1_graph": {"path": s1p}},
          "actions": [{"op": "move_in", "nodes": [2], "dest_diagram": 30}, {"op": "remove_bad_wires"}]}
    S10 = run(pr, "rbw", log=quiet)
    gate("G27 remove_bad_wires clears exactly the sourceless / sinkless wires the move left (2,4,5,6,7)",
         _j(S10["steps"][2]["file"]["path"])["effect"]["removed_wires"] == [2, 4, 5, 6, 7],
         _j(S10["steps"][2]["file"]["path"])["effect"])

    # op models
    md = os.path.join(tmp, "opmodels")
    os.makedirs(md)
    with open(os.path.join(md, "move_in.json"), "w", encoding="utf-8") as f:
        json.dump({"op": "move_in", "sim": {"tunnel_flip": False}}, f)
    with open(os.path.join(md, "wire_sr.json"), "w", encoding="utf-8") as f:
        json.dump({"op": "wire_sr", "rule": "no sim params"}, f)
    S11 = run(pf, "full_models", model_dir=md, log=quiet)
    s1src = S11["steps"][1]["model_source"]
    gate("G28 a measured model with `sim` params is used and recorded as measured:<file>@md5 (flip rule off)",
         s1src.startswith("measured:") and _j(S11["steps"][1]["file"]["path"])["effect"]["tunnel_flips"] == [], s1src)
    wsrc = next(s["model_source"] for s in S11["steps"] if s["op"] == "wire")
    gate("G29 a measured model file with no `sim` params is recorded as such, never silently",
         wsrc.startswith("measured-file-present-no-sim-params"), wsrc)

    # naming-free comparison
    Gs = graph(S["_state"])
    E = uid_edges(Gs)
    ren = dict((u, 9000 - u) for u in S["_state"]["sym"].values())
    ren_t = {}
    for r in S["_state"]["terminals"]:
        if r["term_uid"] < 0:
            ren_t[r["term_uid"]] = 8000 - r["term_uid"]
    E2 = set((k, ren.get(a, a), ren_t.get(ta, ta), ren.get(b, b), ren_t.get(tb, tb)) for k, a, ta, b, tb in E)
    clsmap = dict((u, obj_class(S["_state"], u)) for u in S["_state"]["sym"].values())
    cls2 = dict((ren[u], c) for u, c in clsmap.items())
    c1 = canon(E, S["_base_nodes"], clsmap.get)
    c2 = canon(E2, S["_base_nodes"], cls2.get)
    gate("G30 comparison up to new-uid naming: renumbered new objects compare equal (0 diff)",
         canon_diff(c1, c2)["n"] == 0, canon_diff(c1, c2)["n"])
    E3 = set(list(E2)[1:])
    gate("G31 ... and one missing edge is 1 diff", canon_diff(c1, canon(E3, S["_base_nodes"], cls2.get))["n"] == 1)
    gate("G32 nothing LabVIEW-side was imported (gscript / win32com / pythoncom absent)",
         not any(m in sys.modules for m in ("gscript", "win32com", "pythoncom", "stagekit")),
         [m for m in ("gscript", "win32com", "pythoncom", "stagekit") if m in sys.modules])
    n_pass = sum(1 for _l, ok in gates if ok)
    n_fail = len(gates) - n_pass
    first = next((l for l, ok in gates if not ok), None)
    print("=== GATES: {0} pass / {1} fail{2}".format(n_pass, n_fail, "; failing: " + first if first else ""))
    print(protocol.result_line(protocol.make_result(n_pass, n_fail, first)))
    return 0 if n_fail == 0 else 1


def _run_plan(plan, name, gp, tmp, model_dir=None, log=print):
    pp = os.path.join(tmp, "plan_in_{0}.json".format(name))
    plan = dict(plan, stage=name)
    with open(pp, "w", encoding="utf-8") as f:
        json.dump(plan, f)
    return simulate(pp, gp, out_root=os.path.join(tmp, "sim"), plan_out_dir=tmp,
                    model_dir=model_dir or os.path.join(tmp, "no_models"), log=log)


def main(argv):
    if len(argv) >= 2 and argv[1] == "selftest":
        return selftest()
    if len(argv) >= 4 and argv[1] == "simulate":
        kw = {}
        if "--out-root" in argv:
            kw["out_root"] = argv[argv.index("--out-root") + 1]
        if "--plan-out" in argv:
            kw["plan_out_dir"] = argv[argv.index("--plan-out") + 1]
        S = simulate(argv[2], argv[3], **kw)
        ok = S["final"]
        print("SUMMARY final={0} failed={1} end_cdiff_rows={2} first_divergent={3} candidates={4}".format(
            S["final"], S["failed"], S["end_cdiff_rows"], S["first_divergent"], S["n_candidates"]))
        arts = [{"path": S["plan_out"]["path"], "md5": S["plan_out"]["md5"]}]
        print(protocol.result_line(protocol.make_result(1 if ok else 0, 0 if ok else 1,
                                                        None if ok else "not final: {0}".format(
                                                            S["failed"] or S["first_divergent"]), arts)))
        return 0 if ok else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
