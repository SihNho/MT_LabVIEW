r"""elrule - the FIXED Error List predictor (card 143-3, PD333(b)) as a SHARED module (card chat-S5, PD337(c); moved here
from tools/bench/prep_c143_3_elrule.py, which now re-exports it), plus the BY-DESIGN verdict errorlist_check uses on a
good result. OFFLINE, pure (reads JSON states only, no LabVIEW).

The rule, as SETS of item keys so an item that closes is debited and none is counted twice:
  L  ('local', node)   a Local whose every terminal row is unwired      -> EL "Local Variable ...: not connected to anything"
  C  ('cond', body)    a While body Diagram's '' SINK row unwired        -> EL "While Loop: Conditional terminal is not wired"
                       (WhileLoop owns no terminal row; its cond terminal is the '' sink row of its body Diagram, 143-2 run 1)
  A  ('input', node)   a node in `created` (made by this or an earlier counted session), not an L item, with an unwired sink
                       (ControlTerminal rows excluded, as PD322(e))  -> EL "... contains unwired or bad terminal"
  items(start) are already in the base total; predicted = base_total + |items(end) - items(start)| - |items(start) - items(end)|.
  Base nodes with a newly unwired INPUT that are not C are REPORTED (`uncertain`), never counted (an optional input gives no item).

BY DESIGN (card chat-S5, the user's "S1" item 3, 143-1/143-2): a SESSION BOUNDARY leaves a Local read whose consumer the next
session wires (L) and a While loop whose stop wire the next session re-creates (C). When every STOP gate passed and the ONLY
Error List difference is extra items of those two classes, by_design_verdict re-derives the prediction with this rule from the
plan's own simulated step files; it is 'log' (record to gate_soft_log.jsonl, the card is not FAIL) only when
  (1) nothing is missing, (2) every extra item text is an L or C item, (3) the per-class count of extras <= the re-derived
  NEW items of that class, and (4) the re-derived total == the measured item count.
Anything else - another class, a missing item, a count the rule does not reproduce, no plan/step files - is 'stop'.
Self-test: tools/bench/selftest_elpred.py (rule), tools/bench/selftest_s5.py (by-design verdict, 143-1 replay).
"""
import collections
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def owners_map(*states):
    """{body_uid: loop_uid} for every Diagram owned by a WhileLoop, merged over the given states/graphs' `owners` maps."""
    out = {}
    for s in states:
        for d, v in ((s or {}).get("owners") or {}).items():
            try:
                if v and v[0] == "WhileLoop":
                    out[int(d)] = int(v[1])
            except (TypeError, ValueError, IndexError):
                pass
    return out


def items(state, bodies, created=()):
    """(set of item keys, detail dict) for one state (sim step state or graph json: both carry `terminals` rows)."""
    rows = collections.defaultdict(list)
    for r in state.get("terminals") or []:
        rows[int(r["owner_uid"])].append(r)
    created = set(int(u) for u in created)
    out, det = set(), collections.defaultdict(list)
    for u, rs in rows.items():
        cls = rs[0].get("owner_class")
        if cls == "Local" and all(not r.get("wire_uid") for r in rs):
            out.add(("local", u))
            det["local"].append([u, [r.get("term_name") for r in rs]])
            continue
        if cls == "Diagram" and u in bodies:
            for r in rs:
                if not r.get("is_source") and r.get("term_name") == "" and not r.get("wire_uid"):
                    out.add(("cond", u))
                    det["cond"].append([u, bodies[u], int(r["term_uid"])])
        if u in created:
            unw = [r.get("term_name") for r in rs if not r.get("is_source") and not r.get("wire_uid")
                   and r.get("term_class") != "ControlTerminal"]
            if unw:
                out.add(("input", u))
                det["input"].append([u, unw])
    return out, dict(det)


def unwired_inputs(state):
    out = collections.defaultdict(list)
    for r in state.get("terminals") or []:
        if not r.get("is_source") and not r.get("wire_uid") and r.get("term_class") != "ControlTerminal":
            out[int(r["owner_uid"])].append(r.get("term_name"))
    return out


