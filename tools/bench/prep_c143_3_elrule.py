r"""prep_c143_3_elrule - card 143-3 (PD333(b)): the FIXED Error List predictor, one function shared by prep_c142_5_pred.py,
prep_c143_p1_pred.py, prep_c143_3_pred.py and selftest_elpred.py. OFFLINE, pure (reads JSON states only, no LabVIEW).

Existed first (checked): the per-script `unwired_in()` of prep_c142_5_pred.py:65-87 / prep_c143_p1_pred.py:68-89 (PD322(e): one item
per CREATED node with an unwired INPUT; base nodes newly unwired only in an `alternative_total`; nodes closed at the end listed but
never debited). 143-2 + review c143-2-el53 (verdict supported) measured why s02 gave 53, not 51: a Local READ owns one SOURCE
terminal (never counted) and the cut While conditional terminal went only into the alternative.

The rule, as SETS of item keys so an item that closes is debited and none is counted twice:
  L  ('local', node)   a Local whose every terminal row is unwired      -> EL "Local Variable ...: not connected to anything"
  C  ('cond', body)    a While body Diagram's '' SINK row unwired        -> EL "While Loop: Conditional terminal is not wired"
                       (WhileLoop owns no terminal row; its cond terminal is the '' sink row of its body Diagram, 143-2 run 1)
  A  ('input', node)   a node in `created` (made by this or an earlier counted session), not an L item, with an unwired sink
                       (ControlTerminal rows excluded, as PD322(e))  -> EL "... contains unwired or bad terminal"
  items(start) are already in the base total; predicted = base_total + |items(end) - items(start)| - |items(start) - items(end)|.
  Base nodes with a newly unwired INPUT that are not C are REPORTED (`uncertain`), never counted (an optional input gives no item).
"""
import collections


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
            "rule": "PD333(b) fixed predictor (tools/bench/prep_c143_3_elrule.py): L unwired Local + C While cond + A created node with "
                    "an unwired input; items(end) - items(start) added, items(start) - items(end) debited"}
