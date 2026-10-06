# ---
# labview: none
# hardware: none
# ---
"""fn_records.py - per-function TEST PLANS written before the test, per-function RESULT RECORDS from a real LabVIEW run,
and the launch-time ADVISORY gate "this stage calls a function with no fresh PASS record" (card chat-F2 part 2, user
2026-10-06 "1~3번 모두 적용하도록 하자"; purpose: catch errors at the START).

EXISTING FIRST (checked): `tools/bench/scratch_verify/*.json` already holds ad-hoc scratch-VI records (48 files, chat-N4
SCRATCH-VI GATE reads them by function name, stage_prerun.check_scratch). They carry no source md5, so they cannot be
"fresh" under this card's rule; they are FOLDED IN as `legacy_evidence` of the matching function and cited, never
counted as a fresh PASS. stage_prerun.check_launch is the one launch gate (guard_bash calls it); the advisory sits there.

REGISTRY  tools/bench/fn_records/<function>.json  (':' -> '_'), schema `fnrec/1`:
  {"schema": "fnrec/1", "function": "gscript.delete_object",
   "source": {"file": "tools/gscript.py", "defs": ["delete_object"], "line": 2810, "md5": "<md5 of the def's source>"},
   "plan": {"written": iso, "card": "chat-F2", "bed": ..., "inputs": [...], "predicted": {...}, "pass_if": ...},
   "records": [{"status": "PASS|FAIL", "date": iso, "labview": "2026 ...", "log": path, "src_md5": md5, "card": id}],
   "legacy_evidence": [{"file", "status", "card", "log"}]}
  The plan is written BEFORE the test (this card); `records` are appended by the real-LabVIEW run (card chat-F3) through
  `add_record()`. A record is FRESH only while its src_md5 equals the function's CURRENT source md5 (`source_md5`): any
  edit of the function's body makes it STALE.

GATE  `launch_gate(unit)` (unit = a stage script or a stageplan JSON): the functions the unit uses (`functions_for_unit`:
  the plan's route_check routes -> ROUTE_FUNCS, plus direct g./gscript. calls and Stage verbs in a script, plus the base
  set every stagexec run uses) minus those with a fresh PASS record -> ONE line `FN-GATE <mode> | ...` appended to
  tools/bench/fn_gate.log. MODE: tools/bench/fn_records/gate_config.json. In this card it is `advisory` (logged, never
  refuses). THE SWITCH CONDITION (stated in the config and evaluated here, `switch_condition()`): every function used by
  the plans listed in `switch.required_from` has a fresh PASS record (card chat-F3 runs them). With `switch.auto` false
  (this card) the line says `switch condition MET` and a judgement session flips `mode` to `refuse`; with `auto` true the
  gate refuses by itself once the condition is met.

CLI: --write-plans | --status [fn...] | --advise <unit> | --add-record <fn> PASS|FAIL --log <path> [--labview v] [--card id]
Self-test: tools/bench/selftest_fn_f2.py.
"""
import argparse
import ast
import datetime
import glob
import hashlib
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import fncontract as FC                                                            # noqa: E402

REG_DIR = os.path.join(HERE, "bench", "fn_records")
GATE_CONFIG = os.path.join(REG_DIR, "gate_config.json")
GATE_LOG = os.path.join(HERE, "bench", "fn_gate.log")
SCRATCH_DIR = os.path.join(HERE, "bench", "scratch_verify")
RECIPES = os.path.join(HERE, "recipes")
P4_PLANS = ("tools/bench/plan_ring_p4_v18.json", "tools/bench/plan_ring_p4_s02v18.json",
            "tools/bench/plan_ring_p4_s03v18.json")
DEFAULT_CONFIG = {
    "schema": "fn-gate-config/1", "mode": "advisory",
    "switch": {"to": "refuse", "auto": False, "required_from": list(P4_PLANS),
               "when": "every function used by the plans in required_from has a FRESH PASS record (src_md5 == the "
                       "function's current source md5) - card chat-F3 runs them on scratch VIs; until then the gate "
                       "only logs. auto false: a judgement session flips mode to 'refuse' when the line says MET."},
    "set_by": "card chat-F2 2026-10-06 (user: '1~3번 모두 적용하도록 하자'; brief: advisory until chat-F3)"}

