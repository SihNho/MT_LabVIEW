r"""gateclass - STOP gates vs LOG-only gates for stage builds: ONE table, imported by stagekit, stagexec, stage_prerun,
census_predict, errorlist_check and tools/hooks/guard_peer.py (card chat-S2; decision PD327 in docs/d1/tooling.md).

USER, 2026-10-03: "가, 나 둘 다 적용" · "+-1개는 너무 적은듯" (tolerance widened to max(5, 25 %)). Measured basis (brief_chat-S2.md):
cycles 130-140 dispatched ~76 cards, ~48 ended FAIL/BLOCKED, mostly on prediction mismatches that did not change the product
(tunnel/terminal names, +-1 counts of non-semantic classes, the check script's own arithmetic, stale self-test fixtures);
each such stop cost a return, a hypothesis review (guard_peer) and a re-issue.

THE RULE
  STOP (fatal, unchanged): created-node primitive/function class (PRIM, X17), Is Broken? / ExecState where the plan expects a
    runnable state, computation_diff / cdiff vs prediction (E3, PB), lost data wires (D, W1, TD's unwired part), input/bed md5,
    MEMSTOP, the step-end Error List per-class exactness for every class EXCEPT loose ends, and ANY count difference in a
    SEMANTIC class (function nodes of any kind, wires, ControlTerminal/indicators, constants, structures and their frames).
  LOG-only (record one JSON line in tools/bench/gate_soft_log.jsonl, continue, no per-mismatch review - the cycle's judgement
    agent reviews the file in one batch at cycle end): terminal/tunnel/face NAMES; count differences in NON-SEMANTIC classes
    (Terminal rows, Inner/Outer terminals, ParameterTerminal rows, scripting junk Invoke rows, loose-end wire counts) within
    max(5, 25 % of the predicted delta for that class); the check script's own arithmetic (label prefix ARITH); stale
    self-test fixtures (label prefix FIXTURE). Beyond the tolerance a non-semantic difference is a STOP.
  FAIL-CLOSED: a class not named in NON_SEMANTIC_CLASSES is semantic; a gate id not in GATE_TABLE is STOP; a detail the
    classifier cannot read is STOP. Tunnel OBJECT classes (LoopTunnel, FlatSequence*Tunnel, SelectorTunnel, Tunnel) are in
    neither user list and therefore STOP (card chat-S2 OPEN).

USER, 2026-10-03 (card chat-S3, PD328(b)(c)): "메모리 낮추고 터널 개수차이로 멈춤은 유지하고 터널 단자행만 다를 경우 기록하자".
  (b) Tunnel OBJECT count differences STAY STOP - TUNNEL_OBJECT_CLASSES below is the explicit list, kept disjoint from
      NON_SEMANTIC_CLASSES (asserted at import), so count_verdict on any of them is a STOP.
  (c) An E1 per-step diff (stagexec.compare) made ONLY of tunnel FACE/terminal ROWS - only_sim_terms / only_real_terms whose
      owner is a tunnel object that exists, with the same class, on BOTH sides - and no edge, dangling or unbound difference
      is LOG-only (step_face_rows_verdict -> soft log line, the run continues). A row owned by a non-tunnel object, an owner
      present on one side only (an extra/missing tunnel OBJECT), an owner whose class differs, or any wire difference
      in the same step STOPs.

Self-test: tools/bench/selftest_gateclass_s2.py, tools/bench/selftest_gateclass_s3.py.
"""
import ast
import json
import math
import os
import re
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SOFT_LOG = os.environ.get("GATE_SOFT_LOG") or os.path.join(ROOT, "tools", "bench", "gate_soft_log.jsonl")
ACTIVE = os.path.join(ROOT, "tools", "bench", "cards", "active.json")
TOL_MIN = 5            # user 2026-10-03: "+-1개는 너무 적은듯" -> max(5, 25 %)
TOL_FRAC = 0.25

# Classes whose count difference does not change the product (rows/faces of objects, scripting junk). Everything else is
# SEMANTIC (fail-closed). "LooseEnds" is the error-list / wire-count pseudo-class for loose-end wires.
NON_SEMANTIC_CLASSES = frozenset(("Terminal", "InnerTerminal", "OuterTerminal", "ParameterTerminal", "Invoke",
                                  "LooseEnds", "TunnelFace"))
# Named only for the documentation / self-test: what the user listed as semantic. Not consulted (fail-closed default).
SEMANTIC_EXAMPLES = ("Function", "GrowableFunction", "SubVI", "Node", "IndexArray", "Unbundler", "Bundler", "Local", "Wire",
                     "ControlTerminal", "DigitalNumericConstant", "ArrayConstant", "BooleanConstant", "WhileLoop", "ForLoop",
                     "CaseStructure", "FlatSequence", "Diagram")
