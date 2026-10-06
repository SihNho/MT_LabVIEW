# ---
# labview: none
# hardware: none
# ---
"""card chat-F2 self-test - standard outcome + postconditions (part 1), per-function test records + advisory gate
(part 2), generated capability table + drift (part 3).

OFFLINE BY CONSTRUCTION: gscript and stagekit are NOT imported. The functions under test are taken from their SOURCE
(ast, `load_defs`) - gscript's delete_object / term_index / count / _run / _deadline_call / _check_poison /
wire_remove_loose_ends, stagekit's Stage._op / safe / delete_object / delete_wire, the recipe's del_node / del_wire - and
executed in a namespace whose `pythoncom` is an inert stub and whose op / uids / report_all are fakes. The real code
runs; nothing in the process can create a COM object. (An earlier version imported stagekit with COM stubbed in
sys.modules; the launch classifier stage_prerun.is_vi_modifying refused it as a VI-modifying stage - logged as gate
false positive fp-41 - so this version imports neither module.)

PREDICTION (every gate PASS):
  P1 a double delete is caught AT THE CALL: gscript.delete_object removed 0 -> PostconditionFailed (old message first,
     outcome no_output); Stage.delete_object / delete_wire twice over the real del_node / del_wire -> the 2nd op record has
     err PostconditionFailed and outcome no_output.
  P2 a terminal lookup matching 2 rows -> PostconditionValueError (a ValueError), outcome failed; 0 rows -> no_output.
  P3 standard outcome on timeout: the real _run with a blocking fake Invoke and a 0.2 s cap -> timed_out; the next call
     (COMPoisoned) -> timed_out in Stage._op's record.
  P4 behaviour unchanged on success (wrapped == original return value, outcome ok); a `record` postcondition
     (wire_remove_loose_ends broken_after) does not raise but the op record carries outcome failed.
  P5 a record goes STALE when the function's source changes; a record without a plan is refused.
  P6 the advisory gate logs `FN-GATE ADVISORY` and allows; mode refuse refuses; auto switch when the condition is met;
     the real config is advisory with the switch condition stated; stage_prerun.fn_record_gate allows; every function
     the P4 v18 plan uses has a written test plan.
  P7 the generator is idempotent and leaves the prose above the block byte-identical; the real doc has no drift.
  P8 the drift report names a missing row, a gone row and a stale record; doc_lint L12 reports it as WARN.
  P9 table coverage complete; gscript.py ends by installing the wrappers; install is idempotent and keeps signatures;
     Stage.delete_object / delete_wire carry their declared checks (AST).
  P10 (card chat-F3b) gscript.loop_in's PRECONDITION at the call: measured only when the call raised (a success reads
     nothing extra); 0 SubVI -> PreconditionFailed (a RuntimeError, the 1055 text first, outcome failed); 1 SubVI -> the
     original RuntimeError unchanged; install hands the module namespace to the wrapper.
"""
import ast
import functools
import inspect
import json
import os
import shutil
import sys
import tempfile
import threading
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
for _p in (TOOLS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import protocol                                                                    # noqa: E402
import fncontract as FC                                                            # noqa: E402
import fn_records as FR                                                            # noqa: E402
import gen_capabilities as GC                                                      # noqa: E402

GSCRIPT = os.path.join(TOOLS, "gscript.py")
STAGEKIT = os.path.join(TOOLS, "stagekit.py")
RECIPE = os.path.join(TOOLS, "recipes", "build_opfsinnertunnelconnect_v0.py")
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok), str(detail)[:300]))
    print("  %s  %s%s" % ("PASS" if ok else "FAIL", label, ("  | " + str(detail)[:300]) if not ok else ""), flush=True)


