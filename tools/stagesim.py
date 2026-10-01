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
import re
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

TUN1 = ("LoopTunnel", "Tunnel")                     # single-object tunnels (kept for reference; the flip uses TUN_FLIP)
TUN_FLIP = ("LoopTunnel", "Tunnel", "SelectorTunnel")   # single-object tunnels that go undirected (k_op3_read_79.log)
TUN_SIDES = {"InnerTerminal": "OuterTerminal", "OuterTerminal": "InnerTerminal"}
DROP_WHEN_UNWIRED = ("LoopTunnel", "Tunnel")
SR_CLS = ("RightShiftRegister", "LeftShiftRegister")

# The plan table's ops with the provisional rule each one runs until chat-S1's measured model lands.
PROVISIONAL = {
    "move_in": {"params": {"cut_clears": "moved", "tunnel_flip": True,
                           # card 80-6 refit to the L2-A1 reads (tools/bench/l2a1_tunflip_80.log:195-236, fixture
                           # tools/bench/sim/l2a1_real_80.json): closure / sequential / moved-input flips / S2 no-flip /
                           # bare half-wires deleted - see op_move_in's docstring for each rule's evidence
                           "closure": True, "sequential": True, "flip_moved_inputs": True, "flip_needs_wired": True,
                           "bare_half_wire": "delete",
                           # card 101-4: a moved CONSTANT that was a cut wire's only source takes the wire with it
                           # (stage_d1_disp_r4.log:89-90, 1 sample); a node source keeps the outside half-wire
                           # (diag_c71_l7_1a_tunnels.log:60,64,70) - see only_source_fate
                           # card 101-5 TRIED AND REVERTED: {"node": "delete", "subvi": "keep"} (Bundler #11310, r5 k12)
                           # diverged from the r5 REAL reads at k24/k25 (ControlTerminal 8323 kept its half-wire after
                           # BuildArray #11261 moved) and dropped edge 11369->11270 at k12 (diag_c101c_resim.log:33,57);
                           # the fate is not a function of the source class alone - review owed, rule unchanged
                           "only_source": {"constant": "delete", "default": "keep"}},
                "evidence": "tools/bench/diag_c71_l7_1a_tunnels.log (TERM 2043/5050 is_source True->False, FLAG w4337/w5073 "
                            "n_src 0 after move_in #376); tools/bench/stage_d1_l7_1b_r3.log:207-214 (#376's cut terminals read "
                            "wire=0); tools/bench/l2a1_tunflip_80.log:195-196,215-216,235-236 (card 80-5 joint + singles)",
                "gaps": ["SR pair names reset on a cut (15/51 -> '' but 24/1108 kept 'error out') NOT modelled: names only, "
                         "computation_diff collapses registers", "the junk Invoke node each op leaves is NOT modelled "
                                                                     "(stagekit.junk_purge deletes it)",
                         "only_source 'delete' for a constant rests on ONE sample (r4 #8775) and on the single-sink "
                         "shape only; a constant feeding 2+ outside sinks keeps the old rule (unmeasured)"]},
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
             "gaps": ["PROVISIONAL (no opmodel): a sink on a sourceless half-wire is detached from it; the MEASURED rule is "
                      "opmodels/connect_from_wire.json `sourceless_sink: join` - with an UNWIRED source the half-wire "
                      "is joined and keeps its uid (opmodels/tunnel.json:200; stage_d1_l2a3_c109b.log:172, card 109-3)",
                      "an ALREADY-WIRED source onto a sink on a sourceless half-wire: not measured (modelled as branch)"]},
    "remove_bad_wires": {"params": {},
                         "evidence": "vigraph.build4 flags (a wire with n_src != 1 or no sink); stage_d1_l7_r_r2.log "
                                     "'RBW removed no live uid edge'",
                         "gaps": ["LabVIEW may also delete dangling tunnels on RBW - not modelled"]},
    "create": {"params": {}, "evidence": "plan-declared terminal list (no measurement yet); card 100-3: a WhileLoop/"
                                         "ForLoop owns NO row in the terminal read (0 WhileLoop/ForLoop-owned rows among "
                                         "the 5,061 of tools/bench/par1359_95_graph.json, which holds loops #637/#25380/"
                                         "#1359) - BUT (card 101-3) its BODY Diagram owns the unnamed i source row and, for a "
                                         "While, the unnamed cond sink row (#639: #644/#648, #25392: #25406/#25410, For "
                                         "#27537: #27543 only; stage_d1_disp_r2.log:57 real {'Diagram': 1}), "
                                         "a ControlTerminal row is its own node owned by its Diagram "
                                         "(vigraph.node_of), a Local's one terminal carries the control's label "
                                         "(par1359_95_graph.json #2991 'Total Lost Frames')",
               "gaps": ["terminal list must come from an op model or the subVI wiki",
                        "a created primitive's class string and terminal names are the plan's (Max & Min unmeasured)",
                        "values / representation / Visible are recorded, never simulated (the graph carries none)"]},
    "decide": {"params": {}, "evidence": "never applied - listed as a candidate row", "gaps": []},
    "gate": {"params": {}, "evidence": "card 100-3: a VALUE gate reads a constant's value at run time and stops the stage; "
                                       "the graph carries no values, so the simulation only checks the object exists",
             "gaps": ["the value itself is read only by the real run (OpConstValueB_v0)"]},
}
LOOP_CLS = ("WhileLoop", "ForLoop")
MODEL_ALIASES = {"wire": ("wire", "connect_from_wire", "wire_sr", "connect_nested", "connect"),
                 "tunnel": ("tunnel", "tunnel_create", "create_tunnel"),
                 "create": ("create", "const_create", "primitive_create", "create_const", "create_primitive", "const",
                            "primitive")}
ONLY_SINK_FATES = ("keep", "delete", "ambiguous")
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
            if op == "wire" and "border_source_wire" not in sim:
                rule = cfw_border_rule(m.get("data"))              # card 114-3 C2: read from the model's own samples
                if rule:
                    params["border_source_wire"] = rule
            return params, src, "opmodel file", []
        return params, "measured-file-present-no-sim-params:{0}@{1} (provisional rule ran)".format(
            _rel(m["path"]), m.get("md5")), base["evidence"], base["gaps"]
    return params, "provisional", base["evidence"], base["gaps"]


def cfw_border_rule(data):
    """card 114-3 C1/C2 (review archive/peer/2026-09-28-c114b-l2b3d.md s1): 'recreate' when the MEASURED connect_from_wire
    model says a connect that CROSSES A BORDER (the sample made a tunnel, checks.new_tunnels) from an already-WIRED source
    re-creates the source's wire under a new uid - every such sample records its own source terminal in
    checks.source_wire_replaced (opmodels/connect_from_wire.json:266 removes_rule; cfw_1 :45-56 half-wire w9415 -> w24358,
    cfw_2 :158-207 branched net w23519 -> w25348 with its 3 other sinks re-wired). None when the model has no such sample
    or any border sample disagrees (then the old branch rule runs). A SAME-DIAGRAM connect is not covered: it keeps the
    existing wire (stage_d1_l7_1b_r3.log:92,109 `UID 2` = 4969 / 3543), and the model has no same-diagram sample."""
    if not isinstance(data, dict):
        return None
    border = [s for s in data.get("samples") or [] if isinstance(s, dict) and (s.get("checks") or {}).get("new_tunnels")]
    if not border:
        return None
    for s in border:
        src = (s.get("target") or {}).get("src")
        rep = [x for x in (s["checks"].get("source_wire_replaced") or []) if isinstance(x, dict) and x.get("owner_uid") == src
               and len((x.get("changed") or {}).get("wire_uid") or []) == 2]
        if not rep:
            return None
    return "recreate"


def plan_tunnel_face(st, row):
    """True when `row` is a face of a tunnel an earlier `tunnel` action of THIS plan made (a symbolic LoopTunnel/Tunnel,
    negative uid) - i.e. the wire into it is the border-crossing half of a stagexec tunnel group (compile_plan kind
    'tunnel', executed as ONE connect_from_wire from the group's source to its sink)."""
    u = row.get("owner_uid")
    return isinstance(u, int) and u < 0 and row.get("owner_class") in TUN1 and u in st["sym"].values()


# ------------------------------------------------------------------------------------------------ state
def base_state(graph, context=None):
    ctx = context or {}
    # vigraph's load dedupe (card chat-S2b): the state holds what build4 sees, so row-counting ops agree with it
    rows, dd = V.dedupe_rows(graph["terminals"])
    st = {"terminals": [dict(r) for r in rows], "dedupe": dd, "objs": [dict(o) for o in graph.get("objs") or []],
          "loops": copy.deepcopy(graph.get("loops")), "fs_pairs": copy.deepcopy(graph.get("fs_tunnel_pairs")),
          "graph_summary": graph.get("graph_summary") or {}, "sym": {}, "diagrams": {}, "neg": 0,
          "removed_nodes": [], "vi": graph.get("vi"), "md5": graph.get("md5")}
    if ctx.get("loops"):
        st["loops"] = _j(_abs(ctx["loops"]["path"]))["loops"]
    if ctx.get("fs_pairs_wiki"):
        w = _j(_abs(ctx["fs_pairs_wiki"]["path"]))
        st["fs_pairs"] = w.get("fs_tunnel_pairs")
        st["graph_summary"] = w.get("graph_summary") or st["graph_summary"]
    # card 80-6: the OWNER map {uid: [owner class, owner uid]} (build_d1_v0.owner_of, as l2a1_facts_80.py records it under
    # "owners") - the only source of structure -> frame-diagram membership, which the terminal table does not carry
    own = graph.get("owners")
    if ctx.get("owners"):
        d = _j(_abs(ctx["owners"]["path"]))
        own = d.get(ctx["owners"].get("key", "owners"), d) if isinstance(d, dict) else d
    st["owners"] = dict((str(k), [v[0], int(v[1] or 0)]) for k, v in (own or {}).items())
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


def resolve_diag(st, ref):
    """A diagram field (dest_diagram / diagram / body / parent) -> a diagram uid. An int is a base diagram; the string
    'new:<alias>.body' is the body of a loop an EARLIER `create` of this plan made (card 100-3). Anything else, an
    alias no earlier action created, or '.body' of a non-loop is refused (SimError), exactly where a real stage stops."""
    if isinstance(ref, int) and not isinstance(ref, bool):
        return ref
    if isinstance(ref, str) and ref.startswith("new:"):
        # card 120-3 R2: + 'new:<case alias>.f<k>' = frame k of a Case structure an earlier `create` made (op_create
        # CaseStructure registers exactly these symbols); a '.body' ref is resolved exactly as before
        if not ref.endswith(".body") and not re.search(r"\.f[0-9]+$", ref):
            raise SimError("diagram reference {0!r}: a symbolic diagram is 'new:<alias>.body'".format(ref))
        if ref not in st["sym"]:
            raise SimError("symbolic diagram {0} is not created by any earlier action of this plan (unknown alias or "
                           "use before create)".format(ref))
        return st["sym"][ref]
    try:
        return int(ref)
    except (TypeError, ValueError):
        raise SimError("unaddressable diagram reference {0!r}".format(ref))


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
        elif not named and a["term"] == "value":
            pass              # card 100-3: '.value' = the node's one terminal of the wanted direction (a Local's terminal)
        else:
            rows = named
    if side:
        rows = [r for r in rows if r["term_class"] == ("InnerTerminal" if side == "inner" else "OuterTerminal")]
    rows = [r for r in rows if bool(r["is_source"]) == bool(want_source)]
    ctf = (st.get("case_tunnel_frame") or {}).get(str(uid))
    if ctf is not None and len(set(int(r["frame_diagram"] or 0) for r in rows)) > 1:
        # card 120-3 R2: a case tunnel THIS plan made has one inner face per frame; its group wires the frame named by
        # the `tunnel` action's `body` (op_tunnel -> _case_tunnel) - only that frame's face is the address
        rows = [r for r in rows if r["term_class"] != "InnerTerminal" or int(r["frame_diagram"] or 0) == int(ctf)]
    uniq = dict(((r["term_uid"], r["term_class"], r["frame_diagram"]), r) for r in rows)
    if len(uniq) != 1:
        raise SimError("address {0} ({1}) resolves to {2} {3} terminal(s): {4}".format(
            a, uid, len(uniq), "source" if want_source else "sink",
            sorted((r["term_uid"], r["term_name"], r["term_class"]) for r in uniq.values())[:6]))
    return list(uniq.values())[0]