# card chat-S3 (PD328(b)), USER 2026-10-03 "터널 개수차이로 멈춤은 유지": tunnel OBJECTS are semantic - a count difference of any
# of these classes STOPS (they are not in NON_SEMANTIC_CLASSES, asserted below). Their face ROWS are the PD328(c) LOG case.
TUNNEL_OBJECT_CLASSES = frozenset(("LoopTunnel", "FlatSequenceInnerTunnel", "FlatSequenceOuterTunnel", "SelectorTunnel",
                                   "Tunnel"))
assert not (TUNNEL_OBJECT_CLASSES & NON_SEMANTIC_CLASSES), "tunnel object classes must stay semantic (PD328(b))"


def is_tunnel_class(cls):
    c = str(cls or "")
    return c in TUNNEL_OBJECT_CLASSES or (c.startswith("FlatSequence") and c.endswith("Tunnel"))

# Gate id (the label's first token) -> kind. Order matters: first match wins. Kinds:
#   name   - terminal/tunnel/face NAME comparison                       -> LOG
#   census - per-class count comparison (detail: measured/declared)     -> per class: semantic STOP, non-semantic tolerance
#   rows   - base terminal ROWS lost vs plan deletes (detail: unwired / lost_rows / plan_deletes)
#   arith  - the check script's own arithmetic shown wrong by its own log -> LOG
#   fixture- a stale self-test fixture                                   -> LOG
#   stop   - everything else                                             -> STOP
GATE_TABLE = (
    (r"^NG\b", "name", "NG tunnel names vs the simulator's"),
    (r"^NAME-GATE\b", "name", "stagexec per-op tunnel-name gate"),
    (r"^BINDING-NAME\b", "name", "stagexec binding by (class, direction) when only names differ"),
    (r"^CEN\d*\b", "census", "new-object census per class"),
    (r"^X15\b", "census", "prerun census derived vs declared"),
    (r"^CENSUS\b", "census", "census class line"),
    (r"^TD\b", "rows", "base terminal rows lost vs plan deletes"),
    (r"^EL-LOOSE\b", "census", "Error List loose-end count"),
    (r"^ARITH\b", "arith", "the check script's own arithmetic"),
    (r"^FIXTURE\b", "fixture", "stale self-test fixture"),
)
STOP_IDS_DOC = ("PRIM", "X17", "E1", "E2", "E3", "PB", "D", "W1", "FR", "FS", "FU", "L0", "L1", "PS", "AS", "A1", "A2", "B1",
                "MEMSTOP", "HB", "K1", "STOP")


def tolerance(predicted):
    """max(5, 25 % of |predicted delta|), rounded up."""
    return max(TOL_MIN, int(math.ceil(TOL_FRAC * abs(int(predicted or 0)))))


def is_semantic(cls):
    return str(cls) not in NON_SEMANTIC_CLASSES


def count_verdict(cls, measured, predicted):
    """('ok'|'log'|'stop', rule text) for ONE class count."""
    m, p = int(measured or 0), int(predicted or 0)
    if m == p:
        return "ok", "equal"
    if is_semantic(cls):
        return "stop", "semantic class {0}: any difference stops ({1:+d} vs {2:+d})".format(cls, m, p)
    tol = tolerance(p)
    if abs(m - p) <= tol:
        return "log", "non-semantic {0}: |{1:+d} - {2:+d}| = {3} <= max(5, 25%) = {4}".format(cls, m, p, abs(m - p), tol)
    return "stop", "non-semantic {0}: |{1:+d} - {2:+d}| = {3} > max(5, 25%) = {4}".format(cls, m, p, abs(m - p), tol)


def census_verdict(measured, declared):
    """{'verdict': ok|log|stop, 'rows': [{class, measured, predicted, verdict, rule}]} over every class of either side."""
    measured, declared = dict(measured or {}), dict(declared or {})
    rows = []
    for c in sorted(set(measured) | set(declared)):
        v, rule = count_verdict(c, measured.get(c, 0), declared.get(c, 0))
        if v != "ok":
            rows.append({"class": c, "measured": int(measured.get(c, 0)), "predicted": int(declared.get(c, 0)),
                         "verdict": v, "rule": rule})
    worst = "stop" if any(r["verdict"] == "stop" for r in rows) else ("log" if rows else "ok")
    return {"verdict": worst, "rows": rows}


