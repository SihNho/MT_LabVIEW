# ---
# labview: none
# hardware: none
# ---
"""fncontract.py - ONE standard outcome and DECLARED postconditions for every LabVIEW-touching scripting function
(card chat-F2 part 1, user 2026-10-06 "1~3번 모두 적용하도록 하자"; idea from CLI-Anything's harness contracts; purpose
(user 2026-10-04): catch errors at the START, at the call that made them).

EXISTING FIRST (checked before writing): `gscript.delete_object` already measured "expected 1 object gone"
(gscript.py, verify=True) and `gscript.term_index` already refused 0 / >1 name matches - both are GENERALISED here (they
now call `check()`), not duplicated. Many creators already raise on their own (create_primitive_nested, case_wired,
fs_add_frame, struct_copy_nested, wire_control, ...) - the table records those as `existing-raise` with nothing added.
`stagekit.Stage._op` is the one choke point every stagekit/stagexec mutator passes; it now stores the standard outcome
in its op record. Nothing here talks to LabVIEW: this module is pure Python and imports no COM client.

THE STANDARD OUTCOME (a dict, `outcome()`):
    {"outcome": "ok" | "no_output" | "failed" | "timed_out", "fn": "<module>.<function>", "reason": str,
     "measured": {...}, "expected": {...}}
  ok        - the call returned and every declared postcondition held (or none is declared).
  no_output - the call returned but produced NOTHING (every violated quantity measured 0 / empty): a delete that removed
              0 objects, a lookup with 0 matches, a create with 0 new objects.
  failed    - an exception, or a postcondition violated with a non-zero measurement (2 matches, 2 removed).
  timed_out - the COM watchdog expired (`gscript._deadline_call` -> "did not return within") or the module is POISONED
              (`gscript.COMPoisoned`).
A RAISED exception carries it as `e.outcome`; a returned value is recorded in `HISTORY` (read with `mark()`/`since()`).

THE TABLE (`TABLE`, one row per function, data not prose):
    "gscript.delete_object": {"post": {"removed": ("==", 1)}, "measure": "inline", "on_fail": "raise", "how": "..."}
    "gscript.report":        {"none": "read-only query - ..."}
  measure: "inline"         the function measures and calls check() itself (the generalised delete/lookup checks);
           "result"         the wrapper measures from the RETURN value (`_EXTRACT`) - no extra LabVIEW read is added;
           "existing-raise" the function's own pre-existing raise enforces it (cited in "how"); nothing added;
           "caller"         measured by the named caller (e.g. stagexec's step diff) - not re-read here.
  on_fail: "raise"  -> PostconditionFailed at that call (the caller's Stage.safe turns it into the op's err -> ExecStop);
           "record" -> outcome recorded, the return value unchanged: for functions whose contract is "return err in the
                       dict, the caller decides" (wire_remove_loose_ends, set_control_label, _opcw_call wirers) - raising
                       there would change what the function does.
  A function whose postcondition cannot be measured cheaply says so: {"none": "<reason>"}, never silently.

PRECONDITIONS (`PRE`, card chat-F3b 2026-10-07): declared per function, checked AT THE CALL on its failure path only (a call
that raised is re-examined: the precondition measured, and when it does not hold the call fails with PreconditionFailed - a
RuntimeError naming the reason after the original text - instead of the bare op error). Today: gscript.loop_in's default
input-tunnel source Traverse('SubVI')[0] needs a SubVI in the VI (error 1055 otherwise, fntest_g1.log run 2).

install(namespace, "gscript") wraps every gscript function the table names (functools.wraps; idempotent; `__wrapped__`
kept, so inspect.getsource / signature still read the original). Behaviour on success is unchanged except that a
declared `result` postcondition with on_fail raise can now fail the call - the purpose of the card.

Self-test: tools/bench/selftest_fn_f2.py (double delete, 2-match lookup, timed_out, stale record, advisory gate,
generator idempotence, drift, table coverage).
"""
import ast
import collections
import functools
import os
import re
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

OUTCOMES = ("ok", "no_output", "failed", "timed_out")
SEVERITY = {"ok": 0, "no_output": 1, "failed": 2, "timed_out": 3}
TIMEOUT_RE = re.compile(r"did not return within|MODULE POISONED|STILL OUTSTANDING|timed out", re.I)


class PostconditionFailed(RuntimeError):
    """A declared postcondition did not hold at the call. `.outcome` = the standard outcome dict."""

    def __init__(self, msg, outcome_=None):
        RuntimeError.__init__(self, msg)
        self.outcome = outcome_


class PostconditionValueError(ValueError):
    """The same, for a function whose pre-existing check raised ValueError (term_index): callers that catch ValueError
    still catch it. `.outcome` = the standard outcome dict."""

    def __init__(self, msg, outcome_=None):
        ValueError.__init__(self, msg)
        self.outcome = outcome_


