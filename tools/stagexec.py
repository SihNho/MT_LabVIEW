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


# PD192(a), card 86-1: the MEMORY METER. LabVIEW error 2 ("memory full") was observed at ~770 MB private bytes on LV2026
# (.claude/skills/labview-automation/references/com-driving.md:310; a restart dropped it to ~410 MB). The loud stop sits
# 70 MB below that observation so the run ends with a report instead of an error-2 cascade (unroutable_l2a1_85.log:562).
# Handles are logged beside it but gate nothing: the handle count is blind to VI Server refnums (stagekit.py:178).
MEM_STOP_MB = 700.0


class Meter(object):
    """Private bytes (MB) + handle count, stamped per op and per read. `probe()` -> (private_bytes_int_or_None,
    handles_int_or_None). stop_mb=None = warn-only (a measurement run that must reach error 2 to locate it)."""

    def __init__(self, probe, stop_mb=MEM_STOP_MB, log=print):
        self.probe, self.stop_mb, self.log = probe, stop_mb, log
        self.rows = []
        self.warned = None

    def __call__(self, tag, k=None):
        pb, hc = self.probe()
        mb = round(pb / 1048576.0, 1) if pb else None
        prev = self.rows[-1] if self.rows else {}
        d_mb = round(mb - prev["mb"], 1) if mb is not None and prev.get("mb") is not None else None
        d_h = hc - prev["handles"] if hc is not None and prev.get("handles") is not None else None
        row = {"tag": tag, "k": k, "t": round(time.time(), 1), "mb": mb, "handles": hc, "d_mb": d_mb, "d_h": d_h}
        self.rows.append(row)
        self.log("  METER {0:<6} k {1!s:>3}  private {2} MB (d {3})  handles {4} (d {5})".format(
            tag, k, mb, "{0:+.1f}".format(d_mb) if d_mb is not None else "-", hc, "{0:+d}".format(d_h) if d_h is not None else "-"))
        if self.stop_mb and mb is not None and mb >= self.stop_mb:
            raise ExecStop("MEMSTOP: LabVIEW private bytes {0} MB >= {1} MB at {2} k {3} (error 2 observed ~770 MB, "
                           "com-driving.md:310)".format(mb, self.stop_mb, tag, k))
        if mb is not None and mb >= MEM_STOP_MB and self.warned is None:
            self.warned = row
            self.log("  METER WARN private bytes {0} MB crossed {1} MB at {2} k {3} (warn-only run)".format(mb, MEM_STOP_MB, tag, k))
        return row

    def summary(self):
        mbs = [r["mb"] for r in self.rows if r["mb"] is not None]
        per = {"op": [r["d_mb"] for r in self.rows if r["tag"] == "op" and r["d_mb"] is not None],
               "read": [r["d_mb"] for r in self.rows if r["tag"] == "read" and r["d_mb"] is not None]}
        return {"n": len(self.rows), "first_mb": mbs[0] if mbs else None, "peak_mb": max(mbs) if mbs else None,
                "last": self.rows[-1] if self.rows else None,
                "sum_d_mb_op": round(sum(per["op"]), 1), "sum_d_mb_read": round(sum(per["read"]), 1),
                "mean_d_mb_op": round(sum(per["op"]) / len(per["op"]), 2) if per["op"] else None,
                "mean_d_mb_read": round(sum(per["read"]) / len(per["read"]), 2) if per["read"] else None,
                "warned_at": self.warned}


def md5(p):
    return SS.md5_file(p)