def graph(st, labels=None, fs_pairs=None):
    """fs_pairs (card 106-3): an override for the state's own `fs_pairs` (None = the state's) - the finalize cdiff graph
    passes the S1 wiki pairs here (cdiff_inputs) without writing them into the step state."""
    rec = {"terminals": st["terminals"], "graph_summary": st.get("graph_summary") or {}}
    G = JC.from_parts(rec, st["objs"], st["loops"], labels if labels is not None else {},
                      fs_pairs if fs_pairs is not None else st.get("fs_pairs"), "sim")
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
def _flip_orphaned_output_tunnels(st, wires, seeds=(), needs_wired=False, reg=None):
    """A tunnel left with NO SOURCE on its driving side becomes undirected: every terminal on its other side that read
    as a source reads as a sink afterwards (NI 'Wire connected to an undirected tunnel'). Repeated to a fixpoint.
    Output direction (inner sink orphaned -> outer flips): diag_c71_l7_1a_tunnels.log TERM 2043/5050 (LoopTunnel).
    Input direction (outer sink orphaned -> EVERY inner flips), SelectorTunnel: tools/bench/k_op3_read_79.log:93-111
    (card 79-7 M1: after move_in #5058, #2765's outer 2811 and inners 2789/2792 all is_source=False, wires 505/3472/
    2924 kept, 0 sources each). A tunnel with several driving-side terminals (a case tunnel's per-frame inners) flips
    only when NONE of them still sits on a sourced wire.
    card 80-6 additions: `seeds` = sink rows whose wire was CLEARED by the op (a MOVED tunnel's driving-side terminal on
    a cut wire) - the tunnel is checked exactly like one whose wire lost its source (l2a1_tunflip_80.log:195: the moved
    #5540/#10445 input SelectorTunnels #5702 #5725 #5825 #5967 #10750 flipped every inner, wired or not). `needs_wired`:
    a tunnel whose opposite-side terminals are ALL unwired does not flip (l2a1_tunflip_80.log:215-216,235-236: the
    case-selector 'Tunnel's #10465/#5603, inners unwired, stayed sources; compare n 0)."""
    flipped, todo = [], set(w for w in wires if w)
    done = set()

    def try_flip(r):
        rows = node_rows(st, r["owner_uid"])
        if any(o["term_class"] == r["term_class"] and not o["is_source"] and o["wire_uid"] and
               has_source(st, o["wire_uid"]) for o in rows):
            return
        other = [o for o in rows if o["term_class"] == TUN_SIDES[r["term_class"]] and o["is_source"]]
        if needs_wired and not any(o["wire_uid"] for o in other):
            return
        for o in other:
            o["is_source"] = False
            rec = {"tunnel": r["owner_uid"], "term_uid": o["term_uid"], "side": o["term_class"], "wire": o["wire_uid"]}
            if o["term_class"] == "OuterTerminal":
                rec["outer_term_uid"] = o["term_uid"]
            if reg is not None:                  # card 81-5 F1: remember what the flip turned, for the un-flip
                reg[str(o["term_uid"])] = r["owner_uid"]
            flipped.append(rec)
            if o["wire_uid"]:
                todo.add(o["wire_uid"])

    def flippable(r):
        return not r["is_source"] and r["term_class"] in TUN_SIDES and r["owner_class"] in TUN_FLIP

    for r in seeds:
        if flippable(r) and (r["owner_uid"], r["term_class"]) not in done:
            done.add((r["owner_uid"], r["term_class"]))
            try_flip(r)
    while todo:
        w = todo.pop()
        if has_source(st, w):
            continue
        for r in wire_rows(st, w):
            if flippable(r):
                try_flip(r)
    return flipped


def _unflip_restored_tunnels(st, seeds, cascade=False):
    """card 81-5 F1, MEASURED (tools/bench/l2a1_unflip_81_run1.log, l2a1_unflip_81_run2.log): after the joint L2-A1 move
    flipped every inner of the input SelectorTunnels #5702/#5725 to a sink, wiring each one's OUTER from a new register's
    L.inner turned EVERY inner back into a source - wired (5705 w5710, 5733 w6030) and unwired (6033, 5729) alike - while the
    outer stayed a sink and the untouched #5967 stayed flipped (control). Rule: a driving-side sink of a tunnel whose wire now
    has a source reverts every opposite-side terminal that the move's flip turned (st['flip_reg'], written only when the
    move_in model has `unflip_on_source`). `cascade` = the reverted terminals' wires are re-checked the same way (an output
    tunnel fed by a reverted inner), set from run 2's read of #5680/#6016 (move_in.json `unflip_cascade`)."""
    reg = st.get("flip_reg") or {}
    out, todo = [], list(seeds)
    while todo:
        r = todo.pop()
        if r["is_source"] or r["term_class"] not in TUN_SIDES or r["owner_class"] not in TUN_FLIP:
            continue
        if not (r["wire_uid"] and has_source(st, r["wire_uid"])):
            continue
        for o in node_rows(st, r["owner_uid"]):
            if o["term_class"] == TUN_SIDES[r["term_class"]] and not o["is_source"] and \
                    reg.get(str(o["term_uid"])) == r["owner_uid"]:
                o["is_source"] = True
                reg.pop(str(o["term_uid"]), None)
                out.append({"tunnel": r["owner_uid"], "term_uid": o["term_uid"], "side": o["term_class"],
                            "wire": o["wire_uid"]})
                if cascade and o["wire_uid"]:
                    todo += [x for x in wire_rows(st, o["wire_uid"]) if x["term_uid"] != o["term_uid"]]
    return out


def seed_base_flips(st, cascade=False):
    """card 112-1 T3 (PD225(h)3 (iii), brief_110-3 (e)): flips made in an EARLIER session. A base-graph tunnel of a
    TUN_FLIP class whose terminals are ALL sinks is undirected (the flipped state _flip_orphaned_output_tunnels leaves, saved
    to disk: B2-11/-14's #9087/#29911 on the L2-B1 bed, split_plan_111_l2b2.md §3). Every one of its terminals is registered
    in st['flip_reg'] exactly as a same-session flip is, and st['unflip'] is armed, so op_wire's _unflip_restored_tunnels
    reverts the OPPOSITE side once one side gets a source (the 81-5 F1 rule, measured on same-session flips; on a
    saved-file flip it is the PREDICTION the executor's per-step compare checks). Returns the seeded records."""
    reg = st.setdefault("flip_reg", {})
    by = collections.defaultdict(list)
    for r in st["terminals"]:
        if r["owner_class"] in TUN_FLIP and r["term_class"] in TUN_SIDES:
            by[r["owner_uid"]].append(r)
    out = []
    for tun, rows in sorted(by.items()):
        sides = set(r["term_class"] for r in rows)
        if len(sides) != 2 or any(r["is_source"] for r in rows):
            continue
        for r in rows:
            if str(r["term_uid"]) not in reg:
                reg[str(r["term_uid"])] = tun
                out.append({"tunnel": tun, "term_uid": r["term_uid"], "side": r["term_class"], "wire": r["wire_uid"]})
    if out and not st.get("unflip"):
        st["unflip"] = {"cascade": bool(cascade)}
    return out


def seed_base_flips_modelled(st, models):
    """seed_base_flips under the switch that arms the same-session un-flip (the move_in model's `unflip_on_source`,
    card 81-5 F1). ONE definition for simulate() and stagexec's dry backends, so the dry state equals step_00."""
    Pm = model_for("move_in", models)[0]
    return seed_base_flips(st, Pm.get("unflip_cascade", False)) if Pm.get("unflip_on_source", False) else []


def _fate_by_class(rule, src_class):
    if isinstance(rule, dict):
        # card 101-5: a SubVI source is its own kind ('subvi'; falls back to 'node' when a rule has no 'subvi' key)
        # because the measured fates differ - SubVI #376 KEPT its half-wire (diag_c71_l7_1a_tunnels.log:60,64),
        # primitive Bundler #11310 LOST it (stage_d1_disp_r5.log:249, dangling_sim_only [11365]).
        sc = str(src_class)
        kind = "constant" if sc.endswith("Constant") else ("tunnel" if "Tunnel" in sc else (
            "subvi" if sc == "SubVI" else "node"))
        rule = rule.get(kind, rule.get("node" if kind == "subvi" else kind, rule.get("default", "keep")))
    return rule if rule in ONLY_SINK_FATES else "keep"


def only_sink_fate(P, src_class):
    """The only-sink sub-rule (card chat-S3; tools/bench/opmodels_onlysink.log): what happens to a wire whose ONLY
    sink(s) sat on the moved / deleted node. `P['only_sink']` is 'keep' (a source-side half-wire), 'delete', 'ambiguous'
    (kept in the simulation, and the executor accepts either outcome), or {'constant': fate, 'tunnel': fate,
    'node': fate} by the SOURCE's class. Missing => 'keep' (the provisional rule)."""
    return _fate_by_class(P.get("only_sink", "keep"), src_class)


def only_source_fate(P, src_class):
    """card 101-4, the MIRROR of only_sink_fate: a CUT wire whose ONLY source sat on the MOVED node and whose one other
    terminal is a sink OUTSIDE the moved set. 'keep' = the outside sink stays on a sourceless half-wire (MEASURED for a
    SubVI source: move_in #376 + junk purge left 1931 on w5274 and 5044 on w5056, diag_c71_l7_1a_tunnels.log:60,64,70);
    'delete' = the whole wire goes, the outside sink reads wire 0 (MEASURED for a DigitalNumericConstant source: move_in
    #8775 -> sink 8753 of #8741 read neither dangling nor on an edge, stage_d1_disp_r4.log:89-90, 1 sample); 'ambiguous'.
    `P['only_source']` like `P['only_sink']` (a fate or a by-source-class dict). Missing => 'keep' (the pre-101-4 rule)."""
    return _fate_by_class(P.get("only_source", "keep"), src_class)


def _apply_only_source(st, P, cut):
    """card 101-4: for each cut wire (w -> (moved rows, outside rows)) with exactly ONE row on the moved side, a source,
    and exactly ONE outside row, a sink (the r4 shape; a constant feeding 2+ outside sinks is UNMEASURED and keeps the
    pre-101-4 rule), apply only_source_fate to the OUTSIDE row. Runs before the cut clears the moved side and before the
    tunnel flips, so a deleted wire has no rows left to flip. Returns the records (`allow_either` reads 'ambiguous')."""
    out = []
    for w in sorted(cut):
        ins, outs = cut[w]
        if len(ins) != 1 or not ins[0]["is_source"] or len(outs) != 1 or outs[0]["is_source"]:
            continue
        fate = only_source_fate(P, ins[0]["owner_class"])
        if fate == "keep":
            continue
        if fate == "delete":
            outs[0]["wire_uid"] = 0
        out.append({"wire": w, "src_term_uid": ins[0]["term_uid"], "src_uid": V.node_of(ins[0]),
                    "src_class": ins[0]["owner_class"], "sink_term_uid": outs[0]["term_uid"], "fate": fate})
    return out


def _apply_only_sink(st, P, wires, gone):
    """For each wire in `wires` whose every SINK is owned by a node in `gone` and whose source is outside: apply the
    only-sink fate to the source row. Returns the records (the executor reads `allow_either`)."""
    out = []
    for w in sorted(set(x for x in wires if x)):
        rows = wire_rows(st, w)
        srcs = [r for r in rows if r["is_source"] and V.node_of(r) not in gone]
        snks = [r for r in rows if not r["is_source"]]
        if len(srcs) != 1 or not snks or any(V.node_of(r) not in gone for r in snks):
            continue
        fate = only_sink_fate(P, srcs[0]["owner_class"])
        if fate == "delete":
            srcs[0]["wire_uid"] = 0
        out.append({"wire": w, "src_term_uid": srcs[0]["term_uid"], "src_uid": V.node_of(srcs[0]),
                    "src_class": srcs[0]["owner_class"], "fate": fate})
    return out


def closure_of(st, uid):
    """(nodes, diagrams): everything a move of `uid` carries - `uid` itself plus every node with a terminal on a diagram
    nested (at any depth) under it. Membership comes from the owner map (st['owners'], build_d1_v0.owner_of rows); the
    walk is tools/bench/l2a1_facts_80.py:40-46's `closure`, whose 28-node joint set the 80-5 real move matched (compare
    only_sim_terms/only_real_terms both [], l2a1_tunflip_80.log:196)."""
    O = st.get("owners") or {}
    D, grow = set(), {uid}
    while grow:
        f = set(int(d) for d, (c, u) in O.items() if u in grow) - D
        D |= f
        grow = set(int(u) for u, (c, d) in O.items() if d in f and c == "Diagram" and int(u) not in D) - {uid}
    return {uid} | set(V.node_of(r) for r in st["terminals"] if int(r.get("frame_diagram") or 0) in D), D


def op_move_in(st, a, P, S1, labels):
    """MOVE (card 80-6 refit to the L2-A1 reads, fixture tools/bench/sim/l2a1_real_80.json):
    R-CLOSURE  a named structure carries every node on its nested frames (closure_of; needs the owner map - a named uid
               owning no terminal and no frame is REFUSED, never moved as nothing).
    R-SEQ      several named uids are moved ONE AT A TIME in the listed order (the real op moves one uid per call,
               stagekit.move_in; stagexec refuses a multi-node action). A wire between a moved member and a member not
               yet moved is CUT at the earlier move - l2a1_tunflip_80.json runs[0] only_sim_edges (#10247's three edges,
               #9647's two, #17289->#10950). `joint: true` keeps the old simultaneous move (no measured op does that).
    R-FLIP-IN  a MOVED tunnel whose driving-side sink was cleared by the cut flips its other side (seeds of
               _flip_orphaned_output_tunnels); the cascade reaches output tunnels of the same structure (#5680 #6016 outers).
    R-S2       no flip when every opposite-side terminal is unwired (#5603/#10465 case selectors).
    R-BARE     a wire with exactly ONE terminal, that terminal on a moved node, is deleted - AFTER the flips (w5637/w5975 on
               #5680/#6016's outers; the half-wires an earlier sequential step left on #10253/#5634/#17487)."""
    tops = [resolve_uid(st, u) for u in a["nodes"]]
    dest = resolve_diag(st, a["dest_diagram"])
    if len(tops) > 1 and P.get("sequential", True) and not a.get("joint"):
        effs, cands = [], []
        for u in tops:
            e, c = _move_one(st, [u], dest, P, S1, labels)
            effs.append(e)
            cands += c
        cat = lambda k: [x for e in effs for x in e[k]]                                   # noqa: E731
        return {"sequential": [dict((k, v) for k, v in e.items() if k != "reconnect") for e in effs],
                "moved": sorted(set(cat("moved"))), "dest_diagram": dest, "cut_set": sorted(set(cat("cut_set"))),
                "n_cut": sum(e["n_cut"] for e in effs), "reconnect": cat("reconnect"),
                "cleared_term_uids": sorted(set(cat("cleared_term_uids"))), "tunnel_flips": cat("tunnel_flips"),
                "rule_rows": cat("rule_rows"), "only_sink": cat("only_sink"), "only_source": cat("only_source"),
                "allow_either": sorted(set(cat("allow_either"))), "bare_deleted": cat("bare_deleted")}, cands
    return _move_one(st, tops, dest, P, S1, labels)