class PreconditionFailed(RuntimeError):
    """card chat-F3b: a DECLARED precondition (PRE) did not hold when the call failed. A RuntimeError, so every caller that
    caught the function's own RuntimeError still catches it. `.outcome` = the standard outcome dict (outcome failed)."""

    def __init__(self, msg, outcome_=None):
        RuntimeError.__init__(self, msg)
        self.outcome = outcome_


def outcome(status, fn, reason="", measured=None, expected=None):
    if status not in OUTCOMES:
        raise ValueError("outcome %r is not one of %s" % (status, OUTCOMES))
    return {"outcome": status, "fn": fn, "reason": str(reason)[:300], "measured": dict(measured or {}),
            "expected": dict(expected or {})}


def classify_exception(e):
    """timed_out for the watchdog / poison family, else failed (an exception that already carries an outcome keeps it)."""
    oc = getattr(e, "outcome", None)
    if isinstance(oc, dict) and oc.get("outcome") in OUTCOMES:
        return oc["outcome"]
    if type(e).__name__ == "COMPoisoned" or TIMEOUT_RE.search(str(e) or ""):
        return "timed_out"
    return "failed"


def outcome_of_exception(e, fn=None):
    """The standard outcome of an exception: its own `.outcome` when it has one, else a classified new one."""
    oc = getattr(e, "outcome", None)
    if isinstance(oc, dict) and oc.get("outcome") in OUTCOMES:
        return oc
    return outcome(classify_exception(e), fn or "?", "%s: %s" % (type(e).__name__, str(e)[:240]))


def outcome_of_text(err_text, fn=None):
    """For callers that only kept the error STRING (stagekit.Stage.safe): classify from the text."""
    if not err_text:
        return outcome("ok", fn or "?")
    t = str(err_text)
    if t.startswith("COMPoisoned") or TIMEOUT_RE.search(t):
        st = "timed_out"
    elif "-> no_output]" in t:
        st = "no_output"
    else:
        st = "failed"
    return outcome(st, fn or "?", t[:240])


# ------------------------------------------------------------------------------------------------ the record of calls
HISTORY = collections.deque(maxlen=2000)
_SEQ = [0]
_LOCK = threading.Lock()


def _record(oc):
    with _LOCK:
        _SEQ[0] += 1
        HISTORY.append((_SEQ[0], time.time(), oc))


def mark():
    return _SEQ[0]


def since(m):
    return [oc for s, _t, oc in list(HISTORY) if s > m]


def worst(ocs, fn=None):
    """The most severe outcome in a list (ok when empty)."""
    best = None
    for oc in ocs:
        if best is None or SEVERITY[oc["outcome"]] > SEVERITY[best["outcome"]]:
            best = oc
    return best or outcome("ok", fn or "?")


# ------------------------------------------------------------------------------------------------ the checker
OPS = {"==": lambda a, b: a == b, ">=": lambda a, b: a is not None and b is not None and a >= b,
       "<=": lambda a, b: a is not None and b is not None and a <= b, "!=": lambda a, b: a != b}


def _empty(v):
    return v in (0, None, False, "", [], (), {})


def evaluate(fn, measured, post=None):
    """(status, violations, expected) for `measured` against the table's postconditions of `fn` (or `post`)."""
    post = post if post is not None else (TABLE.get(fn) or {}).get("post") or {}
    bad, expected = [], {}
    for q, (op_, want) in post.items():
        w = measured.get(want) if isinstance(want, str) else want
        expected[q] = "%s %s" % (op_, w)
        if q not in measured:
            bad.append((q, op_, w, "UNMEASURED"))
            continue
        if not OPS[op_](measured[q], w):
            bad.append((q, op_, w, measured[q]))
    if not bad:
        return "ok", [], expected
    zero = all(got != "UNMEASURED" and _empty(got) for _q, _o, _w, got in bad)
    return ("no_output" if zero else "failed"), bad, expected


def check(fn, msg="", raise_=None, exc=None, **measured):
    """Evaluate `fn`'s declared postconditions on `measured`; record the outcome; RAISE at this call when one fails and
    the row's on_fail is 'raise' (or raise_=True). The message keeps the caller's own text `msg` first (callers and log
    readers keyed on it stay valid) and appends `[postcondition <fn>: <q> <op> <want>, measured <got> -> <outcome>]`."""
    spec = TABLE.get(fn)
    if spec is None or "post" not in spec:
        raise KeyError("fncontract.check(%r): no postcondition row in fncontract.TABLE" % fn)
    status, bad, expected = evaluate(fn, measured)
    tag = "; ".join("%s %s %s, measured %s" % (q, o, w, g_) for q, o, w, g_ in bad)
    oc = outcome(status, fn, tag, measured, expected)
    _record(oc)
    if status != "ok":
        do_raise = raise_ if raise_ is not None else spec.get("on_fail", "raise") == "raise"
        if do_raise:
            text = "%s%s[postcondition %s: %s -> %s]" % (msg, " " if msg else "", fn, tag, status)
            cls = exc or (PostconditionValueError if spec.get("exc") == "ValueError" else PostconditionFailed)
            raise cls(text, oc)
    return oc