def predict(st0, last, base_total, created, carry=(), extra_owner_states=()):
    """The fixed EL prediction of one session: st0 = its base state (step_00), last = its simulated end, created = uids of the
    nodes this session makes (sim symbols), carry = uids an earlier session's prediction counted as A items (still open)."""
    bodies = owners_map(st0, last, *extra_owner_states)
    i0, d0 = items(st0, bodies, carry)
    i1, d1 = items(last, bodies, set(created) | set(carry))
    new, closed = sorted(i1 - i0), sorted(i0 - i1)
    u0, u1 = unwired_inputs(st0), unwired_inputs(last)
    cond_bodies = set(k[1] for k in i1 if k[0] == "cond")
    uncertain = sorted([u, u1[u]] for u in u1 if u not in u0 and u not in set(created) and u not in cond_bodies)
    return {"base_total": base_total, "new_items": [list(k) for k in new], "closed_items": [list(k) for k in closed],
            "predicted_total": base_total + len(new) - len(closed), "open_at_start": [list(k) for k in sorted(i0)],
            "open_at_end": [list(k) for k in sorted(i1)], "detail_start": d0, "detail_end": d1,
            "uncertain_base_newly_unwired_inputs": uncertain, "while_bodies": len(bodies),
            "rule": "PD333(b) fixed predictor (tools/elrule.py): L unwired Local + C While cond + A created node with "
                    "an unwired input; items(end) - items(start) added, items(start) - items(end) debited"}


# ------------------------------------------------------------------------------------------------ by design (PD337(c))
L_RE = re.compile(r"local\s*variable.*not\s*connected", re.I | re.S)
C_RE = re.compile(r"while\s*loop.*conditional\s*terminal.*not\s*wired", re.I | re.S)


def item_class(text):
    """'local' | 'cond' | None for one Error List item text (raw + detail)."""
    t = str(text or "")
    if L_RE.search(t):
        return "local"
    if C_RE.search(t):
        return "cond"
    return None


def _j(p):
    return json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))


def session_prediction(plan, base_total):
    """The fixed-rule prediction of the session a finalized stageplan describes (its first/last step files), or None."""
    sf = ((plan or {}).get("finalized") or {}).get("step_files") or []
    if len(sf) < 2:
        return None
    st0, last = _j(sf[0]["path"])["state"], _j(sf[-1]["path"])["state"]
    made = (set(int(u) for u in (last.get("sym") or {}).values() if isinstance(u, int))
            - set(int(u) for u in (st0.get("sym") or {}).values() if isinstance(u, int)))
    return predict(st0, last, base_total, made)


def by_design_verdict(extra, missing, measured_total, base_total, plan=None, prediction=None):
    """('log'|'stop', rule, detail) - see the module docstring. `extra`/`missing` = item texts from errorlist_check.compare;
    measured_total = the item count read; base_total = the total the expected file predicted; plan = the bed's finalized
    stageplan (its step files give the re-derivation) or a ready `prediction` (predict()'s dict)."""
    extra, missing = list(extra or []), list(missing or [])
    if missing:
        return "stop", "Error List items MISSING {0} - never by design".format([str(x)[:60] for x in missing[:3]]), {}
    if not extra:
        return "stop", "no extra item to explain (fail-closed)", {}
    cls = [item_class(x) for x in extra]
    if None in cls:
        return "stop", "extra item(s) of another class {0}".format([str(x)[:60] for x, c in zip(extra, cls) if c is None][:3]), {}
    try:
        P = prediction or session_prediction(plan, base_total)
    except Exception as e:                                                         # noqa: BLE001
        return "stop", "re-derivation failed: {0}: {1}".format(type(e).__name__, str(e)[:160]), {}
    if not P:
        return "stop", "no plan step files to re-derive the prediction from (fail-closed)", {}
    newc = collections.Counter(k[0] for k in P["new_items"])
    have = collections.Counter(cls)
    short = dict((c, (n, newc.get(c, 0))) for c, n in have.items() if n > newc.get(c, 0))
    det = {"extra_classes": dict(have), "rederived_new": dict(newc), "rederived_total": P["predicted_total"],
           "measured_total": measured_total, "base_total": base_total, "new_items": P["new_items"],
           "closed_items": P["closed_items"]}
    if short:
        return "stop", "extras exceed the re-derived new items per class {0}".format(short), det
    if P["predicted_total"] != measured_total:
        return "stop", "re-derived total {0} != measured {1}".format(P["predicted_total"], measured_total), det
    return "log", ("by-design session-boundary items {0}: re-derived prediction {1} == measured {2} (fixed rule tools/elrule.py, "
                   "PD337(c))").format(dict(have), P["predicted_total"], measured_total), det