# ---------------------------------------------------------------------------------------------- where a function lives
# Recipe-module functions the stagekit/stagexec paths call through `mod(...)` (stagekit.py Stage methods,
# stagexec.LVBackend._cfw / connect). Qualname 'recipes.<module>.<def>'.
RECIPE_FUNCS = ("recipes.build_opfsinnertunnelconnect_v0.del_node", "recipes.build_opfsinnertunnelconnect_v0.del_wire",
                "recipes.build_opconnectnested_v1.connect_nested_v1",
                "recipes.build_opconnectfromwire_v0.connect_from_wire", "recipes.build_d1_v0.move_in")

# The functions EVERY stagexec LabVIEW run reads through (Stage reads, the executor's live reads, save/close).
BASE_FUNCS = ("gscript.report_all", "gscript.uids", "gscript.count", "gscript.node_terms_uid", "gscript.ensure_loaded",
              "gscript.exec_state", "gscript.save", "gscript.close_panel", "gscript.node_labels")

# A stageplan route (finalized.route_check rows[].route) -> the functions it calls (stagexec.LVBackend + stagekit).
ROUTE_FUNCS = {
    "primitive": ("gscript.create_primitive_nested", "stagekit.op:create_primitive_nested"),
    "cfw": ("recipes.build_opconnectfromwire_v0.connect_from_wire", "stagekit.op:connect_from_wire"),
    "nested": ("recipes.build_opconnectnested_v1.connect_nested_v1", "stagekit.op:connect_nested_v1"),
    "connect": ("recipes.build_opconnectfromwire_v0.connect_from_wire", "recipes.build_opconnectnested_v1.connect_nested_v1",
                "stagekit.op:connect_from_wire", "stagekit.op:connect_nested_v1", "gscript.wire_control"),
    "branch": ("recipes.build_opconnectfromwire_v0.connect_from_wire", "stagekit.op:connect_from_wire",
               "gscript.wire_indicators", "stagekit.op:wire_indicators"),
    "wire_remove_loose_ends": ("gscript.wire_remove_loose_ends", "stagekit.op:wire_remove_loose_ends"),
    "delete_wire": ("stagekit.op:delete_wire", "recipes.build_opfsinnertunnelconnect_v0.del_wire",
                    "gscript.delete_object"),
    "delete_object": ("stagekit.op:delete_object", "recipes.build_opfsinnertunnelconnect_v0.del_node",
                      "gscript.delete_object"),
    "local_read": ("gscript.create_local_read", "stagekit.op:create_local_read", "stagekit.op:move_in",
                   "recipes.build_d1_v0.move_in"),
    "local_write": ("gscript.create_local_write", "stagekit.op:create_local_write"),
    "connect_term_uid": ("gscript.connect_term_uid", "stagekit.op:connect_term_uid"),
    "wire_sr": ("gscript.wire_sr", "gscript.shift_reg", "stagekit.op:wire_sr"),
    "indicator": ("gscript.create_indicator_nested", "gscript.create_indicator_on_const", "gscript.set_control_label",
                  "gscript.set_visible", "gscript.panel_wiring", "stagekit.op:indicator_nested",
                  "stagekit.op:indicator_on_const"),
    "control": ("gscript.create_control_nested", "gscript.set_control_label", "gscript.set_default_in_memory",
                "gscript.panel_wiring"),
    "add_sr": ("gscript.add_shift_reg", "stagekit.op:add_shift_reg"),
    "stop": ("stagekit.op:stop_from_node",),
    "const_sr": ("gscript.wire_const_sr", "stagekit.op:wire_const_sr"),
    "const": ("gscript.wire_const", "stagekit.op:wire_const"),
    "ctlsink": ("gscript.wire_ctlsink", "stagekit.op:wire_ctlsink"),
    "tunouter": ("gscript.wire_tunouter", "stagekit.op:wire_tunouter"),
    "ctl": ("gscript.wire_control", "stagekit.op:wire_control"),
    "while": ("gscript.loop_in", "stagekit.op:loop_in"), "for": ("gscript.loop_in", "stagekit.op:loop_in"),
    "subvi": ("gscript.drop_subvi", "stagekit.op:drop_subvi"),
    "move_in": ("stagekit.op:move_in", "recipes.build_d1_v0.move_in"),
    "const_on_term": ("stagekit.op:create_const_on_term",),
    "fs_create": ("gscript.struct_copy_nested", "gscript.fs_frames", "stagekit.op:struct_copy_nested"),
    "fs_frame": ("gscript.fs_add_frame", "gscript.fs_frames", "stagekit.op:fs_add_frame"),
    "case_frame_wire": ("gscript.case_frame_wire", "stagekit.op:case_frame_wire"),
    "case": ("gscript.case_in", "gscript.case_frames", "stagekit.op:case_in"),
    "case_wired": ("gscript.case_wired", "gscript.struct_copy_nested", "gscript.case_frames", "stagekit.op:case_wired"),
    "queue": ("gscript.queue_node", "stagekit.op:queue_node"),
    "gate": ("gscript.read_bool_const",),
    "set_index_mode": ("gscript.set_index_mode", "gscript.tunnels", "stagekit.op:set_index_mode"),
}