# ------------------------------------------------------------------------------------------------ the wrapper
def _nonzero(v):
    try:
        return 1 if int(v or 0) else 0
    except (TypeError, ValueError):
        return 1 if v else 0


def _arg(a, k, i, name, default=None):
    if name in k:
        return k[name]
    return a[i] if len(a) > i else default


# Measurements taken from the RETURN value only (no extra LabVIEW read). Each returns a dict, or None = not applicable.
_EXTRACT = {
    "gscript.connect_term_uid": lambda r, a, k: {"new_wire": _nonzero((r or {}).get("wire_uid"))},
    "gscript.case_frame_wire": lambda r, a, k: {"new_wire": _nonzero((r or {}).get("wire_uid"))},
    "gscript.add_shift_reg": lambda r, a, k: {"new_register": _nonzero(r)},
    "gscript.loop_in": lambda r, a, k: {"new_loops": (len(r) if isinstance(r, (list, tuple)) else _nonzero(r))},
    "gscript.queue_node": lambda r, a, k: {"new_functions": len(r or [])},
    "gscript.wire_remove_loose_ends": lambda r, a, k: {
        "echo": int((r or {}).get("echo") or 0), "wire_uid": int(_arg(a, k, 1, "wire_uid") or 0),
        "broken_after": int(bool((r or {}).get("broken_after"))), "op_err": int(bool((r or {}).get("err")))},
    "gscript.set_control_label": lambda r, a, k: {"label_back_ok": int(str((r or {}).get("text_back")) ==
                                                                          str(_arg(a, k, 2, "text"))),
                                                  "op_err": int(bool((r or {}).get("err")))},
    "gscript.wire_const": lambda r, a, k: {"new_wires": (r or (None, ""))[0], "op_err": int(bool((r or (0, ""))[1]))},
    "gscript.wire_const_sr": lambda r, a, k: {"new_wires": (r or (None, ""))[0], "op_err": int(bool((r or (0, ""))[1]))},
    "gscript.wire_ctlsink": lambda r, a, k: {"new_wires": (r or (None, ""))[0], "op_err": int(bool((r or (0, ""))[1]))},
    "gscript.wire_tunouter": lambda r, a, k: {"new_wires": (r or (None, ""))[0], "op_err": int(bool((r or (0, ""))[1]))},
    "gscript.connect_terminals": lambda r, a, k: {"new_wires": (r or (None, None))[0]},
    "gscript.create_indicator_nested": lambda r, a, k: {"op_err": int(bool((r or {}).get("err")))},
    "gscript.create_control_nested": lambda r, a, k: {"op_err": int(bool((r or {}).get("err")))},
    "gscript.create_indicator_on_const": lambda r, a, k: {"op_err": int(bool((r or {}).get("err")))},
    "gscript.create_local_read": lambda r, a, k: {"new_locals": _nonzero((r or {}).get("uid")),
                                                  "op_err": int(bool((r or {}).get("err")))},
    "gscript.create_local_write": lambda r, a, k: {"new_locals": _nonzero((r or {}).get("uid")),
                                                   "op_err": int(bool((r or {}).get("err")))},
}

_TLS = threading.local()


# ------------------------------------------------------------------------------------------------ preconditions
# card chat-F3b (chat decision 1, 2026-10-07, after tools/bench/fntest_g1.log run 2): a PRECONDITION is declared per
# function and checked AT THE CALL. It is MEASURED ON THE CALL'S FAILURE PATH ONLY (when the call raised), so a call that
# succeeds issues no extra LabVIEW read and its behaviour, return value and read count are unchanged (the X10 memory model
# counts a stage's reads). When the measurement shows the precondition violated, the wrapper raises PreconditionFailed
# (a RuntimeError) whose message keeps the original exception's text FIRST (log readers keyed on it stay valid) and
# appends the clear reason; outcome `failed`. A precondition that holds, or a measurement that itself raises, leaves the
# original exception exactly as it was (never masked). The wrapped function's own source is never touched.
#   "pre":     {quantity: (op, want)}            what must hold (OPS)
#   "measure": fn(ns, args, kwargs) -> {quantity: value, ...}   ns = the wrapped module's globals (install passes it)
#   "why":     the reason appended to the message when it does not hold
def _loop_in_src(ns, a, k):
    target = _arg(a, k, 1, "target")
    cls = _arg(a, k, 4, "src_cls") or "SubVI"
    idx = int(_arg(a, k, 5, "src_index", 0) or 0)
    n = int(ns["count"](target, cls))
    return {"src_present": 1 if n > idx else 0, "src_cls": cls, "src_index": idx, "count": n}