def gate_kind(label):
    s = str(label or "").strip()
    for rx, kind, why in GATE_TABLE:
        if re.match(rx, s):
            return kind, why
    return "stop", "not a LOG-only gate id (fail-closed default)"


def _as_obj(detail):
    """A dict/list detail, or a str that holds one (a printed Python/JSON literal after the label). None if unreadable."""
    if isinstance(detail, (dict, list)):
        return detail
    s = str(detail or "")
    i = s.find("{")
    if i < 0:
        return None
    for cand in (s[i:], s[i:s.rfind("}") + 1]):
        for parse in (ast.literal_eval, json.loads):
            try:
                o = parse(cand)
                if isinstance(o, dict):
                    return o
            except Exception:                                                      # noqa: BLE001
                pass
    return None


def _rows_verdict(d):
    """TD: unwired (a base terminal that was wired lost its wire) = a lost data wire -> STOP. Otherwise the lost-row set vs the
    plan's delete set is a Terminal-row count difference -> tolerance on the symmetric difference, predicted = plan deletes."""
    if not isinstance(d, dict) or "unwired" not in d:
        return "stop", "TD detail without an 'unwired' list (cannot separate a lost wire from a row count)", []
    if d.get("unwired"):
        return "stop", "TD: base terminal(s) lost their wire {0} (lost data wire)".format(list(d["unwired"])[:6]), []
    lost, plan = d.get("lost_rows"), d.get("plan_deletes")
    if lost is None:
        return "stop", "TD detail without lost_rows", []
    plan = list(plan or [])
    if len(lost) >= 20 or len(plan) >= 20:
        return "stop", "TD lists truncated at 20 in the detail - the count cannot be read (fail-closed)", []
    sym = sorted(set(lost) ^ set(plan))
    if not sym:
        return "ok", "equal", []
    v, rule = count_verdict("Terminal", len(plan) + len(sym), len(plan))
    rule = "Terminal rows lost {0} vs plan deletes {1}, symmetric difference {2}: {3}".format(len(lost), len(plan), sym[:8], rule)
    return v, rule, [{"class": "Terminal", "measured": len(lost), "predicted": len(plan), "verdict": v, "rule": rule,
                      "diff": sym[:20]}]


def classify_gate(label, detail=None, kind=None):
    """{'verdict': 'stop'|'log', 'kind', 'rule', 'rows'} for a FAILED gate. Never 'ok': the caller already saw ok=False;
    a census/rows detail that reads equal is still a STOP (the gate failed for a reason this table cannot see)."""
    k, why = (kind, "declared kind {0}".format(kind)) if kind else gate_kind(label)
    if k in ("name", "arith", "fixture"):
        return {"verdict": "log", "kind": k, "rule": why, "rows": []}
    if k == "census":
        d = _as_obj(detail)
        if isinstance(d, dict) and "measured" in d and "declared" in d and isinstance(d["measured"], dict):
            cv = census_verdict(d["measured"], d["declared"])
            if cv["verdict"] == "log":
                return {"verdict": "log", "kind": k, "rule": "; ".join(r["rule"] for r in cv["rows"])[:400], "rows": cv["rows"]}
            bad = [r["rule"] for r in cv["rows"] if r["verdict"] == "stop"] or ["census detail reads equal (fail-closed)"]
            return {"verdict": "stop", "kind": k, "rule": "; ".join(bad)[:400], "rows": cv["rows"]}
        return {"verdict": "stop", "kind": k, "rule": "census detail unreadable (fail-closed)", "rows": []}
    if k == "rows":
        v, rule, rows = _rows_verdict(_as_obj(detail))
        return {"verdict": "log" if v == "log" else "stop", "kind": k, "rule": rule, "rows": rows}
    return {"verdict": "stop", "kind": "stop", "rule": why, "rows": []}


# ------------------------------------------------------------------------------------------------ the soft log
def _context():
    card = os.environ.get("GATE_CARD")
    if not card:
        try:
            with open(ACTIVE, encoding="utf-8") as f:
                a = json.load(f)
            recs = [v for v in (a.values() if isinstance(a, dict) else []) if isinstance(v, dict)]
            recs.sort(key=lambda v: str(v.get("since") or ""))
            card = recs[-1].get("id") if recs else None
        except Exception:                                                          # noqa: BLE001
            card = None
    cyc = os.environ.get("GATE_CYCLE")
    if not cyc and card:
        m = re.match(r"^(\d+)", str(card))
        cyc = m.group(1) if m else None
    return (int(cyc) if cyc and str(cyc).isdigit() else cyc), card


