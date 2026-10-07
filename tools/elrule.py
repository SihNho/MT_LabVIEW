r"""elrule - the FIXED Error List predictor (card 143-3, PD333(b)) as a SHARED module (card chat-S5, PD337(c); moved here
from tools/bench/prep_c143_3_elrule.py, which now re-exports it), plus the BY-DESIGN verdict errorlist_check uses on a
good result. OFFLINE, pure (reads JSON states only, no LabVIEW).

The rule, as SETS of item keys so an item that closes is debited and none is counted twice:
  L  ('local', node)   a Local whose every terminal row is unwired      -> EL "Local Variable ...: not connected to anything"
  C  ('cond', body)    a While body Diagram's '' SINK row unwired        -> EL "While Loop: Conditional terminal is not wired"
                       (WhileLoop owns no terminal row; its cond terminal is the '' sink row of its body Diagram, 143-2 run 1)
  SR ('sr', rsr)       a RightShiftRegister whose InnerTerminal SINK row is unwired -> EL "Shift Register: unwired from inside the
                       loop" (bench card 144-a2-2 in arm A13K, measured on the s03 scratch; ported to main by card chat-T5, PD349).
                       An unwired OuterTerminal (source) of the RSR and the LeftShiftRegister's unwired InnerTerminal (source) give
                       NO item (measured: 4 such rows, 0 items). Applies to every RSR, created or base.
  A  ('input', node)   a node in `created` (made by this or an earlier counted session), not an L item, with an unwired sink
                       (ControlTerminal rows excluded, as PD322(e))  -> EL "... contains unwired or bad terminal"
                       NARROWED by terminal CLASS (PD349): a sink row that is already the C row (a While body Diagram's '' cond
                       row) or the SR row (an RSR InnerTerminal sink) is not counted again as an A item; the node is A only when
                       ANOTHER unwired sink remains (measured: the created body #29699 whose only unwired sink is its cond row gave
                       ONE item, the cond item - the old rule counted it as C AND A, s03 56 vs measured 55 in all four bench arms;
                       the created RSRs gave only the SR item). No per-uid exception.
                       SUBVI CALLS (card 145-a2-2, PD351(c)): a created node of owner_class 'SubVI' (the class the simulator
                       writes on its terminal rows, the same field every other class here is told apart by) is an A item ONLY
                       if one of its unwired sinks is a connector-pane terminal MEASURED Required (rule 1) in
                       tools/bench/subvi_requiredness.json (measured: every RingPickSlot_v0 / RingSeqCheck_v0 terminal is
                       Recommended, and the s04 read 58 has no item for PS1/SQ1 where the old rule predicted 60). Which VI a
                       node calls comes from the plan's create action ('subvi_path', bound through sym 'new:<as>'); a row maps to
                       its pane index by position when the node's rows align with the table by name, else by a unique name.
                       A SubVI whose VI is unknown or missing from the table, or a row not in the table, is reported in
                       `uncertain_subvi_terminals` - never counted, never defaulted.
  items(start) are already in the base total; predicted = base_total + |items(end) - items(start)| - |items(start) - items(end)|.
  Base nodes with a newly unwired INPUT that are not C or SR are REPORTED (`uncertain`), never counted (an optional input gives
  no item).

BY DESIGN (card chat-S5, the user's "S1" item 3, 143-1/143-2; SR added by PD349): a SESSION BOUNDARY leaves a Local read whose
consumer the next session wires (L), a While loop whose stop wire the next session re-creates (C), and a shift register whose
inner sink the next session wires (SR). When every STOP gate passed and the ONLY Error List difference is extra items of those
classes, by_design_verdict re-derives the prediction with this rule from the
plan's own simulated step files; it is 'log' (record to gate_soft_log.jsonl, the card is not FAIL) only when
  (1) nothing is missing, (2) every extra item text is an L, C or SR item, (3) the per-class count of extras <= the re-derived
  NEW items of that class, and (4) the re-derived total == the measured item count. (SR is accepted under exactly the same
  (3) and (4) as L and C; no other branch changed.)
Anything else - another class, a missing item, a count the rule does not reproduce, no plan/step files - is 'stop'.
Self-test: tools/bench/selftest_elpred.py (rule), tools/bench/selftest_s5.py (by-design verdict, 143-1 replay).
"""
import collections
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REQ_PATH = os.path.join(ROOT, "tools", "bench", "subvi_requiredness.json")   # MEASURED pane rules (card 145-a2-2)