PRE = {
    "gscript.loop_in": {
        "pre": {"src_present": ("==", 1)}, "measure": _loop_in_src,
        "why": "loop_in's input-tunnel source is Traverse(src_cls or 'SubVI')[src_index] (gscript.py:1530): the target VI must "
               "hold more than src_index objects of that class - with the default source at least ONE SubVI; without it "
               "OpWhileLoopIn_v0 / OpForLoopIn_v0 stop with error 1055 at To More Specific Class (tools/bench/fntest_g1.log "
               "run 2, 2026-10-07; PD314(d)) - drop a SubVI on the VI first"},
}


def precondition_error(fn, exc, ns, a, k):
    """card chat-F3b: `fn`'s declared precondition measured after the call raised `exc` -> a PreconditionFailed (its
    outcome recorded) when it does not hold, else None (the caller re-raises `exc` unchanged)."""
    pre = PRE.get(fn)
    if pre is None or ns is None or isinstance(exc, PreconditionFailed):
        return None
    try:
        m = pre["measure"](ns, a, k)
    except Exception:                                                              # noqa: BLE001 - never mask `exc`
        return None
    _st, bad, expected = evaluate(fn, m, pre["pre"])
    if not bad:
        return None
    tag = "; ".join("%s %s %s, measured %s" % (q, o, w, g_) for q, o, w, g_ in bad)
    oc = outcome("failed", fn, "precondition: " + tag, m, expected)
    _record(oc)
    return PreconditionFailed("%s: %s [precondition %s: %s -> failed: %s]" % (
        type(exc).__name__, str(exc)[:300], fn, tag, pre["why"]), oc)


def contract(fn, f, ns=None):
    """Wrap `f` (the function the TABLE row `fn` describes) so every call ends in ONE standard outcome. `ns` = the module's
    globals, needed only by a PRE measurement (install passes it)."""
    if getattr(f, "__fncontract__", None):
        return f
    spec = TABLE.get(fn) or {}

    @functools.wraps(f)
    def wrapper(*a, **k):
        try:
            res = f(*a, **k)
        except Exception as e:                                                     # noqa: BLE001 - re-raised unchanged
            pe = precondition_error(fn, e, ns, a, k)                               # card chat-F3b: failure path only
            if pe is not None:
                raise pe from e
            oc = getattr(e, "outcome", None)
            if not (isinstance(oc, dict) and oc.get("outcome") in OUTCOMES):
                oc = outcome(classify_exception(e), fn, "%s: %s" % (type(e).__name__, str(e)[:240]))
                try:
                    e.outcome = oc
                except Exception:                                                  # noqa: BLE001
                    pass
                _record(oc)
            elif oc.get("fn") != fn:
                _record(dict(oc, fn=fn, reason=("via %s: %s" % (oc.get("fn"), oc.get("reason")))[:300]))
            raise
        ext = _EXTRACT.get(fn) if spec.get("measure") == "result" else None
        if ext is not None:
            try:
                measured = ext(res, a, k)
            except Exception as e:                                                 # noqa: BLE001 - the measurement, not the call
                measured = None
                _record(outcome("ok", fn, "measurement skipped (%s: %s)" % (type(e).__name__, str(e)[:100])))
            if measured is not None:
                check(fn, "%s returned %r;" % (fn.split(".")[-1], res if not isinstance(res, dict) else
                                              dict((x, res.get(x)) for x in list(res)[:6])), **measured)
                return res
        _record(outcome("ok", fn))
        return res

    wrapper.__fncontract__ = fn
    return wrapper


def install(namespace, prefix):
    """Wrap every function of module `prefix` that the TABLE names, inside `namespace` (the module's globals()).
    Idempotent. Returns the list of wrapped names."""
    done = []
    for name in TABLE:
        mod, _, fn = name.partition(".")
        if mod != prefix or ":" in fn or "." in fn:
            continue
        f = namespace.get(fn)
        if not callable(f) or getattr(f, "__fncontract__", None) or isinstance(f, type):
            continue
        namespace[fn] = contract(name, f, namespace)
        done.append(fn)
    return done


# ------------------------------------------------------------------------------------------------ static analysis
GSCRIPT = os.path.join(HERE, "gscript.py")
STAGEKIT = os.path.join(HERE, "stagekit.py")
STAGEXEC = os.path.join(HERE, "stagexec.py")
LV_PRIMITIVES = {"lv", "op", "_run", "_invoke", "_err", "_lv_gui"}
COM_ATTRS = {"SetControlValue", "GetControlValue", "GetVIReference", "SaveInstrument"}
OP_VERB_RE = re.compile(r"\b_op\(\s*\"([A-Za-z_]\w*)\"")


def _read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def functions(path=GSCRIPT, src=None):
    """{name: ast.FunctionDef} of the module's TOP-LEVEL functions."""
    t = ast.parse(src if src is not None else _read(path))
    return dict((n.name, n) for n in t.body if isinstance(n, ast.FunctionDef))