def _script():
    import sys
    return os.path.basename(sys.argv[0]) if sys.argv and sys.argv[0] else None


def soft_record(gate, cls, expected, measured, rule, script=None, path=None):
    """Append ONE JSON line: {ts, cycle, card, script, gate, expected, measured, class, rule}. Never raises."""
    cyc, card = _context()
    rec = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "cycle": cyc, "card": card, "script": script or _script(),
           "gate": str(gate)[:200], "expected": expected, "measured": measured, "class": cls, "rule": str(rule)[:400]}
    try:
        with open(path or SOFT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=True, default=str) + "\n")
    except OSError:
        pass
    return rec


def record_classified(label, c, detail=None, script=None, path=None):
    """One soft line per non-equal class row (census/rows), or one line for a name/arith/fixture gate."""
    out = []
    if c.get("rows"):
        for r in c["rows"]:
            out.append(soft_record(label, r["class"], r["predicted"], r["measured"], r["rule"], script, path))
    else:
        d = _as_obj(detail)
        exp = mea = None
        if isinstance(d, dict):
            exp = d.get("sim", d.get("expected", d.get("declared")))
            mea = d.get("real", d.get("measured"))
        out.append(soft_record(label, c.get("kind"), exp if exp is not None else None,
                               mea if mea is not None else str(detail)[:300], c.get("rule"), script, path))
    return out


# ------------------------------------------------------------------------------------------------ log lines (guard_peer)
FAIL_LINE_RE = re.compile(r"^\s*(?:->\s*)?\*{0,2}FAIL\*{0,2}\s+(.*)$")
HARD_MARK_RE = re.compile(r"OBSERVED:?\s*EXC|Traceback \(most recent call last\)|VERDICT:\s*BROKEN|^BGRUN TIMEOUT|^STALL:"
                          r"|STOP at gate|ExecStop|MEMSTOP", re.M)


def classify_line(line):
    """'log' | 'stop' for one printed `  FAIL  <label>  <detail>` line (stagekit's format); anything else -> 'stop'."""
    m = FAIL_LINE_RE.match(str(line or ""))
    if not m:
        return "stop"
    body = m.group(1)
    parts = body.split("  ", 1)
    label, detail = parts[0], (parts[1] if len(parts) > 1 else "")
    if "{" in label and not detail:                          # a label without the two-space separator
        i = label.find("{")
        label, detail = label[:i], label[i:]
    return classify_gate(label.strip(), detail)["verdict"]


def soft_only(segment, results):
    """True when a failed run's ONLY failures are LOG-only gate lines: no hard marker (exception, timeout, STOP at gate, ...),
    at least one `FAIL` gate line, every such line classifies 'log', and their number equals the failing RESULT lines'
    gates.fail sum. `results` = protocol.all_result_lines(segment)."""
    seg = segment or ""
    if HARD_MARK_RE.search(seg):
        return False
    fails = [ln for ln in seg.splitlines() if FAIL_LINE_RE.match(ln)]
    if not fails or any(classify_line(ln) != "log" for ln in fails):
        return False
    bad = [d for d in results or [] if d.get("status") not in ("PASS", "SKIP") or int((d.get("gates") or {}).get("fail", 1)) > 0]
    if not bad:
        return False
    return sum(int((d.get("gates") or {}).get("fail", 0)) for d in bad) == len(fails)


# ------------------------------------------------------------------------------------------------ address-only (PD337(b))
# card chat-S5 (the user's "S1" item 2): a failure that tier (a) of the mismatch check (tools/addrcheck.py) classifies as an
# ADDRESS or FORMAT mismatch - a plan address that does not bind to the real terminal table, or a prose field over a length
# limit - is a plan-text problem with a mechanical fix, not a failed hypothesis: it owes no hypothesis review. Any other
# failing line, an exception marker, a timeout or a STOP still owes one.
ADDR_FAIL_RE = re.compile(r"ADDRESS-UNRESOLVED|does not bind uniquely|plan does not validate against stageplan/1: \$[^:\s]*"
                          r"\.(?:why|goal|note): \d+ chars > limit")


def address_only(segment, results):
    """True when every failing RESULT line's first_fail, and every printed FAIL / GATE FAIL line, is an address/format
    mismatch (ADDR_FAIL_RE) or a LOG-only gate line, with no hard marker. `results` = protocol.all_result_lines(segment)."""
    seg = segment or ""
    if HARD_MARK_RE.search(seg):
        return False
    bad = [d for d in results or [] if d.get("status") not in ("PASS", "SKIP") or int((d.get("gates") or {}).get("fail", 1)) > 0]
    if not bad or any(not ADDR_FAIL_RE.search(str(d.get("first_fail") or "")) for d in bad):
        return False
    for ln in seg.splitlines():
        if FAIL_LINE_RE.match(ln) or re.match(r"^\s*GATE FAIL\b", ln):
            if not ADDR_FAIL_RE.search(ln) and classify_line(ln) != "log":
                return False
    return True