def rel(p):
    try:
        return os.path.relpath(os.path.abspath(p), ROOT).replace("\\", "/")
    except ValueError:
        return p.replace("\\", "/")


def _abs(p):
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


def _read(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()


_PARSE_CACHE = {}


def _parsed(path):
    """(src, [(qualname, node)]) of a file, cached on (mtime, size) - the launch gate runs inside a hook."""
    st = os.stat(path)
    key = (os.path.normcase(os.path.abspath(path)), st.st_mtime, st.st_size)
    if key not in _PARSE_CACHE:
        src = _read(path)
        _PARSE_CACHE[key] = (src, _defs_with_classes(src))
    return _PARSE_CACHE[key]


def _defs_with_classes(src):
    """[(qualname 'Class.meth' or 'fn', node)] for top-level functions and class methods."""
    t = ast.parse(src)
    out = []
    for n in t.body:
        if isinstance(n, ast.FunctionDef):
            out.append((n.name, n))
        elif isinstance(n, ast.ClassDef):
            out.extend(("%s.%s" % (n.name, m.name), m) for m in n.body if isinstance(m, ast.FunctionDef))
    return out


def locate(fn):
    """(file, [def qualnames], first line) of a registry function name, or (None, [], None)."""
    mod, _, rest = fn.partition(".")
    if mod == "gscript":
        p, want = FC.GSCRIPT, [rest]
    elif mod == "recipes":
        m, _, d = rest.partition(".")
        p, want = os.path.join(RECIPES, m + ".py"), [d]
    elif mod == "stagekit" and rest.startswith("op:"):
        verb = rest[3:]
        hits = []
        for p in (FC.STAGEKIT, FC.STAGEXEC):
            for q, node in _parsed(p)[1]:
                if any(isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr == "_op" and c.args
                       and isinstance(c.args[0], ast.Constant) and c.args[0].value == verb for c in ast.walk(node)):
                    hits.append((p, q, node.lineno))
        if not hits:
            return None, [], None
        p0 = hits[0][0]
        return p0, sorted(set("%s:%s" % (rel(p), q) for p, q, _l in hits)), hits[0][2]
    else:
        return None, [], None
    if not os.path.isfile(p):
        return None, [], None
    defs = dict(_parsed(p)[1])
    if not all(d in defs for d in want):
        return None, [], None
    return p, want, defs[want[0]].lineno


def source_md5(fn):
    """md5 of the function's own source text (ast.get_source_segment of each def, joined) - None when not found.
    For a Stage verb: every def that issues `_op("<verb>")` in stagekit/stagexec."""
    p, defs, _line = locate(fn)
    if p is None:
        return None
    parts = []
    if fn.startswith("stagekit.op:"):
        for d in defs:
            f_, q = d.rsplit(":", 1)
            src, nodes = _parsed(_abs(f_))
            parts.append(ast.get_source_segment(src, dict(nodes)[q]) or "")
    else:
        src, nodes = _parsed(p)
        node_by = dict(nodes)
        parts = [ast.get_source_segment(src, node_by[d]) or "" for d in defs]
    return hashlib.md5("\n".join(parts).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------------------------- registry io
def reg_path(fn, reg_dir=None):
    return os.path.join(reg_dir or REG_DIR, fn.replace(":", "_") + ".json")


def load(fn, reg_dir=None):
    p = reg_path(fn, reg_dir)
    if not os.path.isfile(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def write_record(rec, reg_dir=None):
    os.makedirs(reg_dir or REG_DIR, exist_ok=True)
    p = reg_path(rec["function"], reg_dir)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1, ensure_ascii=False)
        f.write("\n")
    return p


def status(fn, reg_dir=None, md5_now=None):
    """'fresh-pass' | 'fresh-fail' | 'stale' | 'planned' | 'none' (+ the record looked at)."""
    rec = load(fn, reg_dir)
    if rec is None:
        return "none", None
    rs = rec.get("records") or []
    if not rs:
        return "planned", None
    last = rs[-1]
    now = md5_now if md5_now is not None else source_md5(fn)
    if not last.get("src_md5") or last.get("src_md5") != now:
        return "stale", last
    return ("fresh-pass" if last.get("status") == "PASS" else "fresh-fail"), last


def add_record(fn, st, log, labview="LabVIEW 2026", card="", reg_dir=None, md5_now=None):
    """Append ONE result record (card chat-F3 calls this after the real run). Refuses without a plan (plan first)."""
    if st not in ("PASS", "FAIL"):
        raise ValueError("status must be PASS or FAIL")
    rec = load(fn, reg_dir)
    if rec is None or not rec.get("plan"):
        raise ValueError("%s has no test plan in %s - the plan is written BEFORE the test" % (fn, reg_path(fn, reg_dir)))
    rec.setdefault("records", []).append({
        "status": st, "date": datetime.datetime.now().isoformat(timespec="seconds"), "labview": labview,
        "log": rel(log) if log else None, "src_md5": md5_now if md5_now is not None else source_md5(fn), "card": card})
    write_record(rec, reg_dir)
    return rec


# ---------------------------------------------------------------------------------------------- the test plans
def plan_set():
    """The functions whose test plans this card writes: everything the P4 v18 plans route through, the base reads of a
    stagexec run, every gscript function stagekit/stagexec call directly (g.<name>), every Stage verb, the recipe
    functions of those paths. Sorted, deduplicated, restricted to functions that LOCATE (a dead name is reported)."""
    s = set(BASE_FUNCS) | set(RECIPE_FUNCS) | set("stagekit.op:" + v for v in FC.op_verbs())
    for p in P4_PLANS:
        for r in routes_of_plan(_abs(p)):
            s |= set(ROUTE_FUNCS.get(r, ()))
    gfn = set(q for q, _n in _parsed(FC.GSCRIPT)[1] if "." not in q)
    for p in (FC.STAGEKIT, FC.STAGEXEC):
        for n in re.findall(r"\bg\.([a-z][a-z_0-9]*)\s*\(", _read(p)):
            if n in gfn and ("gscript." + n) in FC.TABLE:
                s.add("gscript." + n)
    return sorted(s)


# Hand-written inputs for the functions with an ACTIVE postcondition (the ones F3 must exercise both ways).
PLAN_INPUTS = {
    "gscript.delete_object": [
        {"case": "pos", "call": "delete_object(scratch, 'Function', <index of a known Add>, verify=True)",
         "predict": "removed == 1; outcome ok; the uid absent from uids(scratch,'Function')"},
        {"case": "neg-double", "call": "the same uid deleted again via stagekit.Stage.delete_object",
         "predict": "PostconditionFailed at the call, outcome no_output, measured removed 0"}],
    "stagekit.op:delete_object": [
        {"case": "pos", "call": "Stage.delete_object('Function', <uid>)", "predict": "rec.outcome ok, removed 1"},
        {"case": "neg-double", "call": "Stage.delete_object('Function', <same uid>)",
         "predict": "rec.err 'PostconditionFailed ... removed == 1, measured 0 -> no_output'; rec.outcome no_output"}],
    "stagekit.op:delete_wire": [
        {"case": "pos", "call": "Stage.delete_wire(<wire uid>)", "predict": "rec.outcome ok, found 1; uid gone on re-read"},
        {"case": "neg-double", "call": "Stage.delete_wire(<same wire uid>)", "predict": "rec.outcome no_output, found 0"}],
    "gscript.term_index": [
        {"case": "pos", "call": "term_index(scratch, <diag uid>, <Add uid>, 'x+y', True)",
         "predict": "matches == 1, node_echo == node uid; returns (di, ni, i, row)"},
        {"case": "neg-two", "call": "term_index on a node with two same-named same-direction terminals (e.g. Build "
                                    "Array 'element' x2)", "predict": "PostconditionValueError, outcome failed, matches 2"}],
    "gscript.connect_term_uid": [
        {"case": "pos", "call": "connect_term_uid(scratch, <sink term uid>, <src term uid>) on two bare terminals",
         "predict": "new_wire == 1 (wire_uid != 0), echoes equal, invoke_left 0"}],
    "gscript.case_frame_wire": [
        {"case": "pos", "call": "case_frame_wire(scratch, <case uid>, 0, {'tunnel': t}, {'node': n, 'term': name})",
         "predict": "new_wire == 1, invoke_left []"}],
    "gscript.add_shift_reg": [{"case": "pos", "call": "add_shift_reg(scratch, <while index>, 120)",
                               "predict": "new_register == 1 (uid != 0); ShiftRegister census +1"}],
    "gscript.loop_in": [{"case": "pos", "call": "loop_in('while', scratch, <diag index>, (40, 40))",
                         "predict": "new_loops == 1; WhileLoop census +1, Diagram +1"}],
    "gscript.wire_remove_loose_ends": [{"case": "pos", "call": "wire_remove_loose_ends(scratch, <wire with a loose "
                                                               "joint>)", "predict": "echo == wire_uid, broken_after 0"}],
    "gscript.create_local_read": [{"case": "pos", "call": "create_local_read(scratch, <panel index>)",
                                   "predict": "new_locals == 1, op_err 0"}],
    "gscript.create_local_write": [{"case": "pos", "call": "create_local_write(scratch, <panel index>)",
                                    "predict": "new_locals == 1, op_err 0"}],
    "gscript.create_primitive_nested": [{"case": "pos", "call": "create_primitive_nested(scratch, <body diag uid>, "
                                                                "'Add', (40, 40))", "predict": "one new Function, uid"}],
}


def predicted(fn):
    s = FC.TABLE.get(fn)
    if s is None:
        return {"note": "no fncontract.TABLE row (recipe function): predicted = returns without exception and the "
                        "caller's census/step diff matches the plan"}
    if "post" in s:
        return dict(("%s" % q, "%s %s" % (o, w)) for q, (o, w) in s["post"].items())
    return {"note": "no postcondition (%s); predicted = returns without exception, outcome ok" % s.get("none")}


def legacy_for(fn):
    """scratch_verify records whose `function` names this function (no src md5 -> evidence only, never fresh)."""
    short = fn.split(".", 1)[1] if "." in fn else fn
    short = short.replace("op:", "")
    out = []
    for p in sorted(glob.glob(os.path.join(SCRATCH_DIR, "*.json"))):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except (ValueError, OSError):
            continue
        name = str(d.get("function") or "")
        head = re.split(r"[\s(]", name.replace("gscript.", "").replace("stagexec.", "").replace("stagekit.", ""))[0]
        if head == short or name == fn:
            out.append({"file": rel(p), "status": d.get("status"), "card": d.get("card"), "log": d.get("log"),
                        "note": "folded from scratch_verify: no source md5 recorded, so never a FRESH pass"})
    return out


def make_plan(fn, card="chat-F2", now=None):
    p, defs, line = locate(fn)
    s = FC.TABLE.get(fn) or {}
    ro = "none" in s and "read-only" in str(s.get("none"))
    inputs = PLAN_INPUTS.get(fn) or [{
        "case": "pos",
        "call": ("call it on the scratch bed against a known object (class/uid from the bed's graph JSON)" if ro else
                 "call it once on the scratch bed with the arguments its stagexec route passes (stagexec.LVBackend)"),
        "predict": ("rows equal the offline graph read of the bed (same uids)" if ro else
                    "no exception; outcome ok; the census / step diff the route declares")}]
    return {"schema": "fnrec/1", "function": fn,
            "source": {"file": rel(p) if p else None, "defs": defs, "line": line,
                       "md5": source_md5(fn) if p else None},
            "plan": {"written": now or datetime.datetime.now().isoformat(timespec="seconds"), "card": card,
                     "bed": "a scratch copy (stagekit.Stage.scratch) of a small claudeDev VI holding one While Loop, "
                            "one Add, one Case, one Flat Sequence, two panel controls - created and deleted in the run",
                     "inputs": inputs, "predicted": predicted(fn),
                     "outcome_contract": FC.describe(fn) if fn in FC.TABLE else "recipe function (no TABLE row)",
                     "pass_if": "every input's prediction holds AND the call's standard outcome is the predicted one; "
                                "handle count flat (+-100) over the run",
                     "runs_in": "card chat-F3 (real LabVIEW); never this card"},
            "records": [], "legacy_evidence": legacy_for(fn)}


def write_plans(reg_dir=None, card="chat-F2"):
    """Write (or refresh the plan of) every function in plan_set(). Existing `records` are KEPT."""
    out = []
    for fn in plan_set():
        old = load(fn, reg_dir) or {}
        new = make_plan(fn, card)
        if old.get("plan"):
            new["plan"]["written"] = old["plan"].get("written", new["plan"]["written"])
        new["records"] = old.get("records") or []
        write_record(new, reg_dir)
        out.append(fn)
    return out


# ---------------------------------------------------------------------------------------------- what a unit uses
PLAN_LIT_RE = re.compile(r"tools[/\\\\]+bench[/\\\\]+(plan_[A-Za-z0-9_\-]+\.json)")


def routes_of_plan(path):
    try:
        d = json.load(open(path, encoding="utf-8"))
    except (ValueError, OSError):
        return []
    rows = ((d.get("finalized") or {}).get("route_check") or {}).get("rows") or []
    rs = []
    for r in rows:
        x = str(r.get("route") or r.get("op") or "")
        rs.append(x.split(":")[0])
    if not rows:                                       # not finalized: the op kinds themselves
        rs = [str(a.get("op")) for a in d.get("actions") or []]
    return sorted(set(rs))


def functions_for_unit(unit):
    """Sorted function names a stage script / stageplan JSON uses (see module docstring)."""
    p = _abs(unit)
    fns = set()
    if p.lower().endswith(".json"):
        fns |= set(BASE_FUNCS)
        for r in routes_of_plan(p):
            fns |= set(ROUTE_FUNCS.get(r, ()))
        return sorted(fns)
    src = _read(p)
    plans = set(PLAN_LIT_RE.findall(src))
    for pl in plans:
        fns |= set(functions_for_unit(os.path.join(HERE, "bench", pl)))
    if plans or re.search(r"\bstagexec\b", src):
        fns |= set(BASE_FUNCS)
    gfn = set(q for q, _n in _parsed(FC.GSCRIPT)[1] if "." not in q)
    for n in re.findall(r"\b(?:g|gscript)\.([a-z][a-z_0-9]*)\s*\(", src):
        if n in gfn:
            fns.add("gscript." + n)
    for n in re.findall(r"\b(?:s|st|stage|self\.s)\.([a-z][a-z_0-9]*)\s*\(", src):
        if "stagekit.op:" + n in FC.TABLE:
            fns.add("stagekit.op:" + n)
    return sorted(fns)


# ---------------------------------------------------------------------------------------------- the gate
def load_config(path=None):
    p = path or GATE_CONFIG
    if not os.path.isfile(p):
        return dict(DEFAULT_CONFIG)
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def switch_condition(cfg=None, reg_dir=None):
    """(met, missing) - every function of the plans in switch.required_from has a fresh PASS record."""
    cfg = cfg or load_config()
    need = set()
    for p in (cfg.get("switch") or {}).get("required_from") or []:
        need |= set(functions_for_unit(p))
    missing = sorted(f for f in need if status(f, reg_dir)[0] != "fresh-pass")
    return (not missing and bool(need)), missing


def launch_gate(unit, cfg_path=None, reg_dir=None, log_path=None, now=None):
    """(allow, line). ADVISORY in this card: logs, allows. Refuses only when mode == 'refuse', or switch.auto and the
    switch condition is met, and a used function lacks a fresh PASS record."""
    cfg = load_config(cfg_path)
    fns = functions_for_unit(unit)
    st = dict((f, status(f, reg_dir)[0]) for f in fns)
    missing = [f for f in fns if st[f] != "fresh-pass"]
    met, _m = switch_condition(cfg, reg_dir)
    mode = cfg.get("mode", "advisory")
    if mode != "refuse" and (cfg.get("switch") or {}).get("auto") and met:
        mode = "refuse"
    counts = {}
    for v in st.values():
        counts[v] = counts.get(v, 0) + 1
    line = "FN-GATE {0} | {1} | {2} of {3} function(s) without a fresh PASS record ({4}) | {5}{6} | switch condition {7} | {8}".format(
        mode.upper(), rel(_abs(unit)), len(missing), len(fns), ", ".join("%s %d" % kv for kv in sorted(counts.items())),
        ", ".join(missing[:12]), " ..." if len(missing) > 12 else "", "MET" if met else "not met",
        now or time.strftime("%Y-%m-%d %H:%M:%S"))
    try:
        with open(log_path or GATE_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass
    if mode == "refuse" and missing:
        return False, ("FN-RECORD GATE (card chat-F2/F3): {0} uses {1} function(s) with no fresh PASS record: {2}. Run "
                       "their test plans (tools/bench/fn_records/<function>.json) on a scratch VI and add the record "
                       "(py tools/fn_records.py --add-record <fn> PASS --log <log>).\n").format(
                           rel(_abs(unit)), len(missing), ", ".join(missing[:20]))
    return True, line


# ---------------------------------------------------------------------------------------------- CLI
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-plans", action="store_true")
    ap.add_argument("--write-config", action="store_true", help="write gate_config.json with the default (advisory)")
    ap.add_argument("--status", nargs="*")
    ap.add_argument("--advise")
    ap.add_argument("--add-record", nargs=2, metavar=("FN", "STATUS"))
    ap.add_argument("--log")
    ap.add_argument("--labview", default="LabVIEW 2026")
    ap.add_argument("--card", default="")
    a = ap.parse_args(argv)
    if a.write_config:
        os.makedirs(REG_DIR, exist_ok=True)
        with open(GATE_CONFIG, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=1, ensure_ascii=False)
            f.write("\n")
        print("wrote", rel(GATE_CONFIG))
    if a.write_plans:
        fns = write_plans()
        print("wrote %d test plan(s) under %s" % (len(fns), rel(REG_DIR)))
    if a.status is not None:
        for fn in (a.status or plan_set()):
            st, last = status(fn)
            print("%-60s %-11s %s" % (fn, st, (last or {}).get("log") or ""))
    if a.advise:
        ok, line = launch_gate(a.advise)
        print(line if ok else line)
        return 0 if ok else 2
    if a.add_record:
        add_record(a.add_record[0], a.add_record[1], a.log, a.labview, a.card)
        print("record added:", a.add_record[0], a.add_record[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