def lv_touching(path=GSCRIPT, src=None):
    """Public top-level functions whose call graph reaches lv/op/_run/_invoke/_err/_lv_gui or a COM method (closure)."""
    fns = functions(path, src)
    calls = {}
    for k, n in fns.items():
        s = set()
        for c in ast.walk(n):
            if isinstance(c, ast.Call) and isinstance(c.func, ast.Name):
                s.add(c.func.id)
            if isinstance(c, ast.Attribute) and c.attr in COM_ATTRS:
                s.add("#com")
        calls[k] = s
    prim = LV_PRIMITIVES | {"#com"}
    touch, grew = set(), True
    while grew:
        grew = False
        for k, s in calls.items():
            if k not in touch and (s & prim or s & touch):
                touch.add(k)
                grew = True
    return sorted(k for k in touch if not k.startswith("_") and k not in LV_PRIMITIVES)


def op_verbs(paths=(STAGEKIT, STAGEXEC)):
    """Every literal verb passed to `Stage._op("<verb>", ...)` in stagekit/stagexec."""
    out = set()
    for p in paths:
        out |= set(OP_VERB_RE.findall(_read(p)))
    return sorted(out)


def coverage():
    """{'missing': [...], 'orphan': [...], 'no_reason': [...]} - every LabVIEW-touching public gscript function and every
    Stage._op verb must have a TABLE row; a row whose function is gone is an orphan; a `none` row must give a reason."""
    want = set("gscript." + n for n in lv_touching()) | set("stagekit.op:" + v for v in op_verbs())
    have = set(TABLE)
    gfn = set(functions(GSCRIPT))
    orphan = sorted(n for n in have if (n.startswith("gscript.") and n.split(".", 1)[1] not in gfn) or
                    (n.startswith("stagekit.op:") and n not in want))
    no_reason = sorted(n for n, s in TABLE.items() if "post" not in s and not str(s.get("none") or "").strip())
    return {"missing": sorted(want - have), "orphan": orphan, "no_reason": no_reason}


# ------------------------------------------------------------------------------------------------ THE TABLE
_RO = "none - read-only query: returns LabVIEW's own listing; no count is expected without the caller's plan (the " \
      "caller's census / step diff judges it)"
_LEG = "none - not on a stagekit/stagexec/P4 path; a postcondition is declared before a plan uses it (fn_records lists " \
       "it as unrecorded)"
_SES = "none - session / editor state (panel, load, save, revert); no countable diagram effect"
_VIA = "none at this level - measured by the gscript function it calls (row %s)"