# ------------------------------------------------------------------------------------------------ Error List
LOOSE_RE = re.compile(r"loose\s*ends?", re.I)


def errorlist_verdict(extra, missing, predicted_loose=0):
    """Error List per-class exactness is STOP for every class EXCEPT loose ends. extra/missing = item texts.
    -> ('ok'|'log'|'stop', rule)."""
    extra, missing = list(extra or []), list(missing or [])
    if not extra and not missing:
        return "ok", "equal"
    other = [x for x in extra + missing if not LOOSE_RE.search(str(x or ""))]
    if other:
        return "stop", "non-loose-end Error List class differs: {0}".format([str(x)[:60] for x in other[:4]])
    n, tol = len(extra) + len(missing), tolerance(predicted_loose)
    return ("log" if n <= tol else "stop"), "Error List loose ends extra {0} missing {1}: {2} item(s) {3} max(5, 25%) = {4}".format(
        len(extra), len(missing), n, "<=" if n <= tol else ">", tol)


# ------------------------------------------------------------------------------------------------ E1 step diff (PD328(c))
STEP_HARD_KEYS = ("only_sim_edges", "only_real_edges", "dangling_sim_only", "dangling_real_only", "unbound")


def step_face_rows_verdict(d, sim_rows, real_rows):
    """card chat-S3 (PD328(c), user 2026-10-03 "터널 단자행만 다를 경우 기록하자"): verdict on ONE E1 per-step diff
    (stagexec.compare's dict). sim_rows = the simulated terminal rows AFTER binding translation, real_rows = the real read;
    each row {term_uid, owner_uid, owner_class, term_name, ...}. Returns {'verdict': 'log'|'stop', 'rule', 'rows'}:
    'log' only when the diff is ONLY terminal rows (only_sim_terms / only_real_terms) on tunnel faces whose owner tunnel
    exists with the same class on BOTH sides, and nothing else differs (no edge, dangling or unbound entry). Fail-closed."""
    d = d or {}
    hard = [k for k in STEP_HARD_KEYS if d.get(k)]
    if hard:
        return {"verdict": "stop", "rule": "step diff has wire/binding differences {0}".format(hard), "rows": []}
    os_, or_ = list(d.get("only_sim_terms") or []), list(d.get("only_real_terms") or [])
    if not os_ and not or_:
        return {"verdict": "stop", "rule": "no terminal-row difference to classify (fail-closed)", "rows": []}
    s_term = dict((r["term_uid"], r) for r in sim_rows or [])
    r_term = dict((r["term_uid"], r) for r in real_rows or [])
    s_own = dict((r["owner_uid"], r["owner_class"]) for r in sim_rows or [])
    r_own = dict((r["owner_uid"], r["owner_class"]) for r in real_rows or [])
    rows, bad = [], []
    for side, uids, mine, other in (("only_sim", os_, s_term, r_own), ("only_real", or_, r_term, s_own)):
        for t in uids:
            r = mine.get(t)
            if r is None:
                bad.append("{0} term #{1}: row not found (fail-closed)".format(side, t))
                continue
            o, c = r.get("owner_uid"), r.get("owner_class")
            rows.append({"side": side, "term_uid": t, "owner_uid": o, "owner_class": c, "term_name": r.get("term_name"),
                         "term_class": r.get("term_class")})
            if not is_tunnel_class(c):
                bad.append("{0} term #{1} on a {2} (not a tunnel face)".format(side, t, c))
            elif o not in other:
                bad.append("{0} term #{1}: tunnel #{2} ({3}) exists on one side only (tunnel OBJECT difference, PD328(b))".format(
                    side, t, o, c))
            elif other[o] != c:
                bad.append("{0} term #{1}: tunnel #{2} class {3} vs {4} on the other side".format(side, t, o, c, other[o]))
    if bad:
        return {"verdict": "stop", "rule": "; ".join(bad[:6])[:400], "rows": rows}
    return {"verdict": "log", "rule": "tunnel face rows only: {0} sim-only, {1} real-only on tunnel(s) {2} (PD328(c))".format(
        len(os_), len(or_), sorted(set(r["owner_uid"] for r in rows))[:8]), "rows": rows}
