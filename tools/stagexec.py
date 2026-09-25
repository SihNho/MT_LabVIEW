r"""stagexec - the STAGE EXECUTOR (docs/stage-simulator-plan.md "The method" step 6, build order 5; card chat-S3).
Runs a FINAL stageplan/1 file (tools/stagesim.py wrote it, `final: true`) on a DATED SCRATCH COPY of the plan's base VI,
action by action, under stagekit. After every real op it READS the real graph and compares it with the simulated step
file of the last plan action that op covers; the first difference STOPS the run with a step-diff report. Objects the plan
creates (new:SR1R, new:T1 ...) are BOUND to real uids by diffing the terminal table right before and right after the
creating op; a class/count mismatch stops. Rows come ONLY from the plan file (no uid or terminal name is typed here).

    py tools/stagexec.py run    <plan.json> [--reference <vi> <md5>] [--max-min N]   (LabVIEW; under bgrun + launch gate)
    py tools/stagexec.py dry    <plan.json>          (no LabVIEW: the same executor on a SIMULATED backend)
    py tools/stagexec.py prerun <plan.json>          (no LabVIEW: plan final, step files intact, every op compiles and
                                                      every address resolves on its step's graph)
    py tools/stagexec.py selftest

WHAT EXISTED FIRST (checked 2026-09-24): tools/stagesim.py (the plan + step files + OPS - used, the executor replays
its state files); tools/stagekit.py (Stage: pins, scratch, junk_purge, uid_index, es, close - used unchanged);
gscript (report_all, node_labels, node_terms_uid, add_shift_reg, shift_reg, wire_sr, wire_indicators, tunnels,
set_index_mode, remove_bad_wires_scripted); build_d1_v0.move_in/diag_index; build_opfsinnertunnelconnect_v0.del_wire/
del_node; build_opconnectnested_v1.connect_nested_v1; build_opconnectfromwire_v0.connect_from_wire/wire_source_owner;
wiki_build.read_live (the ~20 s graph read the L7 stages used); tools/bench/opmodels_lib.edges (terminal-uid edges).
The per-action op choice is the one the L7 stages used (stage_d1_l7_1a.py, stage_d1_l7_1b.py, stage_d1_l7_r.py).
No executor existed; no LabVIEW op VI is built here.

COMPILE (pure): plan actions -> REAL OPS. One real op covers one or more actions; the comparison runs after the LAST
action it covers. `tunnel` + the wire into it + the wire out of it = ONE connect (LabVIEW makes the tunnel; nothing
can create a bare one); every further wire out of the same tunnel = a branch off its outer wire (connect_from_wire).
`wire` into new:SRkR.inner = wire_sr RightIn; from new:SRkL.inner = wire_sr LeftIn; a sink that is a front-panel
ControlTerminal = wire_indicators (branch onto the source's existing wire); any other wire = connect_from_wire when the
source is wired, else connect_nested_v1. delete_wire is resolved BY ITS TERMINALS (the plan's wire uid names a wire of
the simulated state; LabVIEW re-creates a source's wire under a new uid on connect_from_wire - opmodels/connect_from_wire).
COMPARE (pure): terminal-uid sets, edges (src term -> sink term, joined by wire inside ONE read), dangling terminals (on
a wire with no source or no sink); new objects through the binding; a source terminal the step marks `allow_either`
(the ambiguous only-sink rule) may be dangling or bare. Wire uids are never compared.
"""
import collections
import copy
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(HERE, "bench")
for _p in (HERE, BENCH, os.path.join(HERE, "recipes")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import stagesim as SS          # noqa: E402
import vigraph as V            # noqa: E402
import protocol                # noqa: E402

SR_CLS = ("RightShiftRegister", "LeftShiftRegister")
FP = "ControlTerminal"


class ExecStop(Exception):
    """The executor stops here (a difference, an unbound object, an unaddressable terminal)."""


def md5(p):
    return SS.md5_file(p)


def _j(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _abs(p):
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


# ============================================================================================ plan + compile (pure)
def load_final_plan(plan_path):
    """The plan, its step states (md5-checked against `finalized.step_files`) and the actions' step numbers."""
    plan = _j(plan_path)
    ok, why = protocol.validate_obj(plan)
    if not ok:
        raise ExecStop("plan does not validate: " + why)
    if plan.get("final") is not True:
        raise ExecStop("plan is not final (final={0!r}, finalized={1})".format(
            plan.get("final"), json.dumps((plan.get("finalized") or {}).get("first_divergent"))))
    fz = plan.get("finalized") or {}
    files = fz.get("step_files") or []
    if len(files) != len(plan["actions"]) + 1:
        raise ExecStop("finalized.step_files has {0} entries for {1} actions + base".format(len(files), len(plan["actions"])))
    stale = [f["path"] for f in files if not os.path.exists(_abs(f["path"])) or md5(_abs(f["path"])) != f["md5"]]
    if stale:
        raise ExecStop("{0} step file(s) missing or changed since finalize ({1}...) - re-simulate".format(len(stale), stale[:2]))
    base = fz.get("base") or plan.get("base")
    if not base or md5(_abs(base["path"])) != base["md5"]:
        raise ExecStop("base graph {0} missing or changed".format(base))
    return plan, [f["path"] for f in files]


def _sym_of(ref):
    """'new:SR1R.inner' / {'uid': 'new:T1', ...} -> ('new:SR1R', 'inner') ; plain -> (None, None)."""
    if isinstance(ref, dict):
        u = ref.get("uid")
        return (u, ref.get("side") or ref.get("term")) if isinstance(u, str) and u.startswith("new:") else (None, None)
    if isinstance(ref, str) and ref.startswith("new:"):
        h, _d, t = ref.partition(".")
        return h, t
    return None, None


def compile_plan(plan):
    """[{kind, acts:[action indices 1-based], ...}] - one entry per REAL op, in order. Raises ExecStop on a shape the
    executor has no real op for (the pre-run gate)."""
    A = plan["actions"]
    created = {}                                         # 'new:X' -> ('sr'|'tunnel', action index)
    for i, a in enumerate(A, 1):
        if a["op"] == "add_shift_reg":
            nm = a.get("as")
            created["new:" + nm + "R"], created["new:" + nm + "L"] = ("srR", i), ("srL", i)
        elif a["op"] == "tunnel":
            created["new:" + a["as"]] = ("tunnel", i)
    ops, i = [], 1
    while i <= len(A):
        a = A[i - 1]
        op = a["op"]
        if op == "move_in":
            if len(a["nodes"]) != 1 or not a.get("pos"):
                raise ExecStop("action {0}: move_in needs ONE node and a `pos`".format(i))
            ops.append({"kind": "move_in", "acts": [i]})
        elif op == "add_shift_reg":
            ops.append({"kind": "add_sr", "acts": [i]})
        elif op == "tunnel":
            t = "new:" + a["as"]
            nxt = A[i:i + 2]
            ins = [k for k, b in enumerate(nxt, i + 1) if b["op"] == "wire" and _sym_of(b["dst"])[0] == t]
            outs = [k for k, b in enumerate(nxt, i + 1) if b["op"] == "wire" and _sym_of(b["src"])[0] == t]
            if len(ins) != 1 or len(outs) != 1:
                raise ExecStop("action {0}: tunnel {1} must be followed by exactly one wire into it and one out of it "
                               "(LabVIEW makes a tunnel only by wiring across the border)".format(i, t))
            ops.append({"kind": "tunnel", "acts": [i, i + 1, i + 2], "tunnel": t, "in_act": ins[0], "out_act": outs[0]})
            i += 3
            continue
        elif op == "wire":
            ss, sside = _sym_of(a["src"])
            ds, dside = _sym_of(a["dst"])
            if ds and created.get(ds, ("",))[0] == "srR" and dside == "inner":
                ops.append({"kind": "wire_sr", "variant": "RightIn", "reg": ds, "acts": [i]})
            elif ss and created.get(ss, ("",))[0] == "srL" and sside == "inner":
                ops.append({"kind": "wire_sr", "variant": "LeftIn", "reg": ss, "acts": [i]})
            elif ss and created.get(ss, ("",))[0] == "tunnel":
                ops.append({"kind": "branch", "tunnel": ss, "acts": [i]})
            elif (ss and created.get(ss, ("",))[0] == "tunnel") or (ds and created.get(ds, ("",))[0] == "tunnel"):
                raise ExecStop("action {0}: a wire into a tunnel outside its tunnel group".format(i))
            else:
                ops.append({"kind": "connect", "acts": [i]})
        elif op in ("delete_wire", "delete_object", "remove_bad_wires"):
            ops.append({"kind": op, "acts": [i]})
        else:
            raise ExecStop("action {0}: op {1!r} has no real executor (create/decide are not executable)".format(i, op))
        i += 1
    return ops


# ============================================================================================ graph helpers (pure)
def dedupe(terms):
    return V.dedupe_rows(terms)[0]


def edges(terms):
    byw = collections.defaultdict(lambda: ([], []))
    for r in terms:
        if r["wire_uid"]:
            byw[r["wire_uid"]][0 if r["is_source"] else 1].append(r["term_uid"])
    E = set()
    dang = set()
    for w, (s, k) in byw.items():
        for a in s:
            for b in k:
                E.add((a, b))
        if not s or not k:
            dang.update(s + k)
    return E, dang


def translate(state_terms, bind):
    """Sim rows with created (negative) uids replaced by their bound real uids. Unbound negatives stay negative."""
    out = []
    for r in state_terms:
        x = dict(r)
        x["term_uid"] = bind["term"].get(r["term_uid"], r["term_uid"])
        x["owner_uid"] = bind["obj"].get(r["owner_uid"], r["owner_uid"])
        out.append(x)
    return out


def compare(sim_terms, real_terms, bind, allow_either=()):
    """{n, only_sim_terms, only_real_terms, only_sim_edges, only_real_edges, dangling_sim_only, dangling_real_only}."""
    S = translate(dedupe(sim_terms), bind)
    R = dedupe(real_terms)
    ts, tr = set(r["term_uid"] for r in S), set(r["term_uid"] for r in R)
    es, ds = edges(S)
    er, dr = edges(R)
    wired_r = set(r["term_uid"] for r in R if r["wire_uid"])
    wired_s = set(r["term_uid"] for r in S if r["wire_uid"])
    allow = set(allow_either)
    d_sim = sorted(t for t in ds - dr if not (t in allow and t not in wired_r))
    d_real = sorted(t for t in dr - ds if not (t in allow and t not in wired_s))
    info = dict((r["term_uid"], (r["owner_uid"], r["owner_class"], r["term_name"])) for r in R + S)
    out = {"only_sim_terms": sorted(ts - tr), "only_real_terms": sorted(tr - ts),
           "only_sim_edges": sorted(es - er), "only_real_edges": sorted(er - es),
           "dangling_sim_only": d_sim, "dangling_real_only": d_real,
           "unbound": sorted(t for t in ts if t < 0)}
    out["n"] = sum(len(v) for v in out.values())
    out["who"] = dict((str(t), info.get(t)) for k in ("only_sim_terms", "only_real_terms", "dangling_sim_only",
                                                      "dangling_real_only") for t in out[k][:12])
    return out


def bind_new(prev_real, real, sim_prev, sim_now, bind):
    """Bind the objects the simulation created between sim_prev and sim_now to the real objects that appeared between
    prev_real and real, by class and then by terminal class. Count/class mismatch => ExecStop."""
    sp = set(r["owner_uid"] for r in sim_prev)
    new_sim = collections.OrderedDict()
    for r in sim_now:
        if r["owner_uid"] < 0 and r["owner_uid"] not in sp and r["owner_uid"] not in bind["obj"]:
            new_sim.setdefault(r["owner_uid"], []).append(r)
    old_t = set(r["term_uid"] for r in prev_real)
    new_real = collections.OrderedDict()
    for r in real:
        if r["term_uid"] not in old_t and r["owner_uid"] not in bind["obj"].values():
            new_real.setdefault(r["owner_uid"], []).append(r)
    cs = collections.Counter(rs[0]["owner_class"] for rs in new_sim.values())
    cr = collections.Counter(rs[0]["owner_class"] for rs in new_real.values())
    if cs != cr:
        raise ExecStop("BINDING: simulated new objects {0} != real new objects {1} (real owners {2})".format(
            dict(cs), dict(cr), list(new_real)[:8]))
    made = {}
    for cls in cs:
        su = [u for u, rs in new_sim.items() if rs[0]["owner_class"] == cls]
        ru = [u for u, rs in new_real.items() if rs[0]["owner_class"] == cls]
        if len(su) != 1:
            raise ExecStop("BINDING: {0} new {1} objects in one op - ambiguous".format(len(su), cls))
        s_rows, r_rows = new_sim[su[0]], new_real[ru[0]]
        ks = collections.Counter(r["term_class"] for r in s_rows)
        kr = collections.Counter(r["term_class"] for r in r_rows)
        if ks != kr or any(v != 1 for v in ks.values()):
            raise ExecStop("BINDING: {0} terminal classes sim {1} vs real {2}".format(cls, dict(ks), dict(kr)))
        bind["obj"][su[0]] = ru[0]
        made[su[0]] = ru[0]
        for sr in s_rows:
            rr = next(x for x in r_rows if x["term_class"] == sr["term_class"])
            bind["term"][sr["term_uid"]] = rr["term_uid"]
    return made


# ============================================================================================ addressing
# PD185 (card 81-8): a SelectorTunnel is NOT in Diagram.Nodes[] (stage_d1_l2a1.log:302). Its OUTER face is a terminal of
# its OWNER STRUCTURE's Terminals[], measured EXACTLY ONE matching face for all five L2-A1 sink ends on D1_k
# (tools/bench/l2a1_faces_81.log M1 5/5; prior build_d1_m3a1.log:1145-1154). The owner = the structure that owns the
# tunnel's inner frame diagram (the plan state's `owners` map). A FlatSequenceInnerTunnel face is reachable only
# through Left/Right Terminal (docs/NAMES.md:1245-1255), never as a (diagram, node, terminal) triple: its end STOPS
# with that route named. The real Addr and SimReader use the SAME rule, so the offline gates see what LabVIEW does.
OWNER_ROUTED = ("SelectorTunnel", "Tunnel")
# "Tunnel" = a case structure's SELECTOR (#5603 on #5540, #10465 on #10445): run 2's PRIME stopped on both
# (stage_d1_l2a1_r2.log:36). Their faces are measured on the owner's Terminals[] too: #5540 t0 ('', sink, w5709) and
# #10445 t0 ('', sink, w9921), exactly one each (l2a1_faces_81.log, owner Terminals[] listings).
FSIT_CLS = "FlatSequenceInnerTunnel"
NOT_NODES = OWNER_ROUTED + (FSIT_CLS,)
# PD187(b) (card 82-1): a front-panel ControlTerminal is NEVER in Diagram.Nodes[] (stage_d1_l2a1_r3.log:439, #5634 moved
# at op 10, bare at op 31). Its address is the 179(b) route: term_uid == its own uid, owner == its Diagram, membership
# proved by report_all('ControlTerminal') (tools/bench/diag_ctlterm_read_80.py). Addr.ct() is that route, in the real
# Addr and in SimReader alike; Addr.triple() REFUSES a ControlTerminal (it is not a Nodes[] triple).


def is_ct(r):
    return V.node_class(r) == FP


# PD187(a) FIT (card 82-1, tools/bench/parity_l2a1_82.log + parity_l2a1_82_real.json, the REAL Diagram.Nodes[] of D1_k on
# #639/#686/#23166): the real Nodes[] holds NO LoopTunnel, NO FlatSequenceOuterTunnel, NO *Constant (Digital/String/
# Cluster measured), NO Diagram-owned terminal owner, NO ControlTerminal, and a loop only on its PARENT diagram (the old
# SimReader appended all 23 loops to every diagram). Before the fit 231 one-side-only entries, all on the SimReader side.
NOT_NODE_CLASSES = ("LoopTunnel", "FlatSequenceOuterTunnel", "Diagram", "TopLevelDiagram")


def listed_as_node(r):
    """Constant / Tunnel / Terminal are OUTSIDE the Node branch of the VI Server hierarchy (gobject/constant/..,
    gobject/tunnel/.. - archive/peer/2026-09-25-parity-l2a1-82-hyp.md 1+2a), so every *Constant and every *Tunnel class
    is excluded, not only the ones measured; owner-routed tunnels still list their OWNER structure (_routed)."""
    c = r["owner_class"]
    if c in NODE_CONSTANTS:
        return True
    return not (c in SR_CLS + NOT_NODES + NOT_NODE_CLASSES or c.endswith("Constant") or c.endswith("Tunnel") or is_ct(r))


# HOLDOUT (all 173 diagrams of D1_k, tools/bench/parity_l2a1_82_holdout.log:45-50): the ONLY one-side-only entries left
# were 21 real-only ControlReferenceConstant on 5 untouched diagrams - that class IS in Diagram.Nodes[].
NODE_CONSTANTS = ("ControlReferenceConstant",)


def loop_parent(st, L):
    """The diagram uid a loop sits on: its own non-body rows, else its registers' / tunnels' OUTER faces (one value)."""
    u = int(L["loop_uid"])
    bodies = set(k for k, v in (st.get("owners") or {}).items() if int(v[1] or 0) == u)
    T = st["terminals"]
    ds = set(int(r["frame_diagram"] or 0) for r in T if r["owner_uid"] == u and str(int(r["frame_diagram"] or 0)) not in bodies)
    if not ds:
        regs = set(int(x) for x in L.get("right_uids") or []) | set(
            int(y) for v in (L.get("left_of") or {}).values() for y in (v if isinstance(v, list) else [v]))
        tuns = set(r["owner_uid"] for r in T if r["term_class"] == "InnerTerminal" and str(int(r["frame_diagram"] or 0)) in bodies)
        ds = set(int(r["frame_diagram"] or 0) for r in T if (r["owner_uid"] in tuns or r["owner_uid"] in regs)
                 and r["term_class"] == "OuterTerminal")
    return ds.pop() if len(ds) == 1 else None


# PD187(a) (card 82-1): READER PARITY. Three runs in cycle 81 stopped on one class - SimReader listed as a Nodes[] entry
# something the real Diagram.Nodes[] does not (border tunnels -> selectors -> ControlTerminals). At PRIME, per diagram the
# plan touches, SimReader's Nodes[] membership (class, uid) is compared with a REAL Nodes[] read; any one-side-only entry
# STOPS before op 1, so the next member of the class shows up offline / at PRIME, not at op N.
def touched_diagrams(plan, st):
    """Base diagram uids the plan touches: moved nodes' source diagrams, move destinations, register/tunnel parent + body,
    and the diagram of every base plan end (resolved on the base state)."""
    base_d = set(int(r["frame_diagram"] or 0) for r in st["terminals"])
    out = set()
    for a in plan["actions"]:
        if a["op"] == "move_in":
            for u in a["nodes"]:
                out |= set(int(r["frame_diagram"] or 0) for r in st["terminals"] if V.node_of(r) == int(u))
            out.add(int(a["dest_diagram"]))
        for k in ("parent", "body"):
            if a.get(k) is not None:
                out.add(int(a[k]))
        for side, src in (("src", True), ("dst", False), ("at", True)):
            e = a.get(side)
            if e is None or _sym_of(e)[0]:
                continue
            try:
                out.add(int(SS.resolve_addr(st, e, src)["frame_diagram"] or 0))
            except SS.SimError:
                pass
    return sorted(out & base_d)


def listing(rd, diag, cls):
    """{(class, uid)} of reader rd's Nodes[] on diagram uid `diag` (None when the reader has no such diagram)."""
    dl = rd.diagrams()
    if diag not in dl:
        return None
    return set((cls.get(u, "?"), u) for u in rd.node_uids(dl.index(diag)))


def reader_parity(real_rd, sim_rd, diags, cls_real, cls_sim):
    """[{diagram, n_real, n_sim, only_real, only_sim}] per diagram; `n` = total one-side-only entries."""
    rows, n = [], 0
    for d in diags:
        R, S = listing(real_rd, d, cls_real), listing(sim_rd, d, cls_sim)
        miss = [k for k, v in (("real", R), ("sim", S)) if v is None]       # a diagram one side lacks = an EMPTY listing
        R, S = R or set(), S or set()
        orr, osm = sorted(R - S), sorted(S - R)
        rows.append(dict({"diagram": d, "n_real": len(R), "n_sim": len(S), "only_real": orr, "only_sim": osm},
                         **({"missing_on": miss} if miss else {})))
        n += len(orr) + len(osm)
    return rows, n


def classes_of(st_or_rows, objs):
    """uid -> class, from the objects list, else from the terminal rows (node_of / node_class)."""
    c = dict((int(o["uid"]), o["class"]) for o in objs or [])
    for r in st_or_rows:
        c.setdefault(V.node_of(r), V.node_class(r))
    return c


class _StateHolder(object):
    def __init__(self, st):
        self.st = st


def connect_route(addr, real, src, dst, loop_of):
    """The connect route BOTH backends take (so the dry run sees what the real run does): 'indicator' (panel sink, wired
    source: wire_indicators), 'cfw' (wired source: connect_from_wire), 'nested' (bare Nodes[] source: connect_nested_v1),
    'ctl' (BARE ControlTerminal source, card 82-2: gscript.wire_control = OpWireCtl_v0, Get Controls by LABEL on the CT's own
    Diagram index -> Wire Inputs onto Traverse(sink class)[i].<sink NAME>; measured on a D1_k scratch at op 31 for
    rw_5634_10256 + rw_17487_9676: Wire +1, sole source = the CT, sole sink = the plan sink, ordered second pass wire_delta 0 /
    Is Broken? False, plan step 35 compare 0 - tools/bench/ctsrc_l2a1_82.log). Both ends are NAME-addressed there, so the
    route stops unless the CT's label is unique among the ControlTerminals on its Diagram and the sink's name is unique
    among its node's sink terminals, and the sink's owner is the node itself (not an owner-routed face / register)."""
    rs = next(r for r in real if r["term_uid"] == src)
    rd = next(r for r in real if r["term_uid"] == dst)
    info = {}
    if is_ct(rs):
        info["src_ct"] = addr.ct(real, src)[1]
    if is_ct(rd):
        info["dst_ct"] = addr.ct(real, dst)[1]
        if not rs["wire_uid"]:
            raise ExecStop("CONNECT-NO-VERB: panel sink #{0} needs a WIRED source for wire_indicators; #{1} is bare".format(dst, src))
        return "indicator", rs, rd, info
    dt, hd = addr.triple(real, dst, False, loop_of)
    info.update(dst=dt, dst_how=hd)
    if rs["wire_uid"]:
        return "cfw", rs, rd, info
    if is_ct(rs):
        c = addr.ct(real, src)[0]
        same = [r for r in real if is_ct(r) and int(r["frame_diagram"] or 0) == c["diag"] and r["term_name"] == rs["term_name"]]
        if not rs["term_name"] or len(same) != 1:
            raise ExecStop("CONNECT-NO-VERB: bare ControlTerminal source #{0} {1!r}: label not unique among the {2} "
                           "ControlTerminal(s) of that name on Diagram #{3} (wire_control is label-addressed)".format(
                               src, rs["term_name"], len(same), c["diag"]))
        if rd["owner_class"] in OWNER_ROUTED or rd["owner_class"] in SR_CLS or rd["owner_class"] == FSIT_CLS \
                or V.node_of(rd) != rd["owner_uid"]:
            raise ExecStop("CONNECT-NO-VERB: bare ControlTerminal source #{0} -> sink #{1} on {2} #{3}: wire_control "
                           "addresses the sink NODE by class traverse; this sink's owner is not that node".format(
                               src, dst, rd["owner_class"], rd["owner_uid"]))
        _e, nt = addr.rd.node_terms(dt[0], dt[1])
        nm = nt[dt[2]]["name"]
        if not nm or sum(1 for x in nt if x["name"] == nm and not x["is_source"]) != 1:
            raise ExecStop("CONNECT-NO-VERB: bare ControlTerminal source #{0} -> sink #{1} {2!r}: sink name not unique "
                           "among its node's sink terminals (wire_control is name-addressed)".format(src, dst, nm))
        info.update(ctl_label=rs["term_name"], ctl_didx=c["didx"], dst_name=nm)
        return "ctl", rs, rd, info
    st_, hs = addr.triple(real, src, True, loop_of)
    info.update(src=st_, src_how=hs)
    return "nested", rs, rd, info


def tunnel_owner(rows, tun, owners):
    """The structure uid owning tunnel `tun` (via its inner frame diagrams in `owners`), else ExecStop."""
    fr = set(str(int(r["frame_diagram"] or 0)) for r in rows if r["owner_uid"] == tun and r["term_class"] == "InnerTerminal")
    own = set(int((owners or {})[f][1]) for f in fr if f in (owners or {}))
    if len(own) != 1:
        raise ExecStop("ADDRESS: tunnel #{0}: owner structure not unique from its inner frames {1} ({2} owners known)".format(
            tun, sorted(fr), len(owners or {})))
    return own.pop()


class Addr(object):
    """Terminal -> live index triple (Diagram idx, Nodes[] idx, Terminals[] idx). `rd` = reader with diagrams(),
    node_uids(didx), node_terms(didx, nidx) -> (echo, rows[i,name,is_source,wire]). Graph rows = the LAST real read.
    A node's terminal index is taken from the ORDER PROOF (the node's rows in the read, in read order, have the same
    (name, direction, wire) sequence as node_terms) or else from a UNIQUE (name, direction, wire) match. A border
    terminal of a created register (outer face) is a terminal of its LOOP (the loop the plan created it on)."""

    def __init__(self, rd, owners=None):
        self.rd = rd
        self.owners = owners or {}  # str(frame diagram uid) -> [structure class, structure uid] (PD185)
        self.cache = {}           # term_uid -> (node uid, Terminals[] index) proved while the terminal was WIRED
        self.loops = {}           # loop uid -> {"diag": diagram uid, "keys": [(name, is_source)], "track": {term_uid: idx}}

    # ------------------------------------------------------------------ REGISTER OUTER FACES (loop Terminals[] indexes)
    # A created register's outer terminals are terminals of the LOOP and are UNWIRED when first used, and their names
    # are not stable (stage_d1_l7_1b.log:274), so neither a wire nor a name can address them. They are TRACKED: the
    # loop's Terminals[] list is read right before and right after add_shift_reg (the two inserted entries, one source
    # and one sink, ARE the new R outer and L outer) and re-aligned after every later op (difflib on (name, direction):
    # equal blocks and same-length replace blocks carry an index over; anything else loses it, and using a lost index
    # stops the run).
    def _loop_list(self, loop):
        L = self.loops[loop]
        didx = self.rd.diagrams().index(L["diag"])
        nidx = self.rd.node_uids(didx).index(loop)
        echo, nt = self.rd.node_terms(didx, nidx)
        if echo != loop:
            raise ExecStop("loop #{0} echo {1!r}".format(loop, echo))
        return [(x["name"], bool(x["is_source"]), int(x["wire"] or 0)) for x in nt]

    def snap_loop(self, loop, diag):
        self.loops.setdefault(loop, {"diag": diag, "keys": None, "track": {}})
        self.loops[loop]["keys"] = self._loop_list(loop)

    def track_new(self, loop, r_outer, l_outer):
        import difflib
        L = self.loops[loop]
        old, new = L["keys"], self._loop_list(loop)
        ins = []
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
            if tag == "insert":
                ins += list(range(j1, j2))
            elif tag != "equal":
                raise ExecStop("add_shift_reg on #{0}: the loop's Terminals[] changed beyond an insertion ({1})".format(loop, tag))
        src = [j for j in ins if new[j][1]]
        snk = [j for j in ins if not new[j][1]]
        if len(src) != 1 or len(snk) != 1:
            raise ExecStop("add_shift_reg on #{0}: inserted entries {1} are not one source + one sink".format(loop, [new[j] for j in ins]))
        L["track"][r_outer], L["track"][l_outer] = src[0], snk[0]
        L["keys"] = new
        return {"r_outer_idx": src[0], "l_outer_idx": snk[0]}

    def retrack(self):
        import difflib
        lost = []
        for loop, L in self.loops.items():
            if not L["track"]:
                continue
            new = self._loop_list(loop)
            m = {}
            if len(new) == len(L["keys"]):
                # the op added/removed no border terminal on this loop: indexes are unchanged. Names are NOT a key
                # here - wiring a register's inner face renames its outer face ('' -> 'error out'), and aligning on
                # names mis-mapped the faces (tools/bench/stagexec_l7_bench.log run 1, op 8 wired SR2L for SR1L)
                m = dict((i, i) for i in range(len(new)))
            else:
                ko = [k[1:] for k in L["keys"]]          # (direction, wire): a wired face is anchored by its wire uid
                kn = [k[1:] for k in new]
                for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ko, kn, autojunk=False).get_opcodes():
                    if tag == "equal" or (tag == "replace" and i2 - i1 == j2 - j1):
                        for k in range(i2 - i1):
                            m[i1 + k] = j1 + k
            for t, i in list(L["track"].items()):
                if i in m:
                    L["track"][t] = m[i]
                else:
                    L["track"][t] = None
                    lost.append(t)
            L["keys"] = new
        return lost

    def triple(self, real, term_uid, is_source, loop_of=None):
        rows = [r for r in real if r["term_uid"] == term_uid]
        if len(rows) != 1:
            raise ExecStop("ADDRESS: terminal #{0}: {1} rows in the live read".format(term_uid, len(rows)))
        r = rows[0]
        if bool(r["is_source"]) != bool(is_source):
            raise ExecStop("ADDRESS: terminal #{0} is_source {1}, wanted {2}".format(term_uid, r["is_source"], is_source))
        t, how = self._triple(real, r, term_uid, loop_of)
        if r["wire_uid"]:
            self.cache[term_uid] = (self.rd.node_uids(t[0])[t[1]], t[2])
        return t, how

    def ct(self, real, term_uid):
        """PD187(b) / 179(b): a ControlTerminal end -> {ct, diag, didx, name, is_source, wire}. term_uid == its own uid,
        owner == its Diagram (which must be in the live Diagram list), membership in report_all('ControlTerminal')."""
        rows = [r for r in real if r["term_uid"] == term_uid]
        if len(rows) != 1:
            raise ExecStop("ADDRESS-CT: #{0}: {1} rows in the live read".format(term_uid, len(rows)))
        r = rows[0]
        if not is_ct(r):
            raise ExecStop("ADDRESS-CT: #{0} is {1}, not a ControlTerminal".format(term_uid, V.node_class(r)))
        diag = int(r["frame_diagram"] or 0)
        if r["owner_class"] not in ("Diagram", "TopLevelDiagram"):
            raise ExecStop("ADDRESS-CT: #{0} owner {1} #{2} is not a Diagram".format(term_uid, r["owner_class"], r["owner_uid"]))
        # the diagram is the row's frame_diagram: stagesim's move_in re-homes frame_diagram but leaves a ControlTerminal
        # row's owner_uid at the old Diagram (prerun_l2a1_82.log, #5634 639 vs 23166); compare() never reads owner_uid
        stale = int(r["owner_uid"]) != diag
        if term_uid not in self.rd.ct_uids():
            raise ExecStop("ADDRESS-CT: #{0} not in report_all('ControlTerminal')".format(term_uid))
        dl = self.rd.diagrams()
        if diag not in dl:
            raise ExecStop("ADDRESS-CT: #{0}'s Diagram #{1} not in the live Diagram list".format(term_uid, diag))
        a = {"ct": term_uid, "diag": diag, "didx": dl.index(diag), "name": r["term_name"], "is_source": bool(r["is_source"]),
             "wire": int(r["wire_uid"] or 0)}
        return a, "ControlTerminal route 179(b): own uid #{0}, owner Diagram #{1} (idx {2}), in report_all{3}".format(
            term_uid, diag, a["didx"], " (row owner_uid #{0} stale)".format(r["owner_uid"]) if stale else "")

    def _triple(self, real, r, term_uid, loop_of):
        node = V.node_of(r)
        if is_ct(r):                                                         # PD187(b): never a Nodes[] triple
            raise ExecStop("ADDRESS: #{0} is a ControlTerminal: not in any Diagram.Nodes[] - its route is 179(b) "
                           "(Addr.ct: own uid, owner Diagram #{1}, report_all('ControlTerminal'))".format(term_uid, r["frame_diagram"]))
        diag = int(r["frame_diagram"])
        mine = [x for x in real if V.node_of(x) == node and int(x["frame_diagram"] or 0) == diag]
        if r["owner_class"] == FSIT_CLS:
            raise ExecStop("ADDRESS: #{0} is a FlatSequenceInnerTunnel face (#{1}): not a Nodes[] triple - its route is "
                           "Left/Right Terminal (docs/NAMES.md:1245-1255, OpFsInnerTunnelConnect_v1)".format(term_uid, node))
        if r["owner_class"] in OWNER_ROUTED:                                 # PD185: via the owner structure's Terminals[]
            if r["term_class"] != "OuterTerminal":
                raise ExecStop("ADDRESS: #{0} is an INNER face of {1} #{2}: only the outer face's owner route is measured "
                               "(l2a1_faces_81.log)".format(term_uid, r["owner_class"], node))
            node, mine = tunnel_owner(real, node, self.owners), None
        if r["owner_class"] in SR_CLS and r["term_class"] == "OuterTerminal":
            if not loop_of or r["owner_uid"] not in loop_of:
                raise ExecStop("ADDRESS: register #{0}'s loop is unknown".format(r["owner_uid"]))
            node, mine = loop_of[r["owner_uid"]], None
            tr = (self.loops.get(node) or {}).get("track", {})
            if term_uid in tr:
                if tr[term_uid] is None:
                    raise ExecStop("ADDRESS: register face #{0}: its tracked loop index was lost by an earlier op".format(term_uid))
                dl = self.rd.diagrams()
                didx = dl.index(diag)
                nidx = self.rd.node_uids(didx).index(node)
                echo, nt = self.rd.node_terms(didx, nidx)
                if echo != node:
                    raise ExecStop("ADDRESS: loop #{0} echo {1!r}".format(node, echo))
                # 1st: the face's LIVE name + direction + wire, if exactly one loop terminal has it (the stage_d1_l7_1b /
                # stage_d1_l7_r route, which worked); 2nd: the tracked index. Both are reported.
                want = (r["term_name"], bool(r["is_source"]), int(r["wire_uid"] or 0))
                hits = [int(x["i"]) for x in nt if (x["name"], bool(x["is_source"]), int(x["wire"] or 0)) == want]
                if len(hits) == 1:
                    return (didx, nidx, hits[0]), "unique live name {0!r} on loop #{1} (tracked index {2}{3})".format(
                        r["term_name"], node, tr[term_uid], "" if tr[term_uid] == hits[0] else " DISAGREES")
                x = nt[tr[term_uid]]
                if bool(x["is_source"]) != bool(r["is_source"]) or int(x["wire"] or 0) != int(r["wire_uid"] or 0):
                    raise ExecStop("ADDRESS: register face #{0}: tracked index {1} reads {2}".format(term_uid, tr[term_uid], x))
                return (didx, nidx, tr[term_uid]), "tracked loop index {0} ({1} loop terminals share its live name {2!r})".format(
                    tr[term_uid], len(hits), r["term_name"])
        dl = self.rd.diagrams()
        if diag not in dl:
            raise ExecStop("ADDRESS: diagram #{0} not in the live Diagram list".format(diag))
        didx = dl.index(diag)
        uids = self.rd.node_uids(didx)
        if node not in uids:
            raise ExecStop("ADDRESS: node #{0} not in Diagram[{1}] (#{2}).Nodes[]".format(node, didx, diag))
        nidx = uids.index(node)
        echo, nt = self.rd.node_terms(didx, nidx)
        if echo != node:
            raise ExecStop("ADDRESS: uid echo {0!r} != #{1}".format(echo, node))
        key = lambda x: (x["name"], bool(x["is_source"]), int(x["wire"] or 0))            # noqa: E731
        c = self.cache.get(term_uid)
        if c and c[0] == node and c[1] < len(nt):
            x = nt[c[1]]
            if bool(x["is_source"]) == bool(r["is_source"]) and int(x["wire"] or 0) == int(r["wire_uid"] or 0):
                return (didx, nidx, c[1]), "cached index (proved by its wire uid while wired)"
        if mine is not None and [key(x) for x in nt] == [(x["term_name"], bool(x["is_source"]), int(x["wire_uid"] or 0))
                                                         for x in mine]:
            return (didx, nidx, [x["term_uid"] for x in mine].index(term_uid)), "order-proof"
        hits = [x for x in nt if key(x) == (r["term_name"], bool(r["is_source"]), int(r["wire_uid"] or 0))]
        if len(hits) != 1:
            raise ExecStop("ADDRESS: #{0} {1!r} on node #{2}: {3} (name,dir,wire) matches in {4}".format(
                term_uid, r["term_name"], node, len(hits), [key(x) for x in nt][:14]))
        return (didx, nidx, int(hits[0]["i"])), "unique-match"


# ============================================================================================ the executor
class Executor(object):
    def __init__(self, plan_path, backend, log=print):
        self.plan_path = plan_path
        self.plan, self.step_paths = load_final_plan(plan_path)
        self.ops = compile_plan(self.plan)
        self.be = backend
        self.log = log
        self.bind = {"obj": {}, "term": {}}
        self.loop_of = {}
        self.allow = set()
        self.report = []
        self.sym_real = {}

    def step(self, n):
        return _j(_abs(self.step_paths[n]))

    def sim_uid(self, st, ref):
        if isinstance(ref, int):
            return ref
        return st["sym"][ref]

    def real_term(self, st_prev, st_after, addr_ref, want_source):
        """The plan end -> the REAL terminal uid: resolved on the simulated state (the plan's own resolver), then
        through the binding."""
        try:
            r = SS.resolve_addr(st_prev, addr_ref, want_source)
        except SS.SimError:
            r = SS.resolve_addr(st_after, addr_ref, want_source)
        t = self.bind["term"].get(r["term_uid"], r["term_uid"])
        if t < 0:
            raise ExecStop("terminal {0} of {1} is not bound yet".format(r["term_uid"], addr_ref))
        return t

    def run(self):
        be, A = self.be, self.plan["actions"]
        real = be.read()
        st0 = self.step(0)["state"]
        d = compare(st0["terminals"], real, self.bind)
        self.report.append({"op": "base", "acts": [0], "diff": d})
        self.log("  STEPX 00 base read vs step_00: diff {0}".format(d["n"]))
        if d["n"]:
            raise ExecStop("BASE: the scratch copy's graph differs from the plan's base graph: {0}".format(
                {k: v[:6] for k, v in d.items() if isinstance(v, list) and v}))
        # PRIME: every plan end on a BASE node whose terminal is wired now gets its Terminals[] index proved by its
        # wire uid, before any edit (the stage_d1_l7_r A0 anchor for #2048 'length', generalised)
        be.addr.owners = st0.get("owners") or be.addr.owners
        # PD187(a): reader parity at base, per touched diagram, BEFORE any address is proved
        diags = touched_diagrams(self.plan, st0)
        rows, npar = reader_parity(be.addr.rd, SimReader(_StateHolder(st0)), diags, be.obj_classes(real),
                                   classes_of(st0["terminals"], st0.get("objs")))
        self.report[0]["parity"] = {"diagrams": diags, "n": npar, "rows": rows}
        self.log("  PARITY {0} touched diagram(s) {1}: one-side-only Nodes[] entries {2}".format(len(diags), diags, npar))
        if npar:
            raise ExecStop("PARITY: SimReader vs real Nodes[] differ on {0} entr(ies) - stop before op 1: {1}".format(
                npar, json.dumps([r for r in rows if r.get("only_real") or r.get("only_sim") or r.get("missing_on")], default=str)[:900]))
        rightin = set(o["acts"][0] for o in self.ops if o["kind"] == "wire_sr" and o["variant"] == "RightIn")
        primed, why, ct_primed = 0, [], 0
        for i, a in enumerate(A, 1):
            for side, src in (("src", True), ("dst", False), ("at", None)):
                e = a.get(side)
                if e is None or _sym_of(e)[0]:
                    continue
                if SS.obj_class(st0, e.get("uid") if isinstance(e, dict) else None) == FP:
                    try:                                   # PD187(b): every ControlTerminal end, source or sink, bare or wired
                        be.addr.ct(real, SS.resolve_addr(st0, e, src if src is not None else True)["term_uid"])
                        ct_primed += 1
                    except (ExecStop, SS.SimError) as x:
                        why.append(str(x)[:160])
                    continue
                if side == "src" and i not in rightin:     # PD185: a connect source is routed by its WIRE, never by index
                    continue
                try:
                    r = SS.resolve_addr(st0, e, src if src is not None else True)
                except SS.SimError:
                    continue
                if r["wire_uid"] and r["term_uid"] not in be.addr.cache:
                    try:
                        be.addr.triple(real, r["term_uid"], r["is_source"])
                        primed += 1
                    except ExecStop as x:
                        why.append(str(x)[:160])
        self.report[0]["primed"] = {"n": primed, "ct": ct_primed, "unprovable": why[:10]}
        self.log("  PRIME {0} terminal indexes proved at base; {1} ControlTerminal end(s) by 179(b); unprovable {2}".format(
            primed, ct_primed, why[:4]))
        if why:                                            # PD185(3): an unprovable end STOPS before op 1
            raise ExecStop("PRIME: {0} wired end(s) not addressable at base - stop before op 1: {1}".format(len(why), why[:6]))
        for k, op in enumerate(self.ops, 1):
            first, last = op["acts"][0], op["acts"][-1]
            prev = self.step(first - 1)["state"]
            after = self.step(last)
            be.addr.owners = prev.get("owners") or be.addr.owners
            t0 = time.time()
            if op["kind"] == "add_sr":
                a = A[first - 1]
                be.addr.snap_loop(int(a["loop"]), int(after["state"]["diagrams"][str(a["body"])]))
            res = self.execute(op, prev, after["state"], real)
            real_new = be.read()
            made = {}
            if op["kind"] in ("add_sr", "tunnel"):
                made = bind_new(real, real_new, prev["terminals"], after["state"]["terminals"], self.bind)
                if op["kind"] == "add_sr":
                    a = A[first - 1]
                    outer = {}
                    for su, ru in made.items():
                        self.loop_of[ru] = int(a["loop"])
                        so = [r for r in after["state"]["terminals"] if r["owner_uid"] == su and r["term_class"] == "OuterTerminal"]
                        outer[so[0]["owner_class"]] = self.bind["term"][so[0]["term_uid"]]
                    res = dict(res or {}, track=be.addr.track_new(int(a["loop"]), outer["RightShiftRegister"],
                                                                  outer["LeftShiftRegister"]))
            lost = be.addr.retrack() if op["kind"] != "add_sr" else []
            if lost:
                res = dict(res or {}, lost_register_faces=lost)
                if op["kind"] == "tunnel":
                    res = dict(res or {}, index_mode=self.be.index_mode_fix(
                        next(iter(made.values())), bool(A[first - 1].get("indexing"))))
            for n in op["acts"]:
                eff = self.step(n).get("effect") or {}
                self.allow.update(eff.get("allow_either") or [])
            d = compare(after["state"]["terminals"], real_new, self.bind, self.allow)
            rec = {"k": k, "op": op["kind"], "acts": op["acts"], "ids": [A[n - 1].get("id") for n in op["acts"]],
                   "checkpoint": [A[n - 1].get("checkpoint") for n in op["acts"] if A[n - 1].get("checkpoint")],
                   "result": res, "bound": made, "diff": d, "secs": round(time.time() - t0, 1)}
            self.report.append(rec)
            self.log("  STEPX {0:02d} {1:<14} acts {2} ids {3} bound {4} diff {5}{6}".format(
                k, op["kind"], op["acts"], rec["ids"], made, d["n"],
                "  CHECKPOINT " + ",".join(rec["checkpoint"]) if rec["checkpoint"] else ""))
            if d["n"]:
                raise ExecStop("STEP-DIFF after real op {0} ({1}, plan actions {2} {3}): {4}".format(
                    k, op["kind"], op["acts"], rec["ids"], json.dumps({x: y for x, y in d.items() if y and x != "n"},
                                                                       default=str)[:1500]))
            real = real_new
        fin = getattr(be, "run_deferred", None)   # card 80-3: deferred op errors are answered by their declared gates
        if fin:
            fin()
        return real

    # --------------------------------------------------------------------------- one real op
    def execute(self, op, prev, after, real):
        A, be = self.plan["actions"], self.be
        a = A[op["acts"][0] - 1]
        kind = op["kind"]
        if kind == "move_in":
            return be.move_in(int(a["nodes"][0]), int(a["dest_diagram"]), tuple(a["pos"]), op)
        if kind == "add_sr":
            return be.add_sr(int(a["loop"]), int(a.get("y") or 120), op)
        if kind == "wire_sr":
            reg = self.bind["obj"].get(prev["sym"][op["reg"]])
            if reg is None:
                raise ExecStop("wire_sr: {0} not bound".format(op["reg"]))
            right = reg if op["variant"] == "RightIn" else self._right_of(prev, op["reg"])
            end = a["src"] if op["variant"] == "RightIn" else a["dst"]
            t = self.real_term(prev, after, end, op["variant"] == "RightIn")
            loop = self.loop_of[reg]
            return be.wire_sr(op["variant"], loop, right, t, real, op)
        if kind == "tunnel":
            ai, ao = A[op["in_act"] - 1], A[op["out_act"] - 1]
            src = self.real_term(prev, after, ai["src"], True)
            dst = self.real_term(prev, after, ao["dst"], False)
            return be.connect(src, dst, real, self.loop_of, op)
        if kind == "branch":
            tun = self.bind["obj"].get(prev["sym"][op["tunnel"]])
            dst = self.real_term(prev, after, a["dst"], False)
            return be.branch(tun, dst, real, self.loop_of, op)
        if kind == "connect":
            src = self.real_term(prev, after, a["src"], True)
            dst = self.real_term(prev, after, a["dst"], False)
            return be.connect(src, dst, real, self.loop_of, op)
        if kind == "delete_wire":
            w = int(a["wire_uid"])
            ts = set(self.bind["term"].get(r["term_uid"], r["term_uid"]) for r in prev["terminals"] if r["wire_uid"] == w)
            live = set(r["wire_uid"] for r in real if r["term_uid"] in ts and r["wire_uid"])
            if not live and ts and ts <= self.allow:
                return {"already_gone": "w{0}: every terminal is an allow_either only-sink source, bare in the live "
                                        "graph (LabVIEW deleted it with the node)".format(w)}
            if len(live) != 1:
                raise ExecStop("delete_wire w{0}: its {1} terminals sit on {2} live wires {3}".format(w, len(ts), len(live), sorted(live)))
            lw = live.pop()
            if set(r["term_uid"] for r in real if r["wire_uid"] == lw) != ts:
                raise ExecStop("delete_wire w{0}: live wire {1} carries other terminals than the simulated one".format(w, lw))
            return be.delete_wire(lw, op, plan_wire=w)
        if kind == "delete_object":
            u = SS.resolve_uid(prev, a["uid"])
            u = self.bind["obj"].get(u, u)
            rows = [r for r in real if r["owner_uid"] == u]
            if not rows:
                if a.get("missing_ok") and u not in set(r["owner_uid"] for r in prev["terminals"]):
                    return {"already_absent": u}
                raise ExecStop("delete_object #{0}: not in the live graph".format(u))
            return be.delete_object(rows[0]["owner_class"], u, op)
        if kind == "remove_bad_wires":
            return be.rbw(op)
        raise ExecStop("no executor for {0}".format(kind))

    def _right_of(self, st, sym_left):
        return self.bind["obj"].get(st["sym"][sym_left[:-1] + "R"])


# ============================================================================================ LabVIEW backend
class LVReader(object):
    def __init__(self, g, work):
        self.g, self.work = g, work

    def diagrams(self):
        return [int(d["uid"]) for d in self.g.report_all(self.work, "Diagram")]

    def node_uids(self, didx):
        return [int(r["uid"]) for r in self.g.node_labels(self.work, didx)]

    def node_terms(self, didx, nidx):
        return self.g.node_terms_uid(self.work, didx, nidx)

    def ct_uids(self):
        return set(int(o["uid"]) for o in self.g.report_all(self.work, "ControlTerminal"))


def check_sink_gates(sink_gates, gates):
    """SINK GATES (card 80-3, retrospective-cycle79 device-failed at the old whitelist here): a recipe may let a
    wire_indicators op error pass ONLY by declaring, per sink, a NAMED gate it owns that reads that exact sink.
    `sink_gates` = [{"gate": <label>, "sink": [<owner_uid>, <term_name>]}]; `gates` = {<label>: callable(entry) ->
    (ok, detail)}. A declaration naming a gate absent from `gates` (or not callable), or a malformed sink, is REFUSED."""
    out = []
    for d in sink_gates or []:
        name, sink = d.get("gate"), d.get("sink")
        if not isinstance(sink, (list, tuple)) or len(sink) != 2:
            raise ExecStop("sink gate {0!r}: sink must be [owner_uid, term_name], got {1!r}".format(name, sink))
        if name not in (gates or {}) or not callable(gates[name]):
            raise ExecStop("sink gate {0!r} for sink {1}: no such gate declared by the recipe (declared: {2})".format(
                name, list(sink), sorted(gates or {})))
        out.append({"gate": name, "sink": [int(sink[0]), str(sink[1])]})
    return out


def sink_gate_for(tag, err, sink, decls):
    """The declaration whose sink == `sink` exactly, else ExecStop (the op error stops the run)."""
    key = [int(sink[0]), str(sink[1])]
    hit = [d for d in decls if d["sink"] == key]
    if not hit:
        raise ExecStop("{0}: op error {1} on sink {2} - no declared gate reads that sink (declared sinks: {3})".format(
            tag, err, key, [d["sink"] for d in decls]))
    return hit[0]


class LVBackend(object):
    """Every mutator is a stagekit / gscript verb the L7 stages used; each is followed by the measured junk purge."""

    def __init__(self, s, fs_pairs, sink_gates=None, gates=None):
        import stagekit as K
        import gscript as g
        self.K, self.g, self.s, self.fs = K, g, s, fs_pairs
        self.B = K.mod("build_d1_v0")
        self.C82 = K.mod("build_opfsinnertunnelconnect_v0")
        self.addr = Addr(LVReader(g, s.work))
        self.reads = []
        self._init_sink_gates(sink_gates, gates)

    def _init_sink_gates(self, sink_gates, gates):
        self.gates = dict(gates or {})
        self.sink_gates = check_sink_gates(sink_gates, self.gates)
        self.deferred = []

    def run_deferred(self):
        """Executor.run's last act: every deferred op error's declared gate READS its sink now; a gate that fails stops."""
        for e in self.deferred:
            ok, detail = self.gates[e["gate"]](dict(e))
            self.s.gate("{0} (declared sink gate for {1} on {2})".format(e["gate"], e["tag"], e["sink"]), ok, detail)
            e["gate_ok"] = bool(ok)
            if not ok:
                raise ExecStop("declared sink gate {0!r} failed on {1}: {2}".format(e["gate"], e["sink"], str(detail)[:300]))

    def read(self):
        lv = self.K.mod("wiki_build").read_live(self.s.work, fs_pairs=self.fs)
        self.reads.append(lv["secs"])
        self.last_objs = lv["objs"]
        return dedupe(lv["terminals"])

    def obj_classes(self, real):
        return classes_of(real, getattr(self, "last_objs", None))

    def _done(self, rec, tag):
        self.s.junk_purge(tag)
        if rec.get("err"):
            raise ExecStop("{0}: op error {1}".format(tag, rec["err"]))
        return {"err": rec.get("err"), "s": rec.get("s")}

    def move_in(self, uid, dest, pos, op):
        rec = self.s.move_in(uid, self.B.diag_index(self.s.work, dest), pos)
        return self._done(rec, "move_in #{0}".format(uid))

    def add_sr(self, loop, y, op):
        rec = self.s.add_shift_reg(self.s.uid_index("WhileLoop", loop), y_position=y)
        return self._done(rec, "add_sr #{0}".format(loop))

    def _reg_index(self, li, right):
        rights = []
        for k in range(16):
            u = self.g.shift_reg(self.s.work, li, k).get("uid")
            if u is None:
                break
            rights.append(int(u))
        if right not in rights:
            raise ExecStop("register #{0} not in Shift Registers[] {1}".format(right, rights))
        return rights.index(right)

    def wire_sr(self, variant, loop, right, term, real, op):
        li = self.s.uid_index("WhileLoop", loop)
        k = self._reg_index(li, right)
        (_d, n, t), how = self.addr.triple(real, term, variant == "RightIn")
        rec = self.s.wire_sr(variant, li, k, node_index=n, term_index=t)
        out = self._done(rec, "wire_sr {0}".format(variant))
        out.update(how=how, triple=[_d, n, t], reg=k)
        return out

    def _cfw(self, w, owner, dst_triple):
        F = self.K.mod("build_opconnectfromwire_v0")
        hit = [x for x in F.wire_source_owner(self.s.work, w, n=8) if x.get("owner_uid") == owner and x.get("is_source")]
        if len(hit) != 1:
            raise ExecStop("w{0}: {1} source term(s) owned by #{2}".format(w, len(hit), owner))
        rec = self.s.connect_from_wire(dst_triple[0], dst_triple[1], dst_triple[2], w, int(hit[0]["i"]))
        res = rec.get("result")
        if isinstance(res, (list, tuple)) and len(res) > 2 and res[2]:
            rec["err"] = rec.get("err") or res[2]
        return rec

    def connect(self, src, dst, real, loop_of, op):
        kind, rs, rd, info = connect_route(self.addr, real, src, dst, loop_of)   # PD187(b): the route both backends take
        if kind == "indicator":
            return self.indicator(rs, rd)
        dt, hd = info["dst"], info["dst_how"]
        if kind == "ctl":                                  # card 82-2: measured in tools/bench/ctsrc_l2a1_82.log
            di = self.s.uid_index(rd["owner_class"], int(rd["owner_uid"]))
            if di is None:
                raise ExecStop("ctl: sink node {0} #{1} not in its class traverse".format(rd["owner_class"], rd["owner_uid"]))
            rec = self.s._op("wire_control", lambda: self.g.wire_control(
                self.s.work, [info["ctl_label"]], rd["owner_class"], di, [info["dst_name"]], src_diagram_index=info["ctl_didx"]),
                "{0!r}@D[{1}] -> {2}[{3}].{4!r}".format(info["ctl_label"], info["ctl_didx"], rd["owner_class"], di, info["dst_name"]))
            out = self._done(rec, "connect #{0}->#{1}".format(src, dst))
            out["how"] = ["ctl", info["src_ct"], hd]
            return out
        if kind == "cfw":
            rec = self._cfw(int(rs["wire_uid"]), V.node_of(rs) if V.node_class(rs) != FP else rs["owner_uid"], dt)
            how = ["cfw", hd]
        else:
            st, hs = info["src"], info["src_how"]
            N = self.K.mod("build_opconnectnested_v1")
            lab = json.load(open(N.MAP_OUT, encoding="utf-8"))
            rec = self.s._op("connect_nested_v1", lambda: N.connect_nested_v1(self.s.work, dt[0], dt[1], dt[2], st[0], st[1], st[2], lab),
                             "D[{0}].N[{1}].t{2} <- D[{3}].N[{4}].t{5}".format(dt[0], dt[1], dt[2], st[0], st[1], st[2]))
            res = rec.get("result")
            if isinstance(res, (list, tuple)) and len(res) > 2 and res[2]:
                rec["err"] = rec.get("err") or res[2]
            how = ["nested", hs, hd]
        out = self._done(rec, "connect #{0}->#{1}".format(src, dst))
        out["how"] = how
        return out

    def indicator(self, rs, rd):
        if not rs["wire_uid"]:
            raise ExecStop("wire_indicators needs a WIRED source (#{0} is bare)".format(rs["term_uid"]))
        di = self.B.diag_index(self.s.work, int(rs["frame_diagram"]))
        rec = self.s.wire_indicators(self.s.uid_index(rs["owner_class"], rs["owner_uid"]), [rs["term_name"]],
                                     [rd["term_name"]], diagram_index=di, node_class=rs["owner_class"])
        tag = "wire_indicators #{0}".format(rs["owner_uid"])
        if rec.get("err"):                        # no whitelist (card 80-3): stop unless a declared gate reads this sink
            self.s.junk_purge(tag)
            sink = [rd["owner_uid"], rd["term_name"]]
            d = sink_gate_for(tag, rec["err"], sink, self.sink_gates)
            self.deferred.append({"gate": d["gate"], "sink": d["sink"], "tag": tag, "err": str(rec["err"])[:300],
                                  "source": [rs["owner_uid"], rs["term_name"]]})
            self.s.fact("OP-ERROR {0} on sink {1} DEFERRED to declared gate {2!r}: {3}".format(tag, d["sink"], d["gate"],
                                                                                                str(rec["err"])[:200]))
            return {"err": rec["err"], "s": rec.get("s"), "how": "wire_indicators", "deferred_to": d["gate"]}
        out = self._done(rec, tag)
        out["how"] = "wire_indicators"
        return out

    def branch(self, tun, dst, real, loop_of, op):
        outer = [r for r in real if r["owner_uid"] == tun and r["term_class"] == "OuterTerminal" and r["is_source"]]
        if len(outer) != 1 or not outer[0]["wire_uid"]:
            raise ExecStop("branch: tunnel #{0} has no wired outer source".format(tun))
        rd = next(r for r in real if r["term_uid"] == dst)
        if V.node_class(rd) == FP:
            return self.indicator(outer[0], rd)
        dt, hd = self.addr.triple(real, dst, False, loop_of)
        out = self._done(self._cfw(int(outer[0]["wire_uid"]), tun, dt), "branch #{0}".format(tun))
        out["how"] = ["cfw off tunnel outer", hd]
        return out

    def index_mode_fix(self, tun, indexing):
        want = 1 if indexing else 0
        li = self.s.uid_index("LoopTunnel", tun)
        t = self.g.tunnels(self.s.work, li)
        if t.get("index_mode") != want:
            self.s._op("set_index_mode", lambda: self.g.set_index_mode(self.s.work, li, want), "#{0} -> {1}".format(tun, want))
            t = self.g.tunnels(self.s.work, self.s.uid_index("LoopTunnel", tun))
        if t.get("index_mode") != want:
            raise ExecStop("tunnel #{0} IndexMode {1} != plan {2}".format(tun, t.get("index_mode"), want))
        return want

    def delete_wire(self, w, op, plan_wire=None):
        rec = self.s.delete_wire(w, "stagexec")
        return self._done(rec, "delete_wire w{0} (plan w{1})".format(w, plan_wire))

    def delete_object(self, cls, uid, op):
        rec = self.s.delete_object(cls, uid, "stagexec")
        return self._done(rec, "delete_object {0} #{1}".format(cls, uid))

    def rbw(self, op):
        r = self.s.broken_wire_count(allow_mutation=True, tag="stagexec RBW")
        return {"rbw": r}


# ============================================================================================ SIMULATED backend (dry)
class SimReader(object):
    def __init__(self, be):
        self.be = be

    def diagrams(self):
        return sorted(set(int(r["frame_diagram"] or 0) for r in self.be.st["terminals"]))

    def _routed(self, d):
        """PD185: (owner structure, outer row) for every owner-routed tunnel face on diagram d - as LabVIEW lists them:
        the tunnel is NOT a node, its outer face is a terminal of its owner structure."""
        st, out = self.be.st, []
        for r in st["terminals"]:
            if r["owner_class"] in OWNER_ROUTED and r["term_class"] == "OuterTerminal" and int(r["frame_diagram"] or 0) == d:
                try:
                    out.append((tunnel_owner(st["terminals"], r["owner_uid"], st.get("owners")), r))
                except ExecStop:
                    pass            # owner unknown: listed nowhere, so addressing it stops in Addr._triple (as the real one)
        return out

    def node_uids(self, didx):
        d = self.diagrams()[didx]
        out = []
        for r in self.be.st["terminals"]:
            n = V.node_of(r)
            if int(r["frame_diagram"] or 0) == d and n not in out and listed_as_node(r):
                out.append(n)
        for o, _r in self._routed(d):
            if o not in out:
                out.append(o)
        for L in self.be.st["loops"] or []:                     # PD187 fit: a loop is a node of its PARENT diagram only
            u = int(L["loop_uid"])
            p = loop_parent(self.be.st, L)                      # unplaceable (no owners map) -> legacy: every diagram,
            if u not in out and p in (d, None):                 # which the PRIME parity then reports as only_sim
                out.append(u)
        return out

    def node_terms(self, didx, nidx):
        d = self.diagrams()[didx]
        u = self.node_uids(didx)[nidx]
        rows = [r for r in self.be.st["terminals"] if V.node_of(r) == u and int(r["frame_diagram"] or 0) == d
                and r["owner_class"] not in NOT_NODES and not is_ct(r)] + [r for o, r in self._routed(d) if o == u]
        loop = next((L for L in self.be.st["loops"] or [] if int(L["loop_uid"]) == u), None)
        if loop:
            regs = set(int(x) for x in loop.get("right_uids") or []) | set(
                int(y) for v in (loop.get("left_of") or {}).values() for y in (v if isinstance(v, list) else [v]))
            rows = rows + [r for r in self.be.st["terminals"] if r["owner_uid"] in regs and r["term_class"] == "OuterTerminal"]
        return u, [{"i": i, "name": r["term_name"], "is_source": r["is_source"], "wire": r["wire_uid"]}
                   for i, r in enumerate(rows)]

    def ct_uids(self):                                                  # the report_all('ControlTerminal') analogue
        return set(r["term_uid"] for r in self.be.st["terminals"] if is_ct(r))


class SimBackend(object):
    """The DRY backend: every real op applies the plan actions it covers with stagesim's own OPS on a private state
    (the measured models), then renumbers the created uids to fresh POSITIVE ones, as LabVIEW would; the executor's
    compile / address / bind / compare path runs unchanged. `fault` injects one defect for the self-test."""

    def __init__(self, plan, base_state, models, fault=None):
        self.plan, self.st, self.models, self.fault = plan, copy.deepcopy(base_state), models, fault or {}
        self.next = 10 ** 7
        self.addr = Addr(SimReader(self))
        self.calls = []
        self.S1 = SS.load_s1(plan)

    def read(self):
        return copy.deepcopy(dedupe(self.st["terminals"]))

    def obj_classes(self, real):
        return classes_of(real, self.st.get("objs"))

    def _apply(self, op, check=None):
        self.calls.append(op["kind"])
        for n in op["acts"]:
            a = self.plan["actions"][n - 1]
            P = SS.model_for(a["op"], self.models)[0]
            SS.OPS[a["op"]](self.st, a, P, self.S1, {})
        ren = {}
        for r in self.st["terminals"]:
            for k in ("owner_uid", "term_uid", "wire_uid"):
                if isinstance(r[k], int) and r[k] < 0:
                    if r[k] not in ren:
                        self.next += 1
                        ren[r[k]] = self.next
                    r[k] = ren[r[k]]
        for o in self.st["objs"]:
            if int(o["uid"]) < 0:
                o["uid"] = ren.setdefault(int(o["uid"]), self.next + 1000)
        for L in self.st["loops"] or []:
            L["right_uids"] = [ren.get(int(u), int(u)) for u in L.get("right_uids") or []]
            L["left_of"] = dict((str(ren.get(int(k), int(k))), [ren.get(int(x), int(x)) for x in (v if isinstance(v, list) else [v])])
                                for k, v in (L.get("left_of") or {}).items())
        self.st["sym"] = dict((k, ren.get(v, v)) for k, v in self.st["sym"].items())
        f = self.fault
        if f.get("at") == op["acts"][-1]:
            if f.get("kind") == "drop_edge":                   # a real op that made one edge fewer
                r = next(r for r in self.st["terminals"] if r["wire_uid"] and not r["is_source"])
                r["wire_uid"] = 0
            elif f.get("kind") == "extra_obj":                 # a junk object the purge missed
                self.st["terminals"].append({"term_uid": 99999999, "term_name": "", "is_source": False, "wire_uid": 0,
                                             "owner_uid": 99999998, "owner_class": "Invoke", "frame_diagram": 0,
                                             "term_class": "Terminal"})
            elif f.get("kind") == "delete_only_sink":           # LabVIEW took the other only-sink fate
                for r in self.st["terminals"]:
                    if r["term_uid"] in f["terms"]:
                        r["wire_uid"] = 0
        return {"applied": op["acts"], "check": check}

    def _check(self, real, term, is_source, loop_of=None):
        (d, n, t), how = self.addr.triple(real, term, is_source, loop_of)
        u, rows = self.addr.rd.node_terms(d, n)
        return {"triple": [d, n, t], "how": how, "resolved_name": rows[t]["name"]}

    def move_in(self, uid, dest, pos, op):
        return self._apply(op)

    def add_sr(self, loop, y, op):
        return self._apply(op)

    def wire_sr(self, variant, loop, right, term, real, op):
        return self._apply(op, self._check(real, term, variant == "RightIn"))

    def connect(self, src, dst, real, loop_of, op):
        kind, _rs, _rd, info = connect_route(self.addr, real, src, dst, loop_of)   # PD187(b): the real backend's route
        chk = None if kind == "indicator" else self._check(real, dst, False, loop_of)
        if chk is not None:
            chk["route"] = kind
        return self._apply(op, chk)

    def branch(self, tun, dst, real, loop_of, op):
        return self._apply(op)

    def index_mode_fix(self, tun, indexing):
        return 1 if indexing else 0

    def delete_wire(self, w, op, plan_wire=None):
        return self._apply(op)

    def delete_object(self, cls, uid, op):
        return self._apply(op)

    def rbw(self, op):
        return self._apply(op)


def dry_run(plan_path, fault=None, log=print, model_dir=None):
    """(status, first_fail, executor). No LabVIEW."""
    plan, _paths = load_final_plan(plan_path)
    base = _j(_abs(plan["finalized"]["base"]["path"]))
    st = SS.base_state(base, plan.get("context"))
    be = SimBackend(plan, st, SS.load_models(model_dir or SS.OPMODEL_DIR), fault)
    ex = Executor(plan_path, be, log)
    try:
        ex.run()
        return "PASS", None, ex
    except ExecStop as e:
        return "FAIL", str(e)[:400], ex


def prerun_plan(plan_path, log=print, model_dir=None):
    """Offline gates for a plan launch: final + step files intact (load_final_plan), compile, open_rows declared and
    matched, the dry run PASS. Returns (gates list, ok)."""
    gates = []

    def gate(label, ok, detail=""):
        gates.append((label, bool(ok), str(detail)[:300]))
        log("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:300]))
    try:
        plan, paths = load_final_plan(plan_path)
        gate("X1 plan final, base graph + {0} step files unchanged since finalize".format(len(paths)), True)
    except ExecStop as e:
        gate("X1 plan final, base graph + step files unchanged since finalize", False, e)
        return gates, False
    fz = plan["finalized"]
    gate("X2 end cdiff rows == the plan's declared open_rows", fz.get("open_rows_match") is True,
         (fz.get("end_cdiff_rows"), fz.get("open_rows")))
    try:
        ops = compile_plan(plan)
        gate("X3 every action compiles to a real op ({0} actions -> {1} real ops)".format(len(plan["actions"]), len(ops)), True)
    except ExecStop as e:
        gate("X3 every action compiles to a real op", False, e)
        return gates, False
    st, fs, fl = dry_run(plan_path, log=lambda *_a: None, model_dir=model_dir)
    gate("X4 dry run on the simulated backend: every real op matches its step, every address resolves", st == "PASS", fs)
    return gates, all(g_[1] for g_ in gates)


# ============================================================================================ LabVIEW run
def lv_run(plan_path, reference=None, max_min=60):
    import stagekit as K
    import jev_candidates as JC
    plan, _p = load_final_plan(plan_path)
    base = _j(_abs(plan["finalized"]["base"]["path"]))
    vi, vi_md5 = base["vi"], base["md5"]
    if reference and not os.path.isabs(reference[0]):
        reference = (os.path.join(K.CLAUDEDEV, reference[0]), reference[1])      # a bare name = a claudeDev file
    wiki = _j(_abs(plan["context"]["fs_pairs_wiki"]["path"]))
    pins = tuple(K.DEFAULT_PINS) + (("plan base VI", vi, vi_md5),) + ((("reference VI", reference[0], reference[1]),) if reference else ())
    name = "stagexec_" + plan["stage"]
    s = K.Stage(vi, vi_md5, name, preload=False, deadline_min=max_min - 3, pins=pins,
                out_json=os.path.join(BENCH, name + ".json"))
    out = {}

    def body(s):
        s.head("stagexec {0}: plan {1} md5 {2} ({3} actions)".format(plan["stage"], plan_path, md5(plan_path), len(plan["actions"])))
        s.start()
        s.discard_work()                      # the scratch copy is never saved
        be = LVBackend(s, wiki["fs_tunnel_pairs"])
        ex = Executor(plan_path, be, log=lambda m: print(m, flush=True))
        s.fact("COMPILED {0} real ops: {1}".format(len(ex.ops), [(o["kind"], o["acts"]) for o in ex.ops]))
        out["ex"] = ex
        try:
            real = ex.run()
            s.gate("E1 every real op's graph == its simulated step ({0} ops, first difference none)".format(len(ex.ops)), True)
        except ExecStop as e:
            s.R["stagexec"] = ex.report
            s.gate("E1 every real op's graph == its simulated step", False, str(e)[:1500], fatal=True)
        s.R["stagexec"] = ex.report
        s.fact("BINDING obj {0}".format(ex.bind["obj"]))
        s.fact("GRAPH READ seconds {0}".format([r.get("total") for r in be.reads]))
        s.es("end (warm)")
        es = s.R["es_timeline"][-1]["exec_state"]
        s.gate("E2 ExecState 1 warm at the end", es == 1, es)
        # computation_diff on the REAL end graph (register table = the simulation's, translated through the binding)
        last = ex.step(len(plan["actions"]))["state"]
        loops = copy.deepcopy(last["loops"])
        for L in loops or []:
            L["right_uids"] = [ex.bind["obj"].get(int(u), int(u)) for u in L.get("right_uids") or []]
            L["left_of"] = dict((str(ex.bind["obj"].get(int(k), int(k))), [ex.bind["obj"].get(int(x), int(x)) for x in (v if isinstance(v, list) else [v])])
                                for k, v in (L.get("left_of") or {}).items())
        Greal = JC.from_parts({"terminals": real, "graph_summary": wiki["graph_summary"]}, be.last_objs, loops,
                              JC.node_labels_default(), wiki["fs_tunnel_pairs"], "stagexec end")
        cd = V.computation_diff(SS.load_s1(plan), Greal)
        got = sorted(set((V.key_parts(r["sink"])[0], V.key_parts(r["sink"])[2]) for r in cd["rows"]))
        want = sorted(set((int(r["node"]), r["term"]) for r in plan.get("open_rows") or []))
        s.gate("E3 computation_diff(S1, real end) rows == the plan's open_rows {0}".format(want), got == [list(x) for x in want] or got == want, got)
        if reference:
            sc = s.scratch("ref", source=reference[0])
            lv = K.mod("wiki_build").read_live(sc, fs_pairs=wiki["fs_tunnel_pairs"])
            s.drop_scratch(sc, "H4 reference")
            base_nodes = set(V.node_of(r) for r in base["terminals"])
            d = canon_diff(real, dedupe(lv["terminals"]), base_nodes)
            s.fact("REFERENCE canon diff {0}".format(json.dumps(d, default=str)[:1500]))
            s.gate("E4 end graph == {0} up to new-uid naming (edges, terminals, node classes)".format(
                os.path.basename(reference[0])), d["n"] == 0, d["n"])
        s.dump()
    rc = K.run(body, s)
    K.mod("bench_prep").restart_labview()
    return rc


def canon_diff(real_a, real_b, base_nodes):
    """Two real reads compared up to new-uid naming: a node outside `base_nodes` is its class."""
    def canon(rows):
        own = dict((r["term_uid"], (V.node_of(r), V.node_class(r), r["term_class"])) for r in rows)
        key = lambda t: (own[t][0], t) if own[t][0] in base_nodes else ("NEW:" + own[t][1], own[t][2])  # noqa: E731
        E, D = edges(rows)
        e = collections.Counter((key(a), key(b)) for a, b in E)
        n = collections.Counter(("B", own[t][0]) if own[t][0] in base_nodes else ("NEW", own[t][1]) for t in own)
        t_ = collections.Counter(key(t) for t in own)
        return e, n, t_
    ea, na, ta = canon(real_a)
    eb, nb, tb = canon(real_b)
    out = {"edges_only_a": sorted((ea - eb).elements(), key=repr)[:20], "edges_only_b": sorted((eb - ea).elements(), key=repr)[:20],
           "nodes_only_a": sorted(set(na) - set(nb), key=repr)[:20], "nodes_only_b": sorted(set(nb) - set(na), key=repr)[:20],
           "terms_only_a": sorted((ta - tb).elements(), key=repr)[:20], "terms_only_b": sorted((tb - ta).elements(), key=repr)[:20]}
    out["n"] = sum(len(v) for v in out.values())
    return out


# ============================================================================================ self-test
def selftest():
    import tempfile
    gates = []

    def gate(label, ok, detail=""):
        gates.append((label, bool(ok)))
        print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)
    tmp = tempfile.mkdtemp(prefix="stagexec_selftest_")
    base = SS._synthetic()
    gp = os.path.join(tmp, "graph_base.json")
    json.dump(base, open(gp, "w", encoding="utf-8"))
    pf = SS._plan_full("xs", gp)
    # executable shape: a tunnel group is (tunnel, wire in, wire out) adjacent - so delete_wire 7 moves before tunnel T2
    A = pf["actions"]
    A[0]["pos"] = [0, 0]
    pf["actions"] = A[:8] + [A[10], A[8], A[9], A[11]] + A[12:]
    pp = os.path.join(tmp, "plan_in.json")
    json.dump(dict(pf, stage="xs"), open(pp, "w", encoding="utf-8"))
    md = os.path.join(tmp, "models")
    os.makedirs(md)
    json.dump({"op": "move_in", "sim": {"only_sink": "ambiguous"}}, open(os.path.join(md, "move_in.json"), "w"))
    S = SS.simulate(pp, gp, out_root=os.path.join(tmp, "sim"), plan_out_dir=tmp, model_dir=md, log=lambda *_a: None)
    fin = os.path.join(tmp, "plan_xs.json")
    gate("T01 the synthetic executable plan simulates FINAL", S["final"], (S["failed"], S["end_cdiff_rows"]))
    plan = _j(fin)
    ops = compile_plan(plan)
    kinds = [o["kind"] for o in ops]
    gate("T02 compile: tunnel+in+out -> ONE real op; SR inner wires -> wire_sr; the rest 1:1",
         kinds.count("tunnel") == 2 and kinds.count("wire_sr") == 2 and len(ops) == len(plan["actions"]) - 4, kinds)
    bad = copy.deepcopy(plan)
    bad["actions"] = [x for x in bad["actions"] if not (x["op"] == "wire" and x.get("dst") == "new:T1.outer")]
    try:
        compile_plan(bad)
        gate("T03 a tunnel without its in-wire does not compile", False)
    except ExecStop as e:
        gate("T03 a tunnel without its in-wire does not compile", "exactly one wire" in str(e), e)
    q = lambda *_a: None                                                           # noqa: E731
    if True:
        st, ff, ex = dry_run(fin, log=q, model_dir=md)
        gate("T04 dry run PASS: every real op's state == its step file after binding", st == "PASS", ff)
        gate("T05 binding: 2 SR objects + 2 tunnels bound to POSITIVE uids", len(ex.bind["obj"]) == 4 and
             all(v > 0 for v in ex.bind["obj"].values()), ex.bind["obj"])
        hows = [(r["result"].get("check") or {}).get("how") for r in ex.report[1:] if isinstance(r.get("result"), dict)
                and r["result"].get("check")]
        gate("T06 addressing: base ends primed by their wire, every checked end resolved to its own terminal name",
             ex.report[0]["primed"]["n"] >= 4 and hows and all(hows) and
             all((r["result"]["check"] or {}).get("resolved_name") is not None for r in ex.report[1:]
                 if isinstance(r.get("result"), dict) and r["result"].get("check")),
             (ex.report[0]["primed"], hows))
        st2, ff2, ex2 = dry_run(fin, fault={"at": 5, "kind": "drop_edge"}, log=q, model_dir=md)
        gate("T07 a real op that made one edge fewer STOPS at that op with a step-diff report",
             st2 == "FAIL" and "STEP-DIFF" in str(ff2) and ex2.report[-1]["acts"][-1] == 5, ff2)
        st3, ff3, _ = dry_run(fin, fault={"at": 2, "kind": "extra_obj"}, log=q, model_dir=md)
        gate("T08 an extra real object after add_shift_reg stops at BINDING (count/class)", st3 == "FAIL" and "BINDING" in str(ff3), ff3)
        st4, ff4, ex4 = dry_run(fin, fault={"at": 1, "kind": "delete_only_sink", "terms": [1602]}, log=q, model_dir=md)
        gate("T09 the other only-sink fate on an allow_either terminal is accepted", st4 == "PASS" and 1602 in ex4.allow, ff4)
        st5, ff5, _ = dry_run(fin, fault={"at": 1, "kind": "delete_only_sink", "terms": [1001]}, log=q, model_dir=md)
        gate("T10 ... but not on a terminal the step does not allow", st5 == "FAIL" and "STEP-DIFF" in str(ff5), ff5)
        g_, ok = prerun_plan(fin, log=q, model_dir=md)
        gate("T11 prerun_plan passes the final plan", ok, [x for x in g_ if not x[1]])
    nf = copy.deepcopy(plan)
    nf["final"] = False
    p2 = os.path.join(tmp, "plan_nf.json")
    json.dump(nf, open(p2, "w", encoding="utf-8"))
    g2, ok2 = prerun_plan(p2, log=q, model_dir=md)
    gate("T12 prerun_plan refuses a non-final plan", not ok2 and "not final" in g2[0][2], g2[0])
    stp = plan["finalized"]["step_files"][3]["path"]
    with open(_abs(stp), "a", encoding="utf-8") as f:
        f.write(" ")
    g3, ok3 = prerun_plan(fin, log=q, model_dir=md)
    gate("T13 prerun_plan refuses a plan whose step file changed after finalize", not ok3 and "changed" in g3[0][2], g3[0])
    class FR(object):                     # a scripted loop Terminals[] list (regression of stagexec_l7_bench.log run 1)
        cur = []

        def diagrams(self):
            return [686]

        def node_uids(self, didx):
            return [500]

        def node_terms(self, didx, nidx):
            return 500, [{"i": i, "name": n, "is_source": s, "wire": w} for i, (n, s, w) in enumerate(FR.cur)]
    ad = Addr(FR())
    FR.cur = [("x", False, 9)]
    ad.snap_loop(500, 686)
    FR.cur = [("x", False, 9), ("", True, 0), ("", False, 0)]
    ad.track_new(500, 1, 2)
    ad.snap_loop(500, 686)
    FR.cur = FR.cur + [("", True, 0), ("", False, 0)]
    ad.track_new(500, 3, 4)
    FR.cur = [("x", False, 9), ("error out", True, 0), ("", False, 0), ("total", True, 0), ("", False, 0)]
    lost = ad.retrack()
    t15 = dict(ad.loops[500]["track"])
    FR.cur = FR.cur + [("", False, 33)]
    lost2 = ad.retrack()
    gate("T15 register faces keep their loop index when inner wiring RENAMES them (no name alignment), and across an "
         "appended tunnel face", not lost and not lost2 and t15 == {1: 1, 2: 2, 3: 3, 4: 4} and
         ad.loops[500]["track"] == {1: 1, 2: 2, 3: 3, 4: 4}, (t15, ad.loops[500]["track"], lost, lost2))
    # PD185 (card 81-8): owner-routed SelectorTunnel ends, FSIT ends, the legacy node listing, PRIME stop
    def row(t, n, s, w, o, oc, fd, tc):
        return {"term_uid": t, "term_name": n, "is_source": s, "wire_uid": w, "owner_uid": o, "owner_class": oc,
                "frame_diagram": fd, "term_class": tc}

    class FB(object):
        st = {"loops": [], "owners": {"2": ["CaseStructure", 100]},
              "terminals": [row(101, "", False, 8, 100, "CaseStructure", 1, "Terminal"),
                            row(201, "", False, 9, 200, "SelectorTunnel", 1, "OuterTerminal"),
                            row(202, "", True, 10, 200, "SelectorTunnel", 2, "InnerTerminal"),
                            row(301, "out", True, 9, 300, "Function", 1, "Terminal"),
                            row(302, "o2", True, 8, 300, "Function", 1, "Terminal"),
                            row(401, "", True, 11, 400, FSIT_CLS, 1, "OuterTerminal"),
                            row(501, "", False, 12, 500, "Tunnel", 1, "OuterTerminal"),      # the case SELECTOR (run 2)
                            row(502, "", True, 13, 500, "Tunnel", 2, "InnerTerminal"),
                            row(303, "o3", True, 12, 300, "Function", 1, "Terminal")]}
    sr = SimReader(FB())
    real = FB.st["terminals"]
    nu = sr.node_uids(0)
    gate("T16 SimReader lists the owner structure, never the SelectorTunnel / FSIT, as a Nodes[] entry (PD185)",
         100 in nu and 200 not in nu and 400 not in nu, nu)
    try:
        (d_, n_, t_), how = Addr(sr, FB.st["owners"]).triple(real, 201, False)
        e_, nt_ = sr.node_terms(d_, n_)
        gate("T17 a SelectorTunnel outer sink resolves on its OWNER's Terminals[] (the measured route, l2a1_faces_81.log)",
             e_ == 100 and nt_[t_]["wire"] == 9 and not nt_[t_]["is_source"], (d_, n_, t_, how))
    except ExecStop as e:
        gate("T17 a SelectorTunnel outer sink resolves on its OWNER's Terminals[]", False, e)
    try:
        (d_, n_, t_), how = Addr(sr, FB.st["owners"]).triple(real, 501, False)
        e_, nt_ = sr.node_terms(d_, n_)
        gate("T17b a case SELECTOR (class Tunnel) sink resolves on its owner's Terminals[] (stage_d1_l2a1_r2.log:36)",
             e_ == 100 and nt_[t_]["wire"] == 12 and 500 not in sr.node_uids(0), (d_, n_, t_, how))
    except ExecStop as e:
        gate("T17b a case SELECTOR (class Tunnel) sink resolves on its owner's Terminals[]", False, e)

    class Legacy(SimReader):                                                        # the pre-PD185 listing: tunnel = node
        def node_uids(self, didx):
            return [200, 300]
    for lab_, ad_ in (("T18a owners unknown", Addr(sr, {})), ("T18b tunnel listed only as a node", Addr(Legacy(FB()), FB.st["owners"]))):
        try:
            ad_.triple(real, 201, False)
            gate(lab_ + " -> the end is NOT addressable (negative)", False, "resolved")
        except ExecStop as e:
            gate(lab_ + " -> the end is NOT addressable (negative)", "ADDRESS" in str(e), e)
    try:
        Addr(sr, FB.st["owners"]).triple(real, 401, True)
        gate("T19 an FSIT end stops with its Left/Right Terminal route named", False, "resolved")
    except ExecStop as e:
        gate("T19 an FSIT end stops with its Left/Right Terminal route named", "Left/Right Terminal" in str(e), e)
    txt = open(_abs(stp), encoding="utf-8").read()                               # undo T13's appended space
    with open(_abs(stp), "w", encoding="utf-8") as f:
        f.write(txt[:-1] if txt.endswith(" ") else txt)
    pl_, _pp = load_final_plan(fin)
    be_ = SimBackend(pl_, SS.base_state(_j(_abs(pl_["finalized"]["base"]["path"])), pl_.get("context")), SS.load_models(md))

    def _no(*_a, **_k):
        raise ExecStop("ADDRESS: injected unprovable end")
    be_.addr.triple = _no
    try:
        Executor(fin, be_, log=q).run()
        gate("T20 an unprovable PRIME end STOPS before op 1 (PD185(3))", False, "ran")
    except ExecStop as e:
        gate("T20 an unprovable PRIME end STOPS before op 1 (PD185(3))", "PRIME" in str(e) and be_.calls == [], (str(e)[:120], be_.calls))
    # PD187(a) (card 82-1): reader parity at PRIME
    gate("T21 PARITY recorded at PRIME on the synthetic plan: touched diagrams listed, 0 one-side-only entries",
         ex.report[0].get("parity", {}).get("n") == 0 and ex.report[0]["parity"]["diagrams"], ex.report[0].get("parity", {}).get("diagrams"))
    be2 = SimBackend(pl_, SS.base_state(_j(_abs(pl_["finalized"]["base"]["path"])), pl_.get("context")), SS.load_models(md))

    class Extra(SimReader):                                     # a SimReader listing a node the "real" one lacks
        def node_uids(self, didx):
            return SimReader.node_uids(self, didx) + [99999]
    rows_, n_ = reader_parity(SimReader(be2), Extra(be2), touched_diagrams(pl_, be2.st), be2.obj_classes(be2.read()),
                              be2.obj_classes(be2.read()))
    gate("T22a NEGATIVE: SimReader listing a class the real read lacks -> parity n > 0 with an only_sim entry",
         n_ > 0 and any(r.get("only_sim") for r in rows_), n_)
    be2.addr.rd = Extra(be2)                                    # the backend's "real" reader lacks nothing but lists extra
    try:
        Executor(fin, be2, log=q).run()
        gate("T22b NEGATIVE: a parity difference STOPS at PRIME before op 1", False, "ran")
    except ExecStop as e:
        gate("T22b NEGATIVE: a parity difference STOPS at PRIME before op 1", "PARITY" in str(e) and be2.calls == [], (str(e)[:120], be2.calls))
    # PD187(b): ControlTerminal ends (source/sink, bare/wired) by the 179(b) route, never as a Nodes[] triple

    class FC(object):
        st = {"loops": [], "owners": {}, "objs": [],
              "terminals": [row(601, "Reset Tracking", True, 0, 1, "Diagram", 1, FP),        # bare CT source (#5634 at op 31)
                            row(602, "min value", False, 14, 1, "Diagram", 1, FP),           # wired CT sink (#17272)
                            row(603, "Auto-Reset", True, 15, 1, "Diagram", 1, FP),           # wired CT source
                            row(701, "y", False, 0, 700, "Function", 1, "ParameterTerminal"),
                            row(702, "x", True, 14, 700, "Function", 1, "ParameterTerminal"),
                            row(703, "z", False, 15, 700, "Function", 1, "ParameterTerminal")]}
    sc = SimReader(FC())
    adc, rc_ = Addr(sc, {}), FC.st["terminals"]
    try:
        got = [adc.ct(rc_, u)[0] for u in (601, 602, 603)]
        gate("T23 ControlTerminal ends resolve by 179(b) (bare source, wired sink, wired source): own uid, owner Diagram, "
             "in ct_uids; and SimReader never lists a ControlTerminal in Nodes[]",
             [x["diag"] for x in got] == [1, 1, 1] and [x["is_source"] for x in got] == [True, False, True] and
             not (set([601, 602, 603]) & set(sc.node_uids(0))) and 700 in sc.node_uids(0), (got, sc.node_uids(0)))
    except ExecStop as e:
        gate("T23 ControlTerminal ends resolve by 179(b)", False, e)

    class LegacyCT(SimReader):                                  # the pre-PD187 listing: a ControlTerminal = a node
        def node_uids(self, didx):
            return [601, 602, 603, 700]
    for lab_, rd_ in (("T24a", sc), ("T24b (reader lists the CT as a node)", LegacyCT(FC()))):
        try:
            Addr(rd_, {}).triple(rc_, 601, True)
            gate(lab_ + " NEGATIVE: a ControlTerminal as a Nodes[] triple FAILS", False, "resolved")
        except ExecStop as e:
            gate(lab_ + " NEGATIVE: a ControlTerminal as a Nodes[] triple FAILS", "ControlTerminal" in str(e), e)

    class NoCT(SimReader):
        def ct_uids(self):
            return set()
    try:
        Addr(NoCT(FC()), {}).ct(rc_, 601)
        gate("T25a NEGATIVE: a ControlTerminal absent from report_all('ControlTerminal') is not addressable", False, "resolved")
    except ExecStop as e:
        gate("T25a NEGATIVE: a ControlTerminal absent from report_all('ControlTerminal') is not addressable", "ADDRESS-CT" in str(e), e)
    kinds_ = []
    for s_, d_ in ((603, 703), (702, 602), (601, 701)):
        try:
            kinds_.append(connect_route(adc, rc_, s_, d_, {})[0])
        except ExecStop as e:
            kinds_.append("STOP:" + str(e)[:40])
    gate("T25b connect_route: wired CT source -> cfw; wired source -> CT sink = indicator; BARE CT source -> ctl "
         "(wire_control, card 82-2; the same in the real and the simulated backend)",
         kinds_ == ["cfw", "indicator", "ctl"], kinds_)
    info_ = connect_route(adc, rc_, 601, 701, {})[3]
    gate("T26 ctl route carries the CT label, its Diagram index and the sink NAME (what wire_control addresses)",
         (info_.get("ctl_label"), info_.get("ctl_didx"), info_.get("dst_name")) == ("Reset Tracking", 0, "y"), info_)
    negs = (("T27a NEGATIVE: a second CT with the same label on that Diagram -> STOP",
             rc_ + [row(604, "Reset Tracking", True, 0, 1, "Diagram", 1, FP)], 601, 701, "label not unique"),
            ("T27b NEGATIVE: a sink whose name repeats on its node -> STOP",
             rc_ + [row(704, "y", False, 16, 700, "Function", 1, "ParameterTerminal")], 601, 701, "sink name not unique"),
            ("T27c NEGATIVE: a sink owned by an owner-routed tunnel -> STOP (at addressing or at the owner check)",
             rc_ + [row(801, "", False, 0, 800, "SelectorTunnel", 1, "OuterTerminal")], 601, 801, None))
    for lab_, rows2, s_, d_, want in negs:
        fn = SimReader(_StateHolder({"loops": [], "owners": {}, "objs": [], "terminals": rows2}))
        try:
            k_ = connect_route(Addr(fn, {}), rows2, s_, d_, {})[0]
            gate(lab_, False, "routed " + k_)
        except ExecStop as e:
            gate(lab_, (want is None or want in str(e)), str(e)[:160])
    gate("T14 nothing LabVIEW-side imported", not any(m in sys.modules for m in ("gscript", "win32com", "pythoncom", "stagekit")),
         [m for m in ("gscript", "win32com", "pythoncom", "stagekit") if m in sys.modules])
    n_pass = sum(1 for _l, ok in gates if ok)
    n_fail = len(gates) - n_pass
    first = next((l for l, ok in gates if not ok), None)
    print("=== GATES: {0} pass / {1} fail{2}".format(n_pass, n_fail, "; failing: " + first if first else ""))
    print(protocol.result_line(protocol.make_result(n_pass, n_fail, first)))
    return 0 if n_fail == 0 else 1


def main(argv):
    if len(argv) >= 2 and argv[1] == "selftest":
        return selftest()
    if len(argv) >= 3 and argv[1] in ("dry", "prerun", "run"):
        plan = os.path.abspath(argv[2])
        if argv[1] == "dry":
            st, ff, ex = dry_run(plan)
            print(protocol.result_line(protocol.make_result(int(st == "PASS"), int(st != "PASS"), ff)))
            return 0 if st == "PASS" else 1
        if argv[1] == "prerun":
            g_, ok = prerun_plan(plan)
            n = sum(1 for x in g_ if x[1])
            print(protocol.result_line(protocol.make_result(n, len(g_) - n, next((x[0] + ": " + x[2] for x in g_ if not x[1]), None))))
            return 0 if ok else 1
        ref = None
        if "--reference" in argv:
            i = argv.index("--reference")
            ref = (argv[i + 1], argv[i + 2])
        mm = int(argv[argv.index("--max-min") + 1]) if "--max-min" in argv else 60
        return lv_run(plan, ref, mm)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