TABLE = {
    # ---- deletes and lookups: the generalised inline checks -----------------------------------------------------
    "gscript.delete_object": {"post": {"removed": ("==", 1)}, "measure": "inline", "on_fail": "raise",
                              "how": "uid set of `cls` before/after (verify=True); verify=False skips both snapshots BY "
                                     "DESIGN - the caller measures (stagekit.op:delete_object / op:delete_wire)"},
    "gscript.term_index": {"post": {"matches": ("==", 1), "node_echo": ("==", "node_uid")}, "measure": "inline",
                           "on_fail": "raise", "exc": "ValueError",
                           "how": "rows of node_terms_uids whose name and direction match; the node uid echoed"},
    # ---- creators / wirers measured from their return value -----------------------------------------------------
    "gscript.connect_term_uid": {"post": {"new_wire": ("==", 1)}, "measure": "result", "on_fail": "raise",
                                 "how": "wire_uid read back non-zero; sink/src echoes and junk Invokes: existing raise"},
    "gscript.case_frame_wire": {"post": {"new_wire": ("==", 1)}, "measure": "result", "on_fail": "raise",
                                "how": "wire_uid non-zero (the function's own raise covers it too)"},
    "gscript.add_shift_reg": {"post": {"new_register": ("==", 1)}, "measure": "result", "on_fail": "raise",
                              "how": "the op's uid indicator non-zero"},
    "gscript.loop_in": {"post": {"new_loops": ("==", 1)}, "measure": "result", "on_fail": "raise",
                        "how": "new uids of the loop class (the function returns one uid, or the list when != 1)"},
    "gscript.queue_node": {"post": {"new_functions": (">=", 1)}, "measure": "result", "on_fail": "record",
                           "how": "new Function uids (record only: the per-kind count is not measured)"},
    "gscript.wire_remove_loose_ends": {"post": {"echo": ("==", "wire_uid"), "broken_after": ("==", 0),
                                                "op_err": ("==", 0)}, "measure": "result", "on_fail": "record",
                                       "how": "uid echo, Is Broken? after, op error (returned in the dict; stagexec "
                                              "LVBackend.rle stops on them)"},
    "gscript.set_control_label": {"post": {"label_back_ok": ("==", 1), "op_err": ("==", 0)}, "measure": "result",
                                  "on_fail": "record", "how": "TextBack == the label written"},
    "gscript.wire_const": {"post": {"new_wires": ("==", 1), "op_err": ("==", 0)}, "measure": "result",
                           "on_fail": "record", "how": "Wire count delta and op error (the (delta, err) tuple)"},
    "gscript.wire_const_sr": {"post": {"new_wires": ("==", 1), "op_err": ("==", 0)}, "measure": "result",
                              "on_fail": "record", "how": "Wire count delta and op error (the (delta, err) tuple)"},
    "gscript.wire_ctlsink": {"post": {"new_wires": ("==", 1), "op_err": ("==", 0)}, "measure": "result",
                             "on_fail": "record", "how": "Wire count delta and op error (the (delta, err) tuple)"},
    "gscript.wire_tunouter": {"post": {"new_wires": ("==", 1), "op_err": ("==", 0)}, "measure": "result",
                              "on_fail": "record", "how": "Wire count delta and op error (the (delta, err) tuple)"},
    "gscript.connect_terminals": {"post": {"new_wires": (">=", 1)}, "measure": "result", "on_fail": "record",
                                  "how": "Wire count delta (>= 1: a crossing adds tunnels' wires)"},
    "gscript.create_indicator_nested": {"post": {"op_err": ("==", 0)}, "measure": "result", "on_fail": "record",
                                        "how": "err column (uid echo, dangling indicator folded in by the function)"},
    "gscript.create_control_nested": {"post": {"op_err": ("==", 0)}, "measure": "result", "on_fail": "record",
                                      "how": "err column (uid echo, dangling control folded in by the function)"},
    "gscript.create_indicator_on_const": {"post": {"op_err": ("==", 0)}, "measure": "result", "on_fail": "record",
                                          "how": "err column (one new wired indicator, label back)"},
    "gscript.create_local_read": {"post": {"new_locals": ("==", 1), "op_err": ("==", 0)}, "measure": "result",
                                  "on_fail": "record", "how": "uid of the one new Local, err column"},
    "gscript.create_local_write": {"post": {"new_locals": ("==", 1), "op_err": ("==", 0)}, "measure": "result",
                                   "on_fail": "record", "how": "uid of the one new Local, err column"},
    # ---- enforced by the function's own pre-existing raise --------------------------------------------------------
    "gscript.create_primitive_nested": {"post": {"new_objects": ("==", 1)}, "measure": "existing-raise",
                                        "how": "raises unless exactly one new node of the donor class (gscript.py "
                                               "create_primitive_nested `probs`)"},
    "gscript.struct_copy_nested": {"post": {"new_objects": ("==", 1)}, "measure": "existing-raise",
                                   "how": "raises unless exactly one new structure (`probs`)"},
    "gscript.fs_add_frame": {"post": {"new_frames": ("==", 1)}, "measure": "existing-raise",
                             "how": "raises on an op error / no new frame (fs_add_frame `out` check)"},
    "gscript.case_wired": {"post": {"new_objects": ("==", 1), "selector_wired": ("==", 1)}, "measure": "existing-raise",
                           "how": "raises on echo, bare-sink count != 1, junk Invokes, selector/source wire missing"},
    "gscript.case_in": {"post": {"new_objects": ("==", 1)}, "measure": "existing-raise",
                        "how": "raises unless exactly one new CaseStructure"},
    "gscript.wire_control": {"post": {"new_wires": (">=", 1)}, "measure": "existing-raise",
                             "how": "raises when the Wire delta is outside the expected +n..+m"},
    "gscript.wire": {"post": {"new_wires": (">=", 1)}, "measure": "existing-raise",
                     "how": "raises when the Wire count is outside before+1..before+1+crossings (branch=False)"},
    "gscript.set_index_mode": {"post": {"mode_back": ("==", "mode")}, "measure": "caller",
                               "how": "raises on op error; the mode read back by stagexec LVBackend.index_mode_fix "
                                      "(tunnels() after the call)"},
    "gscript.fs_frames": {"post": {"echo": ("==", "fs_uid")}, "measure": "existing-raise",
                          "how": "raises when Traverse('FlatSequence') echoes another uid"},
    "gscript.save": {"post": {"saved": ("==", 1)}, "measure": "existing-raise",
                     "how": "refuses outside claudeDev and on a broken VI; returns the file size"},
    "gscript.drop_subvi": {"none": "none at this level - returns only the run time; the new SubVI is measured by the "
                                   "caller (stagexec create 'subvi': SubVI uid diff == 1)"},
    "gscript.create_indicator": {"none": _LEG}, "gscript.create_control": {"none": _LEG},
    "gscript.wire_sr": {"none": "none at this level - returns nothing; the wire is measured by the caller's census "
                                "(stagekit wire_sr / stagexec step diff)"},
    "gscript.wire_indicators": {"none": "none at this level - the op's err column is returned; stagexec's indicator "
                                        "route stops on it or defers it to a declared sink gate"},
    "gscript.set_visible": {"none": "none - returns the op's read-back dict; Visible is a display property the step "
                                    "diff does not model"},
    "gscript.set_default_in_memory": {"none": "none - the function itself re-reads the value after reinit and returns "
                                              "it; the caller compares it with the plan default"},
    "gscript.remove_bad_wires_scripted": {"none": "none - the number of bad wires is not known in advance; returns the "
                                                  "Wire count and ExecState for the caller"},
    "gscript.remove_bad_wires": {"none": _LEG},
    # ---- read-only queries ---------------------------------------------------------------------------------------
    "gscript.report": {"none": _RO}, "gscript.report_all": {"none": _RO}, "gscript.uids": {"none": _RO},
    "gscript.count": {"none": _RO}, "gscript.new_since": {"none": _RO}, "gscript.node_terms": {"none": _RO},
    "gscript.node_terms_uid": {"none": _RO}, "gscript.node_terms_uids": {"none": _RO}, "gscript.tunnels": {"none": _RO},
    "gscript.shift_reg": {"none": _RO}, "gscript.shift_reg_left": {"none": _RO}, "gscript.panel_wiring": {"none": _RO},
    "gscript.node_labels": {"none": _RO}, "gscript.fp_labels": {"none": _RO}, "gscript.node_info": {"none": _RO},
    "gscript.net_map": {"none": _RO}, "gscript.exec_state": {"none": _RO}, "gscript.conpane": {"none": _RO},
    "gscript.read_bool_const": {"none": _RO}, "gscript.read_const_value": {"none": _RO},
    "gscript.read_term_type": {"none": _RO}, "gscript.case_frames": {"none": _RO}, "gscript.wire_health": {"none": _RO},
    "gscript.wire_joints": {"none": _RO}, "gscript.loop_diagram": {"none": _RO}, "gscript.loop_face_index": {"none": _RO},
    "gscript.find_at": {"none": _RO}, "gscript.node_rank": {"none": _RO}, "gscript.const_class_index": {"none": _RO},
    "gscript.case_inner_face": {"none": _RO}, "gscript.vi_ref": {"none": _RO}, "gscript.subvis": {"none": _RO},
    "gscript.loop_cast": {"none": _RO},
    # ---- session / editor state ----------------------------------------------------------------------------------
    "gscript.open_panel": {"none": _SES}, "gscript.close_panel": {"none": _SES}, "gscript.ensure_loaded": {"none": _SES},
    "gscript.revert": {"none": _SES}, "gscript.gui_save": {"none": _SES}, "gscript.hygiene_run": {"none": _SES},
    "gscript.main": {"none": _SES}, "gscript.ensure_move_files_pristine": {"none": _SES},
    "gscript.set_auto_error_handling": {"none": _SES}, "gscript.make_default": {"none": _SES},
    # ---- legacy builders, not on a stagekit/stagexec/P4 path -----------------------------------------------------
    "gscript.build_case": {"none": _LEG}, "gscript.build_clfn": {"none": _LEG}, "gscript.build_index_array": {"none": _LEG},
    "gscript.build_invoke": {"none": _LEG}, "gscript.build_kernel": {"none": _LEG}, "gscript.build_property": {"none": _LEG},
    "gscript.connect2": {"none": _LEG}, "gscript.connect_ctl": {"none": _LEG}, "gscript.connect_ctl_ind": {"none": _LEG},
    "gscript.conpane_assign": {"none": _LEG}, "gscript.const_indicator_on_diagram": {"none": _LEG},
    "gscript.copy_by_index": {"none": _LEG}, "gscript.copy_into": {"none": _LEG},
    "gscript.create_const_loop_term": {"none": _LEG}, "gscript.delete_by_label": {"none": _LEG},
    "gscript.exit_loop": {"none": _LEG}, "gscript.exit_while": {"none": _LEG}, "gscript.for_loop": {"none": _LEG},
    "gscript.loop_kernel": {"none": _LEG}, "gscript.loop_par_set": {"none": _LEG}, "gscript.move_by_label": {"none": _LEG},
    "gscript.move_into_frame": {"none": _LEG}, "gscript.move_into_frame_finish": {"none": _LEG},
    "gscript.move_object": {"none": _LEG}, "gscript.move_out": {"none": _LEG}, "gscript.replace_object": {"none": _LEG},
    "gscript.set_node_label": {"none": _LEG}, "gscript.sr_init_const": {"none": _LEG},
    "gscript.tunnel_indicator": {"none": _LEG}, "gscript.tunnel_use_default": {"none": _LEG},
    "gscript.tunnel_use_default_at": {"none": _LEG}, "gscript.while_loop": {"none": _LEG},
    # ---- stagekit.Stage._op verbs (stagekit + stagexec): the op record carries the outcome --------------------------
    "stagekit.op:delete_object": {"post": {"removed": ("==", 1)}, "measure": "inline", "on_fail": "raise",
                                  "how": "build_opfsinnertunnelconnect_v0.del_node's own after-read: the uid in the "
                                         "gone set (False when already gone = a double delete)"},
    "stagekit.op:delete_wire": {"post": {"found": ("==", 1)}, "measure": "inline", "on_fail": "raise",
                                "how": "the wire uid present in del_wire's own Wire listing before the delete (0 = a "
                                       "double delete). Removal itself is checked by stagexec's next step read, not "
                                       "re-read here: one more whole-VI Wire read per delete would move the X10 model"},
    "stagekit.op:add_shift_reg": {"none": _VIA % "gscript.add_shift_reg"},
    "stagekit.op:case_frame_wire": {"none": _VIA % "gscript.case_frame_wire"},
    "stagekit.op:case_in": {"none": _VIA % "gscript.case_in"},
    "stagekit.op:case_wired": {"none": _VIA % "gscript.case_wired"},
    "stagekit.op:connect": {"none": "none - gscript.connect_nested_v2 raises at entry (its op VI was never built); the "
                                    "live route is op:connect_nested_v1"},
    "stagekit.op:connect_from_wire": {"none": "none at this level - recipes.build_opconnectfromwire_v0.connect_from_wire "
                                              "returns its readout; LVBackend._cfw stops on its err / wire delta"},
    "stagekit.op:connect_nested_v1": {"none": "none at this level - recipes.build_opconnectnested_v1.connect_nested_v1 "
                                              "returns (wire delta, ExecState, err); LVBackend.connect stops on err"},
    "stagekit.op:connect_term_uid": {"none": _VIA % "gscript.connect_term_uid"},
    "stagekit.op:connect_terminals": {"none": _VIA % "gscript.connect_terminals"},
    "stagekit.op:copy_in": {"none": "none at this level - the copied object is bound by stagexec's next read "
                                    "(bind_new)"},
    "stagekit.op:create_const_on_term": {"none": "none at this level - OpCreateConstOnTerm_v0's readout; bound by the "
                                                 "next read"},
    "stagekit.op:create_local_read": {"none": _VIA % "gscript.create_local_read"},
    "stagekit.op:create_local_write": {"none": _VIA % "gscript.create_local_write"},
    "stagekit.op:create_primitive_nested": {"none": _VIA % "gscript.create_primitive_nested"},
    "stagekit.op:drop_subvi": {"none": "none at this level - stagexec create 'subvi' measures the SubVI uid diff"},
    "stagekit.op:fs_add_frame": {"none": _VIA % "gscript.fs_add_frame"},
    "stagekit.op:indicator_nested": {"none": _VIA % "gscript.create_indicator_nested"},
    "stagekit.op:indicator_on_const": {"none": _VIA % "gscript.create_indicator_on_const"},
    "stagekit.op:loop_in": {"none": _VIA % "gscript.loop_in"},
    "stagekit.op:move_in": {"none": "none at this level - recipes.build_d1_v0.move_in; the new owner is read by stagexec's "
                                    "step diff"},
    "stagekit.op:queue_node": {"none": _VIA % "gscript.queue_node"},
    "stagekit.op:set_index_mode": {"none": _VIA % "gscript.set_index_mode"},
    "stagekit.op:stop_from_node": {"none": "none - OpStopFromNode_v0's error string is returned; the step diff checks "
                                           "the new wire"},
    "stagekit.op:struct_copy_nested": {"none": _VIA % "gscript.struct_copy_nested"},
    "stagekit.op:wire_const": {"none": _VIA % "gscript.wire_const"},
    "stagekit.op:wire_const_sr": {"none": _VIA % "gscript.wire_const_sr"},
    "stagekit.op:wire_control": {"none": _VIA % "gscript.wire_control"},
    "stagekit.op:wire_ctlsink": {"none": _VIA % "gscript.wire_ctlsink"},
    "stagekit.op:wire_indicators": {"none": _VIA % "gscript.wire_indicators"},
    "stagekit.op:wire_remove_loose_ends": {"none": _VIA % "gscript.wire_remove_loose_ends"},
    "stagekit.op:wire_sr": {"none": _VIA % "gscript.wire_sr"},
    "stagekit.op:wire_tunouter": {"none": _VIA % "gscript.wire_tunouter"},
}


def describe(fn):
    """One line for the generated capability table: the outcome contract of `fn`."""
    s = TABLE.get(fn)
    if s is None:
        return "MISSING from fncontract.TABLE"
    pre = ("; PRE " + ", ".join("%s %s %s" % (q, o, w) for q, (o, w) in PRE[fn]["pre"].items()) +
           " (measured when the call raised)") if fn in PRE else ""
    if "post" not in s:
        return str(s.get("none")) + pre
    post = ", ".join("%s %s %s" % (q, o, w) for q, (o, w) in s["post"].items())
    return "%s [%s, %s]%s" % (post, s.get("measure", "?"), s.get("on_fail", "raise") if s.get("measure") in
                              ("inline", "result") else "existing" if s.get("measure") == "existing-raise" else "caller", pre)


if __name__ == "__main__":
    import json
    import sys
    c = coverage()
    print(json.dumps(c, indent=1))
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if not any(c.values()) else "FAIL",
                                  "gates": {"pass": int(not any(c.values())), "fail": int(bool(any(c.values())))},
                                  "first_fail": None if not any(c.values()) else "coverage %s" % c, "artefacts": []}))
    sys.exit(0 if not any(c.values()) else 1)