def _j(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _abs(p):
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


# ============================================================================================ plan + compile (pure)
def load_final_plan(plan_path, require_final=True):
    """The plan, its step states (md5-checked against `finalized.step_files`) and the actions' step numbers.
    require_final=False is the DIAGNOSTIC dry run only (`dry --nonfinal`, card 100-3: routability of a plan whose end
    computation rows are not settled yet); prerun_plan and lv_run always require final."""
    plan = _j(plan_path)
    ok, why = protocol.validate_obj(plan)
    if not ok:
        raise ExecStop("plan does not validate: " + why)
    if require_final and plan.get("final") is not True:
        raise ExecStop("plan is not final (final={0!r}, finalized={1})".format(
            plan.get("final"), json.dumps((plan.get("finalized") or {}).get("first_divergent"))))
    fz = plan.get("finalized") or {}
    files = fz.get("step_files") or []
    if fz.get("failed"):
        raise ExecStop("the simulation stopped at action {0}: {1}".format(fz["failed"].get("n"), fz["failed"].get("error")))
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


# card 100-3: `create` rows -> the verb each one routes to (LVBackend.create; the dry backend checks the same table).
# The LabVIEW verbs marked (100-2) are built by card 100-2 under the names fixed in requires_disp-stage.json.
CREATE_ROUTES = {
    "while": "gscript.loop_in('while') - OpWhileLoopIn_v0",
    "for": "gscript.loop_in('for') - OpForLoopIn_v0",
    "local_read": "stagekit.create_local_read (OpCreateLocal_v0) + stagekit.move_in",
    "local_write": "stagekit.create_local_write (100-2) + stagekit.move_in when it does not place it",
    "indicator": "gscript.create_indicator_nested (100-2) + set_control_label + set_visible (100-2)",
    "control": "gscript.create_control_nested (100-2) + set_control_label + set_default_in_memory",
    "primitive": "gscript.create_primitive_nested (100-2)",
    "copy_in": "stagekit.copy_in (OpMoveByIndex_v0 duplicate, donor = the base)",
    "const_on_term": "stagekit.const_row (OpCreateConstOnTerm_v0, a node in a WhileLoop body)",
}
ROUTE_VERBS = {
    "while": [("gscript", "loop_in")], "for": [("gscript", "loop_in")],
    "local_read": [("stagekit", "create_local_read"), ("stagekit", "move_in")],
    "local_write": [("stagekit", "create_local_write")],
    "indicator": [("gscript", "create_indicator_nested"), ("gscript", "set_control_label"), ("gscript", "set_visible"),
                  ("gscript", "panel_wiring")],
    "control": [("gscript", "create_control_nested"), ("gscript", "set_control_label"),
                ("gscript", "set_default_in_memory"), ("gscript", "panel_wiring")],
    "primitive": [("gscript", "create_primitive_nested")],
    "copy_in": [("stagekit", "copy_in")],
    "const_on_term": [("stagekit", "const_row")],
    "gate": [("gscript", "read_bool_const")],
    "stop": [("file", "tools/bench/opstopfromnode_labels.json")],
}


def verbs_missing(route):
    """The verbs a route calls that are NOT defined in the source (a text check - the dry run imports no LabVIEW side,
    self-test T14; the same `def <name>(` rule as protocol.py requires)."""
    import re
    out = []
    for mod_, name in ROUTE_VERBS.get(route, []):
        if mod_ == "file":
            if not os.path.exists(_abs(name)):
                out.append(name)
            continue
        try:
            txt = open(os.path.join(HERE, mod_ + ".py"), encoding="utf-8").read()
        except OSError:
            txt = ""
        if not re.search(r"^\s*def {0}\(".format(re.escape(name)), txt, re.M):
            out.append("{0}.{1}".format(mod_, name))
    return out


DIAG_FIELDS = ("diagram", "dest_diagram", "body", "parent")
END_FIELDS = ("src", "dst", "at", "on", "born_on")


def create_route(a):
    """The CREATE_ROUTES key for a create action, else ExecStop (no executor for that shape)."""
    c = a.get("class")
    if c == "WhileLoop":
        return "while"
    if c == "ForLoop":
        return "for"
    if c == "Local":
        m = a.get("mode")
        if m not in ("read", "write") or not a.get("label"):
            raise ExecStop("create Local needs `mode` read|write and the control's `label` (got {0!r}, {1!r})".format(m, a.get("label")))
        return "local_" + m
    if c == "ControlTerminal":
        if not a.get("label"):
            raise ExecStop("create ControlTerminal needs `label`")
        if a.get("indicator"):
            if a.get("born_on") is None:
                raise ExecStop("create indicator needs `born_on` (the source terminal it is created on)")
            return "indicator"
        if a.get("on") is None:
            raise ExecStop("create control needs `on` (the sink terminal it is created on)")
        return "control"
    if a.get("donor_uid") is not None:
        return "copy_in"
    if a.get("prim"):
        return "primitive"
    if str(c).endswith("Constant") and a.get("on") is not None:
        return "const_on_term"
    raise ExecStop("create class {0!r} has no executor (no donor_uid / prim / on)".format(c))


def tunnel_outer_face(real, term, diagram):
    """card 100-6 (PD213(f)3): the row of terminal `term` when it is the OUTER SOURCE face of a LoopTunnel sitting on
    Diagram #diagram - the one tunnel face gscript.create_indicator_nested(W, face, None) reaches (OpTunnelInd_v0,
    gscript.py _tunnel_outer_face). Anything else (an inner face, a sink face, another class, another diagram) -> None,
    and the row takes the Node route, which refuses a non-Node owner (T38)."""
    r = next((x for x in real if x["term_uid"] == term), None)
    if (r is None or r["owner_class"] != "LoopTunnel" or r["term_class"] != "OuterTerminal" or not r["is_source"]
            or int(r["frame_diagram"] or 0) != int(diagram)):
        return None
    return r


def _heads(v):
    """The symbolic heads a field value names: 'new:X.body' / 'new:X.t' -> ['new:X'], {'uid': 'new:X'} -> ['new:X']."""
    if isinstance(v, dict):
        return _heads(v.get("uid"))
    if isinstance(v, str) and v.startswith("new:"):
        return [v.partition(".")[0]]
    return []


def check_symbols(A):
    """card 100-3: every symbolic reference names an alias an EARLIER action created; '.body' only of a loop create,
    '.cond' only of a WhileLoop create. ExecStop names the action (unknown alias / use before create)."""
    defined = {}                                          # head -> kind ('srR','srL','tunnel','loop:<cls>','obj')
    for i, a in enumerate(A, 1):
        for f in DIAG_FIELDS + END_FIELDS + ("loop", "uid"):
            v = a.get(f)
            for h in _heads(v):
                if h not in defined:
                    raise ExecStop("action {0} ({1}): {2}={3!r} names {4}, which no EARLIER action creates (unknown alias "
                                   "or use before create)".format(i, a.get("id"), f, v, h))
                kind = defined[h]
                tail = v.partition(".")[2] if isinstance(v, str) else (v.get("term") if isinstance(v, dict) else "")
                if f in DIAG_FIELDS and (tail != "body" or not kind.startswith("loop:")):
                    raise ExecStop("action {0} ({1}): {2}={3!r} - a symbolic diagram is 'new:<loop alias>.body'".format(
                        i, a.get("id"), f, v))
                if tail == "cond" and kind != "loop:WhileLoop":
                    raise ExecStop("action {0} ({1}): '.cond' of {2} ({3}) - only a WhileLoop has a conditional "
                                   "terminal".format(i, a.get("id"), h, kind))
        nm = a.get("as")
        if a["op"] == "add_shift_reg" and nm:
            defined["new:" + nm + "R"], defined["new:" + nm + "L"] = "srR", "srL"
        elif a["op"] == "tunnel" and nm:
            defined["new:" + nm] = "tunnel"
        elif a["op"] == "create" and nm:
            defined["new:" + nm] = ("loop:" + a["class"]) if a.get("class") in ("WhileLoop", "ForLoop") else "obj"
    return defined


def compile_plan(plan):
    """[{kind, acts:[action indices 1-based], ...}] - one entry per REAL op, in order. Raises ExecStop on a shape the
    executor has no real op for (the pre-run gate)."""
    A = plan["actions"]
    check_symbols(A)
    created = {}                                         # 'new:X' -> ('sr'|'tunnel'|'loop', action index)
    for i, a in enumerate(A, 1):
        if a["op"] == "add_shift_reg":
            nm = a.get("as")
            created["new:" + nm + "R"], created["new:" + nm + "L"] = ("srR", i), ("srL", i)
        elif a["op"] == "tunnel":
            created["new:" + a["as"]] = ("tunnel", i)
        elif a["op"] == "create" and a.get("class") == "WhileLoop" and a.get("as"):
            created["new:" + a["as"]] = ("while", i)
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
            if ds and created.get(ds, ("",))[0] == "while" and dside == "cond":
                ops.append({"kind": "stop", "loop": ds, "acts": [i]})          # card 100-3 R8: OpStopFromNode_v0
            elif ds and created.get(ds, ("",))[0] == "srR" and dside == "inner":
                ops.append({"kind": "wire_sr", "variant": "RightIn", "reg": ds, "acts": [i]})
            elif ss and created.get(ss, ("",))[0] == "srL" and sside == "inner":
                ops.append({"kind": "wire_sr", "variant": "LeftIn", "reg": ss, "acts": [i]})
            elif ss and created.get(ss, ("",))[0] == "tunnel":
                ops.append({"kind": "branch", "tunnel": ss, "side": sside or "outer", "acts": [i]})
            elif (ss and created.get(ss, ("",))[0] == "tunnel") or (ds and created.get(ds, ("",))[0] == "tunnel"):
                raise ExecStop("action {0}: a wire into a tunnel outside its tunnel group".format(i))
            else:
                ops.append({"kind": "connect", "acts": [i]})
        elif op in ("delete_wire", "delete_object", "remove_bad_wires"):
            ops.append({"kind": op, "acts": [i]})
        elif op == "create":                              # card 100-3: exec_create
            try:
                ops.append({"kind": "create", "route": create_route(a), "acts": [i]})
            except ExecStop as e:
                raise ExecStop("action {0} ({1}): {2}".format(i, a.get("id"), e))
        elif op == "gate":                                # card 100-3: a VALUE gate (stops the run when it holds)
            if a.get("read") != "bool_const" or not isinstance(a.get("stop_if"), bool):
                raise ExecStop("action {0}: gate needs read 'bool_const' and a boolean stop_if".format(i))
            ops.append({"kind": "gate", "acts": [i]})
        else:
            raise ExecStop("action {0}: op {1!r} has no real executor (decide is not executable)".format(i, op))
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


def uid_reuse(prev_real, real):
    """Evidence that LabVIEW re-issued a freed uid to a NEW object within one op (hyp-optunouter-uidreuse-85.md:78-82; NI:
    'if you delete an object, LabVIEW might assign the UID for that deleted object to a different object'). A uid present
    before and after whose identity changed: (1) owner uid with another owner_class, (2) terminal uid with another
    term_class/owner_class, (3) non-Diagram owner uid whose terminal-uid sets before/after are both non-empty and DISJOINT
    (same class re-issued, e.g. Property #136 in unroutable_l2a1_85_build_tun.log:34). Diagram owners are exempt from (3):
    control terminals move between diagrams legitimately."""
    oc0 = dict((r["owner_uid"], r["owner_class"]) for r in prev_real)
    oc1 = dict((r["owner_uid"], r["owner_class"]) for r in real)
    tk0 = dict((r["term_uid"], (r["term_class"], r["owner_class"])) for r in prev_real)
    tk1 = dict((r["term_uid"], (r["term_class"], r["owner_class"])) for r in real)
    ts0, ts1 = collections.defaultdict(set), collections.defaultdict(set)
    for r in prev_real:
        ts0[r["owner_uid"]].add(r["term_uid"])
    for r in real:
        ts1[r["owner_uid"]].add(r["term_uid"])
    out = ["owner #{0} {1}->{2}".format(u, oc0[u], oc1[u]) for u in sorted(set(oc0) & set(oc1)) if oc0[u] != oc1[u]]
    out += ["term #{0} {1}->{2}".format(t, tk0[t], tk1[t]) for t in sorted(set(tk0) & set(tk1)) if tk0[t] != tk1[t]]
    out += ["owner #{0} ({1}) terminals {2}->{3}".format(u, oc1[u], sorted(ts0[u])[:4], sorted(ts1[u])[:4])
            for u in sorted(set(ts0) & set(ts1)) if oc1[u] != "Diagram" and ts0[u] and ts1[u] and not ts0[u] & ts1[u]]
    return out


def bind_new(prev_real, real, sim_prev, sim_now, bind):
    """Bind the objects the simulation created between sim_prev and sim_now to the real objects that appeared between
    prev_real and real, by class and then by terminal class. Count/class mismatch => ExecStop. A uid re-issued to a new
    object inside the op => ExecStop 'UID-REUSE' FIRST (it would otherwise be dropped as 'old' and misreported as a
    sim/real mismatch; card 85-3 P4)."""
    ru_ = uid_reuse(prev_real, real)
    if ru_:
        raise ExecStop("UID-REUSE: {0} uid(s) re-issued to a different object in one op: {1}".format(len(ru_), ru_[:6]))
    # card 100-3: grouped by GRAPH NODE (vigraph.node_of), so a created ControlTerminal (its own node, owned by its
    # Diagram) binds like any object; for every other row node_of == owner_uid (the old grouping, unchanged)
    sp = set(V.node_of(r) for r in sim_prev)
    # card 101-3 (c100-6-r2.md s2): a created loop's BODY Diagram is bound by the create op's return (bind['diag']), and
    # its own unnamed i/cond rows (node = the body) are bound here by (term_class, direction, name) - never as an object
    dg = bind.get("diag") or {}
    new_sim = collections.OrderedDict()
    for r in sim_now:
        n = V.node_of(r)
        if n < 0 and n not in sp and n not in bind["obj"] and n not in dg:
            new_sim.setdefault(n, []).append(r)
    old_t = set(r["term_uid"] for r in prev_real)
    new_real = collections.OrderedDict()
    for r in real:
        if r["term_uid"] not in old_t and V.node_of(r) not in bind["obj"].values() and V.node_of(r) not in dg.values():
            new_real.setdefault(V.node_of(r), []).append(r)
    bkey = lambda r: (r["term_class"], bool(r["is_source"]), r["term_name"])        # noqa: E731
    for sb, rb in dg.items():
        s_b = [r for r in sim_now if V.node_of(r) == sb and sb not in sp and r["term_uid"] not in bind["term"]]
        r_b = [r for r in real if V.node_of(r) == rb and r["term_uid"] not in old_t]
        if not s_b and not r_b:
            continue
        ks, kr = collections.Counter(bkey(r) for r in s_b), collections.Counter(bkey(r) for r in r_b)
        if ks != kr or any(v != 1 for v in ks.values()):
            raise ExecStop("BINDING: body #{0} -> #{1} own rows sim {2} vs real {3}".format(sb, rb, dict(ks), dict(kr)))
        for sr in s_b:
            bind["term"][sr["term_uid"]] = next(x for x in r_b if bkey(x) == bkey(sr))["term_uid"]
    cs = collections.Counter(V.node_class(rs[0]) for rs in new_sim.values())
    cr = collections.Counter(V.node_class(rs[0]) for rs in new_real.values())
    if cs != cr:
        raise ExecStop("BINDING: simulated new objects {0} != real new objects {1} (real owners {2})".format(
            dict(cs), dict(cr), list(new_real)[:8]))
    made = {}
    for cls in cs:
        su = [u for u, rs in new_sim.items() if V.node_class(rs[0]) == cls]
        ru = [u for u, rs in new_real.items() if V.node_class(rs[0]) == cls]
        if len(su) != 1:
            raise ExecStop("BINDING: {0} new {1} objects in one op - ambiguous".format(len(su), cls))
        s_rows, r_rows = new_sim[su[0]], new_real[ru[0]]
        key = lambda r: r["term_class"]                                            # noqa: E731
        if any(v != 1 for v in collections.Counter(key(r) for r in s_rows).values()):
            # card 100-3: a created primitive has several ParameterTerminals - bind by (class, direction, NAME);
            # registers/tunnels keep the class-only key (their names are not stable, stage_d1_l7_1b.log:274)
            key = lambda r: (r["term_class"], bool(r["is_source"]), r["term_name"])  # noqa: E731
        ks = collections.Counter(key(r) for r in s_rows)
        kr = collections.Counter(key(r) for r in r_rows)
        if ks != kr or any(v != 1 for v in ks.values()):
            raise ExecStop("BINDING: {0} terminal keys sim {1} vs real {2}".format(cls, dict(ks), dict(kr)))
        bind["obj"][su[0]] = ru[0]
        made[su[0]] = ru[0]
        for sr in s_rows:
            rr = next(x for x in r_rows if key(x) == key(sr))
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


def is_const(r):
    """PD188(c) (card 85-1): a diagram CONSTANT end - outside Diagram.Nodes[] (listed_as_node), addressed by its class
    traverse (report_all(<class>), the same order OpConstWire_v1's Traverse uses), never by a Nodes[] triple."""
    c = r["owner_class"]
    return c.endswith("Constant") and c not in NODE_CONSTANTS and not is_ct(r)


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
    if not ds:                   # card 100-3: a loop the plan CREATED owns no row; its body's parent is in st['diagrams']
        ds = set(int(v) for k, v in (st.get("diagrams") or {}).items() if k in bodies)
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
            if isinstance(a["dest_diagram"], int):        # card 100-3: a symbolic body is not a base diagram
                out.add(int(a["dest_diagram"]))
        for k in ("parent", "body", "diagram"):
            if isinstance(a.get(k), int) and not isinstance(a.get(k), bool):
                out.add(int(a[k]))
        for side, src in (("src", True), ("dst", False), ("at", True), ("born_on", True), ("on", False)):
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
            # PD191(a) (card 85-2): a BARE node terminal -> a ControlTerminal sink = 'ctlsink' (gscript.wire_ctlsink,
            # OpCtlSinkWire_v1: Connect Wire invoked ON the CT, Wire Source = Traverse(src class)[j].Terminals[t]).
            # wire_indicators stays for WIRED sources only (its measured limit, tools/gscript.py:1835-1838).
            if is_ct(rs) or is_const(rs) or rs["owner_class"] in NOT_NODES + SR_CLS or V.node_of(rs) != rs["owner_uid"]:
                raise ExecStop("CONNECT-NO-VERB: panel sink #{0} needs a WIRED source for wire_indicators; #{1} is bare and "
                               "not a node's own terminal (ctlsink addresses the source NODE by class traverse)".format(dst, src))
            st_, hs = addr.triple(real, src, True, loop_of)
            info.update(ct=addr.ct(real, dst)[0], src=st_, src_how=hs, src_term=st_[2])
            return "ctlsink", rs, rd, info
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
    if is_const(rs):                                       # PD188(c), card 85-1: gscript.wire_const (OpConstWire_v1)
        if rd["owner_class"] in OWNER_ROUTED or rd["owner_class"] in SR_CLS or rd["owner_class"] == FSIT_CLS \
                or V.node_of(rd) != rd["owner_uid"]:
            raise ExecStop("CONNECT-NO-VERB: bare constant source #{0} -> sink #{1} on {2} #{3}: wire_const addresses the "
                           "sink NODE by class traverse; this sink's owner is not that node".format(
                               src, dst, rd["owner_class"], rd["owner_uid"]))
        c, hc = addr.const(real, src)
        info.update(const=c, const_how=hc, dst_term=dt[2])
        return "const", rs, rd, info
    if rs["owner_class"] in OWNER_ROUTED and rs["term_class"] == "OuterTerminal" and len(face_twins(real, rs, addr.owners)) > 1:
        # PD191(b), card 85-2: by the TUNNEL uid - only where the owner's Terminals[] holds a TWIN face (same name and
        # direction: R45 #6007 / R46 #6026 on #5540). A face with no twin keeps its measured owner route ('nested',
        # rw_10594_10259 at op 34, constsrc_l2a1_85.log diff 0).
        if rd["owner_class"] in OWNER_ROUTED or rd["owner_class"] in SR_CLS or rd["owner_class"] == FSIT_CLS \
                or V.node_of(rd) != rd["owner_uid"]:
            raise ExecStop("CONNECT-NO-VERB: bare tunnel outer face #{0} -> sink #{1} on {2} #{3}: wire_tunouter addresses "
                           "the sink NODE by class traverse; this sink's owner is not that node".format(
                               src, dst, rd["owner_class"], rd["owner_uid"]))
        c, hc = addr.tun(real, src)
        info.update(tun=c, tun_how=hc, dst_term=dt[2])
        return "tunouter", rs, rd, info
    st_, hs = addr.triple(real, src, True, loop_of)
    info.update(src=st_, src_how=hs)
    return "nested", rs, rd, info


def face_twins(rows, r, owners):
    """PD191(b): the owner-routed OUTER faces on the same owner structure as row r with r's (name, direction) - r included.
    A face whose owner is unknown has no twins (its owner route stops in Addr._triple as before)."""
    def own(x):
        try:
            return tunnel_owner(rows, x["owner_uid"], owners)
        except ExecStop:
            return None
    o = own(r)
    if o is None:
        return [r]
    return [x for x in rows if x["owner_class"] in OWNER_ROUTED and x["term_class"] == "OuterTerminal"
            and x["term_name"] == r["term_name"] and bool(x["is_source"]) == bool(r["is_source"]) and own(x) == o]


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

    def const(self, real, term_uid):
        """PD188(c): a bare diagram-CONSTANT source -> {const, cls, term}. Its terminal row must be the constant's own
        (node == owner), and the owner must be in the reader's class listing (report_all(<class>) on the real reader)."""
        rows = [r for r in real if r["term_uid"] == term_uid]
        if len(rows) != 1:
            raise ExecStop("ADDRESS-CONST: #{0}: {1} rows in the live read".format(term_uid, len(rows)))
        r = rows[0]
        if not is_const(r) or V.node_of(r) != r["owner_uid"]:
            raise ExecStop("ADDRESS-CONST: #{0} is {1} #{2} (node #{3}), not a constant's own terminal".format(
                term_uid, r["owner_class"], r["owner_uid"], V.node_of(r)))
        cls, u = r["owner_class"], int(r["owner_uid"])
        if u not in self.rd.obj_uids(cls):
            raise ExecStop("ADDRESS-CONST: #{0} not in report_all({1!r})".format(u, cls))
        return {"const": u, "cls": cls, "term": term_uid}, "constant route 188(c): {0} #{1} in report_all, terminal #{2}".format(
            cls, u, term_uid)

    def tun(self, real, term_uid):
        """PD191(b): a structure tunnel's OUTER face -> {tun, cls, term}, addressed by the TUNNEL uid (Tunnel.Outside
        Terminal 6356001), never through the owner's Terminals[] (T2c2, docs/NAMES.md:1132-1137). The tunnel must own exactly
        ONE OuterTerminal row (this one) and be in the reader's class listing (report_all(<class>) on the real reader)."""
        rows = [r for r in real if r["term_uid"] == term_uid]
        if len(rows) != 1:
            raise ExecStop("ADDRESS-TUN: #{0}: {1} rows in the live read".format(term_uid, len(rows)))
        r = rows[0]
        if r["owner_class"] not in OWNER_ROUTED or r["term_class"] != "OuterTerminal":
            raise ExecStop("ADDRESS-TUN: #{0} is {1} {2}, not a tunnel's outer face".format(term_uid, r["owner_class"], r["term_class"]))
        cls, u = r["owner_class"], int(r["owner_uid"])
        outer = [x["term_uid"] for x in real if x["owner_uid"] == u and x["term_class"] == "OuterTerminal"]
        if outer != [term_uid]:
            raise ExecStop("ADDRESS-TUN: tunnel #{0} has outer faces {1}, not exactly #{2}".format(u, outer, term_uid))
        if u not in self.rd.obj_uids(cls):
            raise ExecStop("ADDRESS-TUN: tunnel #{0} not in report_all({1!r})".format(u, cls))
        return {"tun": u, "cls": cls, "term": term_uid}, "tunnel route 191(b): {0} #{1} in report_all, Outside Terminal #{2}".format(
            cls, u, term_uid)

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
BIND_KINDS = ("add_sr", "tunnel", "create")         # ops that make objects: a fresh read is required after each


class Executor(object):
    """PD193(a), card 86-4: `checkpoints` = the real-op numbers k after which the whole-VI read + step diff run. None =
    every op (the default; unchanged behaviour). A set must hold every add_sr/tunnel op (bind_new needs the fresh read)
    and the LAST op (the final state is always compared and returned); otherwise ExecStop CHECKPOINT before op 1.
    Between checkpoints the last real read is reused; each op keeps its own connect read-back. A pre-mutation
    addressing ExecStop on a reused read gets ONE fresh read + one retry (connect/tunnel/wire_sr), as meter_l2a1_86d.py."""
    RETRY_KINDS = ("connect", "tunnel", "wire_sr")

    def __init__(self, plan_path, backend, log=print, checkpoints=None, require_final=True, record=False):
        # card 101-4 RECORD MODE: a STEP-DIFF is logged into self.diffs and the run CONTINUES on the (unsaved) scratch;
        # any other ExecStop (binding, addressing, op error, MEMSTOP) still stops, and self.cur names the op it stopped
        # in. The caller saves nothing unless self.diffs is empty.
        self.record = bool(record)
        self.diffs, self.cur = [], None
        self.checkpoints = None if checkpoints is None else set(int(k) for k in checkpoints)
        self.reads_skipped, self.reads_real, self.stale_retries = [], [], []
        self.plan_path = plan_path
        self.plan, self.step_paths = load_final_plan(plan_path, require_final)
        self.ops = compile_plan(self.plan)
        self.be = backend
        self.log = log
        self.bind = {"obj": {}, "term": {}, "diag": {}}     # card 100-3: sim diagram uid -> real (a created loop's body)
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

    def diag_real(self, st, ref):
        """card 100-3: a diagram field -> the REAL diagram uid (an int as is; 'new:X.body' through the binding the create
        of loop X recorded from the uid it returned)."""
        if isinstance(ref, int) and not isinstance(ref, bool):
            return ref
        try:
            su = SS.resolve_diag(st, ref)
        except SS.SimError as e:
            raise ExecStop(str(e))
        r = self.bind["diag"].get(su)
        if r is None:
            raise ExecStop("diagram {0} (simulated #{1}) is not bound to a real diagram yet".format(ref, su))
        return r

    def obj_real(self, st, ref):
        u = SS.resolve_uid(st, ref)
        r = self.bind["obj"].get(u, u)
        if r < 0:
            raise ExecStop("object {0} (simulated #{1}) is not bound yet".format(ref, u))
        return r

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
        meter = getattr(be, "meter", None) or (lambda *_a, **_k: None)     # PD192(a): per op + per read; absent on dry runs
        meter("start", 0)
        real = be.read()
        meter("read", 0)
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
        cp = self.checkpoints
        if cp is not None:
            need = set(k for k, o in enumerate(self.ops, 1) if o["kind"] in BIND_KINDS) | {len(self.ops)}
            bad = sorted(need - cp) + sorted(k for k in cp if not 0 <= k <= len(self.ops))
            if bad:
                raise ExecStop("CHECKPOINT: set {0} lacks binding/last op(s) or is out of range: {1} (need {2}) - stop before op 1".format(
                    sorted(cp), bad, sorted(need)))
            self.log("  CHECKPOINTS whole-VI read+diff after ops {0} of {1}".format(sorted(k for k in cp if k), len(self.ops)))
        stale = False
        last_read_k = 0
        for k, op in enumerate(self.ops, 1):
            self.cur = {"k": k, "op": op["kind"], "acts": op["acts"], "ids": [A[n - 1].get("id") for n in op["acts"]]}
            first, last = op["acts"][0], op["acts"][-1]
            prev = self.step(first - 1)["state"]
            after = self.step(last)
            be.addr.owners = prev.get("owners") or be.addr.owners
            t0 = time.time()
            if op["kind"] == "add_sr":
                a = A[first - 1]
                be.addr.snap_loop(int(a["loop"]), int(after["state"]["diagrams"][str(a["body"])]))
            meter("pre", k)                        # parity/PRIME (k=1) or retrack/bind reads since the last whole-VI read
            try:
                be.strict = stale and op["kind"] in self.RETRY_KINDS
                res = self.execute(op, prev, after["state"], real)
            except ExecStop as e:                  # PD193: a stale read may mis-address; one fresh read, one retry
                if not stale or op["kind"] not in self.RETRY_KINDS or "op error" in str(e):
                    raise
                self.log("  STALE-ADDRESS op {0}: fresh read + one retry ({1})".format(k, str(e)[:200]))
                self.stale_retries.append({"k": k, "err": str(e)[:200]})
                real, stale, be.strict = be.read(), False, False
                meter("read_retry", k)
                res = self.execute(op, prev, after["state"], real)
            be.strict = False
            meter("op", k)
            if cp is not None and k not in cp:     # PD193(a): no whole-VI read/diff between checkpoints
                self.reads_skipped.append(k)
                stale = True
                lost = be.addr.retrack()           # never add_sr/tunnel here (both are required checkpoints)
                if lost:
                    res = dict(res or {}, lost_register_faces=lost)
                for n in op["acts"]:
                    self.allow.update((self.step(n).get("effect") or {}).get("allow_either") or [])
                rec = {"k": k, "op": op["kind"], "acts": op["acts"], "ids": [A[n - 1].get("id") for n in op["acts"]],
                       "result": res, "bound": {}, "diff": {"n": 0, "skipped": True}, "secs": round(time.time() - t0, 1)}
                self.report.append(rec)
                self.log("  STEPX {0:02d} {1:<14} acts {2} ids {3} diff skipped (not a checkpoint)".format(
                    k, op["kind"], op["acts"], rec["ids"]))
                continue
            real_new = be.read()
            stale = False
            self.reads_real.append(k)
            meter("read", k)
            made = {}
            if op["kind"] == "create":                     # card 100-3: a loop owns no row - bound from the op's return
                made = self._bind_create(op, after["state"], res)
            if op["kind"] in BIND_KINDS:
                made.update(bind_new(real, real_new, prev["terminals"], after["state"]["terminals"], self.bind))
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
                msg = "STEP-DIFF after real op {0} ({1}, plan actions {2} {3}): {4}".format(
                    k, op["kind"], op["acts"], rec["ids"], json.dumps({x: y for x, y in d.items() if y and x != "n"},
                                                                       default=str)[:1500])
                if not self.record:
                    raise ExecStop(msg)
                prev = self.diffs[-1]["diff"] if self.diffs else {}
                new = dict((x, sorted(set(map(json.dumps, y)) - set(map(json.dumps, prev.get(x) or []))))
                           for x, y in d.items() if isinstance(y, list) and y)
                self.diffs.append({"k": k, "op": op["kind"], "acts": op["acts"], "ids": rec["ids"], "diff": d,
                                   "new_since_last_diff": dict((x, [json.loads(v) for v in y]) for x, y in new.items() if y),
                                   "ops_since_last_read": list(range(last_read_k + 1, k + 1))})
                self.log("  RECORD " + msg[:1600])
            last_read_k = k
            real = real_new
        un = getattr(be, "unroutable", None)      # a collecting (dry) backend: every unroutable row, reported at the end
        if un:
            raise ExecStop("UNROUTABLE {0} row(s): {1}".format(len(un), "; ".join(
                "acts {0} {1}: {2}".format(u["acts"], u["ids"], u["err"][:160]) for u in un)))
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
            return be.move_in(int(a["nodes"][0]), self.diag_real(prev, a["dest_diagram"]), tuple(a["pos"]), op)
        if kind == "create":                               # card 100-3: exec_create
            return be.create(op["route"], a, self._create_args(a, prev, after), real, op)
        if kind == "gate":
            return be.value_gate(self.obj_real(prev, a["uid"]), a, op)
        if kind == "stop":
            loop = self.obj_real(prev, op["loop"])
            src = self.real_term(prev, after, a["src"], True)
            return be.stop(loop, src, real, op)
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
            return be.branch(tun, dst, real, self.loop_of, op, side=op.get("side", "outer"))
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

    def _bind_create(self, op, after, res):
        """A created LOOP owns no terminal row: bind its object and its body diagram from the uids the op returned
        (res 'uid', 'body'); a missing or non-positive return STOPS (the body could not be addressed)."""
        a = self.plan["actions"][op["acts"][0] - 1]
        if op["route"] not in ("while", "for"):
            return {}
        su, sb = after["sym"]["new:" + a["as"]], after["sym"]["new:" + a["as"] + ".body"]
        ru, rb = (res or {}).get("uid"), (res or {}).get("body")
        if not isinstance(ru, int) or not isinstance(rb, int) or ru <= 0 or rb <= 0:
            raise ExecStop("BINDING: create {0} returned uid {1!r} body {2!r} - a loop and its body must both come back".format(
                a.get("id"), ru, rb))
        self.bind["obj"][su] = ru
        self.bind["diag"][sb] = rb
        return {su: ru, sb: rb}

    def _create_args(self, a, prev, after):
        """The REAL inputs of a create row: its diagram, and the real terminal of born_on / on (resolved on the simulated
        state, then through the binding)."""
        out = {"diagram": self.diag_real(prev, a["diagram"]), "pos": a.get("pos")}
        if a.get("born_on") is not None:
            out["born_on"] = self.real_term(prev, after, a["born_on"], True)
        if a.get("on") is not None:
            out["on"] = self.real_term(prev, prev, a["on"], False)
        if a.get("donor_uid") is not None:
            out["donor_uid"] = int(a["donor_uid"])
        return out


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

    def obj_uids(self, cls):                                           # PD188(c): the class traverse wire_const indexes
        return [int(o["uid"]) for o in self.g.report_all(self.work, cls)]


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

    def __init__(self, s, fs_pairs, sink_gates=None, gates=None, mem_stop_mb=MEM_STOP_MB):
        import stagekit as K
        import gscript as g
        self.K, self.g, self.s, self.fs = K, g, s, fs_pairs
        self.B = K.mod("build_d1_v0")
        self.C82 = K.mod("build_opfsinnertunnelconnect_v0")
        self.addr = Addr(LVReader(g, s.work))
        self.reads = []
        bp = K.mod("bench_prep")                     # PD192(a): stagekit.private_bytes() + bench_prep.labview_handles()
        self.meter = Meter(lambda: (K.private_bytes(), bp.labview_handles()), stop_mb=mem_stop_mb,
                           log=lambda m: print(m, flush=True))
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
        if kind == "ctlsink":                              # card 85-2, PD191(a): OpCtlSinkWire_v1 (build_opctlsinkwire_v1.py)
            ci = self.s.uid_index("ControlTerminal", int(dst))
            si = self.s.uid_index(rs["owner_class"], int(rs["owner_uid"]))
            if ci is None or si is None:
                raise ExecStop("ctlsink: CT #{0} / {1} #{2} not in their class traverses ({3}, {4})".format(
                    dst, rs["owner_class"], rs["owner_uid"], ci, si))
            t = info["src_term"]
            rec = self.s._op("wire_ctlsink", lambda: self.g.wire_ctlsink(self.s.work, ci, rs["owner_class"], si, t),
                             "ControlTerminal[{0}] #{1} <- {2}[{3}].t{4}".format(ci, dst, rs["owner_class"], si, t))
            res = rec.get("result")
            if isinstance(res, (list, tuple)) and len(res) > 1 and res[1]:
                rec["err"] = rec.get("err") or res[1]
            out = self._done(rec, "connect #{0}->#{1}".format(src, dst))
            out["how"] = ["ctlsink", info["dst_ct"], info["src_how"]]
            return out
        dt, hd = info["dst"], info["dst_how"]
        if kind == "tunouter":                             # card 85-2, PD191(b): OpTunOuterWire_v1 (build_optunouter_v1.py)
            c = info["tun"]
            ti = self.s.uid_index(c["cls"], c["tun"])
            di = self.s.uid_index(rd["owner_class"], int(rd["owner_uid"]))
            if ti is None or di is None:
                raise ExecStop("tunouter: {0} #{1} -> {2} #{3} not in their class traverses ({4}, {5})".format(
                    c["cls"], c["tun"], rd["owner_class"], rd["owner_uid"], ti, di))
            rec = self.s._op("wire_tunouter", lambda: self.g.wire_tunouter(self.s.work, c["cls"], ti, rd["owner_class"], di, dt[2]),
                             "{0}[{1}] #{2} -> {3}[{4}].t{5}".format(c["cls"], ti, c["tun"], rd["owner_class"], di, dt[2]))
            res = rec.get("result")
            if isinstance(res, (list, tuple)) and len(res) > 1 and res[1]:
                rec["err"] = rec.get("err") or res[1]
            out = self._done(rec, "connect #{0}->#{1}".format(src, dst))
            out["how"] = ["tunouter", info["tun_how"], hd]
            return out
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
        if kind == "const":                                # card 85-1: OpConstWire_v1 (tools/recipes/build_opconstwire_v1.py)
            c = info["const"]
            si = self.s.uid_index(c["cls"], c["const"])
            di = self.s.uid_index(rd["owner_class"], int(rd["owner_uid"]))
            if si is None or di is None:
                raise ExecStop("const: {0} #{1} -> {2} #{3} not in their class traverses ({4}, {5})".format(
                    c["cls"], c["const"], rd["owner_class"], rd["owner_uid"], si, di))
            rec = self.s._op("wire_const", lambda: self.g.wire_const(self.s.work, c["cls"], si, rd["owner_class"], di, dt[2]),
                             "{0}[{1}] #{2} -> {3}[{4}].t{5}".format(c["cls"], si, c["const"], rd["owner_class"], di, dt[2]))
            res = rec.get("result")
            if isinstance(res, (list, tuple)) and len(res) > 1 and res[1]:
                rec["err"] = rec.get("err") or res[1]
            out = self._done(rec, "connect #{0}->#{1}".format(src, dst))
            out["how"] = ["const", info["const_how"], hd]
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

    # ------------------------------------------------------------------ card 100-3: exec_create / stop / value gate
    def create(self, route, a, args, real, op):
        """One `create` row -> its verb (CREATE_ROUTES). Returns {err, s, uid[, body], how}. Every verb is followed by the
        junk purge (_done)."""
        g, s, W = self.g, self.s, self.s.work
        missing = verbs_missing(route)
        if missing:
            raise ExecStop("create {0} ({1}): verb(s) not defined: {2}".format(a.get("id"), route, missing))
        dg, pos = args["diagram"], tuple(args.get("pos") or (40, 40))
        di = self.B.diag_index(W, dg)
        tag = "create {0} {1}".format(route, a.get("id"))
        if route in ("while", "for"):
            d0 = set(int(d["uid"]) for d in g.report_all(W, "Diagram"))
            rec = s._op("loop_in", lambda: g.loop_in(route, W, di, pos), "{0} on Diagram[{1}] #{2}".format(route, di, dg))
            out = self._done(rec, tag)
            body = sorted(set(int(d["uid"]) for d in g.report_all(W, "Diagram")) - d0)
            if len(body) != 1:
                raise ExecStop("{0}: {1} new Diagram(s) after loop_in, expected the one body: {2}".format(tag, len(body), body))
            out.update(uid=int(rec["result"]), body=body[0], how=CREATE_ROUTES[route])
            return out
        if route == "local_read":
            l0 = set(int(u) for u in g.uids(W, "Local"))
            out = self._done(s.create_local_read(a["label"], tag=tag), tag)
            new = sorted(set(int(u) for u in g.uids(W, "Local")) - l0)
            if len(new) != 1:
                raise ExecStop("{0}: {1} new Local(s)".format(tag, len(new)))
            if di != 0:
                self._done(s.move_in(new[0], di, pos), tag + " move_in")
            out.update(uid=new[0], how=CREATE_ROUTES[route])
            return out
        if route == "local_write":
            rec = s.create_local_write(a["label"], dest_diagram_uid=dg, position=pos, tag=tag)
            res = rec.get("result") or {}
            if res.get("err"):
                rec["err"] = rec.get("err") or res["err"]
            out = self._done(rec, tag)
            out.update(uid=res.get("uid"), how=CREATE_ROUTES[route])
            return out
        if route in ("indicator", "control"):
            end = args["born_on"] if route == "indicator" else args["on"]
            face = tunnel_outer_face(real, end, dg) if route == "indicator" else None
            if face is not None:                   # card 100-6 (PD213(f)3): create_indicator_nested(W, <face term>, None)
                how = "LoopTunnel #{0} outer face #{1} (OpTunnelInd_v0)".format(face["owner_uid"], end)
                rec = s._op("indicator_nested", lambda: g.create_indicator_nested(W, int(end), None), how)
            else:
                (_d, _n, t), how = self.addr.triple(real, end, route == "indicator")
                node = V.node_of(next(r for r in real if r["term_uid"] == end))
                fn = g.create_indicator_nested if route == "indicator" else g.create_control_nested
                rec = s._op(route + "_nested", lambda: fn(W, node, t), "#{0}.t{1}".format(node, t))
            res = rec.get("result") or {}
            if res.get("err") or len(res.get("new_panel") or []) != 1:
                rec["err"] = rec.get("err") or res.get("err") or "{0} new panel objects".format(len(res.get("new_panel") or []))
            out = self._done(rec, tag)
            pu = int(res["new_panel"][0]["uid"])
            pi = [int(r["uid"]) for r in g.panel_wiring(W)].index(pu)
            lab = g.set_control_label(W, pi, a["label"])
            if lab.get("err") or lab.get("text_back") != a["label"]:
                raise ExecStop("{0}: label write read back {1!r} err {2!r}".format(tag, lab.get("text_back"), lab.get("err")))
            if a.get("visible") is not None:
                vis = g.set_visible(W, pu, bool(a["visible"]))
                if vis.get("err") or bool(vis.get("visible_back")) != bool(a["visible"]):
                    raise ExecStop("{0}: Visible read back {1!r} err {2!r}".format(tag, vis.get("visible_back"), vis.get("err")))
            if route == "control" and a.get("default") is not None:
                dv = g.set_default_in_memory(W, a["label"], a["default"], a["default"] + 1)
                if dv.get("err") or dv.get("after_reinit") != a["default"]:
                    raise ExecStop("{0}: default read back {1!r} err {2!r}".format(tag, dv.get("after_reinit"), dv.get("err")))
            out.update(uid=pu, how=[CREATE_ROUTES[route], how])
            return out
        if route == "primitive":
            rec = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, dg, a["prim"], pos),
                        "{0!r} on #{1}".format(a["prim"], dg))
            out = self._done(rec, tag)
            out.update(uid=rec.get("result"), how=CREATE_ROUTES[route])
            return out
        if route == "copy_in":
            u = s.copy_in(a["class"], args["donor_uid"], dg, pos, tag=tag)
            return {"err": None, "uid": u, "how": CREATE_ROUTES[route]}
        if route == "const_on_term":
            rs = next(r for r in real if r["term_uid"] == args["on"])
            loop = int((self.addr.owners.get(str(int(rs["frame_diagram"]))) or [None, 0])[1] or 0)
            rec = s.const_row({"loop_uid": loop, "body_diagram": int(rs["frame_diagram"]), "node": V.node_of(rs),
                               "term": rs["term_name"], "value": a.get("value")}, tag=tag)
            out = self._done(rec, tag)
            out["how"] = CREATE_ROUTES[route]
            return out
        raise ExecStop("create route {0!r} has no LabVIEW executor".format(route))

    def stop(self, loop, src, real, op):
        """OpStopFromNode_v0 (tools/recipes/build_opcreateconstonterm_v0.py:528-537): the While loop's conditional terminal
        <- Terminals[t] of Nodes[n] of the loop's BODY (the source addressed by the same Addr triple as any connect)."""
        (_d, n, t), how = self.addr.triple(real, src, True)
        lab = json.load(open(os.path.join(BENCH, "opstopfromnode_labels.json"), encoding="utf-8"))
        li = self.s.uid_index("WhileLoop", loop)

        def _call():
            vs = self.g.op(os.path.join(self.g.CLAUDEDEV, "OpStopFromNode_v0.vi"))
            vs.SetControlValue("vi path", self.s.work)
            vs.SetControlValue("Class Name", "WhileLoop")
            vs.SetControlValue("index", int(li))
            vs.SetControlValue(lab["index_node"], int(n))
            vs.SetControlValue(lab["index_term"], int(t))
            self.g._run(vs)
            return self.g._err(vs, "error out") or ""
        rec = self.s._op("stop_from_node", _call, "WhileLoop[{0}] #{1} cond <- N[{2}].t{3}".format(li, loop, n, t))
        if rec.get("result"):
            rec["err"] = rec.get("err") or rec["result"]
        out = self._done(rec, "stop #{0}".format(loop))
        out["how"] = ["OpStopFromNode_v0", how]
        return out

    def value_gate(self, uid, a, op):
        """read_bool_const (OpConstValueB_v0, card 100-2 V4): the stage STOPS when the value equals `stop_if`."""
        r = self.g.read_bool_const(self.s.work, uid)
        self.s.fact("VALUE GATE {0} #{1} = {2!r} (stop_if {3!r}) err {4!r}".format(a.get("id"), uid, r.get("value"),
                                                                               a.get("stop_if"), r.get("err")))
        if r.get("err") or r.get("echo") not in (None, uid) or not isinstance(r.get("value"), bool):
            raise ExecStop("VALUE-GATE {0}: #{1} not read ({2})".format(a.get("id"), uid, r))
        if r["value"] == a["stop_if"]:
            raise ExecStop("VALUE-GATE {0}: #{1} is {2!r} - the plan says stop".format(a.get("id"), uid, r["value"]))
        return {"err": None, "value": r["value"], "how": "read_bool_const"}

    def branch(self, tun, dst, real, loop_of, op, side="outer"):
        face = "InnerTerminal" if side == "inner" else "OuterTerminal"     # card 100-3: an INPUT tunnel branches inside
        outer = [r for r in real if r["owner_uid"] == tun and r["term_class"] == face and r["is_source"]]
        if len(outer) != 1 or not outer[0]["wire_uid"]:
            raise ExecStop("branch: tunnel #{0} has no wired {1} source".format(tun, side))
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
        # card 100-3: + every body the plan made (an EMPTY new body is in report_all('Diagram') as soon as its loop exists)
        return sorted(set(int(r["frame_diagram"] or 0) for r in self.be.st["terminals"]) |
                      set(int(k) for k in (self.be.st.get("diagrams") or {})))

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

    def obj_uids(self, cls):                                            # the report_all(<class>) analogue (PD188(c))
        out = []
        for r in self.be.st["terminals"]:
            if r["owner_class"] == cls and int(r["owner_uid"]) not in out:
                out.append(int(r["owner_uid"]))
        return out