def _move_one(st, tops, dest, P, S1, labels):
    moved, inner_d = set(), set()
    for u in tops:
        n, D = closure_of(st, u) if P.get("closure", True) else ({u}, set())
        if not D and not node_rows(st, u):
            raise SimError("move_in: #{0} owns no terminal and no frame diagram (a structure needs context.owners "
                           "for its closure)".format(u))
        moved |= n
        inner_d |= D
    G0 = graph(st, labels)
    inside = [r for r in st["terminals"] if V.node_of(r) in moved]
    if not inside:
        raise SimError("move_in: none of {0} owns a terminal".format(sorted(moved)))
    by_w = collections.defaultdict(lambda: ([], []))
    n_rows = collections.Counter()
    for r in st["terminals"]:
        if r["wire_uid"]:
            by_w[r["wire_uid"]][0 if V.node_of(r) in moved else 1].append(r)
            n_rows[r["wire_uid"]] += 1
    cut = dict((w, v) for w, v in by_w.items() if v[0] and v[1])
    bare = [(w, v[0][0]) for w, v in sorted(by_w.items()) if n_rows[w] == 1 and v[0]] \
        if P.get("bare_half_wire", "keep") == "delete" else []
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
    only = _apply_only_sink(st, P, cut.keys(), moved)
    only_src = _apply_only_source(st, P, cut)                     # card 101-4 (stage_d1_disp_r4.log:90)
    for r in inside:
        if int(r.get("frame_diagram") or 0) not in inner_d:      # rows on the structure's nested frames stay put
            r["frame_diagram"] = dest
    cleared, seeds = [], []
    for w, (ins, outs) in cut.items():
        victims = ins if P.get("cut_clears", "moved") == "moved" else outs
        for r in victims:
            r["wire_uid"] = 0
            cleared.append(r["term_uid"])
            if not r["is_source"] and V.node_of(r) in moved:
                seeds.append(r)
    reg = None
    if P.get("unflip_on_source", False):         # card 81-5 F1: op_wire reverts these flips (_unflip_restored_tunnels)
        reg = st.setdefault("flip_reg", {})
        st["unflip"] = {"cascade": bool(P.get("unflip_cascade", False))}
    # PD214(d)1 (cycle 102): an OUTSIDE sink whose wire the only-source rule DELETED is a seed too - its tunnel lost its
    # source exactly like one left on a sourceless wire (r5 k12 real read: 11365 wire 0 AND #11363's outer 11369 flipped;
    # diag_c101c_resim.log:33 - without this seed the node:delete re-sim kept edge 11369->11270, the one thing LabVIEW
    # did not). A deleted wire has no rows left for the wire walk, so the seed is the only way the flip is reached.
    del_seeds = [r for r in st["terminals"] if r["term_uid"] in set(x["sink_term_uid"] for x in only_src if x["fate"] == "delete")]
    flipped = _flip_orphaned_output_tunnels(
        st, cut.keys(), list(seeds if P.get("flip_moved_inputs", False) else ()) + del_seeds,
        needs_wired=P.get("flip_needs_wired", False), reg=reg) if P.get("tunnel_flip", True) else []
    bare_deleted = []
    for w, r in bare:
        if r["wire_uid"] == w:
            r["wire_uid"] = 0
            bare_deleted.append({"wire": w, "term_uid": r["term_uid"], "node": V.node_of(r), "is_source": r["is_source"]})
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
    return {"moved": sorted(moved), "tops": tops, "inner_diagrams": sorted(inner_d), "dest_diagram": dest,
            "cut_set": sorted(cut), "n_cut": len(cut),
            "reconnect": table, "cleared_term_uids": sorted(cleared), "tunnel_flips": flipped,
            "bare_deleted": bare_deleted, "rule_rows": rule_rows, "only_sink": only, "only_source": only_src,
            "allow_either": sorted([x["src_term_uid"] for x in only if x["fate"] == "ambiguous"] +
                                   [x["sink_term_uid"] for x in only_src if x["fate"] == "ambiguous"])}, cands


def _parent_of(st, body, a, labels):
    if a.get("parent") is not None:
        return resolve_diag(st, a["parent"])
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
    loop, body = resolve_uid(st, a["loop"]), resolve_diag(st, a["body"])
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


def _case_tunnel(st, a, case, body, parent):
    """card 120-3 R2 (i)/(ii): a DATA tunnel of a Case structure, made by the border-crossing wire of its `tunnel` group.
    MEASURED shape (tools/bench/selftest_c120_caseshape.log, graph_qrt_pool_20260928.json #2222/#2857/#3826): ONE
    SelectorTunnel object (owner CaseStructure), ONE OuterTerminal on the parent diagram and ONE InnerTerminal on EVERY frame;
    dir 'in' = outer sink + inner sources, dir 'out' = outer source + inner sinks. The group wires the frame `body` only;
    the other frames' inner faces stay UNWIRED. ASSUMED, UNMEASURED here (no sample of a freshly scripted case tunnel):
    (1) connecting across a case border makes exactly this object (as a loop border makes a LoopTunnel, tunnel.json);
    (2) an OUTPUT tunnel is created with 'Use Default If Unwired' OFF (LabVIEW's default), so each unwired frame breaks
    the VI until it is wired or the flag is set - recorded as `broken_unless_wired`, never hidden."""
    frames = [int(k) for k, v in (st.get("owners") or {}).items() if v[0] == "CaseStructure" and int(v[1] or 0) == case]
    if body not in frames:
        raise SimError("tunnel {0}: body #{1} is not a frame of CaseStructure #{2} (frames {3})".format(a.get("as"), body, case, frames))
    if a.get("indexing"):
        raise SimError("tunnel {0}: a case tunnel has no indexing mode".format(a.get("as")))
    din = a.get("dir", "in") == "in"
    T = _new_obj(st, "SelectorTunnel", "CaseStructure")
    o = _new_term(st, T, "SelectorTunnel", "OuterTerminal", not din, parent)
    inners = [(f, _new_term(st, T, "SelectorTunnel", "InnerTerminal", din, f)) for f in frames]
    st.setdefault("case_tunnel_frame", {})[str(T)] = body
    st["diagrams"][str(body)] = parent
    unw = [f for f in frames if f != body]
    eff = {"tunnel": _sym(st, a.get("as") or "T{0}".format(-T), T), "case": case, "dir": a.get("dir", "in"), "indexing": False,
           "outer": o, "inner": dict(inners)[body], "inners": [t for _f, t in inners], "body": body, "parent": parent,
           "frame": body, "unwired_frames": unw, "model": "measured shape (selftest_c120_caseshape.log); creation UNMEASURED"}
    if not din:
        eff.update(use_default_if_unwired="ASSUMED False (LabVIEW default; UNMEASURED for a scripted case tunnel)",
                   broken_unless_wired=unw)
    return eff, []


def op_tunnel(st, a, P, S1, labels):
    loop, body = resolve_uid(st, a["loop"]), resolve_diag(st, a["body"])
    parent = _parent_of(st, body, a, labels)
    if obj_class(st, loop) == "CaseStructure":          # card 120-3 R2: a case's data tunnel (a loop is unchanged below)
        return _case_tunnel(st, a, loop, body, parent)
    T = _new_obj(st, "LoopTunnel", obj_class(st, loop) or "WhileLoop")
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
    gone = list(dict.fromkeys(gone))
    ws = set(r["wire_uid"] for u in gone for r in node_rows(st, u) if r["wire_uid"])
    only = _apply_only_sink(st, P, ws, set(gone))
    out = {}
    for u in gone:
        if obj_class(st, u) is not None:
            out[u] = _drop_node(st, u)
    flipped = _flip_orphaned_output_tunnels(st, ws) if P.get("tunnel_flip", False) else []
    return {"deleted": sorted(out), "class": cls, "terminals_removed": sum(out.values()), "only_sink": only,
            "allow_either": sorted(x["src_term_uid"] for x in only if x["fate"] == "ambiguous"),
            "tunnel_flips": flipped}, []


def cond_row(st, loop):
    """card 101-3: the conditional-terminal row of a While loop a `create` made = the body Diagram's one unnamed
    'Terminal' SINK (op_create). Exactly one, else SimError."""
    body = [int(b) for b, (c, u) in (st.get("owners") or {}).items() if int(u) == loop]
    rs = [r for r in st["terminals"] if r["owner_uid"] in body and r["owner_class"] == "Diagram" and
          r["term_class"] == "Terminal" and not r["is_source"]]
    if len(rs) != 1:
        raise SimError("the conditional terminal of While #{0}: {1} body sink row(s) on {2}".format(loop, len(rs), body))
    return rs[0]


def cond_target(st, ref):
    """'new:<alias>.cond' naming a WhileLoop an earlier `create` made -> that loop's uid, else None. The conditional
    terminal is the body Diagram's unnamed sink row (cond_row; card 101-3 - it was modelled as absent until then)."""
    if isinstance(ref, dict):
        head, term = ref.get("uid"), ref.get("term")
    elif isinstance(ref, str) and ref.startswith("new:"):
        head, _d, term = ref.partition(".")
    else:
        return None
    if term != "cond" or not (isinstance(head, str) and head.startswith("new:")):
        return None
    u = resolve_uid(st, head)
    if obj_class(st, u) != "WhileLoop":
        raise SimError("{0}: '.cond' names a While loop's conditional terminal; {1} is {2}".format(ref, head, obj_class(st, u)))
    return u


def op_wire(st, a, P, S1, labels):
    s = resolve_addr(st, a["src"], True)
    loop = cond_target(st, a["dst"])
    if loop is not None:
        # card 100-3 R8: a body node's source -> the loop's conditional terminal (OpStopFromNode_v0). card 101-3: the
        # conditional terminal IS in the read (the body's unnamed sink row, cond_row) and is wired like any sink.
        body = [int(b) for b, (c, u) in (st.get("owners") or {}).items() if int(u) == loop]
        if int(s["frame_diagram"] or 0) not in body:
            raise SimError("wire {0} -> {1}: the source is on diagram {2}, not on the loop's body {3}".format(
                a["src"], a["dst"], s["frame_diagram"], body))
        d = cond_row(st, loop)
        if st.setdefault("cond_wired", {}).get(str(loop)) or d["wire_uid"]:
            raise SimError("wire -> {0}: the conditional terminal is already wired".format(a["dst"]))
        how = "branch" if s["wire_uid"] else "new"
        if not s["wire_uid"]:
            s["wire_uid"] = new_uid(st)
        d["wire_uid"] = s["wire_uid"]
        st["cond_wired"][str(loop)] = s["term_uid"]
        return {"wire": s["wire_uid"], "how": how, "src_term_uid": s["term_uid"], "dst_term_uid": d["term_uid"],
                "cond_of": loop}, []
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
    join = bool(detached and P.get("sourceless_sink") == "join")
    recreated, rewired = None, []
    if s["wire_uid"] and P.get("border_source_wire") == "recreate" and plan_tunnel_face(st, d):
        # card 114-3 C2 (cfw_border_rule): the border-crossing connect from a WIRED source RE-CREATES the source's wire -
        # the old uid is LOST (and may be re-issued at once to another object: the junk Invoke took 5174,
        # stage_d1_l2b3.log:74,94), a new wire carries the source, every old sink (same (src, sink) pairs) and the new
        # tunnel face. Measured: connect_from_wire.json:266; real B3 end = 6 new / lost [5174, 5336, 28392]
        # (stage_d1_l2b3.log:103)
        recreated = s["wire_uid"]
        w, how = new_uid(st), "recreate"
        for r in wire_rows(st, recreated):
            r["wire_uid"] = w
            if r is not s:
                rewired.append(r["term_uid"])
    elif s["wire_uid"]:
        w, how = s["wire_uid"], "branch"
    elif join:
        # card 109-3 (review archive/peer/2026-09-27-c109b-l2a3-dgate.md s1/s6): an UNWIRED source onto a sink on a
        # sourceless half-wire JOINS that half-wire and the wire KEEPS ITS UID - measured, opmodels/tunnel.json:200
        # ("a sink-side half-wire is JOINED and keeps its uid", tunnel_2: the outer took w2160) and the c109b run
        # (stage_d1_l2a3_c109b.log:120,:141 connect readback `UID 2` = 9921 / 11389; :172 real new [] lost []).
        # An ALREADY-WIRED source onto such a stub is NOT measured and keeps the branch rule above (tunnel_1 went the
        # other way on the source side, tunnel.json:200).
        w, how = detached, "join_stub"
        s["wire_uid"] = w
    else:
        w, how = new_uid(st), "new"
        s["wire_uid"] = w
    d["wire_uid"] = w
    joined = []
    if join:
        # measured (opmodels/tunnel.json tunnel_2): a sink on a sourceless half-wire is JOINED - every other terminal
        # still on that half-wire ends up on the resulting net as well (on the same uid when how == 'join_stub')
        for r in wire_rows(st, detached):
            if r is s or r is d:
                continue
            r["wire_uid"] = w
            joined.append(r["term_uid"])
    eff = {"wire": w, "how": how, "src_term_uid": s["term_uid"], "dst_term_uid": d["term_uid"],
           "detached_from": detached, "joined": joined, "kept_stub_uid": how == "join_stub"}
    if recreated:                                # only then: every other effect record stays byte-identical
        eff.update(recreated_from=recreated, rewired=sorted(rewired))
    if st.get("unflip"):                         # card 81-5 F1 (measured l2a1_unflip_81_run1.log); absent = old behaviour
        eff["unflipped"] = _unflip_restored_tunnels(st, [d], st["unflip"].get("cascade", False))
    return eff, []


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
    dropped = []
    if P.get("drop_unconnected_fsit"):
        # measured (opmodels/remove_bad_wires.json, RBW_1 #2283/#2301): a FlatSequenceInnerTunnel the deletion left
        # with no wired terminal is deleted too
        touched = set(V.node_of(r) for w in bad for r in by_w[w] if r["owner_class"] == "FlatSequenceInnerTunnel")
        for u in sorted(touched):
            if not any(r["wire_uid"] for r in node_rows(st, u)):
                _drop_node(st, u)
                dropped.append(u)
    return {"removed_wires": sorted(bad), "dropped_fsit": dropped}, []