def load_requiredness(path=None):
    """The measured SubVI requiredness table ({'vis': {file name: {'terminals': [...]}}}); an unreadable file gives an EMPTY
    table, so every created SubVI becomes uncertain (never a default rule)."""
    try:
        return json.load(open(path or REQ_PATH, encoding="utf-8"))
    except (OSError, ValueError):
        return {"vis": {}}


def subvis_from_plan(plan, *states):
    """{uid: VI file name} for every SubVI the plan creates ('create' action, class SubVI, 'subvi_path'), bound through the
    sim states' sym map ('new:<as>' -> uid)."""
    sym = {}
    for s in states:
        sym.update((s or {}).get("sym") or {})
    out = {}
    for a in (plan or {}).get("actions") or []:
        if a.get("op") == "create" and a.get("class") == "SubVI" and a.get("subvi_path") and a.get("as"):
            u = sym.get("new:" + a["as"])
            if isinstance(u, int):
                out[u] = os.path.basename(str(a["subvi_path"]).replace("\\", "/"))
    return out


def subvi_rules(rs, vi, table):
    """([rule or None per row of rs], how) - the measured pane rule of each terminal row of one SubVI node."""
    ent = ((table or {}).get("vis") or {}).get(vi) if vi else None
    if not ent:
        return [None] * len(rs), ("subvi not in table" if vi else "subvi identity unknown")
    terms = ent.get("terminals") or []
    names = [r.get("term_name") or "" for r in rs]
    if len(rs) == len(terms) and names == [t.get("name") or "" for t in terms]:
        return [t.get("rule") for t in terms], "pane index by position"
    out = []
    for n in names:
        hit = [t for t in terms if n and (t.get("name") or "") == n]
        out.append(hit[0].get("rule") if len(hit) == 1 else None)
    return out, "pane terminal by unique name"


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


def items(state, bodies, created=(), subvis=None, table=None):
    """(set of item keys, detail dict) for one state (sim step state or graph json: both carry `terminals` rows).
    subvis = {uid: VI file name} of created SubVI calls; table = the measured requiredness table (load_requiredness()).
    Uncertain SubVI rows go to detail['uncertain_subvi'] = [[uid, vi, [[term_name, why], ...]], ...]."""
    subvis = subvis or {}
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
        claimed = set()                     # sink rows already an item of class C or SR: never also an A item (PD349)
        if cls == "Diagram" and u in bodies:
            for r in rs:
                if not r.get("is_source") and r.get("term_name") == "" and not r.get("wire_uid"):
                    out.add(("cond", u))
                    det["cond"].append([u, bodies[u], int(r["term_uid"])])
                    claimed.add(int(r["term_uid"]))
        if cls == "RightShiftRegister":
            inner = [r for r in rs if not r.get("is_source") and r.get("term_class") == "InnerTerminal" and not r.get("wire_uid")]
            if inner:
                out.add(("sr", u))
                det["sr"].append([u, [int(r["term_uid"]) for r in inner]])
                claimed.update(int(r["term_uid"]) for r in inner)
        if u in created and cls == "SubVI":            # card 145-a2-2: only a MEASURED Required pane terminal is an item
            vi = subvis.get(u)
            rules, how = subvi_rules(rs, vi, table)
            req, unc = [], []
            for r, rule in zip(rs, rules):
                if r.get("is_source") or r.get("wire_uid") or r.get("term_class") == "ControlTerminal" \
                        or int(r["term_uid"]) in claimed:
                    continue
                if rule is None:
                    unc.append([r.get("term_name"), how])
                elif rule == 1:
                    req.append(r.get("term_name"))
            if unc:
                det["uncertain_subvi"].append([u, vi, unc])
            if req:
                out.add(("input", u))
                det["input"].append([u, req])
        elif u in created:
            unw = [r.get("term_name") for r in rs if not r.get("is_source") and not r.get("wire_uid")
                   and r.get("term_class") != "ControlTerminal" and int(r["term_uid"]) not in claimed]
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