class SimBackend(object):
    """The DRY backend: every real op applies the plan actions it covers with stagesim's own OPS on a private state
    (the measured models), then renumbers the created uids to fresh POSITIVE ones, as LabVIEW would; the executor's
    compile / address / bind / compare path runs unchanged. `fault` injects one defect for the self-test."""

    def __init__(self, plan, base_state, models, fault=None):
        self.plan, self.st, self.models, self.fault = plan, copy.deepcopy(base_state), models, fault or {}
        self.next = 10 ** 7
        self.addr = Addr(SimReader(self))
        self.calls = []
        self.unroutable = []
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

        def rn(v):                                     # every created (negative) id -> a fresh positive one, once
            if isinstance(v, int) and v < 0:
                if v not in ren:
                    self.next += 1
                    ren[v] = self.next
                return ren[v]
            return v
        for r in self.st["terminals"]:
            for k in ("owner_uid", "term_uid", "wire_uid", "frame_diagram"):     # card 100-3: + a created body diagram
                r[k] = rn(r[k])
        for o in self.st["objs"]:
            o["uid"] = rn(int(o["uid"]))
        for L in self.st["loops"] or []:
            L["loop_uid"] = rn(int(L["loop_uid"]))
            L["right_uids"] = [ren.get(int(u), int(u)) for u in L.get("right_uids") or []]
            L["left_of"] = dict((str(ren.get(int(k), int(k))), [ren.get(int(x), int(x)) for x in (v if isinstance(v, list) else [v])])
                                for k, v in (L.get("left_of") or {}).items())
        self.st["diagrams"] = dict((str(rn(int(k))), rn(int(v))) for k, v in (self.st.get("diagrams") or {}).items())
        self.st["owners"] = dict((str(rn(int(k))), [v[0], rn(int(v[1] or 0))]) for k, v in (self.st.get("owners") or {}).items())
        self.st["sym"] = dict((k, rn(v)) for k, v in self.st["sym"].items())
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
        if dest not in self.addr.rd.diagrams():                  # card 100-3: a symbolic dest must have been bound
            return self._unroutable(op, ExecStop("move_in #{0}: destination diagram #{1} not in the diagram list".format(uid, dest)))
        return self._apply(op)

    def add_sr(self, loop, y, op):
        return self._apply(op)

    # ------------------------------------------------------------------ card 100-3: the dry side of exec_create
    def _node_end(self, real, term, is_source, verb):
        """The end a node-addressed creator needs: a terminal of a Diagram.Nodes[] node (Traverse('Node') by uid finds
        nodes only - a tunnel face, register, constant or ControlTerminal is not one), then its Addr triple."""
        r = next((x for x in real if x["term_uid"] == term), None)
        if r is None:
            raise ExecStop("{0}: terminal #{1} not in the live read".format(verb, term))
        if not listed_as_node(r) or is_const(r) or V.node_of(r) != r["owner_uid"]:
            raise ExecStop("{0} addresses Traverse('Node') by uid; #{1} {2!r} belongs to {3} #{4}, which is not a Node "
                           "(a tunnel face / register / constant / panel terminal)".format(
                               verb, term, r["term_name"], r["owner_class"], r["owner_uid"]))
        return self._check(real, term, is_source)

    def create(self, route, a, args, real, op):
        try:
            miss = verbs_missing(route)
            if miss:
                raise ExecStop("CREATE-NO-VERB {0}: not defined: {1}".format(route, miss))
            dl = self.addr.rd.diagrams()
            if args["diagram"] not in dl:
                raise ExecStop("create {0}: diagram #{1} not in the diagram list".format(route, args["diagram"]))
            chk = {"route": route, "verbs": ROUTE_VERBS.get(route)}
            if route in ("local_read", "local_write"):
                cts = [r for r in real if is_ct(r) and r["term_name"] == a["label"]]
                if len(cts) != 1:
                    raise ExecStop("create {0}: {1} front-panel terminal(s) labelled {2!r} (a local binds to exactly one)".format(
                        route, len(cts), a["label"]))
                chk["panel_ct"] = cts[0]["term_uid"]
            elif route == "indicator":
                face = tunnel_outer_face(real, args["born_on"], args["diagram"])
                if face is not None:                   # card 100-6 (PD213(f)3): the tunnel-face route of the real backend
                    chk.update(tunnel_face=face["term_uid"], tunnel=face["owner_uid"],
                               via="gscript.create_indicator_nested(W, face, None) -> OpTunnelInd_v0")
                else:
                    chk.update(self._node_end(real, args["born_on"], True, "create_indicator_nested"))
            elif route == "control":
                chk.update(self._node_end(real, args["on"], False, "create_control_nested"))
            elif route == "const_on_term":
                chk.update(self._node_end(real, args["on"], False, "const_row (OpCreateConstOnTerm_v0)"))
                rs = next(x for x in real if x["term_uid"] == args["on"])
                own = (self.st.get("owners") or {}).get(str(int(rs["frame_diagram"])))
                if not own or own[0] != "WhileLoop":
                    raise ExecStop("const_row: the sink's diagram #{0} is not a WhileLoop body ({1})".format(rs["frame_diagram"], own))
            elif route == "copy_in":
                S0 = SS.base_state(_j(_abs(self.plan["finalized"]["base"]["path"])), self.plan.get("context"))
                if SS.obj_class(S0, args["donor_uid"]) != a["class"]:
                    raise ExecStop("copy_in: donor #{0} is {1} in the base, not {2}".format(
                        args["donor_uid"], SS.obj_class(S0, args["donor_uid"]), a["class"]))
            elif route == "primitive" and not a.get("prim"):
                raise ExecStop("create_primitive_nested needs `prim`")
        except ExecStop as e:
            return self._unroutable(op, e)
        out = self._apply(op, chk)
        if route in ("while", "for"):
            out.update(uid=self.st["sym"]["new:" + a["as"]], body=self.st["sym"]["new:" + a["as"] + ".body"])
        return out

    def stop(self, loop, src, real, op):
        try:
            miss = verbs_missing("stop")
            if miss:
                raise ExecStop("CREATE-NO-VERB stop: {0}".format(miss))
            if int(loop) not in [int(L["loop_uid"]) for L in self.st["loops"] or []]:
                raise ExecStop("stop: loop #{0} not in the loop table".format(loop))
            chk = self._node_end(real, src, True, "OpStopFromNode_v0 (body Nodes[] index)")
        except ExecStop as e:
            return self._unroutable(op, e)
        return self._apply(op, chk)

    def value_gate(self, uid, a, op):
        try:
            miss = verbs_missing("gate")
            if miss:
                raise ExecStop("CREATE-NO-VERB gate: {0}".format(miss))
            if int(uid) not in self.addr.rd.obj_uids("BooleanConstant"):
                raise ExecStop("gate: #{0} not in report_all('BooleanConstant')".format(uid))
        except ExecStop as e:
            return self._unroutable(op, e)
        out = self._apply(op, {"value": "not read offline (the graph carries no values)"})
        out["value"] = None
        return out

    def wire_sr(self, variant, loop, right, term, real, op):
        try:
            chk = self._check(real, term, variant == "RightIn")
        except ExecStop as e:
            return self._unroutable(op, e)
        return self._apply(op, chk)

    def _unroutable(self, op, e):
        """violation-decisions 16:10 (card 85-1): the DRY run records EVERY unroutable row and keeps simulating (the op is
        still applied from the plan), so one dry run lists them all; dry_run() then FAILS naming each. The real backend
        never collects - it stops at the first."""
        if getattr(self, "strict", False):             # PD193: on a reused (stale) read the executor retries once on a
            raise e                                    # fresh read, as the real backend's pre-mutation stop would
        rec = {"acts": op["acts"], "ids": [self.plan["actions"][n - 1].get("id") for n in op["acts"]], "err": str(e)[:300]}
        self.unroutable.append(rec)
        return self._apply(op, {"unroutable": rec["err"]})

    def connect(self, src, dst, real, loop_of, op):
        try:
            if self.fault.get("kind") == "unroutable" and op["acts"][-1] in self.fault.get("at_acts", ()):
                raise ExecStop("CONNECT-NO-VERB: injected unroutable row (self-test)")
            kind, _rs, _rd, info = connect_route(self.addr, real, src, dst, loop_of)   # PD187(b): the real backend's route
            chk = None if kind == "indicator" else ({"src_triple": list(info["src"]), "how": info["src_how"]}
                                                     if kind == "ctlsink" else self._check(real, dst, False, loop_of))
        except ExecStop as e:
            return self._unroutable(op, e)
        if chk is not None:
            chk["route"] = kind
        return self._apply(op, chk)

    def branch(self, tun, dst, real, loop_of, op, side="outer"):
        face = "InnerTerminal" if side == "inner" else "OuterTerminal"     # card 100-3: the real backend's face rule
        try:
            f = [r for r in real if r["owner_uid"] == tun and r["term_class"] == face and r["is_source"]]
            if len(f) != 1 or not f[0]["wire_uid"]:
                raise ExecStop("branch: tunnel #{0} has no wired {1} source".format(tun, side))
            rd = next(r for r in real if r["term_uid"] == dst)
            chk = None if is_ct(rd) else self._check(real, dst, False, loop_of)
        except ExecStop as e:
            return self._unroutable(op, e)
        return self._apply(op, chk)

    def index_mode_fix(self, tun, indexing):
        return 1 if indexing else 0

    def delete_wire(self, w, op, plan_wire=None):
        return self._apply(op)

    def delete_object(self, cls, uid, op):
        return self._apply(op)

    def rbw(self, op):
        return self._apply(op)