# card 120-3 R1 (PD237(k)): the Dequeue Element node gscript.queue_node('dequeue') places (gscript.py:1339-1371). Terminal
# NAMES and DIRECTIONS are MEASURED: docs/NAMES.md:993-995 (test_opqueue.log: "Dequeue Element: queue, timeout in ms (-1),
# error in (no error) -> queue out, element, timed out?, error out"), the same set as docs/NAMES.md:910-911. UNMEASURED for
# Dequeue: the rows' term_class (only Obtain's rows were read - ParameterTerminal, tools/bench/facts_c120_qrtw.json:119-200)
# and the Terminals[] read order - the scratch check reads both (tools/bench/scratch_plan_c120_routes.md).
QUEUE_TERM_TABLE = {"dequeue": (("queue", False), ("timeout in ms (-1)", False), ("error in (no error)", False),
                                ("queue out", True), ("element", True), ("timed out?", True), ("error out", True))}
QUEUE_TERM_UNMEASURED = {"dequeue": ("term_class", "Terminals[] read order")}
# card 120-3 R2: gscript.case_in (gscript.py:3508-3543) = build_case on the TOP-LEVEL diagram with its selector wired from
# the top-level panel control `label`, then OpMoveIn_v0 into the loop body (which SEVERS that wire, docs/cycle27-plan.md:
# 846-851), then owner + frames read back. Frame names default False/True (a boolean selector).
CASE_FRAMES_DEFAULT = ("False", "True")
CASE_ASSUMED = ("the moved case keeps an UNWIRED selector (the severed wire leaves no stub on the case side)",
                "the panel control `label` is left as it was before case_in (no stub wire) - UNMEASURED",
                "build_case accepts the frame names as given for a boolean selector - UNMEASURED (its contract names "
                "'0, Default','1' for a numeric one, gscript.py:3508)")


def _dequeue_check(a):
    """card 120-3 R1: every DECLARED terminal of a dequeue create is in the measured table with the same direction."""
    tab = dict(QUEUE_TERM_TABLE["dequeue"])
    bad = [(t["name"], t["is_source"]) for t in a.get("terminals") or [] if tab.get(t["name"]) is None or
           bool(tab[t["name"]]) != bool(t["is_source"])]
    if bad or a.get("src_into") != "queue":
        raise SimError("create dequeue {0}: declared terminal(s) {1} not in the measured Dequeue table (docs/NAMES.md:993-995)"
                       "{2}".format(a.get("id"), bad, "" if a.get("src_into") == "queue" else
                                    "; src_into {0!r} is not the refnum sink 'queue'".format(a.get("src_into"))))


def _create_case(st, a, dg, name, eff):
    """card 120-3 R2: a Case structure in a LOOP BODY (gscript.case_in's contract, gscript.py:3509). MEASURED shape of an
    existing case (tools/bench/selftest_c120_caseshape.log, graph_qrt_pool_20260928.json #2222/#2857/#3826): the
    CaseStructure object (owner Diagram), one frame Diagram per frame (owners[frame] = [CaseStructure, case]), and the
    SELECTOR = a 'Tunnel' object (owner CaseStructure) with ONE unnamed OuterTerminal SINK on the parent diagram and ONE
    unnamed InnerTerminal SOURCE per frame. The selector comes out UNWIRED (case_in's move severs it) and is wired by a later
    `wire` to 'new:<selector_as>.outer'. Symbols: new:<as>, new:<as>.f<k> (frame k, in `frames` order), new:<selector_as>."""
    names = list(a.get("frames") or CASE_FRAMES_DEFAULT)
    wired = a.get("src") is not None and not a.get("label")      # card 123-7: gscript.case_wired (selector wired from `src`)
    if not name or not a.get("selector_as") or not (a.get("label") or wired):
        raise SimError("create CaseStructure needs `as`, `selector_as` and `label` (the top-level panel control case_in wires "
                       "to the selector before the move severs it) or `src` (case_wired: a node OUTPUT on the same diagram)")
    if len(names) < 2 or len(set(names)) != len(names):
        raise SimError("create CaseStructure {0}: frames {1} (need >= 2 distinct names)".format(name, names))
    if wired:
        return _create_case_wired(st, a, dg, name, eff, names)
    own = (st.get("owners") or {}).get(str(dg))
    if not own or own[0] not in LOOP_CLS:
        raise SimError("create CaseStructure on diagram {0}: not a For/While body in the owners map ({1}) - gscript.case_in "
                       "places a case in a loop body (gscript.py:3509)".format(dg, own))
    cts = [r for r in st["terminals"] if r["term_class"] == "ControlTerminal" and r["term_name"] == a["label"]]
    if len(cts) != 1 or not cts[0]["is_source"]:
        raise SimError("create CaseStructure {0}: {1} panel terminal(s) labelled {2!r}, need exactly one CONTROL (case_in's "
                       "build_case wires the selector from it by label)".format(name, len(cts), a["label"]))
    u = _new_obj(st, "CaseStructure", "Diagram")
    frames = []
    for _k in names:
        f = new_uid(st)
        st["diagrams"][str(f)] = dg
        st.setdefault("owners", {})[str(f)] = ["CaseStructure", u]
        frames.append(f)
    S = _new_obj(st, "Tunnel", "CaseStructure")
    so = _new_term(st, S, "Tunnel", "OuterTerminal", False, dg)
    si = [_new_term(st, S, "Tunnel", "InnerTerminal", True, f) for f in frames]
    key = _sym(st, name, u)
    fk = [_sym(st, "{0}.f{1}".format(name, k), f) for k, f in enumerate(frames)]
    eff.update(node=key, frames=frames, frame_syms=fk, frame_names=names, selector=_sym(st, a["selector_as"], S),
               selector_outer=so, selector_inners=si, selector_ct=cts[0]["term_uid"], selector_ct_wired=bool(cts[0]["wire_uid"]),
               assumed=list(CASE_ASSUMED))
    return eff, []


CASE_WIRED_ASSUMED = ("the source must be a Node output (gscript.case_wired resolves it through Diagram.Nodes[]; constants, "
                      "tunnels and shift registers are not Nodes) - a refusal here, not a measurement",)


def _create_case_wired(st, a, dg, name, eff, names):
    """card 123-7 (PD248(d)): gscript.case_wired = struct_copy_nested(CaseStructure, DonorCase_v0 #742) onto Diagram dg (ANY
    diagram - no loop-body rule) + the selector's outer face <- `src` (a node OUTPUT on the SAME diagram, connect_nested_v1)
    + the junk-Invoke purge. MEASURED (diag_c123_struct.log:43-44 / diag_c123_wired.log): the same object shape as
    _create_case (CaseStructure, one frame Diagram per frame, a selector 'Tunnel' with one OUTER SINK on dg and one INNER
    SOURCE per frame) and the selector WIRED from `src` (a branch when `src` is already wired). Frames: the donor's numeric
    '0, Default'/'1' are renamed by the Boolean source to False/True, so ONLY ('False','True') is accepted."""
    if list(names) != list(CASE_FRAMES_DEFAULT):
        raise SimError("create CaseStructure {0} (case_wired): frames {1} - the donor case + a Boolean selector gives exactly "
                       "{2}".format(name, names, list(CASE_FRAMES_DEFAULT)))
    s = resolve_addr(st, a["src"], True)
    if not s["is_source"] or int(s["frame_diagram"] or 0) != int(dg):
        raise SimError("create CaseStructure {0} (case_wired): src #{1} source={2} on diagram {3}, case on {4} - needs a SOURCE "
                       "on the same diagram (connect_nested_v1 same-diagram triple)".format(name, s["term_uid"], s["is_source"],
                                                                                           s["frame_diagram"], dg))
    oc = str(s["owner_class"])
    if oc.endswith("Constant") or "Tunnel" in oc or "ShiftRegister" in oc or s["term_class"] in ("OuterTerminal", "InnerTerminal"):
        raise SimError("create CaseStructure {0} (case_wired): src #{1} is owned by {2} #{3}, not a Node (Nodes[] route)".format(
            name, s["term_uid"], oc, s["owner_uid"]))
    u = _new_obj(st, "CaseStructure", "Diagram")
    frames = []
    for _k in names:
        f = new_uid(st)
        st["diagrams"][str(f)] = dg
        st.setdefault("owners", {})[str(f)] = ["CaseStructure", u]
        frames.append(f)
    S = _new_obj(st, "Tunnel", "CaseStructure")
    so = _new_term(st, S, "Tunnel", "OuterTerminal", False, dg)
    si = [_new_term(st, S, "Tunnel", "InnerTerminal", True, f) for f in frames]
    key = _sym(st, name, u)
    fk = [_sym(st, "{0}.f{1}".format(name, k), f) for k, f in enumerate(frames)]
    row = next(r for r in st["terminals"] if r["term_uid"] == so)
    eff["src_branch"] = bool(s["wire_uid"])
    eff["wire"] = _join(st, s, row)
    eff.update(node=key, frames=frames, frame_syms=fk, frame_names=list(names), selector=_sym(st, a["selector_as"], S),
               selector_outer=so, selector_inners=si, selector_src=s["term_uid"], wired=True, assumed=list(CASE_WIRED_ASSUMED))
    return eff, []


def _join(st, s, d):
    """Wire source row s to sink row d (d must be unwired): s's wire is branched, else a new (negative) wire."""
    if d["wire_uid"]:
        raise SimError("create: the sink #{0} {1!r} is already wired (w{2})".format(d["term_uid"], d["term_name"], d["wire_uid"]))
    if not s["wire_uid"]:
        s["wire_uid"] = new_uid(st)
    d["wire_uid"] = s["wire_uid"]
    return s["wire_uid"]


def op_create(st, a, P, S1, labels):
    """card 100-3: `diagram` may be 'new:<alias>.body'. By class:
    WhileLoop / ForLoop - the loop object + a NEW body diagram (sym new:<as> and new:<as>.body; owners/diagrams/loops
                          tables updated); NO terminal row (the read carries none for a loop).
    ControlTerminal     - one row, its own node (term_class ControlTerminal, owner = its Diagram), named `label`;
                          `indicator` true = a sink, else a source; `born_on` <source addr> joins the indicator to that
                          source's wire; `on` <sink addr> wires the control to that (unwired) sink.
    anything else       - the plan's `terminals` (a Local, a copied/created primitive); a constant with `on` and no
                          `terminals` gets ONE source row named after that sink and is wired to it."""
    cls, dg = a["class"], resolve_diag(st, a["diagram"])
    name = a.get("as")
    eff = {"class": cls, "diagram": dg}
    if cls in LOOP_CLS:
        u = _new_obj(st, cls, "Diagram")
        body = new_uid(st)
        st["diagrams"][str(body)] = dg
        st.setdefault("owners", {})[str(body)] = [cls, u]
        if st["loops"] is None:
            st["loops"] = []
        st["loops"].append({"loop_uid": u, "right_uids": [], "left_of": {}})
        key = _sym(st, name or "L{0}".format(-u), u)
        _sym(st, (name or "L{0}".format(-u)) + ".body", body)
        # card 101-3 (PD213(h)(1)-(2), MEASURED in par1359_95_graph.json, result_101-1.json): the BODY Diagram owns the
        # loop's own terminals as term_class 'Terminal' rows with an EMPTY name, owner = the body, frame = the body:
        # While bodies #639 (#644 source i, #648 sink cond) and #25392 (#25406 source, #25410 sink); For body #27537 only
        # #27543 (source i). Unwired rows are in the read too (#27543 wire 0). So: i for every loop, cond for a While.
        rows = [_new_term(st, body, "Diagram", "Terminal", True, body)]
        if cls == "WhileLoop":
            rows.append(_new_term(st, body, "Diagram", "Terminal", False, body))
        else:
            # card 101-3, stage_d1_disp_r3.log:69 (real op 3 create For: new object {'Tunnel': 1} #23403) and
            # diag_c101_forn.log (all 17 S1 ForLoops): a For loop's count terminal N is a 'Tunnel' object (objs owner
            # 'ForLoop', same pos as the loop) with an unnamed OuterTerminal SINK on the PARENT diagram and an unnamed
            # InnerTerminal SOURCE on the body (#27492: #27491 frame 81548 / #27494 frame 27537)
            N = _new_obj(st, "Tunnel", "ForLoop")
            rows.append(_new_term(st, N, "Tunnel", "OuterTerminal", False, dg))
            rows.append(_new_term(st, N, "Tunnel", "InnerTerminal", True, body))
            eff["count_terminal"] = N
        eff.update(node=key, body=body, terminals=rows)
        return eff, []
    if cls == "ControlTerminal":
        if not a.get("label"):
            raise SimError("create ControlTerminal: `label` is required (it is the row's name)")
        t = new_uid(st)
        ind = bool(a.get("indicator"))
        st["terminals"].append({"term_uid": t, "term_name": a["label"], "is_source": not ind, "wire_uid": 0,
                                "owner_uid": dg, "owner_class": "Diagram", "frame_diagram": dg,
                                "term_class": "ControlTerminal"})
        row = st["terminals"][-1]
        if ind and a.get("born_on") is not None:
            s = resolve_addr(st, a["born_on"], True)
            if int(s["frame_diagram"] or 0) != dg:
                raise SimError("create indicator on {0}: source on diagram {1}, indicator on {2}".format(
                    a["born_on"], s["frame_diagram"], dg))
            eff["wire"] = _join(st, s, row)
        elif not ind and a.get("on") is not None:
            d = resolve_addr(st, a["on"], False)
            if int(d["frame_diagram"] or 0) != dg:
                raise SimError("create control on {0}: sink on diagram {1}, control on {2}".format(a["on"], d["frame_diagram"], dg))
            eff["wire"] = _join(st, row, d)
        eff.update(node=_sym(st, name or "C{0}".format(-t), t), terminals=[t], visible=a.get("visible"))
        return eff, []
    if cls == "CaseStructure" and a.get("donor_uid") is None and not a.get("prim"):
        # card 120-3 R2: a NEW case (gscript.case_in); a copied case (donor_uid, copy_in) keeps the generic path below
        return _create_case(st, a, dg, name, eff)
    if a.get("queue_kind") == "dequeue":         # card 120-3 R1: the declared terminals against the measured table
        _dequeue_check(a)
    u = _new_obj(st, cls, "Diagram")
    decl = list(a.get("terminals") or [])
    d = None
    if a.get("on") is not None:
        d = resolve_addr(st, a["on"], False)
        if int(d["frame_diagram"] or 0) != dg:
            raise SimError("create {0} on {1}: sink on diagram {2}, object on {3}".format(cls, a["on"], d["frame_diagram"], dg))
        if not decl:
            decl = [{"name": d["term_name"], "is_source": True}]
    ts = [_new_term(st, u, cls, t.get("term_class") or "Terminal", t["is_source"], dg, t["name"]) for t in decl]
    if a.get("src") is not None and a.get("src_into"):
        # card 118-1 (queue route, gscript.queue_node): the op wires `src` (an existing SOURCE on the same diagram) into
        # the new node's sink named `src_into` - a branch when the source is already wired, else a new wire
        s = resolve_addr(st, a["src"], True)
        into = [r for r in st["terminals"] if r["owner_uid"] == u and not r["is_source"] and r["term_name"] == a["src_into"]]
        if len(into) != 1:
            raise SimError("create {0}: {1} declared sinks named {2!r}, need exactly 1".format(cls, len(into), a["src_into"]))
        sd = int(s["frame_diagram"] or 0)
        if sd == dg:
            eff["src_branch"] = bool(s["wire_uid"])
            eff["wire"] = _join(st, s, into[0])
        elif str(dg) in st["diagrams"] and int(st["diagrams"][str(dg)]) == sd and (st.get("owners") or {}).get(str(dg)):
            # card 118-3 (PD234(i), measured prior art build_track_v6_queue.py:202 + NAMES.md:911-912): the creator wires a
            # PARENT-diagram refnum source into a node it places in a loop BODY and auto-makes the (non-indexed) LoopTunnel:
            # outer sink face on the parent joined to `src` (a branch when already wired), inner source face on the body
            # joined to the new node's sink. The body must be a loop body this plan created (st.diagrams/owners know it).
            lcls, loop = st["owners"][str(dg)]
            Tn = _new_obj(st, "LoopTunnel", lcls)
            o = _new_term(st, Tn, "LoopTunnel", "OuterTerminal", False, sd)
            i = _new_term(st, Tn, "LoopTunnel", "InnerTerminal", True, dg)
            for x in st["objs"]:
                if x["uid"] == Tn:
                    x["indexing"] = False
            rowof = lambda t: next(r for r in st["terminals"] if r["term_uid"] == t)                  # noqa: E731
            eff["src_branch"] = bool(s["wire_uid"])
            eff["outer_wire"] = _join(st, s, rowof(o))
            eff["wire"] = _join(st, rowof(i), into[0])
            eff["auto_tunnel"] = {"tunnel": _sym(st, (name or "N{0}".format(-u)) + ".tunnel", Tn), "loop": loop, "outer": o, "inner": i,
                                  "indexing": False}
        else:
            raise SimError("create {0}: src on diagram {1}, node on {2} (same diagram, or a loop body of that diagram created by "
                           "this plan)".format(cls, s["frame_diagram"], dg))
    if d is not None:
        src = [r for r in st["terminals"] if r["owner_uid"] == u and r["is_source"]]
        if len(src) != 1:
            raise SimError("create {0} on {1}: {2} source terminals, need exactly 1".format(cls, a["on"], len(src)))
        eff["wire"] = _join(st, src[0], d)
    eff.update(node=_sym(st, name or "N{0}".format(-u), u), terminals=ts)
    return eff, []