def predict(st0, last, base_total, created, carry=(), extra_owner_states=(), subvis=None, table=None):
    """The fixed EL prediction of one session: st0 = its base state (step_00), last = its simulated end, created = uids of the
    nodes this session makes (sim symbols), carry = uids an earlier session's prediction counted as A items (still open),
    subvis = {uid: VI file name} of created SubVI calls (subvis_from_plan), table = requiredness table (default: the file)."""
    bodies = owners_map(st0, last, *extra_owner_states)
    table = load_requiredness() if table is None else table
    i0, d0 = items(st0, bodies, carry, subvis, table)
    i1, d1 = items(last, bodies, set(created) | set(carry), subvis, table)
    d0.pop("uncertain_subvi", None)
    unc_subvi = d1.pop("uncertain_subvi", [])
    new, closed = sorted(i1 - i0), sorted(i0 - i1)
    u0, u1 = unwired_inputs(st0), unwired_inputs(last)
    cond_bodies = set(k[1] for k in i1 if k[0] in ("cond", "sr"))     # owners whose newly unwired sink is a C or SR item
    uncertain = sorted([u, u1[u]] for u in u1 if u not in u0 and u not in set(created) and u not in cond_bodies)
    return {"base_total": base_total, "new_items": [list(k) for k in new], "closed_items": [list(k) for k in closed],
            "predicted_total": base_total + len(new) - len(closed), "open_at_start": [list(k) for k in sorted(i0)],
            "open_at_end": [list(k) for k in sorted(i1)], "detail_start": d0, "detail_end": d1,
            "uncertain_base_newly_unwired_inputs": uncertain, "uncertain_subvi_terminals": unc_subvi, "while_bodies": len(bodies),
            "rule": "PD333(b) fixed predictor (tools/elrule.py; SR class + narrowed A by PD349; SubVI A by measured pane rule, "
                    "PD351(c)): L unwired Local + C While cond + SR RightShiftRegister with an unwired inner sink + A created node "
                    "with an unwired input other than its C/SR row (a created SubVI: only a MEASURED Required pane terminal, "
                    "tools/bench/subvi_requiredness.json; unknown = uncertain, not counted); items(end) - items(start) added, "
                    "items(start) - items(end) debited"}


# ------------------------------------------------------------------------------------------------ by design (PD337(c))
L_RE = re.compile(r"local\s*variable.*not\s*connected|local\s*or\s*global\s*variable\s*is\s*not\s*wired", re.I | re.S)  # 2nd: empty-raw row, card 145-a2-5
C_RE = re.compile(r"while\s*loop.*conditional\s*terminal.*not\s*wired", re.I | re.S)
SR_RE = re.compile(r"shift\s*register.*unwired\s*from\s*inside", re.I | re.S)


def item_class(text):
    """'local' | 'cond' | 'sr' | None for one Error List item text (raw + detail)."""
    t = str(text or "")
    if L_RE.search(t):
        return "local"
    if C_RE.search(t):
        return "cond"
    if SR_RE.search(t):
        return "sr"
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
    return predict(st0, last, base_total, made, subvis=subvis_from_plan(plan, st0, last))


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
# ---
# labview: none
# hardware: none
# ---