def load_defs(path, names, ns, cls=None):
    """Compile the named top-level defs/classes (or methods of class `cls`) of `path` into `ns` - their real source."""
    t = ast.parse(open(path, encoding="utf-8").read(), filename=path)
    body = t.body
    if cls:
        body = next(n for n in t.body if isinstance(n, ast.ClassDef) and n.name == cls).body
    got = [n for n in body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    exec(compile(ast.Module(body=got, type_ignores=[]), path, "exec"), ns)
    missing = set(names) - set(n.name for n in got)
    if missing:
        raise KeyError("not found in %s: %s" % (path, sorted(missing)))
    return ns


# ---- an inert pythoncom (the exec'd _run marshals through it; Invoke goes to the fake op VI) ------------------------
STUB_PC = types.SimpleNamespace(IID_IDispatch=None, DISPATCH_METHOD=1, CoInitialize=lambda *a: None,
                                CoUninitialize=lambda *a: None,
                                CoMarshalInterThreadInterfaceInStream=lambda iid, ole: ole,
                                CoGetInterfaceAndReleaseStream=lambda stream, iid: stream)


class FakeVI(object):
    def __init__(self, values=None, block_s=0.0):
        self.values, self.block_s = dict(values or {}), block_s
        vi = self

        class _Ole(object):
            def GetIDsOfNames(self, *a):
                return 1

            def Invoke(self, *a):
                if vi.block_s:
                    time.sleep(vi.block_s)
        self._oleobj_ = _Ole()

    def SetControlValue(self, k, v):
        pass

    def GetControlValue(self, k):
        return self.values.get(k, 0)


def gscript_ns():
    """The real gscript functions under test, in a namespace with stubbed COM and fakes for everything they reach."""
    ns = {"_fc": FC, "os": os, "sys": sys, "time": time, "json": json, "threading": threading, "pythoncom": STUB_PC,
          "_poison": None, "SHOT_DIR": tempfile.gettempdir(), "OP_DELETE": "OpDelete", "OP_REPORT": "OpReport",
          "CLAUDEDEV": "C:\\fake", "C126_LABELS": os.path.join(TOOLS, "bench", "diag_c126_4_oplabels.json"),
          "_lv_gui": lambda *a: "VERDICT: OK", "ensure_loaded": lambda t: None, "_recover_poison": lambda: None}
    load_defs(GSCRIPT, ["COMPoisoned", "clear_poison", "_set_poison", "_check_poison", "_deadline_call", "_run",
                        "delete_object", "term_index", "count", "wire_remove_loose_ends", "_set_common"], ns)
    return ns


def stage_cls(mod_fn):
    """A Stage built from stagekit's REAL _op / safe / delete_object / delete_wire source, everything else faked."""
    ns = {"_fc": FC, "time": time, "mod": mod_fn}
    load_defs(STAGEKIT, ["_op", "safe", "delete_object", "delete_wire"], ns, cls="Stage")
    attrs = dict((n, ns[n]) for n in ("_op", "safe", "delete_object", "delete_wire"))
    attrs.update(_rowcheck=lambda self: None, node_mark=lambda self, tag="": None, fact=lambda self, line: None)
    st = type("FakeStage", (object,), attrs)()
    st.work, st.R, st.name, st._nodes = "W.vi", {"ops": []}, "selftest", None
    return st


# ============================================================ P1 double delete caught at the call
def p1():
    ns = gscript_ns()
    ns["op"] = lambda p: FakeVI()
    ns["_run"] = lambda vi, **k: 0.0
    ns["_err"] = lambda vi, name="error out": None
    snaps = [{1, 2, 3}, {1, 2}]
    ns["uids"] = lambda t, c: snaps.pop(0)
    dobj = FC.contract("gscript.delete_object", ns["delete_object"])
    m = FC.mark()
    gone = dobj("T.vi", "Function", 2)
    gate("P1a gscript.delete_object removed 1 -> the gone set, outcome ok", gone == {3} and
         FC.since(m)[-1]["outcome"] == "ok", gone)
    ns["uids"] = lambda t, c: {1, 2}
    try:
        dobj("T.vi", "Function", 2)
        gate("P1b gscript.delete_object removed 0 raises at the call", False, "no exception")
    except FC.PostconditionFailed as e:
        oc = e.outcome
        gate("P1b gscript.delete_object removed 0 -> PostconditionFailed (a RuntimeError) at the call, outcome no_output, "
             "measured removed 0, the old message first", isinstance(e, RuntimeError) and oc["outcome"] == "no_output"
             and oc["measured"].get("removed") == 0 and str(e).startswith(
                 "delete_object(Function[2]): expected 1 object gone, got 0"), str(e))
    graph = {"Function": [10, 11, 12], "Wire": [20, 21]}
    rns = {"fact": lambda line: None, "print": lambda *a, **k: None,
           "g": types.SimpleNamespace(report_all=lambda tg, cls: [{"uid": u} for u in graph[cls]],
                                      uids=lambda tg, cls: set(graph[cls]),
                                      delete_object=lambda tg, cls, idx, verify=True: graph[cls].pop(idx))}
    load_defs(RECIPE, ["del_node", "del_wire"], rns)
    c82 = types.SimpleNamespace(del_node=rns["del_node"], del_wire=rns["del_wire"])
    st = stage_cls(lambda name: c82)
    r1 = st.delete_object("Function", 11)
    r2 = st.delete_object("Function", 11)
    gate("P1c Stage.delete_object #11 first call: err '', outcome ok, the uid removed", not r1["err"] and
         r1["outcome"]["outcome"] == "ok" and 11 not in graph["Function"], r1)
    gate("P1d Stage.delete_object #11 AGAIN (double delete) fails AT THE CALL: op err PostconditionFailed, outcome "
         "no_output, measured removed 0", "PostconditionFailed" in r2["err"] and r2["outcome"]["outcome"] ==
         "no_output" and r2["outcome"]["measured"].get("removed") == 0, r2)
    w1, w2 = st.delete_wire(21), st.delete_wire(21)
    gate("P1e Stage.delete_wire w21 twice: 1st ok, 2nd op err + outcome no_output (found 0)", not w1["err"] and
         w1["outcome"]["outcome"] == "ok" and "PostconditionFailed" in w2["err"] and
         w2["outcome"]["outcome"] == "no_output", (w1, w2))


# ============================================================ P2 terminal lookup with 2 / 0 matches
def p2():
    ns = gscript_ns()
    ns["_uid_index"] = lambda t, c, u: 0
    ns["_node_index"] = lambda t, d, u: 0
    two = [{"name": "element", "is_source": False, "i": 1}, {"name": "element", "is_source": False, "i": 2}]
    ns["node_terms_uids"] = lambda t, d, n: (77, two)
    ti = FC.contract("gscript.term_index", ns["term_index"])
    try:
        ti("T.vi", 5, 77, "element", False)
        gate("P2a term_index 2 matches raises", False, "no exception")
    except ValueError as e:
        oc = getattr(e, "outcome", {})
        gate("P2a term_index with 2 matching rows -> PostconditionValueError (a ValueError) at the call, outcome failed, "
             "measured matches 2", isinstance(e, FC.PostconditionValueError) and oc.get("outcome") == "failed" and
             oc["measured"].get("matches") == 2 and str(e).startswith("term_index: node echo 77"), str(e))
    ns["node_terms_uids"] = lambda t, d, n: (77, [])
    try:
        ti("T.vi", 5, 77, "element", False)
        gate("P2b term_index 0 matches raises", False, "no exception")
    except ValueError as e:
        gate("P2b term_index with 0 rows -> outcome no_output", e.outcome["outcome"] == "no_output", e.outcome)
    ns["node_terms_uids"] = lambda t, d, n: (78, two[:1])
    try:
        ti("T.vi", 5, 77, "element", False)
        gate("P2c node echo mismatch raises", False, "no exception")
    except ValueError as e:
        gate("P2c one row but the node echo differs -> outcome failed (node_echo)", e.outcome["outcome"] == "failed" and
             "node_echo" in e.outcome["reason"], e.outcome)
    ns["node_terms_uids"] = lambda t, d, n: (77, two[:1])
    r = ti("T.vi", 5, 77, "element", False)
    gate("P2d exactly 1 row -> (di, ni, i, row) unchanged", r == (0, 0, 1, two[0]), r)


# ============================================================ P3 timed_out
def p3():
    ns = gscript_ns()
    ns["op"] = lambda p: FakeVI(block_s=1.0)
    ns["_err"] = lambda vi, name="error out": None
    real_run = ns["_run"]
    ns["_run"] = functools.partial(real_run, hard_timeout_s=0.2)
    cnt = FC.contract("gscript.count", ns["count"])
    try:
        cnt("T.vi", "Wire")
        gate("P3a count under a blocking Invoke raises", False, "no exception")
    except RuntimeError as e:
        gate("P3a the REAL _run times out (0.2 s cap) -> the wrapped count's outcome timed_out, module poisoned",
             getattr(e, "outcome", {}).get("outcome") == "timed_out" and ns["_poison"] is not None, str(e)[:160])
    st = stage_cls(lambda name: None)
    rec = st._op("count_probe", lambda: cnt("T.vi", "Wire"))
    gate("P3b next call while poisoned (COMPoisoned) -> Stage._op record outcome timed_out", rec["outcome"]["outcome"]
         == "timed_out" and "COMPoisoned" in rec["err"], rec)
    th = (ns["_poison"] or {}).get("thread")
    if th is not None:
        th.join(3)
    gate("P3c classify: watchdog text and COMPoisoned -> timed_out, anything else -> failed",
         FC.classify_exception(RuntimeError("COM Run did not return within 3s")) == "timed_out" and
         FC.classify_exception(ns["COMPoisoned"]("x")) == "timed_out" and FC.classify_exception(KeyError("k")) == "failed")


# ============================================================ P4 behaviour unchanged on success; record mode
def p4():
    ns = gscript_ns()
    ns["_run"] = lambda vi, **k: 0.0
    ns["_err"] = lambda vi, name="error out": None
    ns["op"] = lambda p: FakeVI({"# of Refs": 7})
    cnt = FC.contract("gscript.count", ns["count"])
    m = FC.mark()
    a, b = cnt("T.vi", "Wire"), cnt.__wrapped__("T.vi", "Wire")
    gate("P4a wrapped count returns exactly the original's value; outcome ok recorded", a == b == 7 and
         [o["outcome"] for o in FC.since(m) if o["fn"] == "gscript.count"] == ["ok"], (a, b))
    lab = json.load(open(ns["C126_LABELS"], encoding="utf-8"))["OpWireRemoveLooseEnds_v0"]
    ns["op"] = lambda p: FakeVI({lab["UID"]: 31, lab["before"]: True, lab["after"]: True})
    rle = FC.contract("gscript.wire_remove_loose_ends", ns["wire_remove_loose_ends"])
    st = stage_cls(lambda name: None)
    rec = st._op("wire_remove_loose_ends", lambda: rle("T.vi", 31, index=0))
    gate("P4b record-mode postcondition (broken_after) does NOT raise: same dict returned, err '' - the op record "
         "carries outcome failed with measured broken_after 1", not rec["err"] and rec["result"]["broken_after"] is True
         and rec["outcome"]["outcome"] == "failed" and rec["outcome"]["measured"].get("broken_after") == 1, rec)
    ext = FC._EXTRACT["gscript.connect_term_uid"]({"wire_uid": 0}, ("T", 5, 6), {})
    try:
        FC.check("gscript.connect_term_uid", "connect_term_uid returned wire_uid 0;", **ext)
        gate("P4c connect_term_uid wire_uid 0 raises", False, "no exception")
    except FC.PostconditionFailed as e:
        gate("P4c connect_term_uid returning wire_uid 0 -> PostconditionFailed, outcome no_output (row on_fail raise)",
             e.outcome["outcome"] == "no_output" and e.outcome["measured"] == {"new_wire": 0}, str(e)[:160])


# ============================================================ P5 stale after a source change
def p5(tmp):
    reg = os.path.join(tmp, "reg")
    fake = os.path.join(tmp, "gscript.py")
    shutil.copy(FC.GSCRIPT, fake)
    real = FC.GSCRIPT
    FC.GSCRIPT = fake
    try:
        FR.write_record(FR.make_plan("gscript.delete_object"), reg)
        FR.add_record("gscript.delete_object", "PASS", os.path.join(tmp, "x.log"), card="selftest", reg_dir=reg)
        s1 = FR.status("gscript.delete_object", reg)[0]
        body = open(fake, encoding="utf-8").read()
        body = body.replace("    before = uids(target, cls) if verify else None",
                            "    before = uids(target, cls) if verify else None\n    _probe = 1", 1)
        time.sleep(0.05)
        with open(fake, "w", encoding="utf-8") as f:
            f.write(body)
        s2 = FR.status("gscript.delete_object", reg)[0]
        s3 = FR.status("gscript.count", reg)[0]
        gate("P5a record fresh-pass, then STALE after the function's body changed; another function unaffected",
             (s1, s2, s3) == ("fresh-pass", "stale", "none"), (s1, s2, s3))
        try:
            FR.add_record("gscript.count", "PASS", None, reg_dir=reg)
            gate("P5b a record without a plan is refused (plan first)", False, "accepted")
        except ValueError:
            gate("P5b a record without a plan is refused (plan first)", True)
    finally:
        FC.GSCRIPT = real


# ============================================================ P6 the advisory gate
def p6(tmp):
    reg = os.path.join(tmp, "reg6")
    log = os.path.join(tmp, "fn_gate.log")
    cfg = os.path.join(tmp, "cfg.json")
    plan = "tools/bench/plan_ring_p4_s03v18.json"
    json.dump(FR.DEFAULT_CONFIG, open(cfg, "w", encoding="utf-8"))
    ok, line = FR.launch_gate(plan, cfg_path=cfg, reg_dir=reg, log_path=log, now="T0")
    txt = open(log, encoding="utf-8").read()
    gate("P6a advisory: allowed, ONE `FN-GATE ADVISORY` line logged naming the unit and the missing functions",
         ok and line.startswith("FN-GATE ADVISORY | %s |" % plan) and txt.count("FN-GATE ADVISORY") == 1 and
         "switch condition not met" in line, line[:200])
    json.dump(dict(FR.DEFAULT_CONFIG, mode="refuse"), open(cfg, "w", encoding="utf-8"))
    ok2, why = FR.launch_gate(plan, cfg_path=cfg, reg_dir=reg, log_path=log)
    gate("P6b mode refuse: refused with the record-gate text", not ok2 and "FN-RECORD GATE" in why, why[:160])
    fns = FR.functions_for_unit(plan)
    for fn in fns:
        FR.write_record(FR.make_plan(fn), reg)
        FR.add_record(fn, "PASS", None, reg_dir=reg)
    sw = dict(FR.DEFAULT_CONFIG, switch=dict(FR.DEFAULT_CONFIG["switch"], auto=True, required_from=[plan]))
    json.dump(sw, open(cfg, "w", encoding="utf-8"))
    ok3, line3 = FR.launch_gate(plan, cfg_path=cfg, reg_dir=reg, log_path=log)
    gate("P6c auto switch: condition MET -> mode REFUSE, nothing missing -> allowed", ok3 and line3.startswith(
        "FN-GATE REFUSE") and "switch condition MET" in line3 and "| 0 of %d" % len(fns) in line3, line3[:200])
    real = json.load(open(FR.GATE_CONFIG, encoding="utf-8"))
    rf = real["switch"]["required_from"]
    met_real, _miss = FR.switch_condition(real)
    # card chat-F3b: required_from = the P4 v18 plan + the existing session plans from s03v18 on (chat decision 2026-10-07
    # (2) to card chat-F3, gate_config required_from_why); mode is 'advisory' until the switch condition is MET, then the
    # judgement may set 'refuse' - the self-test checks that rule, not one frozen value
    gate("P6d the real config states the switch rule: auto false, required_from = plan_ring_p4_v18 + plan_ring_p4_s03v18 "
         "(chat decision 2026-10-07 (2)), every listed plan on disk; mode advisory, or refuse only with the condition MET",
         real["switch"]["auto"] is False and rf[:2] == [FR.P4_PLANS[0], FR.P4_PLANS[2]] and
         all(os.path.isfile(os.path.join(ROOT, p)) for p in rf) and "fresh pass" in real["switch"]["when"].lower() and
         (real["mode"] == "advisory" or (real["mode"] == "refuse" and met_real)), (real["mode"], rf, met_real))
    import stage_prerun as SP
    real_log = FR.GATE_LOG
    FR.GATE_LOG = os.path.join(tmp, "fn_gate_sp.log")
    try:
        r = SP.fn_record_gate(plan)
        n1 = open(FR.GATE_LOG, encoding="utf-8").read().count("FN-GATE ADVISORY")
    finally:
        FR.GATE_LOG = real_log
    gate("P6e stage_prerun.fn_record_gate (the launch gate's hook point) allows and logs one ADVISORY line",
         r == (True, "") and n1 == 1, (r, n1))
    p4fns = FR.functions_for_unit("tools/bench/plan_ring_p4_v18.json")
    missing_plans = [f for f in p4fns if FR.status(f)[0] == "none"]
    gate("P6f every function the P4 v18 plan uses (%d) has a written test plan in tools/bench/fn_records" % len(p4fns),
         not missing_plans, missing_plans)


# ============================================================ P7 / P8 generator and drift
def p78(tmp):
    doc = os.path.join(tmp, "tc.md")
    full = open(GC.DOC, encoding="utf-8", newline="").read()
    before, block, _after = GC.split(full)
    with open(doc, "w", encoding="utf-8", newline="") as f:
        f.write(before.rstrip("\n") + "\n")
    w1 = GC.write(doc)
    t1 = open(doc, encoding="utf-8", newline="").read()
    w2 = GC.write(doc)
    t2 = open(doc, encoding="utf-8", newline="").read()
    gate("P7a generator: appends once, second run is a no-op, prose before the block byte-identical", w1 and not w2 and
         t1 == t2 and t1.startswith(before.rstrip("\n") + "\n") and t1.count(GC.BEGIN) == 1, (w1, w2))
    d0 = GC.drift_line(GC.drift())
    gate("P7b the real doc's block is current (generated, no drift)", block is not None and not d0, d0)
    lines = t2.splitlines(True)
    drop = next(i for i, ln in enumerate(lines) if ln.startswith("| `gscript.delete_object`"))
    lines[drop] = "| `gscript.no_such_function` | target | none - x | none | tools/gscript.py:1 |\n"
    with open(doc, "w", encoding="utf-8", newline="") as f:
        f.write("".join(lines))
    reg = os.path.join(tmp, "reg8")
    FR.write_record(FR.make_plan("gscript.count"), reg)
    FR.add_record("gscript.count", "PASS", None, reg_dir=reg, md5_now="0" * 32)
    d = GC.drift(doc, reg)
    gate("P8a drift names the function missing from the block, the block row whose function is gone, the STALE record",
         d["missing"] == ["gscript.delete_object"] and d["gone"] == ["gscript.no_such_function"] and
         d["stale"] == ["gscript.count"] and bool(GC.drift_line(d)), GC.drift_line(d))
    import doc_lint as DL
    del DL.RESULT[:]
    DL.check_fn_drift(doc)
    gate("P8b doc_lint L12 reports the drift as WARN", DL.RESULT and DL.RESULT[-1][0] == "WARN" and
         "missing 1" in DL.RESULT[-1][2], DL.RESULT[-1:])


# ============================================================ P9 coverage and wiring
def p9():
    c = FC.coverage()
    gate("P9a table coverage: every LabVIEW-touching gscript function and Stage._op verb has a row; no orphan; every "
         "`none` row gives a reason", not any(c.values()), c)
    src = open(GSCRIPT, encoding="utf-8").read()
    t = ast.parse(src)
    last = [n for n in t.body if not isinstance(n, (ast.FunctionDef, ast.ClassDef))][-1]
    gate("P9b gscript.py's last statement installs the wrappers: FNCONTRACT_WRAPPED = _fc.install(globals(), 'gscript')",
         "FNCONTRACT_WRAPPED = _fc.install(globals(), \"gscript\")" == ast.get_source_segment(src, last),
         ast.get_source_segment(src, last))
    ns = gscript_ns()
    names = ["delete_object", "term_index", "count", "wire_remove_loose_ends"]
    sig0 = dict((n, inspect.signature(ns[n])) for n in names)
    w = FC.install(ns, "gscript")
    gate("P9c install wraps the table's rows, keeps __wrapped__ and signatures, and is idempotent",
         set(names) <= set(w) and all(inspect.signature(ns[n]) == sig0[n] and hasattr(ns[n], "__wrapped__")
                                      for n in names) and FC.install(ns, "gscript") == [], w)
    sk = open(STAGEKIT, encoding="utf-8").read()
    gate("P9d Stage.delete_object / delete_wire call the declared checks (removed / found)",
         '_fc.check("stagekit.op:delete_object"' in sk and "removed=1 if ok else 0" in sk and
         '_fc.check("stagekit.op:delete_wire"' in sk and "found=1 if ok else 0" in sk)


# ============================================================ P10 precondition at the call (card chat-F3b)
def p10():
    """gscript.loop_in's REAL source with fakes: PRE measured only when the call raised; a violated precondition ->
    PreconditionFailed (a RuntimeError, original text first, outcome failed); a held one -> the original exception."""
    st = {"err": "", "after": {77}, "n": 0, "counts": []}
    ns = {"_fc": FC, "os": os, "json": json, "__file__": GSCRIPT, "_LOOPIN_LABELS": {}, "CLAUDEDEV": "C:\\fake",
          "op": lambda p: FakeVI({}), "_run": lambda vi, **k: 0.0, "_err": lambda vi, name="error out": st["err"],
          "uids": lambda t, c: set() if st.get("before") is None else st["before"],
          "count": lambda t, c: st["counts"].append((t, c)) or st["n"]}
    load_defs(GSCRIPT, ["loop_in"], ns)
    seq = {"k": 0}

    def uids(t, c):                                     # before = {}, after = st["after"] (one call each per loop_in)
        seq["k"] += 1
        return set() if seq["k"] % 2 == 1 else set(st["after"])
    ns["uids"] = uids
    w = FC.contract("gscript.loop_in", ns["loop_in"], ns)
    m = FC.mark()
    r = w("while", "T.vi", 0, (40, 40))
    gate("P10a success: returns the new loop uid, NO precondition read (count not called), outcome ok",
         r == 77 and st["counts"] == [] and [o["outcome"] for o in FC.since(m) if o["fn"] == "gscript.loop_in"] == ["ok"],
         (r, st["counts"]))
    st.update(err="error 1055: To More Specific Class in OpWhileLoopIn_v0.vi", after=set(), n=0)
    try:
        w("while", "T.vi", 0, (40, 40))
        gate("P10b no SubVI -> PreconditionFailed", False, "no exception")
    except FC.PreconditionFailed as e:
        gate("P10b no SubVI: PreconditionFailed (a RuntimeError), original 1055 text FIRST, reason src_present 0, outcome "
             "failed, count('T.vi','SubVI') read once", isinstance(e, RuntimeError) and
             str(e).startswith("RuntimeError: loop_in(while): error 1055") and "src_present == 1, measured 0" in str(e)
             and "drop a SubVI" in str(e) and e.outcome["outcome"] == "failed" and st["counts"] == [("T.vi", "SubVI")],
             str(e)[:200])
    st.update(n=1, counts=[])
    try:
        w("while", "T.vi", 0, (40, 40))
        gate("P10c SubVI present -> the original error", False, "no exception")
    except Exception as e:                                                         # noqa: BLE001
        gate("P10c precondition HOLDS (1 SubVI): the ORIGINAL RuntimeError unchanged, not PreconditionFailed",
             type(e) is RuntimeError and str(e).startswith("loop_in(while): error 1055") and
             st["counts"] == [("T.vi", "SubVI")], "%s: %s" % (type(e).__name__, str(e)[:160]))
    st.update(n=2, counts=[])
    try:
        w("while", "T.vi", 0, (40, 40), src_cls="WhileLoop", src_index=2)
        gate("P10d explicit src_cls/index -> PreconditionFailed", False, "no exception")
    except FC.PreconditionFailed as e:
        gate("P10d explicit src_cls 'WhileLoop' index 2 with 2 present -> PreconditionFailed (needs > index)",
             e.outcome["measured"].get("src_cls") == "WhileLoop" and st["counts"] == [("T.vi", "WhileLoop")], str(e)[:160])
    ns2 = {"loop_in": lambda *a, **k: (_ for _ in ()).throw(RuntimeError("loop_in(while): error 1055")),
           "count": lambda t, c: 0}
    FC.install(ns2, "gscript")
    try:
        ns2["loop_in"]("while", "T.vi", 0, (1, 1))
        ok = False
    except FC.PreconditionFailed:
        ok = True
    except Exception:                                                              # noqa: BLE001
        ok = False
    gate("P10e install passes the module namespace (a wrapped loop_in measures through its own module's count); "
         "describe names the PRE", ok and "PRE src_present == 1" in FC.describe("gscript.loop_in"),
         FC.describe("gscript.loop_in")[-120:])


def main():
    tmp = tempfile.mkdtemp(prefix="fnf2_")
    try:
        for f in (p1, p2, p3, p4, p9, p10):
            try:
                f()
            except Exception as e:                                                 # noqa: BLE001
                gate("%s raised" % f.__name__, False, "%s: %s" % (type(e).__name__, e))
        for f in (p5, p6, p78):
            try:
                f(tmp)
            except Exception as e:                                                 # noqa: BLE001
                gate("%s raised" % f.__name__, False, "%s: %s" % (type(e).__name__, e))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    bad = [g_ for g_ in gates if not g_[1]]
    print("=== %d pass / %d fail" % (len(gates) - len(bad), len(bad)), flush=True)
    print(protocol.result_line(protocol.make_result(len(gates) - len(bad), len(bad),
                                                    bad[0][0] if bad else None, [])), flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