def op_gate(st, a, P, S1, labels):
    """card 100-3: a VALUE gate on a base constant (the real run reads it and stops when it equals `stop_if`). The graph
    carries no values: the simulation checks the object exists with the expected class and changes nothing."""
    u = resolve_uid(st, a["uid"])
    cls = obj_class(st, u)
    want = a.get("class")
    if cls is None or (want and cls != want):
        raise SimError("gate: #{0} is {1}, expected {2}".format(u, cls, want or "an object in the graph"))
    return {"gate": a.get("read"), "uid": u, "class": cls, "stop_if": a.get("stop_if"), "value": "read by the real run only"}, []


def op_decide(st, a, P, S1, labels):
    c = {"intent": dict(a.get("row") or {}, from_="stagesim decide", options=a["options"]),
         "resolved": {}, "pairs": [{"row_key": (a.get("row") or {}).get("row_key"), "mechanism": m}
                                   for m in a["options"]], "excluded": {}, "undecided": True}
    return {"undecided": True, "options": a["options"]}, [c]


OPS = {"move_in": op_move_in, "add_shift_reg": op_add_shift_reg, "tunnel": op_tunnel, "delete_wire": op_delete_wire,
       "delete_object": op_delete_object, "wire": op_wire, "remove_bad_wires": op_remove_bad_wires,
       "create": op_create, "decide": op_decide, "gate": op_gate}


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


def cdiff_inputs(plan, st, labels=None):
    """card 106-3 (PD217(d), facts_c104c_e3.json): the node labels + fs tunnel pairs the FINALIZE cdiff graph is built
    with = the E3 inputs (stagexec.e3_graph: JC.node_labels_default() and the S1 wiki's fs_tunnel_pairs, context
    fs_pairs_wiki else s1_key). Before this the cdiff graph had NO labels and the base graph's (0) fs pairs, which made
    the 15 PD213(d) class-(4) rows of plan_disp look open. Explicit `labels` win; the fs pairs are used only when the
    state carries none. A plan with no wiki S1 (the synthetic self-tests, context s1_graph) -> the old inputs.
    Returns (labels, fs_pairs_or_None, record)."""
    ctx = plan.get("context") or {}
    wiki_p = _abs(ctx["fs_pairs_wiki"]["path"]) if ctx.get("fs_pairs_wiki") else \
        os.path.join(JC.WIKI, ctx["s1_key"] + ".json") if ctx.get("s1_key") else None
    if wiki_p is None:
        lab = labels if labels is not None else {}
        return lab, None, {"labels": "explicit" if labels is not None else "none", "labels_n": len(lab),
                           "fs_pairs": "state", "fs_pairs_n": len(st.get("fs_pairs") or [])}
    lab = labels if labels is not None else JC.node_labels_default()
    fs = None if st.get("fs_pairs") else (_j(wiki_p).get("fs_tunnel_pairs") or None)
    return lab, fs, {"labels": "explicit" if labels is not None else "node_labels_default", "labels_n": len(lab),
                     "fs_pairs": _rel(wiki_p) if fs is not None else "state",
                     "fs_pairs_n": len(fs if fs is not None else st.get("fs_pairs") or [])}


E3_CLASS_RE = re.compile(r"PD213\(d\)\((\d)\)")


def open_row_class(r):
    """PD217(c): a plan open row's PD213(d) class - a `class` field, else the class the finalizer wrote into `why`
    ("PD213(d)(4): ..."). None when the row names none (a class is never guessed). Shared with stagexec.e3_eval
    (moved here from stagexec.py by card 106-3, unchanged)."""
    c = r.get("class")
    if c is None:
        m = E3_CLASS_RE.search(str(r.get("why") or ""))
        c = m.group(1) if m else None
    try:
        return int(c)
    except (TypeError, ValueError):
        return None


def c4_check(S1, G, c4):
    """PD217(c): for every class-(4) (node, term) row, the end graph's effective sources == S1's, on every sink key of
    that name in either graph. Returns (bad list, n keys compared). Shared by stagexec.e3_eval and the finalize rule."""
    ma, mb, bad, n = {}, {}, [], 0
    for node, t in c4:
        keys = sorted(set(k for gg in (S1, G) for k in V.terminals(gg, node=node, is_source=False) if V.key_parts(k)[2] == t))
        if not keys:
            bad.append({"row": (node, t), "why": "no sink key in S1 or the end graph"})
        for k in keys:
            n += 1
            sa = sorted(V.effective_sources(S1, k, ma)) if k in S1["rows"] else None
            sb = sorted(V.effective_sources(G, k, mb)) if k in G["rows"] else None
            if sa != sb:
                bad.append({"row": (node, t), "sink": k, "S1": sa, "end": sb})
    return bad, n


def open_rows_classed(plan, S1, G, end_pairs):
    """card 106-3: the finalize open-row rule under PD217(c)'s classes (the E3 rule applied at plan time): every declared
    open row carries a class 1-4, the end rows == the class 1-3 rows, and every class-(4) row's end sources == S1's."""
    cls = [(int(r["node"]), r["term"], open_row_class(r)) for r in plan.get("open_rows") or []]
    unclassed = sorted(set((n, t) for n, t, c in cls if c not in (1, 2, 3, 4)))
    want = sorted(set((n, t) for n, t, c in cls if c in (1, 2, 3)))
    c4 = sorted(set((n, t) for n, t, c in cls if c == 4))
    bad, nk = c4_check(S1, G, c4) if (S1 is not None and G is not None and not unclassed) else ([], 0)
    ok = bool(cls) and not unclassed and end_pairs is not None and list(end_pairs) == want and not bad
    return {"ok": ok, "want": [list(x) for x in want], "c4_n": len(c4), "c4_keys": nk, "c4_bad": bad[:10],
            "unclassed": [list(x) for x in unclassed]}


def route_report(plan_out_path, model_dir=OPMODEL_DIR, log=print, require_final=True):
    """card 112-1 T4: stagexec.dry_run on a just-finalized plan -> {status, first_fail, rows: [{k, op, ids, route, how,
    unroutable}]}. stagexec imports this module, so the import is lazy. Any exception fails closed (status ERROR).
    require_final=False = the diagnostic routability run on a non-final plan (stagexec.dry_run's card 100-3 mode)."""
    try:
        import stagexec as X
        st_, ff, ex = X.dry_run(plan_out_path, log=lambda *_a: None, model_dir=model_dir, require_final=require_final)
    except Exception as e:                                                    # noqa: BLE001 - fail closed, reported
        return {"status": "ERROR", "first_fail": "{0}: {1}".format(type(e).__name__, e)[:1500], "rows": []}
    un = dict((tuple(u["acts"]), u["err"]) for u in (getattr(ex, "unroutable", None) or []) if u.get("acts"))
    rows = []
    for r in ex.report:
        if r.get("op") in ("base", "from_step"):
            continue
        chk = ((r.get("result") or {}).get("check") or {}) if isinstance(r.get("result"), dict) else {}
        rows.append({"k": r.get("k"), "op": r.get("op"), "ids": r.get("ids"), "route": chk.get("route") or r.get("op"),
                     "how": chk.get("how"), "unroutable": un.get(tuple(r.get("acts") or ())) or chk.get("unroutable")})
    for acts, err in un.items():                                            # rows the run never reached (a hard stop)
        if not any(tuple(x.get("acts") or ()) == acts for x in ex.report):
            rows.append({"k": None, "op": None, "ids": None, "acts": list(acts), "route": None, "how": None, "unroutable": err})
    for x in rows:
        log("  ROUTE {0} {1} {2}: {3}{4}".format(x.get("k"), x.get("op"), x.get("ids"), x.get("route"),
                                                "  UNROUTABLE " + str(x["unroutable"])[:200] if x.get("unroutable") else ""))
    return {"status": st_, "first_fail": ff, "rows": rows}