def dry_run(plan_path, fault=None, log=print, model_dir=None, require_final=True):
    """(status, first_fail, executor). No LabVIEW. require_final=False = the DIAGNOSTIC routability run (card 100-3)."""
    plan, _paths = load_final_plan(plan_path, require_final)
    base = _j(_abs(plan["finalized"]["base"]["path"]))
    st = SS.base_state(base, plan.get("context"))
    be = SimBackend(plan, st, SS.load_models(model_dir or SS.OPMODEL_DIR), fault)
    ex = Executor(plan_path, be, log, require_final=require_final)
    ex.unroutable = be.unroutable
    try:
        ex.run()                                       # raises UNROUTABLE at the end when any row was unroutable
        return "PASS", None, ex
    except ExecStop as e:
        for u in be.unroutable:                        # every unroutable row, not only the first (violation-decisions 16:10)
            log("  UNROUTABLE acts {0} ids {1}: {2}".format(u["acts"], u["ids"], u["err"]))
        msg = str(e)
        if be.unroutable and not msg.startswith("UNROUTABLE"):     # a later hard stop: name the rows collected before it
            msg = "UNROUTABLE {0} row(s) before the stop: {1} | STOP {2}".format(
                len(be.unroutable), "; ".join("acts {0} {1}".format(u["acts"], u["ids"]) for u in be.unroutable), msg)
        return "FAIL", msg[:4000], ex


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
            s.R["stagexec"], s.R["meter"] = ex.report, be.meter.rows
            s.fact("METER SUMMARY {0}".format(json.dumps(be.meter.summary(), default=str)))
            s.gate("E1 every real op's graph == its simulated step", False, str(e)[:1500], fatal=True)
        s.R["stagexec"], s.R["meter"] = ex.report, be.meter.rows
        s.fact("METER SUMMARY {0}".format(json.dumps(be.meter.summary(), default=str)))
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
    # PD188(c) (card 85-1): a BARE diagram-constant source -> 'const' (gscript.wire_const, OpConstWire_v1), both backends
    rk = rc_ + [row(901, "disabled index (col)", True, 0, 900, "DigitalNumericConstant", 1, "Terminal")]
    sk = SimReader(_StateHolder({"loops": [], "owners": {}, "objs": [], "terminals": rk}))
    try:
        k_, _a1, _a2, i_ = connect_route(Addr(sk, {}), rk, 901, 701, {})
        gate("T28 bare constant source -> 'const' route: constant #900 by its class listing, sink terminal index 0 ('y'), "
             "and the constant is NOT a Nodes[] entry", k_ == "const" and i_["const"]["const"] == 900 and i_["dst_term"] == 0
             and 900 not in sk.node_uids(0), (k_, i_))
    except ExecStop as e:
        gate("T28 bare constant source -> 'const' route", False, e)

    class NoConst(SimReader):
        def obj_uids(self, cls):
            return []
    negk = (("T28b NEGATIVE: a constant absent from report_all(<class>) is not addressable", Addr(NoConst(sk.be), {}), 901, 701, "ADDRESS-CONST"),
            ("T28c NEGATIVE: constant -> a sink owned by an owner-routed tunnel -> STOP", Addr(SimReader(_StateHolder(
                {"loops": [], "owners": {}, "objs": [], "terminals": rk + [row(801, "", False, 0, 800, "SelectorTunnel", 1, "OuterTerminal")]})), {}),
             901, 801, None))
    for lab_, ad_, s_, d_, want in negk:
        rows3 = rk + [row(801, "", False, 0, 800, "SelectorTunnel", 1, "OuterTerminal")]
        try:
            k_ = connect_route(ad_, rows3, s_, d_, {})[0]
            gate(lab_, False, "routed " + k_)
        except ExecStop as e:
            gate(lab_, (want is None or want in str(e)), str(e)[:160])
    try:
        Addr(sk, {}).triple(rk, 901, True)
        gate("T28d NEGATIVE: a constant as a Nodes[] triple FAILS", False, "resolved")
    except ExecStop as e:
        gate("T28d NEGATIVE: a constant as a Nodes[] triple FAILS", "ADDRESS" in str(e), e)
    # PD191 (card 85-2): 'ctlsink' (bare node terminal -> CT sink) and 'tunouter' (bare tunnel outer face, by the TUNNEL uid)
    r30 = rc_ + [row(710, "min value", True, 0, 705, "Function", 1, "ParameterTerminal"),
                 row(711, "x", False, 0, 705, "Function", 1, "ParameterTerminal"),
                 row(606, "min value", False, 0, 1, "Diagram", 1, FP)]
    s30 = SimReader(_StateHolder({"loops": [], "owners": {}, "objs": [], "terminals": r30}))
    try:
        k_, _a1, _a2, i_ = connect_route(Addr(s30, {}), r30, 710, 606, {})
        gate("T30 bare node terminal -> ControlTerminal sink -> 'ctlsink': the CT by 179(b), the source by its node's "
             "Terminals[] index", k_ == "ctlsink" and i_["ct"]["ct"] == 606 and i_["src_term"] == 0, (k_, i_))
    except ExecStop as e:
        gate("T30 bare node terminal -> ControlTerminal sink -> 'ctlsink'", False, e)
    for lab_, s_ in (("T30b NEGATIVE: a bare ControlTerminal source -> CT sink STOPS", 601),
                     ("T30c NEGATIVE: a bare constant source -> CT sink STOPS", 901)):
        rr = r30 + [row(901, "c", True, 0, 900, "DigitalNumericConstant", 1, "Terminal")]
        try:
            k_ = connect_route(Addr(SimReader(_StateHolder({"loops": [], "owners": {}, "objs": [], "terminals": rr})), {}),
                               rr, s_, 606, {})[0]
            gate(lab_, False, "routed " + k_)
        except ExecStop as e:
            gate(lab_, "needs a WIRED source" in str(e), str(e)[:160])
    ow31 = {"2": ["CaseStructure", 820]}
    r31 = rc_ + [row(811, "", True, 0, 810, "SelectorTunnel", 1, "OuterTerminal"),
                 row(812, "", False, 33, 810, "SelectorTunnel", 2, "InnerTerminal"),
                 row(816, "", True, 0, 815, "SelectorTunnel", 1, "OuterTerminal"),          # the TWIN (#6026 beside #6007)
                 row(817, "", False, 34, 815, "SelectorTunnel", 2, "InnerTerminal")]
    s31 = SimReader(_StateHolder({"loops": [], "owners": ow31, "objs": [], "terminals": r31}))
    try:
        k_, _a1, _a2, i_ = connect_route(Addr(s31, ow31), r31, 811, 701, {})
        gate("T31 bare tunnel outer face with a twin on its owner -> 'tunouter' by the TUNNEL uid (#810), sink terminal "
             "index 0 ('y')", k_ == "tunouter" and i_["tun"]["tun"] == 810 and i_["dst_term"] == 0, (k_, i_))
    except ExecStop as e:
        gate("T31 bare tunnel outer face -> 'tunouter'", False, e)
    r31d = rc_ + r31[-4:-2]
    try:
        k_ = connect_route(Addr(SimReader(_StateHolder({"loops": [], "owners": ow31, "objs": [], "terminals": r31d})), ow31),
                           r31d, 811, 701, {})[0]
    except ExecStop as e:
        k_ = "STOP " + str(e)[:80]
    gate("T31d a tunnel outer face WITHOUT a twin keeps its measured owner route (not 'tunouter')", k_ == "nested", k_)
    r31b = r31 + [row(813, "", True, 0, 810, "SelectorTunnel", 1, "OuterTerminal")]
    for lab_, ad_, rr in (("T31b NEGATIVE: a tunnel with TWO outer faces is not addressable by its uid",
                           Addr(SimReader(_StateHolder({"loops": [], "owners": ow31, "objs": [], "terminals": r31b})), ow31), r31b),
                          ("T31c NEGATIVE: a tunnel absent from report_all(<class>) is not addressable",
                           Addr(NoConst(s31.be), ow31), r31)):
        try:
            k_ = connect_route(ad_, rr, 811, 701, {})[0]
            gate(lab_, False, "routed " + k_)
        except ExecStop as e:
            gate(lab_, "ADDRESS-TUN" in str(e), str(e)[:160])
    # violation-decisions 16:10 (card 85-1): the dry run reports EVERY unroutable row, not only the first
    two =[o["acts"][-1] for o in ops if o["kind"] in ("tunnel", "connect")][:2]
    st6, ff6, ex6 = dry_run(fin, fault={"kind": "unroutable", "at_acts": two}, log=q, model_dir=md)
    gate("T29 two unroutable rows -> the dry run FAILS naming BOTH, and simulates on to the last op",
         len(two) == 2 and st6 == "FAIL" and "UNROUTABLE 2" in str(ff6) and [u["acts"][-1] for u in ex6.unroutable] == two
         and len(ex6.report) == len(ops) + 1, (two, str(ff6)[:200], len(ex6.report), len(ops)))
    be7 = SimBackend(pl_, SS.base_state(_j(_abs(pl_["finalized"]["base"]["path"])), pl_.get("context")), SS.load_models(md),
                     fault={"kind": "unroutable", "at_acts": two})
    try:                                          # a recipe's own DryBE calls Executor.run() directly, not dry_run()
        Executor(fin, be7, log=q).run()
        gate("T29b NEGATIVE: Executor.run() on a collecting backend with unroutable rows RAISES at the end (never silent)", False, "ran clean")
    except ExecStop as e:
        gate("T29b NEGATIVE: Executor.run() on a collecting backend with unroutable rows RAISES at the end (never silent)",
             str(e).startswith("UNROUTABLE 2"), str(e)[:160])
    # card 85-3 P4 (hyp-optunouter-uidreuse-85.md:78-82): a uid re-issued inside one op is named, not misreported
    p32 = [row(900, "Terminal", True, 0, 136, "Property", 5, "Terminal"), row(901, "ref", False, 0, 136, "Property", 5, "Terminal"),
           row(910, "x", False, 0, 300, "WhileLoop", 5, "OuterTerminal"), row(920, "c", True, 0, 5, "Diagram", 5, "ControlTerminal")]
    r32 = [row(950, "Outer Term", True, 0, 136, "Property", 5, "Terminal"), row(951, "ref", False, 0, 136, "Property", 5, "Terminal"),
           row(910, "x", False, 0, 300, "WhileLoop", 5, "OuterTerminal"), row(920, "c", True, 0, 5, "Diagram", 5, "ControlTerminal")]
    try:
        bind_new(p32, r32, [], [], {"obj": {}, "term": {}})
        gate("T32 NEGATIVE: Property #136 deleted and re-issued in one op (disjoint terminals) -> ExecStop UID-REUSE", False, "bound")
    except ExecStop as e:
        gate("T32 NEGATIVE: Property #136 deleted and re-issued in one op (disjoint terminals) -> ExecStop UID-REUSE",
             str(e).startswith("UID-REUSE") and "#136" in str(e), str(e)[:200])
    r32b = [dict(r, owner_class="Constant") if r["owner_uid"] == 136 else r for r in p32]
    try:
        bind_new(p32, r32b, [], [], {"obj": {}, "term": {}})
        gate("T32b NEGATIVE: a uid whose class changed (Property -> Constant) -> ExecStop UID-REUSE", False, "bound")
    except ExecStop as e:
        gate("T32b NEGATIVE: a uid whose class changed (Property -> Constant) -> ExecStop UID-REUSE", str(e).startswith("UID-REUSE"),
             str(e)[:200])
    r32c = p32[:3] + [row(911, "", True, 0, 300, "WhileLoop", 5, "OuterTerminal"), row(920, "c", True, 0, 6, "Diagram", 6,
                                                                                         "ControlTerminal")]
    gate("T32c a structure GAINING a face and a control terminal MOVING diagram are not reuse", uid_reuse(p32, r32c) == [],
         uid_reuse(p32, r32c))
    # PD192(a), card 86-1: the memory meter (fake probe; no LabVIEW)
    seq = iter([(400 << 20, 31500), (412 << 20, 31600), (409 << 20, 31550), (705 << 20, 40000)])
    mt = Meter(lambda: next(seq), stop_mb=700.0, log=q)
    r1, r2, r3 = mt("read", 0), mt("op", 1), mt("read", 1)
    gate("T33 meter: MB from bytes, deltas vs the previous stamp (op +12.0 MB/+100 h, read -3.0 MB/-50 h)",
         r1["mb"] == 400.0 and r1["d_mb"] is None and r2["d_mb"] == 12.0 and r2["d_h"] == 100 and r3["d_mb"] == -3.0
         and r3["d_h"] == -50, (r1, r2, r3))
    try:
        mt("op", 2)
        gate("T33b NEGATIVE: private bytes >= stop_mb -> ExecStop MEMSTOP", False, "no stop")
    except ExecStop as e:
        gate("T33b NEGATIVE: private bytes >= stop_mb -> ExecStop MEMSTOP", str(e).startswith("MEMSTOP") and "705.0" in str(e), str(e)[:160])
    mw = Meter(lambda: (800 << 20, 1), stop_mb=None, log=q)
    mw("op", 1)
    mw("op", 2)
    gate("T33c warn-only meter (stop_mb=None) passes 800 MB and records the FIRST crossing",
         mw.warned is not None and mw.warned["k"] == 1 and len(mw.rows) == 2, mw.warned)
    cnt = [0]

    def fprobe(lim=None):
        cnt[0] += 1
        return ((300 + cnt[0]) << 20, 30000 + cnt[0])
    bem = SimBackend(pl_, SS.base_state(_j(_abs(pl_["finalized"]["base"]["path"])), pl_.get("context")), SS.load_models(md))
    bem.meter = Meter(fprobe, stop_mb=None, log=q)
    exm = Executor(fin, bem, log=q)
    exm.run()
    tags = [r["tag"] for r in bem.meter.rows]
    gate("T34 Executor stamps start + base read + (pre, op, read) per op on a backend with a meter",
         tags[:2] == ["start", "read"] and tags[2:] == ["pre", "op", "read"] * len(exm.ops) and
         [r["k"] for r in bem.meter.rows if r["tag"] == "op"] == list(range(1, len(exm.ops) + 1)), (len(tags), len(exm.ops), tags[:8]))
    cnt[0] = 0
    bes = SimBackend(pl_, SS.base_state(_j(_abs(pl_["finalized"]["base"]["path"])), pl_.get("context")), SS.load_models(md))
    bes.meter = Meter(fprobe, stop_mb=300 + 2 + 3 * 3 + 0.5, log=q)   # 311.5: the 12th stamp (312) = op 4's 'pre'
    exs = Executor(fin, bes, log=q)
    try:
        exs.run()
        gate("T34b NEGATIVE: a meter crossing stop_mb mid-run STOPS the executor with MEMSTOP", False, "ran clean")
    except ExecStop as e:
        lr = bes.meter.rows[-1]
        gate("T34b NEGATIVE: a meter crossing stop_mb mid-run STOPS the executor with MEMSTOP (last stamp = op 4 'pre')",
             str(e).startswith("MEMSTOP") and (lr["tag"], lr["k"]) == ("pre", 4) and len(exs.report) == 4, (str(e)[:120], lr, len(exs.report)))
    # PD193(a), card 86-4: the checkpoint read set
    mkbe = lambda fault=None: SimBackend(pl_, SS.base_state(_j(_abs(pl_["finalized"]["base"]["path"])), pl_.get("context")),  # noqa: E731
                                         SS.load_models(md), fault)
    opsx = compile_plan(pl_)
    bindk = set(k for k, o in enumerate(opsx, 1) if o["kind"] in ("add_sr", "tunnel"))
    cps = bindk | {0, len(opsx)}
    exc_ = Executor(fin, mkbe(), log=q, checkpoints=cps)
    exc_.run()
    gate("T35 checkpoint set (binding ops + last): run PASS, whole-VI reads only at the set, the rest skipped",
         exc_.reads_real == sorted(cps - {0}) and exc_.reads_skipped == sorted(set(range(1, len(opsx) + 1)) - cps) and
         len(exc_.reads_skipped) > 0, (sorted(cps), exc_.reads_real, exc_.reads_skipped))
    gate("T35d a stale-read addressing stop is recovered by ONE fresh read + retry (no unroutable row left)",
         len(exc_.stale_retries) >= 1 and not exc_.be.unroutable, (exc_.stale_retries, exc_.be.unroutable))
    fk = next((k for k in range(1, len(opsx)) if k not in cps and any(c > k for c in cps)), None)
    nxt = min(c for c in cps if fk is not None and c > fk) if fk else None
    try:
        Executor(fin, mkbe({"at": opsx[fk - 1]["acts"][-1], "kind": "drop_edge"}), log=q, checkpoints=cps).run()
        gate("T35b NEGATIVE: an edge dropped at a skipped op is caught by the NEXT checkpoint diff", False, "ran clean")
    except ExecStop as e:
        gate("T35b NEGATIVE: an edge dropped at skipped op {0} is caught by the NEXT checkpoint diff (op {1})".format(fk, nxt),
             "STEP-DIFF after real op {0} ".format(nxt) in str(e), str(e)[:200])
    try:
        Executor(fin, mkbe(), log=q, checkpoints={0, len(opsx)}).run()
        gate("T35c NEGATIVE: a set missing a binding op (add_sr/tunnel) stops before op 1", False, "ran")
    except ExecStop as e:
        gate("T35c NEGATIVE: a set missing a binding op (add_sr/tunnel) stops before op 1", str(e).startswith("CHECKPOINT"), str(e)[:200])
    # card 101-4: RECORD MODE - a STEP-DIFF is recorded and the run goes on; other stops still stop
    kd = next(k for k, o in enumerate(opsx, 1) if o["acts"][-1] == 5)
    exr = Executor(fin, mkbe({"at": 5, "kind": "drop_edge"}), log=q, record=True)
    try:
        exr.run()
        gate("T39 record mode: the dropped edge (op {0}) is RECORDED and the run CONTINUES to the last op".format(kd),
             exr.diffs and exr.diffs[0]["k"] == kd and exr.diffs[0]["diff"]["only_sim_edges"] and
             exr.diffs[0]["new_since_last_diff"].get("only_sim_edges") and exr.cur["k"] == len(opsx) and
             len(exr.report) == len(opsx) + 1, [(d["k"], d["diff"]["n"], d["new_since_last_diff"]) for d in exr.diffs][:4])
        gate("T39b record mode attributes a persisting diff ONCE (later records carry no new entry for it)",
             all("only_sim_edges" not in d["new_since_last_diff"] for d in exr.diffs[1:]), [d["k"] for d in exr.diffs])
    except ExecStop as e:
        gate("T39 record mode: the dropped edge is RECORDED and the run CONTINUES to the last op", False, str(e)[:200])
    exr0 = Executor(fin, mkbe(), log=q, record=True)
    exr0.run()
    gate("T39c record mode on a clean run: no diff recorded", exr0.diffs == [] and exr0.cur["k"] == len(opsx), exr0.diffs)
    try:
        Executor(fin, mkbe({"at": 2, "kind": "extra_obj"}), log=q, record=True).run()
        gate("T39d NEGATIVE: record mode does NOT swallow a BINDING stop", False, "ran clean")
    except ExecStop as e:
        gate("T39d NEGATIVE: record mode does NOT swallow a BINDING stop", "BINDING" in str(e), str(e)[:160])
    _selftest_create(gate, tmp, q)
    gate("T14 nothing LabVIEW-side imported",not any(m in sys.modules for m in ("gscript", "win32com", "pythoncom", "stagekit")),
         [m for m in ("gscript", "win32com", "pythoncom", "stagekit") if m in sys.modules])
    n_pass = sum(1 for _l, ok in gates if ok)
    n_fail = len(gates) - n_pass
    first = next((l for l, ok in gates if not ok), None)
    print("=== GATES: {0} pass / {1} fail{2}".format(n_pass, n_fail, "; failing: " + first if first else ""))
    print(protocol.result_line(protocol.make_result(n_pass, n_fail, first)))
    return 0 if n_fail == 0 else 1