def simulate(plan_path, graph_path, out_root=SIM_ROOT, plan_out_dir=BENCH, model_dir=OPMODEL_DIR, labels=None,
             log=print, route_check=True):
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
    # card 112-1 T3: flips saved in the base file are seeded under the SAME model switch that arms the same-session un-flip
    # (move_in `unflip_on_source`, card 81-5 F1); with no such model (the self-test's provisional rules) nothing changes
    base_flips = seed_base_flips_modelled(st, models)
    if base_flips:
        log("  BASE-FLIPS seeded {0} terminal(s) on {1} undirected tunnel(s): {2}".format(
            len(base_flips), len(set(f["tunnel"] for f in base_flips)), sorted(set(f["tunnel"] for f in base_flips))[:20]))
    base_nodes = set(V.node_of(r) for r in st["terminals"])
    cd_lab, cd_fs, cd_rec = cdiff_inputs(plan, st, labels)          # card 106-3: the finalize graph = the E3 inputs
    labels = labels if labels is not None else {}                   # the ops keep their old inputs (step states unchanged)
    steps, all_cands, cls_new = [], [], {}

    def write_step(n, name, action, effect, src, prev, err=None):
        p = os.path.join(out_dir, "step_{0:02d}_{1}.json".format(n, name))
        rec = {"schema": "stagesim-step/1", "stage": stage, "n": n, "action": action, "model_source": src,
               "prev": prev, "effect": effect, "error": err, "state": st}
        with open(p, "w", encoding="utf-8") as f:
            json.dump(rec, f, separators=(",", ":"), default=str)
        return {"path": p, "md5": md5_file(p)}

    prev = write_step(0, "base", None, {"graph": _rel(graph_path), "graph_md5": md5_file(graph_path)}, "input", None)
    g_end = graph(st, cd_lab, cd_fs) if S1 is not None else None
    cd0 = V.computation_diff(S1, g_end) if S1 is not None else None
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
            g_end = graph(st, cd_lab, cd_fs)
            cd = V.computation_diff(S1, g_end)
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
    # FINALIZE RULE (card chat-S3): a plan may declare `open_rows` - rows it leaves for a later stage by design (e.g.
    # 376 'current frame data array in', Pre-decided 175). Final iff the end rows are EXACTLY those, no more, no fewer.
    open_rows = sorted(set((int(r["node"]), r["term"]) for r in plan.get("open_rows") or []))
    end_pairs = sorted(set((V.key_parts(k)[0], V.key_parts(k)[2]) for k in end_rows)) if end_rows is not None else None
    open_legacy = end_pairs is not None and end_pairs == open_rows
    # card 106-3: OR the PD217(c) classed rule (end rows == the class 1-3 rows, class-4 sources == S1's) - the E3 rule
    classed = open_rows_classed(plan, S1, g_end if not failed else None, end_pairs)
    open_match = open_legacy or classed["ok"]
    final = bool(S1 is not None and not failed and open_match and not undecided)
    cands_path = os.path.join(out_dir, "candidates.json")
    with open(cands_path, "w", encoding="utf-8") as f:
        json.dump({"schema": "stagesim-candidates/1", "stage": stage, "note": "jev_candidates shape; the "
                   "simulator decided none of these", "rows": all_cands}, f, indent=1, default=str)
    summary = {"schema": "stagesim-summary/1", "stage": stage, "plan": {"path": _rel(plan_path),
               "md5": md5_file(plan_path)}, "graph": {"path": _rel(graph_path), "md5": md5_file(graph_path)},
               "s1": (plan.get("context") or {}).get("s1_key") or (plan.get("context") or {}).get("s1_graph"),
               "models_loaded": dict((k, {"path": _rel(v["path"]), "md5": v.get("md5")}) for k, v in models.items()),
               "steps": steps, "failed": failed, "final": final, "end_cdiff_rows": end_rows,
               "open_rows": [list(x) for x in open_rows], "open_rows_match": open_match,
               "open_rows_match_legacy": open_legacy, "open_rows_classed": classed, "cdiff_inputs": cd_rec,
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
                             "open_rows": [list(x) for x in open_rows], "open_rows_match": open_match,
                             "open_rows_match_legacy": open_legacy, "open_rows_classed": classed,
                             "cdiff_inputs": cd_rec,
                             "step_files": [{"n": s["n"], "op": s["op"], "path": _rel(s["file"]["path"]),
                                             "md5": s["file"]["md5"]} for s in steps if s.get("file")],
                             "undecided": len(undecided), "at": time.strftime("%Y-%m-%d %H:%M:%S")}
    pp = os.path.join(plan_out_dir, "plan_{0}.json".format(stage))
    with open(pp, "w", encoding="utf-8") as f:
        json.dump(out_plan, f, indent=1, default=str)
    if final and route_check:
        # card 112-1 T4 (PD225(h)3 (iv), brief_110-3 (b)): FINALIZE RUNS THE ROUTE CHECK. The finalized plan is dry-run
        # through stagexec's collecting backend, whose connect / wire_sr / branch / create take the SAME route functions
        # the real backend takes (connect_route, Addr) - so an UNROUTABLE row fails at plan time, not at the dry of the
        # launch card (plan_l2b1_dry3.log:84). Per-row route report in finalized.route_check.
        rc = route_report(pp, model_dir, log)
        out_plan["finalized"]["route_check"] = rc
        if rc["status"] != "PASS":
            final = out_plan["final"] = summary["final"] = False
            log("  FINALIZE REFUSED: route check {0}: {1}".format(rc["status"], str(rc["first_fail"])[:600]))
        with open(pp, "w", encoding="utf-8") as f:
            json.dump(out_plan, f, indent=1, default=str)
        summary["route_check"] = rc
    elif route_check and not failed and S1 is not None:
        # review archive/peer/2026-09-27-c112a-b2aroute.md: a NON-final plan also carries the route report, ADVISORY
        # (stagexec.dry_run's require_final=False diagnostic mode); it never makes a plan final
        rc = route_report(pp, model_dir, log, require_final=False)
        rc["advisory"] = True
        out_plan["finalized"]["route_check"] = rc
        with open(pp, "w", encoding="utf-8") as f:
            json.dump(out_plan, f, indent=1, default=str)
        summary["route_check"] = rc
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
    # card chat-S3: open_rows finalize rule
    po1 = copy.deepcopy(pe)
    po1["stage"] = "openrows"
    po1["open_rows"] = [{"node": 4, "term": "x", "why": "left for a later stage (self-test)"}]
    S12 = run(po1, "openrows", log=quiet)
    gate("G33 open_rows == the end rows => final (the #4 'x' row declared open)", S12["final"] and S12["open_rows_match"],
         (S12["final"], S12["end_cdiff_rows"], S12["open_rows"]))
    po2 = copy.deepcopy(pf)
    po2["stage"] = "openextra"
    po2["open_rows"] = [{"node": 4, "term": "x", "why": "declared but not open (self-test)"}]
    S13 = run(po2, "openextra", log=quiet)
    gate("G34 a declared open row that is NOT open (end rows []) => not final", not S13["final"] and not S13["open_rows_match"],
         (S13["final"], S13["end_cdiff_rows"]))
    po3 = copy.deepcopy(pd)
    po3["stage"] = "openfewer"
    po3["actions"] = [x for x in po3["actions"] if x.get("dst") != "4.x"]
    po3["open_rows"] = [{"node": 4, "term": "x", "why": "only one of two open rows declared (self-test)"}]
    S14 = run(po3, "openfewer", log=quiet)
    gate("G35 more end rows than declared open => not final", not S14["final"] and len(S14["end_cdiff_rows"]) == 2,
         S14["end_cdiff_rows"])
    # card 106-3: the classed finalize rule (PD217(c) at plan time) - end rows [4 x]; 2 'in' is reconnected (== S1)
    r4x1 = {"node": 4, "term": "x", "why": "PD213(d)(1): left for a later stage (self-test)"}
    r2in4 = {"node": 2, "term": "in", "why": "PD213(d)(4): already open at the base (self-test)"}
    pc1 = copy.deepcopy(pe)
    pc1["open_rows"] = [r4x1, r2in4]
    S15 = run(pc1, "classed", log=quiet)
    gate("G57 classed rule: end rows == the class 1-3 rows [4 x] and the class-4 row 2 'in' has S1's sources => final "
         "(the legacy all-rows rule alone would refuse it)", S15["final"] and not S15["open_rows_match_legacy"] and
         S15["open_rows_classed"]["ok"] and S15["open_rows_classed"]["c4_keys"] >= 1, (S15["final"], S15["open_rows_classed"]))
    pc2 = copy.deepcopy(pe)
    pc2["open_rows"] = [dict(r4x1, why="PD213(d)(4): claimed already open (self-test)"), r2in4]    # legacy refuses too
    S16 = run(pc2, "classed_c4bad", log=quiet)
    gate("G58 NEGATIVE: an open row (4 x) declared class 4 is extra AND its sources differ from S1 => not final",
         not S16["final"] and not S16["open_rows_classed"]["ok"] and S16["open_rows_classed"]["c4_bad"],
         S16["open_rows_classed"])
    pc3 = copy.deepcopy(pe)
    pc3["open_rows"] = [r4x1, {"node": 2, "term": "in", "why": "no class named (self-test)"}]
    S17 = run(pc3, "classed_unclassed", log=quiet)
    gate("G59 NEGATIVE: a declared row without a PD213(d) class => the classed rule refuses (a class is never guessed), not final",
         not S17["final"] and S17["open_rows_classed"]["unclassed"] == [[2, "in"]], S17["open_rows_classed"])
    st_s = base_state(_synthetic())
    l0, f0, c0 = cdiff_inputs(pf, st_s)
    st_n = dict(st_s, fs_pairs=None)
    l1, f1, c1_ = cdiff_inputs({"context": {"s1_key": JC.S1_KEY}}, st_n)
    l2, f2, c2_ = cdiff_inputs({"context": {"s1_key": JC.S1_KEY}}, dict(st_s, fs_pairs=[{"x": 1}]))
    gate("G60 cdiff_inputs: a synthetic (s1_graph) plan keeps the old inputs; an s1_key plan gets node_labels_default + the "
         "S1 wiki fs pairs when the state has none, and keeps the state's pairs when it has some",
         l0 == {} and f0 is None and c0["fs_pairs"] == "state" and len(l1) == len(JC.node_labels_default()) > 0 and f1
         and c1_["fs_pairs"].endswith(JC.S1_KEY + ".json") and f2 is None and c2_["fs_pairs"] == "state",
         (c0, c1_, c2_))
    # card chat-S3: only-sink fates (const #1 'v' -> tunnel #60 is branched; #3 'err' -> #51 outer is a sole sink)
    pdel = {"schema": "stageplan/1", "stage": "onlysink", "context": {"s1_graph": {"path": s1p}},
            "actions": [{"op": "delete_object", "uid": 51}]}
    fates = {}
    for nm, rule in (("keep", "keep"), ("delete", "delete"), ("ambiguous", "ambiguous"),
                     ("byclass", {"constant": "delete", "node": "keep"})):
        mdx = os.path.join(tmp, "om_" + nm)
        os.makedirs(mdx)
        with open(os.path.join(mdx, "delete_object.json"), "w", encoding="utf-8") as f:
            json.dump({"op": "delete_object", "sim": {"only_sink": rule, "sr_pair": False}}, f)
        Sx = run(pdel, "onlysink_" + nm, model_dir=mdx, log=quiet)
        ex = _j(Sx["steps"][1]["file"]["path"])
        w3 = [r["wire_uid"] for r in ex["state"]["terminals"] if r["term_uid"] == 1003]
        fates[nm] = (ex["effect"]["only_sink"], ex["effect"]["allow_either"], w3)
    gate("G36 only_sink keep: the constant's wire 3 survives as a source-side half-wire",
         fates["keep"][2] == [3] and fates["keep"][0][0]["fate"] == "keep", fates["keep"])
    gate("G37 only_sink delete: the constant's terminal reads wire 0", fates["delete"][2] == [0], fates["delete"])
    gate("G38 only_sink ambiguous: kept, and its source terminal is listed in allow_either for the executor",
         fates["ambiguous"][2] == [3] and fates["ambiguous"][1] == [1003], fates["ambiguous"])
    gate("G39 only_sink by source class: a constant source takes the 'constant' fate",
         fates["byclass"][2] == [0] and fates["byclass"][0][0]["src_class"] == "Constant", fates["byclass"])

    # G40-G42 the undirected-tunnel rule, both directions (k_op3_read_79.log:93-111, card 79-7 M2)
    def tr(tu, src, w, owner, ocls, tc, fd=10):
        return {"term_uid": tu, "term_name": "x", "is_source": src, "wire_uid": w, "owner_uid": owner,
                "owner_class": ocls, "frame_diagram": fd, "term_class": tc}
    sel = [tr(1801, False, 1, 80, "SelectorTunnel", "OuterTerminal"), tr(1802, True, 2, 80, "SelectorTunnel", "InnerTerminal", 21),
           tr(1803, True, 3, 80, "SelectorTunnel", "InnerTerminal", 22), tr(1051, False, 2, 5, "SubVI", "Terminal", 21),
           tr(1061, False, 3, 6, "SubVI", "Terminal", 22), tr(1001, True, 0, 1, "SubVI", "Terminal")]
    ss = {"terminals": sel}
    fl = _flip_orphaned_output_tunnels(ss, [1])
    gate("G40 input SelectorTunnel whose outer sink lost its source: EVERY inner flips to a sink, wires kept (M1 read)",
         sorted(f["term_uid"] for f in fl) == [1802, 1803] and all(not r["is_source"] for r in sel if r["owner_uid"] == 80)
         and [r["wire_uid"] for r in sel if r["owner_uid"] == 80] == [1, 2, 3], fl)
    osel = [tr(1901, True, 9, 90, "SelectorTunnel", "OuterTerminal"), tr(1902, False, 7, 90, "SelectorTunnel", "InnerTerminal", 21),
            tr(1903, False, 8, 90, "SelectorTunnel", "InnerTerminal", 22), tr(1071, True, 8, 7, "SubVI", "Terminal", 22),
            tr(1091, False, 9, 9, "SubVI", "Terminal")]
    fo = _flip_orphaned_output_tunnels({"terminals": osel}, [7])
    gate("G41 output SelectorTunnel with ONE frame still sourced stays directed (outer stays a source)",
         fo == [] and osel[0]["is_source"] is True, fo)
    lt = [tr(1601, False, 1, 60, "LoopTunnel", "OuterTerminal"), tr(1602, True, 2, 60, "LoopTunnel", "InnerTerminal", 20),
          tr(1611, False, 6, 61, "LoopTunnel", "InnerTerminal", 20), tr(1612, True, 7, 61, "LoopTunnel", "OuterTerminal")]
    fl2 = _flip_orphaned_output_tunnels({"terminals": lt}, [6])
    gate("G42 output LoopTunnel rule unchanged: orphaned inner sink flips ONLY its outer (outer_term_uid kept)",
         [(f["tunnel"], f.get("outer_term_uid")) for f in fl2] == [(61, 1612)] and lt[1]["is_source"] is True, fl2)
    # card 100-3: create a loop with a symbolic body; move/tunnel/create into it; the cond wire; the refusals (direct OPS)
    sc = base_state(_synthetic())
    P0 = {}
    e1, _c = op_create(sc, {"class": "WhileLoop", "diagram": 10, "as": "DL1"}, P0, None, {})
    b1 = sc["sym"]["new:DL1.body"]
    br1 = [r for r in sc["terminals"] if r["owner_uid"] == b1]
    gate("G43 create WhileLoop: object + NEW body diagram (sym new:DL1 / new:DL1.body), owners + diagrams + loops tables, "
         "NO loop-owned row", b1 < 0 and sc["owners"][str(b1)] == ["WhileLoop", sc["sym"]["new:DL1"]] and
         sc["diagrams"][str(b1)] == 10 and not [r for r in sc["terminals"] if r["owner_uid"] == sc["sym"]["new:DL1"]] and
         any(L["loop_uid"] == sc["sym"]["new:DL1"] for L in sc["loops"]), e1)
    # card 101-3: the rows MEASURED on While bodies #639/#25392 (1 unnamed source + 1 unnamed sink, owner = the body
    # Diagram, term_class Terminal, frame = the body) and For body #27537 (1 unnamed source only)
    key_ = lambda rs: sorted((r["owner_class"], r["term_class"], r["term_name"], bool(r["is_source"]), r["frame_diagram"],  # noqa: E731
                              r["wire_uid"]) for r in rs)
    gate("G43b created While body owns EXACTLY the measured rows: 1 unnamed source + 1 unnamed sink, Diagram-owned, "
         "Terminal, frame = body, unwired", key_(br1) == [("Diagram", "Terminal", "", False, b1, 0),
                                                          ("Diagram", "Terminal", "", True, b1, 0)] and
         sorted(e1["terminals"]) == sorted(r["term_uid"] for r in br1), br1)
    op_create(sc, {"class": "ForLoop", "diagram": "new:DL1.body", "as": "DF1"}, P0, None, {})
    bf1 = sc["sym"]["new:DF1.body"]
    gate("G43c created For body owns EXACTLY 1 unnamed Diagram-owned source (i), no sink",
         key_([r for r in sc["terminals"] if r["owner_uid"] == bf1]) == [("Diagram", "Terminal", "", True, bf1, 0)],
         [r for r in sc["terminals"] if r["owner_uid"] == bf1])
    nf = [r for r in sc["terminals"] if r["owner_class"] == "Tunnel" and r["owner_uid"] < 0]
    gate("G43e created For has ONE count-terminal 'Tunnel' object (objs owner ForLoop): unnamed OuterTerminal sink on the "
         "parent (new:DL1.body) + unnamed InnerTerminal source on the For body (measured, diag_c101_forn.log)",
         len(set(r["owner_uid"] for r in nf)) == 1 and
         key_(nf) == sorted([("Tunnel", "InnerTerminal", "", True, bf1, 0), ("Tunnel", "OuterTerminal", "", False, b1, 0)]) and
         any(int(o["uid"]) == nf[0]["owner_uid"] and o["class"] == "Tunnel" and o["owner"] == "ForLoop" for o in sc["objs"]), nf)
    gate("G43f created While has NO count-terminal object (r3 op 2 real diff 0 with the body rows only)",
         not [r for r in br1 if r["owner_class"] == "Tunnel"], "")
    Gb = graph(sc)
    gate("G43d the new body rows are one graph node each (node_of = the body, class Diagram), as bind_new groups them",
         set(V.node_of(r) for r in br1) == {b1} and set(V.node_class(r) for r in br1) == {"Diagram"} and Gb is not None, "")
    op_move_in(sc, {"nodes": [4], "dest_diagram": "new:DF1.body"}, dict(PROVISIONAL["move_in"]["params"]), None, {})
    gate("G44 move_in into 'new:DF1.body' re-homes #4's rows onto the new For body (nested in the new While body)",
         all(r["frame_diagram"] == sc["sym"]["new:DF1.body"] for r in sc["terminals"] if r["owner_uid"] == 4) and
         sc["diagrams"][str(sc["sym"]["new:DF1.body"])] == b1, [r["frame_diagram"] for r in sc["terminals"] if r["owner_uid"] == 4])
    sc["terminals"].append({"term_uid": 5001, "term_name": "Stop", "is_source": True, "wire_uid": 0, "owner_uid": 10,
                            "owner_class": "Diagram", "frame_diagram": 10, "term_class": "ControlTerminal"})
    op_create(sc, {"class": "Local", "diagram": "new:DL1.body", "as": "LR1", "label": "Stop",
                   "terminals": [{"name": "Stop", "is_source": True}]}, P0, None, {})
    ew, _c = op_wire(sc, {"src": "new:LR1.value", "dst": "new:DL1.cond"}, dict(PROVISIONAL["wire"]["params"]), None, {})
    lr = [r for r in sc["terminals"] if r["owner_uid"] == sc["sym"]["new:LR1"]]
    cr_ = [r for r in br1 if not r["is_source"]]
    gate("G45 '.value' names a Local's one terminal; wire -> new:DL1.cond wires it to the body's unnamed SINK row "
         "(card 101-3: the cond row is in the read)", ew.get("cond_of") == sc["sym"]["new:DL1"] and len(lr) == 1 and
         lr[0]["wire_uid"] < 0 and len(cr_) == 1 and ew.get("dst_term_uid") == cr_[0]["term_uid"] and
         sorted(r["term_uid"] for r in wire_rows(sc, lr[0]["wire_uid"])) == sorted([lr[0]["term_uid"], cr_[0]["term_uid"]]), ew)
    e_i, _c = op_create(sc, {"class": "ControlTerminal", "diagram": 20, "as": "IND1", "label": "plot", "indicator": True,
                             "born_on": "2.out"}, P0, None, {})
    ct = [r for r in sc["terminals"] if r["term_uid"] == sc["sym"]["new:IND1"]]
    gate("G46 create indicator born_on 2.out: its own node (term_class ControlTerminal, owner = diagram 20), joined to w6",
         len(ct) == 1 and ct[0]["owner_uid"] == 20 and ct[0]["wire_uid"] == 6 and not ct[0]["is_source"] and
         V.node_of(ct[0]) == ct[0]["term_uid"], ct)
    # card 122-4 (PD241(a)): a CREATED valued constant (donor copy, one declared unnamed source) feeding a CREATED indicator
    # born on it (gscript.const_indicator_on_diagram; stagexec const_born_on) - one NEW wire joins exactly those two rows
    op_create(sc, {"class": "ArrayConstant", "diagram": 20, "as": "CK1", "prim": "const_donor",
                   "donor": {"donor": "DonorRingConst_v0.vi", "uid": 1}, "terminals": [{"name": "", "is_source": True}]}, P0, None, {})
    e_k, _c = op_create(sc, {"class": "ControlTerminal", "diagram": 20, "as": "IND2", "label": "Num", "indicator": True,
                             "born_on": {"uid": "new:CK1"}}, P0, None, {})
    kr = [r for r in sc["terminals"] if r["owner_uid"] == sc["sym"]["new:CK1"]]
    kt = [r for r in sc["terminals"] if r["term_uid"] == sc["sym"]["new:IND2"]]
    gate("G46b created constant new:CK1 (one source row on #20) -> created indicator born_on it: ONE new wire joins exactly the "
         "two rows, indicator a sink on #20", len(kr) == 1 and kr[0]["is_source"] and len(kt) == 1 and not kt[0]["is_source"] and
         kt[0]["owner_uid"] == 20 and kr[0]["wire_uid"] < 0 and kr[0]["wire_uid"] == kt[0]["wire_uid"] == e_k.get("wire") and
         sorted(r["term_uid"] for r in wire_rows(sc, kr[0]["wire_uid"])) == sorted([kr[0]["term_uid"], kt[0]["term_uid"]]), (kr, kt, e_k))
    refs = []
    for lab_, fn in (("unknown alias", lambda: op_move_in(sc, {"nodes": [2], "dest_diagram": "new:ZZ1.body"},
                                                           dict(PROVISIONAL["move_in"]["params"]), None, {})),
                     ("'.body' spelled without body", lambda: resolve_diag(sc, "new:DL1")),
                     ("'.cond' of a For loop", lambda: op_wire(sc, {"src": "new:LR1.value", "dst": "new:DF1.cond"},
                                                               dict(PROVISIONAL["wire"]["params"]), None, {})),
                     ("occupied sink for create-on", lambda: op_create(sc, {"class": "DigitalNumericConstant", "diagram": 20,
                                                                            "on": "2.in"}, P0, None, {}))):
        try:
            fn()
            refs.append((lab_, "applied"))
        except SimError as e:
            refs.append((lab_, "refused: " + str(e)[:60]))
    gate("G47 NEGATIVE: unknown alias / malformed symbolic diagram / '.cond' of a For / create-on an occupied sink are "
         "each refused (SimError)", all(x[1].startswith("refused") for x in refs), refs)
    gate("G48 gate op: checks the object and changes nothing", op_gate(sc, {"uid": 3, "read": "bool_const", "stop_if": True},
                                                                       P0, None, {})[0]["class"] == "Constant", "")
    # card 101-4: the only-SOURCE rule (stage_d1_disp_r4.log:90 constant; diag_c71_l7_1a_tunnels.log:60,64 SubVI)
    def mv(uid, rule=None):
        s_ = base_state(_synthetic())
        p_ = dict(PROVISIONAL["move_in"]["params"])
        if rule is not None:
            p_["only_source"] = rule
        e_, _c = op_move_in(s_, {"nodes": [uid], "dest_diagram": 30}, p_, None, {})
        return s_, e_, dict((r["term_uid"], r["wire_uid"]) for r in s_["terminals"])
    s49, e49, w49 = mv(3)
    gate("G49 PROVISIONAL: a moved Constant that was the ONLY source of a single-sink cut wire takes it along: the outside "
         "sink 1511 reads wire 0, the constant's 1003 wire 0, fate recorded 'delete'",
         w49[1511] == 0 and w49[1003] == 0 and [(x["wire"], x["fate"], x["sink_term_uid"]) for x in e49["only_source"]] ==
         [(3, "delete", 1511)] and 1511 not in e49["allow_either"], (e49["only_source"], w49[1511], w49[1003]))
    s50, e50, w50 = mv(2)
    gate("G50 a moved SubVI (a node) keeps the measured rule: its only-source wires w6/w5 stay on the outside sinks "
         "1611/1501 as sourceless half-wires, no only_source record", w50[1611] == 6 and w50[1501] == 5 and
         e50["only_source"] == [] and not has_source(s50, 6), (e50["only_source"], w50[1611], w50[1501]))
    s51, e51, w51 = mv(1)
    gate("G51 a moved Constant feeding TWO outside sinks (w1 -> 1601, 1701) is outside the measured shape: both keep w1",
         w51[1601] == 1 and w51[1701] == 1 and e51["only_source"] == [], (e51["only_source"], w51[1601], w51[1701]))
    s52, e52, w52 = mv(3, "ambiguous")
    s53, e53, w53 = mv(3, "keep")
    gate("G52 only_source 'ambiguous' keeps the half-wire and lists the outside sink in allow_either; 'keep' = the pre-101-4 "
         "result (1511 on sourceless w3, no record)", w52[1511] == 3 and e52["allow_either"] == [1511] and
         w53[1511] == 3 and e53["only_source"] == [] and 1511 not in e53["allow_either"], (e52["allow_either"], w53[1511]))
    # card 101-5: a moved PRIMITIVE node (not a SubVI) that was the only source of single-sink cut wires takes them
    # (the 'subvi' kind exists so a plan may state {"node": .., "subvi": ..}; PROVISIONAL keeps {"constant": delete} only)
    def mv_prim(uid, cls, rule):
        s_ = base_state(_synthetic())
        for r in s_["terminals"]:
            if r["owner_uid"] == uid:
                r["owner_class"] = cls
        for o in s_["objs"]:
            if o["uid"] == uid:
                o["class"] = cls
        p_ = dict(PROVISIONAL["move_in"]["params"], only_source=rule)
        e_, _c = op_move_in(s_, {"nodes": [uid], "dest_diagram": 30}, p_, None, {})
        return s_, e_, dict((r["term_uid"], r["wire_uid"]) for r in s_["terminals"])
    s54, e54, w54 = mv_prim(2, "Bundler", {"constant": "delete", "node": "delete", "subvi": "keep", "default": "keep"})
    gate("G54 under an explicit {node: delete, subvi: keep} rule a moved PRIMITIVE (Bundler) only-source: w6/w5 are deleted, "
         "outside sinks 1611/1501 read wire 0, two 'delete' records", w54[1611] == 0 and w54[1501] == 0 and
         sorted((x["wire"], x["fate"], x["sink_term_uid"]) for x in e54["only_source"]) == [(5, "delete", 1501), (6, "delete", 1611)],
         (e54["only_source"], w54[1611], w54[1501]))
    s56, e56, w56 = mv_prim(2, "Bundler", PROVISIONAL["move_in"]["params"]["only_source"])
    gate("G55 the SubVI rule is unchanged beside it (G50); a rule dict without 'subvi' falls back to 'node'; under the "
         "PROVISIONAL rule a moved Bundler KEEPS its half-wires (the r5 k24/k25 real reads, diag_c101c_resim.log:57)",
         _fate_by_class({"node": "delete"}, "SubVI") == "delete" and _fate_by_class({"node": "delete", "subvi": "keep"}, "SubVI") == "keep"
         and _fate_by_class({"node": "delete", "subvi": "keep"}, "Bundler") == "delete" and w56[1611] == 6 and w56[1501] == 5
         and e56["only_source"] == [], (w56[1611], w56[1501], e56["only_source"]))
    # PD214(d)1 (cycle 102): a sink whose wire the only-source rule DELETED still seeds the undirected-tunnel flip
    src54 = dict((r["term_uid"], r["is_source"]) for r in s54["terminals"])
    src56 = dict((r["term_uid"], r["is_source"]) for r in s56["terminals"])
    gate("G56 under node:delete the deleted sink 1611 (LoopTunnel #61 inner) still flips the outer 1612 to a sink (r5 k12: 11365 "
         "wire 0 AND 11369 flipped); under keep the sourceless half-wire flips it the same way - the two rules agree on the tunnel",
         src54[1612] is False and any(f["tunnel"] == 61 and f["term_uid"] == 1612 for f in e54["tunnel_flips"]) and
         src56[1612] is False and any(f["tunnel"] == 61 for f in e56["tunnel_flips"]), (e54["tunnel_flips"], e56["tunnel_flips"]))
    # card 109-3: connect onto a SOURCELESS STUB (tunnel.json:200 keep-uid; stage_d1_l2a3_c109b.log:172 real new [] lost [])
    def stub():
        s_ = base_state(_synthetic())
        for r in s_["terminals"]:
            if r["term_uid"] == 1023:                    # 2.out leaves w6 -> w6 = sourceless stub {1611}, 2.out unwired
                r["wire_uid"] = 0
        s_["terminals"].append({"term_uid": 9001, "term_name": "z", "is_source": False, "wire_uid": 6, "owner_uid": 9,
                                "owner_class": "SubVI", "frame_diagram": 20, "term_class": "Terminal"})
        return s_
    PJ = dict(PROVISIONAL["wire"]["params"], sourceless_sink="join")
    s61 = stub(); n61 = s61["neg"]                                                 # noqa: E702
    e61, _c = op_wire(s61, {"src": "2.out", "dst": {"uid": 61, "term_uid": 1611}}, PJ, None, {})
    gate("G61 join: an UNWIRED source onto a sink on a sourceless stub KEEPS the stub uid (w6): no new uid, source + sink + "
         "the stub's other sink 9001 all on w6 (opmodels/tunnel.json:200)",
         e61["how"] == "join_stub" and e61["wire"] == 6 and e61["kept_stub_uid"] and s61["neg"] == n61 and
         sorted(r["term_uid"] for r in wire_rows(s61, 6)) == [1023, 1611, 9001] and e61["joined"] == [9001], e61)
    s62 = stub()
    e62, _c = op_wire(s62, {"src": "2.err out", "dst": {"uid": 61, "term_uid": 1611}}, PJ, None, {})
    s63 = stub(); n63 = s63["neg"]                                                 # noqa: E702
    e63, _c = op_wire(s63, {"src": "2.out", "dst": {"uid": 61, "term_uid": 1611}}, dict(PROVISIONAL["wire"]["params"]), None, {})
    gate("G62 unchanged beside it: an ALREADY-WIRED source (2.err out, w5) onto the stub BRANCHES w5 and takes 9001 along "
         "(unmeasured, old rule); with no opmodel (provisional detach) the sink gets a NEW uid and 9001 stays on w6",
         e62["how"] == "branch" and e62["wire"] == 5 and sorted(r["term_uid"] for r in wire_rows(s62, 6)) == [] and
         e63["how"] == "new" and e63["wire"] == n63 - 1 and [r["term_uid"] for r in wire_rows(s63, 6)] == [9001],
         (e62, e63))
    # card 112-1 T3: a flip SAVED in the base (B2-11/-14 shape: input LoopTunnel #9087 on the L2-B1 bed, outer t9092 bare
    # sink, inner a sink on w9076 -> #8634 'array'); a register's L.inner wired onto the outer reverts the inner to a source
    def b2_11():
        T = [tr(9092, False, 0, 9087, "LoopTunnel", "OuterTerminal", 20), tr(9093, False, 76, 9087, "LoopTunnel", "InnerTerminal", 21),
             tr(8640, False, 76, 8634, "SubVI", "Terminal", 21), tr(25587, True, 0, 10544, "LeftShiftRegister", "InnerTerminal", 20),
             tr(7001, True, 71, 7000, "SubVI", "Terminal", 21), tr(7002, False, 71, 7003, "SubVI", "Terminal", 21),
             tr(7101, False, 0, 7100, "LoopTunnel", "OuterTerminal", 20), tr(7102, True, 72, 7100, "LoopTunnel", "InnerTerminal", 21)]
        return base_state({"terminals": T})
    s64 = b2_11()
    seeded = seed_base_flips(s64, False)
    e64, _c = op_wire(s64, {"src": {"uid": 10544, "term_uid": 25587}, "dst": {"uid": 9087, "term_uid": 9092}},
                      dict(PROVISIONAL["wire"]["params"]), None, {})
    r64 = dict((r["term_uid"], r) for r in s64["terminals"])
    gate("G63 base flip seeding: only the all-sink tunnel #9087 is seeded (both faces), the directed #7100 is not",
         sorted(f["term_uid"] for f in seeded) == [9092, 9093] and s64.get("unflip") == {"cascade": False}, seeded)
    gate("G64 B2-11 shape: SR L.inner -> the saved-flipped outer reverts the inner 9093 to a SOURCE, so w76 -> #8634 has a "
         "source; the outer stays a sink",
         r64[9093]["is_source"] is True and has_source(s64, 76) and r64[9092]["is_source"] is False and
         [u["term_uid"] for u in e64.get("unflipped") or []] == [9093], e64)
    s65 = b2_11()
    e65, _c = op_wire(s65, {"src": {"uid": 10544, "term_uid": 25587}, "dst": {"uid": 9087, "term_uid": 9092}},
                      dict(PROVISIONAL["wire"]["params"]), None, {})
    gate("G65 negative control: without seeding the saved flip is NOT reverted (the pre-112 behaviour, stagesim.py "
         "_unflip_restored_tunnels reads flip_reg only)", not has_source(s65, 76) and "unflipped" not in e65, e65)
    # card 112-1 T4: finalize runs the route check. Positive: wired Constant #1 -> SubVI #4 'x' ('cfw' route). Negative:
    # a wired source -> a LoopTunnel's INNER sink face (not addressable by stagexec Addr: the toy's #61 is in no
    # Diagram.Nodes[]) - the sim alone finalizes it, the route check must refuse it.
    rp = {"schema": "stageplan/1", "stage": "r", "goal": "route check", "context": {"s1_graph": {"path": s1p}},
          "open_rows": [{"node": 4, "term": "x", "why": "toy"}]}
    ok66 = run(dict(rp, actions=[{"op": "delete_wire", "wire_uid": 7}, {"op": "wire", "src": {"uid": 1, "term_uid": 1001},
                                  "dst": {"uid": 4, "term_uid": 1041}}]), "route_ok", log=quiet, route_check=True)
    acts67 = [{"op": "delete_wire", "wire_uid": 6}, {"op": "wire", "src": {"uid": 2, "term_uid": 1024},
                                                     "dst": {"uid": 61, "term_uid": 1611}}]
    pre67 = run(dict(rp, actions=acts67), "route_bad0", log=quiet)                     # the end rows, declared open below
    open67 = [{"node": V.key_parts(k)[0], "term": V.key_parts(k)[2], "why": "toy"} for k in pre67.get("end_cdiff_rows") or []]
    gate("G66 finalize route check PASS on a routable row: final, finalized.route_check lists the row's route",
         ok66["final"] and ok66.get("route_check", {}).get("status") == "PASS" and
         [x["route"] for x in ok66["route_check"]["rows"]][-1:] == ["cfw"],
         (ok66.get("route_check"), ok66.get("failed"), ok66.get("end_cdiff_rows"), ok66.get("open_rows_match")))
    bad = run(dict(rp, actions=acts67, open_rows=open67), "route_bad", log=quiet, route_check=True)
    rcb = bad.get("route_check") or {}
    gate("G67 NEGATIVE: an UNROUTABLE row fails FINALIZE (not final, although the sim alone finalizes), the row is named",
         bad.get("open_rows_match") and not bad["final"] and rcb.get("status") == "FAIL" and
         any(x.get("unroutable") for x in rcb.get("rows") or []),
         # printed lower-case: selftest_stagesim_l2a1_80.py E1 counts every output line carrying the upper-case word
         (bad.get("open_rows_match"), bad.get("final"), str(rcb.get("status")).lower(), str(rcb.get("first_fail"))[:300].lower()))
    # card 114-3 C2: a border-crossing connect from a WIRED source re-creates the source's wire (connect_from_wire.json:266)
    cfw_path = os.path.join(OPMODEL_DIR, "connect_from_wire.json")
    cfw = _j(cfw_path) if os.path.isfile(cfw_path) else None
    nob = copy.deepcopy(cfw) if cfw else {"samples": []}
    for s_ in nob.get("samples") or []:
        s_["checks"]["new_tunnels"] = []
    dis = copy.deepcopy(cfw) if cfw else {"samples": []}
    if dis.get("samples"):
        dis["samples"][0]["checks"]["source_wire_replaced"] = []
    gate("G68 cfw_border_rule: the measured model -> 'recreate'; no border sample -> None; one border sample without its "
         "source's wire change -> None",
         cfw_border_rule(cfw) == "recreate" and cfw_border_rule(nob) is None and cfw_border_rule(dis) is None,
         (cfw_border_rule(cfw), cfw_border_rule(nob), cfw_border_rule(dis)))
    PR = dict(PROVISIONAL["wire"]["params"], border_source_wire="recreate")

    def into_tunnel(P):
        s_ = base_state(_synthetic())
        et, _c = op_tunnel(s_, {"loop": 200, "body": 30, "dir": "in", "as": "TX"}, {}, None, {})
        n0 = s_["neg"]
        ew, _c = op_wire(s_, {"src": "1.v", "dst": "new:TX.outer"}, P, None, {})
        return s_, et, ew, n0
    s69, et69, e69, n69 = into_tunnel(PR)
    on_new = sorted(r["term_uid"] for r in wire_rows(s69, e69["wire"]))
    gate("G69 RECREATE: const 1.v (w1, sinks 1601/1701) -> a plan tunnel's outer: w1 LOST, one NEW negative wire carries "
         "the source, both old sinks and the new outer; effect names recreated_from 1, rewired [1601, 1701]",
         e69["how"] == "recreate" and e69["wire"] == n69 - 1 and not wire_rows(s69, 1) and
         on_new == sorted([1001, 1601, 1701, et69["outer"]]) and e69.get("recreated_from") == 1 and
         e69.get("rewired") == [1601, 1701], (e69, on_new))
    s70, _et, e70, _n = into_tunnel(dict(PROVISIONAL["wire"]["params"]))
    s70b = base_state(_synthetic())
    e70b, _c = op_wire(s70b, {"src": "1.v", "dst": "4.y"}, PR, None, {})
    gate("G70 unchanged beside it: without the measured rule (provisional) the same row BRANCHES w1; with the rule a "
         "SAME-DIAGRAM sink (4.y, no plan tunnel) also branches w1 (stage_d1_l7_1b_r3.log:92,109 kept the uid)",
         e70["how"] == "branch" and e70["wire"] == 1 and "recreated_from" not in e70 and
         e70b["how"] == "branch" and e70b["wire"] == 1 and "recreated_from" not in e70b, (e70, e70b))
    if cfw:
        md = os.path.join(tmp, "models_cfw_only")
        os.makedirs(md, exist_ok=True)
        with open(os.path.join(md, "connect_from_wire.json"), "w", encoding="utf-8") as f:
            json.dump(cfw, f)
        S71 = run(pf, "full_cfw", log=quiet, model_dir=md)
        e71 = _j(S71["steps"][4]["file"]["path"])["effect"]
        gate("G71 full toy plan under the measured cfw model: step 4 (1.v -> T1.outer) RE-CREATES w1, every step still "
             "applies and the end computation_diff(S1) is unchanged ({0} rows)".format(len(S["end_cdiff_rows"] or [])),
             e71["how"] == "recreate" and e71.get("recreated_from") == 1 and S71["failed"] is None and
             S71["end_cdiff_rows"] == S["end_cdiff_rows"], (e71, S71["failed"], S71["end_cdiff_rows"]))
    else:
        gate("G71 full toy plan under the measured cfw model", False, "no opmodels/connect_from_wire.json")
    # card 118-3 (PD234(i)): the queue route's AUTO TUNNEL - a Function created in a loop body THIS plan made, `src` on the parent
    s72 = base_state(_synthetic())
    op_create(s72, {"op": "create", "id": "pf", "class": "ForLoop", "diagram": 10, "as": "PF", "pos": [0, 0]}, PR, None, {})
    EQ = {"op": "create", "id": "enq", "class": "Function", "diagram": "new:PF.body", "as": "ENQ", "pos": [1, 1], "src": "1.v", "src_into": "queue",
          "terminals": [{"name": "queue", "is_source": False}, {"name": "queue out", "is_source": True}]}
    e72, _c = op_create(s72, EQ, PR, None, {})
    at = e72.get("auto_tunnel") or {}
    orow = next((r for r in s72["terminals"] if r["term_uid"] == at.get("outer")), {})
    irow = next((r for r in s72["terminals"] if r["term_uid"] == at.get("inner")), {})
    qrow = next((r for r in s72["terminals"] if r["owner_uid"] == s72["sym"]["new:ENQ"] and r["term_name"] == "queue"), {})
    gate("G72 queue route across the border: ONE new non-indexed LoopTunnel; outer sink on diagram 10 BRANCHES w1 (1.v already wired); "
         "inner source on the new body shares the new node's 'queue' wire",
         at and orow.get("frame_diagram") == 10 and not orow.get("is_source") and orow.get("wire_uid") == 1 and e72.get("src_branch") is True
         and irow.get("frame_diagram") == s72["sym"]["new:PF.body"] and irow.get("is_source") and irow.get("wire_uid") == qrow.get("wire_uid")
         and qrow.get("wire_uid") and qrow.get("wire_uid") < 0 and at.get("indexing") is False
         and sum(1 for o in s72["objs"] if o["class"] == "LoopTunnel" and o["uid"] == at.get("tunnel") and False) == 0, (e72, orow, irow, qrow))
    try:
        op_create(base_state(_synthetic()), dict(EQ, diagram=20), PR, None, {})
        e73 = "no error"
    except SimError as e:
        e73 = str(e)
    gate("G73 the same node on a body the plan did NOT create (diagram 20, base loop A) is still refused", "same diagram" in e73, e73)
    n_pass = sum(1 for _l, ok in gates if ok)
    n_fail = len(gates) - n_pass
    first = next((l for l, ok in gates if not ok), None)
    print("=== GATES: {0} pass / {1} fail{2}".format(n_pass, n_fail, "; failing: " + first if first else ""))
    print(protocol.result_line(protocol.make_result(n_pass, n_fail, first)))
    return 0 if n_fail == 0 else 1


def _run_plan(plan, name, gp, tmp, model_dir=None, log=print, route_check=False):
    # route_check off by default here (card 112-1 T4): G01-G62 test the SIMULATION model on a toy graph whose objects the
    # executor's readers were never meant to address; G66-G67 turn the finalize route check on explicitly
    pp = os.path.join(tmp, "plan_in_{0}.json".format(name))
    plan = dict(plan, stage=name)
    with open(pp, "w", encoding="utf-8") as f:
        json.dump(plan, f)
    return simulate(pp, gp, out_root=os.path.join(tmp, "sim"), plan_out_dir=tmp,
                    model_dir=model_dir or os.path.join(tmp, "no_models"), log=log, route_check=route_check)


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