PROPOSED_SCHEMA = os.path.join(BENCH, "sim", "disp", "stageplan_schema_proposed.json")


def proposed_schema(on=True):
    """TEST / DIAGNOSTIC ONLY (card 100-3): the installed docs/protocol/stageplan.json has integer-only diagram fields,
    so a plan with 'new:X.body' does not validate until the proposed amendment replaces it. This swaps the IN-PROCESS
    schema cache; simulate/prerun/run in any other process read the installed file. Returns the label of the schema used."""
    p = protocol.schema_path("stageplan/1")
    protocol._SCHEMAS.pop(p, None)
    if not on:
        return "installed"
    inst = protocol.load_schema("stageplan/1")
    if "diagref" in inst.get("definitions", {}) and "gate" in inst["definitions"]["action"]["properties"]["op"]["enum"]:
        return "installed (already amended)"
    protocol._SCHEMAS[p] = _j(PROPOSED_SCHEMA)
    return "PROPOSED " + os.path.relpath(PROPOSED_SCHEMA, ROOT)


def _selftest_create(gate, tmp, q):
    """card 100-3: create executor + symbolic diagrams, on the synthetic graph plus a panel terminal 'Stop' and a
    BooleanConstant #600."""
    def row(t, n, s, w, o, oc, fd, tc="Terminal"):
        return {"term_uid": t, "term_name": n, "is_source": s, "wire_uid": w, "owner_uid": o, "owner_class": oc,
                "frame_diagram": fd, "term_class": tc}
    base = SS._synthetic()
    base["terminals"] += [row(5001, "Stop", True, 0, 10, "Diagram", 10, FP), row(6001, "", True, 0, 600, "BooleanConstant", 10)]
    base["objs"].append({"uid": 600, "class": "BooleanConstant", "pos": [0, 0], "owner": "Diagram"})
    gp = os.path.join(tmp, "graph_cr.json")
    json.dump(base, open(gp, "w", encoding="utf-8"))
    loc = lambda nm, d: {"op": "create", "id": "lr_" + nm, "class": "Local", "diagram": d, "as": nm, "label": "Stop",  # noqa: E731
                         "mode": "read", "pos": [5, 5], "terminals": [{"name": "Stop", "is_source": True}]}
    acts = [{"op": "gate", "id": "g600", "uid": 600, "class": "BooleanConstant", "read": "bool_const", "stop_if": True},
            {"op": "create", "id": "dl", "class": "WhileLoop", "diagram": 10, "as": "DL1", "pos": [0, 0]},
            {"op": "create", "id": "df", "class": "ForLoop", "diagram": "new:DL1.body", "as": "DF1", "pos": [0, 0]},
            {"op": "move_in", "id": "mv4", "nodes": [4], "dest_diagram": "new:DF1.body", "pos": [10, 10]},
            loc("LR1", "new:DL1.body"),
            {"op": "wire", "id": "stop", "src": "new:LR1.value", "dst": "new:DL1.cond"},
            loc("LR2", "new:DL1.body"),
            {"op": "tunnel", "id": "t1", "loop": "new:DF1", "body": "new:DF1.body", "parent": "new:DL1.body", "dir": "in",
             "as": "T1", "indexing": False},
            {"op": "wire", "id": "t1o", "src": "new:LR2.value", "dst": "new:T1.outer"},
            {"op": "wire", "id": "t1i", "src": "new:T1.inner", "dst": "4.y"},
            {"op": "create", "id": "ind", "class": "ControlTerminal", "diagram": 20, "as": "IND1", "label": "plot",
             "indicator": True, "visible": False, "born_on": "2.out"},
            {"op": "create", "id": "cp", "class": "SubVI", "diagram": "new:DL1.body", "as": "CP1", "donor_uid": 4, "pos": [9, 9],
             "terminals": [{"name": "x", "is_source": False}, {"name": "y", "is_source": False}]},
            {"op": "create", "id": "one", "class": "DigitalNumericConstant", "diagram": "new:DL1.body", "as": "ONE1",
             "on": "new:CP1.x", "value": 1}]
    plan = {"schema": "stageplan/1", "stage": "xcr", "context": {"s1_graph": {"path": gp}}, "actions": acts}
    which = proposed_schema(True)
    try:
        ok_v = protocol.validate_obj(plan)
        pp = os.path.join(tmp, "plan_in_xcr.json")
        json.dump(plan, open(pp, "w", encoding="utf-8"))
        md = os.path.join(tmp, "models_cr")
        os.makedirs(md, exist_ok=True)
        S = SS.simulate(pp, gp, out_root=os.path.join(tmp, "sim"), plan_out_dir=tmp, model_dir=md, log=q)
        gate("T36 [{0}] a create plan validates and SIMULATES to the end (loop body symbolic, For inside it, move into "
             "new:DF1.body, locals, cond wire, tunnel across the new border)".format(which),
             ok_v[0] and S["failed"] is None and "new:DL1.body" in S["sym"] and "new:DF1.body" in S["sym"],
             (ok_v, S["failed"]))
        ops = compile_plan(plan)
        got = [(o["kind"], o.get("route")) for o in ops]
        gate("T36b compile: gate / while / for / local_read / stop / tunnel / indicator / copy_in / const_on_term rows each "
             "route to a real op", got == [("gate", None), ("create", "while"), ("create", "for"), ("move_in", None),
                                            ("create", "local_read"), ("stop", None), ("create", "local_read"),
                                            ("tunnel", None), ("create", "indicator"), ("create", "copy_in"),
                                            ("create", "const_on_term")], got)
        fin = os.path.join(tmp, "plan_xcr.json")
        st, ff, ex = dry_run(fin, log=q, model_dir=md, require_final=False)
        bd = ex.bind.get("diag") or {}
        gate("T36c dry run (non-final diagnostic mode): every row routable, both bodies bound to POSITIVE diagram uids, "
             "every created node bound", st == "PASS" and len(bd) == 2 and all(k < 0 < v for k, v in bd.items())
             and len(ex.bind["obj"]) >= 8, (st, str(ff)[:300], bd, len(ex.bind["obj"])))
        rt = dict((r["ids"][0], (r.get("result") or {}).get("check")) for r in ex.report[1:] if r.get("ids"))
        last = ex.step(len(acts))["state"]
        cp_terms = [r["term_uid"] for r in last["terminals"] if r["owner_uid"] == last["sym"]["new:CP1"]]
        ind_t = last["sym"]["new:IND1"]
        gate("T36d the copied SubVI's two sink terminals (same class twice) bind by NAME; the indicator binds as its own "
             "node and was addressed on #2's Nodes[] entry",
             len(cp_terms) == 2 and all(ex.bind["term"].get(t, -1) > 0 for t in cp_terms) and ex.bind["obj"].get(ind_t, -1) > 0
             and (rt.get("ind") or {}).get("route") == "indicator" and (rt.get("ind") or {}).get("resolved_name") == "out",
             (cp_terms, rt.get("ind")))
        negs =(("T37a NEGATIVE: an unknown alias in a diagram field", [{"op": "move_in", "nodes": [4], "dest_diagram": "new:ZZ1.body",
                                                                         "pos": [0, 0]}], "no EARLIER action creates"),
                ("T37b NEGATIVE: use before create", [acts[2], acts[1]], "no EARLIER action creates"),
                ("T37c NEGATIVE: '.body' of a non-loop", [acts[1], acts[4], {"op": "move_in", "nodes": [4],
                                                                             "dest_diagram": "new:LR1.body", "pos": [0, 0]}],
                 "symbolic diagram"),
                ("T37d NEGATIVE: '.cond' of a For loop", [acts[1], acts[2], dict(acts[4], diagram="new:DF1.body"),
                                                          {"op": "wire", "src": "new:LR1.value", "dst": "new:DF1.cond"}],
                 "only a WhileLoop"))
        for lab_, aa, want in negs:
            try:
                compile_plan({"actions": aa})
                gate(lab_ + " is refused by compile_plan", False, "compiled")
            except ExecStop as e:
                gate(lab_ + " is refused by compile_plan", want in str(e), str(e)[:160])
        bad = dict(plan, stage="xcrbad", actions=acts[:2] + [{"op": "create", "id": "ind2", "class": "ControlTerminal",
                                                               "diagram": 20, "as": "IND2", "label": "p2", "indicator": True,
                                                               "born_on": {"uid": 60, "term_uid": 1602}}])
        pb = os.path.join(tmp, "plan_in_xcrbad.json")
        json.dump(bad, open(pb, "w", encoding="utf-8"))
        SS.simulate(pb, gp, out_root=os.path.join(tmp, "sim"), plan_out_dir=tmp, model_dir=md, log=q)
        st2, ff2, _ex2 = dry_run(os.path.join(tmp, "plan_xcrbad.json"), log=q, model_dir=md, require_final=False)
        gate("T38 NEGATIVE: an indicator born on a LoopTunnel face is UNROUTABLE (create_indicator_nested finds Nodes only)",
             st2 == "FAIL" and "UNROUTABLE 1" in str(ff2) and "not a Node" in str(ff2), str(ff2)[:200])
        okf = dict(plan, stage="xcrface", actions=acts[:2] + [{"op": "create", "id": "ind3", "class": "ControlTerminal",
                                                                "diagram": 10, "as": "IND3", "label": "p3", "indicator": True,
                                                                "born_on": {"uid": 61, "term_uid": 1612}}])
        pf3 = os.path.join(tmp, "plan_in_xcrface.json")
        json.dump(okf, open(pf3, "w", encoding="utf-8"))
        SS.simulate(pf3, gp, out_root=os.path.join(tmp, "sim"), plan_out_dir=tmp, model_dir=md, log=q)
        st3, ff3, ex3 = dry_run(os.path.join(tmp, "plan_xcrface.json"), log=q, model_dir=md, require_final=False)
        rt3 = dict((r["ids"][0], (r.get("result") or {}).get("check")) for r in ex3.report[1:] if r.get("ids"))
        gate("T38d card 100-6: an indicator born on a LoopTunnel OUTER SOURCE face (#1612 of #61, on its diagram) ROUTES "
             "as create_indicator_nested(W, face, None)", st3 == "PASS" and (rt3.get("ind3") or {}).get("tunnel_face") == 1612,
             (st3, str(ff3)[:200], rt3.get("ind3")))
        gate("T38e NEGATIVE: tunnel_outer_face refuses the inner face #1602, the sink outer face #1601, and #1612 on a "
             "diagram it does not sit on", tunnel_outer_face(base["terminals"], 1602, 20) is None
             and tunnel_outer_face(base["terminals"], 1601, 10) is None and tunnel_outer_face(base["terminals"], 1612, 20) is None
             and tunnel_outer_face(base["terminals"], 1612, 10) is not None)
        g_, okp = prerun_plan(fin, log=q, model_dir=md)
        gate("T38b prerun_plan still REFUSES the non-final create plan (the diagnostic mode is not a launch gate)",
             not okp and "not final" in g_[0][2], g_[0])
        ROUTE_VERBS["zz"] = [("gscript", "nope_verb_c100")]
        mz = verbs_missing("zz")
        ROUTE_VERBS.pop("zz", None)
        gate("T38c verbs_missing reads the source text: loop_in present, a made-up verb absent (NEGATIVE)",
             not verbs_missing("while") and mz == ["gscript.nope_verb_c100"], (verbs_missing("while"), mz))
    finally:
        proposed_schema(False)


def main(argv):
    if len(argv) >= 2 and argv[1] == "selftest":
        return selftest()
    if len(argv) >= 3 and argv[1] in ("dry", "prerun", "run"):
        plan = os.path.abspath(argv[2])
        if argv[1] == "dry":
            st, ff, ex = dry_run(plan, require_final="--nonfinal" not in argv)
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
