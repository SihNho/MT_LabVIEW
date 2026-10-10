# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_163-a1-3.md
# ---
r"""prep_c163_a1_3_el - card 163-a1-3 (OFFLINE, json only): the PREDICTED step-3-end Error List of P5-2 step 3 (group I = A41..A52,
docs/d1/ring-p5b.md PD396(d)) -> tools/bench/errorlist_predicted_D1_ring_p5s02c_end.json, item by item from the 53-item expected file of the
f9ae7751 bed (errorlist_expected_D1_ring_p5s02b_20261010_105511.json 60e02787, NOT edited; 52 entries, one with count 2):
  CLEARED  = every row whose object uid is a BASE object a group-I action names (loop / body / parent / diagram / a dict end's uid or term uid);
             a row whose clears_by.step == 3 names an action that is NOT in plan_ring_p5s02c.json (A70 / A80 belong to a later step after the
             PD396(c) I-alone split) is a STALE expectation: reported, the row stays STANDING (entry unchanged);
  RAISED   = tools/elrule.py predict (the FIXED rule, no second classifier) on the plan's step_00 -> step_12 sim states, each new item tied to the
             action that made its owner (sim symbol map) or wires one of its terminals;
  UNPREDICTED:<action> = each connect_term_uid register_end_case_border op group (read from the session compile): the same verb on step 2 (A32 /
             A39) left +2 'Wire has loose ends.' items that no read attributes by uid (diag_c162_a1_2_facts.md, PD396(a)(2)); the scratch measures it;
  STANDING = the rest, entries unchanged. Classes by stagekit.el_class; checker errorlist_check.compare (shared calls). Flow of prep_c160_c3_1_el.py.
PREDICTION CONTRACT: M0 pins (expected 60e02787, read == measured_md5, plan 930699ec, session e8daf1fe, graph 431cfd83); B compare(read 53, the 53-row
  file) extra 0 missing 0; CL cleared rows each mapped to a group-I action (0 expected); ST stale step-3 rows listed (items 4, 6, 7, 8, 49, 50
  expected: A70 / A80 not in the plan); R elrule new / closed printed, every new item attributed; U unpredicted = the two register_end_case_border
  groups; F compare(read minus cleared, predicted) extra 0, missing == raised; PC per-class predicted total == item total; W file written.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c163_a1_3_el.log -- py -u tools/bench/prep_c163_a1_3_el.py"""
import collections, copy, json, os, sys                                                   # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import elrule as ELR                                                                        # noqa: E402  the fixed rule (shared)
import errorlist_check as EC                                                                # noqa: E402  compare (shared, offline import)
import stagekit as K                                                                        # noqa: E402  el_class (shared)
import prep_c156_a1_1_lib as L                                                              # noqa: E402  Gate (shared)
md5, rel, J = L.md5, L.rel, L.J
B = os.path.join(ROOT, "tools", "bench")
PLAN, SESS = os.path.join(B, "plan_ring_p5s02c.json"), os.path.join(B, "prep_c163_a1_2_session.json")
EXPF = os.path.join(B, "errorlist_expected_D1_ring_p5s02b_20261010_105511.json")
OUT = os.path.join(B, "errorlist_predicted_D1_ring_p5s02c_end.json")
GRAPH = os.path.join(B, "graph_ring_p5s02b_20261010_111905.json")
PINS = {EXPF: "60e02787", PLAN: "930699ec", SESS: "e8daf1fe", GRAPH: "431cfd83"}
STEP = 3
EL_KEYS = {"input": ["containsunwiredorbadterminal"], "sr": ["shiftregister", "unwiredfrominside"], "local": ["localvariable", "notconnected"],
           "cond": ["conditionalterminal", "notwired"]}                                    # elrule class -> norm_all of its Error List text (elrule.py:6-13)
gate = L.Gate(width=1000)
ex, P, S = J(EXPF), J(PLAN), J(SESS)
READF = os.path.join(ROOT, ex["measured_from"])
gate("M0 pins {0}; read md5 == expected file's measured_md5".format(dict((os.path.basename(p), w) for p, w in PINS.items())),
     all(md5(p).startswith(w) for p, w in PINS.items()) and md5(READF) == ex["measured_md5"], dict((os.path.basename(p), md5(p)[:8]) for p in PINS))
RI = [dict((k, v) for k, v in it.items() if k != "licensed_by") for it in J(READF).get("items") or []]
ROWS = ex["expected"]
NROW = sum(int(r.get("count") or 1) for r in ROWS)
xb, mb, _u = EC.compare(copy.deepcopy(RI), ROWS)
gate("B compare(read {0} items, the {1} expected entries = {2} items) extra {3} missing {4} (baseline)".format(len(RI), len(ROWS), NROW, len(xb), len(mb)),
     len(RI) == NROW == int(ex["total"]) and not xb and not mb, (xb, mb))
A = P["actions"]
AID = set(a["id"] for a in A)
base = J(P["finalized"]["base"]["path"])


def base_uids(a):
    """Base (int) uids a plan action names: loop / body / parent / diagram and the uid / term_uid of a dict end."""
    out = set(int(a[k]) for k in ("loop", "body", "parent", "diagram") if isinstance(a.get(k), int))
    for k in ("src", "dst"):
        e = a.get(k)
        if isinstance(e, dict):
            out |= set(int(e[q]) for q in ("uid", "term_uid") if isinstance(e.get(q), int))
    return out


TOUCH = dict((u, a["id"]) for a in A for u in base_uids(a))
print("FACT group-I actions {0}; base uids named {1}".format([a["id"] for a in A], sorted(TOUCH.items())), flush=True)
cleared, stale = [], []
for r in ROWS:
    cb, ou = r.get("clears_by") or {}, (r.get("object") or {}).get("uid")
    if ou is not None and int(ou) in TOUCH:
        cleared.append({"item": r.get("item"), "class": r.get("class"), "object_uid": ou, "action": TOUCH[int(ou)], "how": "group-I action names #{0}".format(ou)})
    elif cb.get("step") == STEP:
        nm = str(cb.get("action") or "")
        stale.append({"item": r.get("item"), "class": r.get("class"), "object_uid": ou, "was": nm, "in_plan": nm.split()[-1] in AID if nm else False,
                      "now": "STANDING (entry unchanged): {0} is not an action of plan_ring_p5s02c.json (group I A41..A52 alone, PD396(c)); it moves "
                             "with the step that carries it".format(nm)})
for e in cleared:
    print("FACT CLEARED item {item} {class} uid {object_uid} by {action} - {how}".format(**e), flush=True)
for e in stale:
    print("FACT STALE item {item} {class} uid {object_uid}: clears_by step 3 '{was}' in plan {in_plan} -> STANDING".format(**e), flush=True)
gate("CL {0} row(s) cleared by a group-I action (items {1})".format(len(cleared), [e["item"] for e in cleared]), all(e["action"] in AID for e in cleared), cleared)
gate("ST {0} stale step-3 row(s) (items {1}): none names an action of this plan".format(len(stale), [e["item"] for e in stale]),
     not any(e["in_plan"] for e in stale), stale)
sf = P["finalized"]["step_files"]
st0, last = J(sf[0]["path"])["state"], J(sf[-1]["path"])["state"]
sym0 = set(v for v in (st0.get("sym") or {}).values() if isinstance(v, int))
SYMR = dict((int(u), s) for s, u in (last.get("sym") or {}).items() if isinstance(u, int))
madeu = set(SYMR) - sym0
ELP = ELR.predict(st0, last, NROW, madeu, carry=(), extra_owner_states=(base,), subvis=ELR.subvis_from_plan(P, st0, last))
print("FACT ELRULE new {0} closed {1} uncertain base {2} uncertain subvi {3}".format(ELP["new_items"], ELP["closed_items"],
      ELP["uncertain_base_newly_unwired_inputs"], ELP["uncertain_subvi_terminals"]), flush=True)
AS = dict((a["as"], a["id"]) for a in A if a.get("as"))
raised = []
for k, (c, u) in enumerate(ELP["new_items"]):
    s = (SYMR.get(int(u)) or "")[4:]
    who = next((AS[x] for x in sorted(AS, key=len, reverse=True) if s.startswith(x)), None) or TOUCH.get(int(u))
    raised.append({"item": "r{0}".format(k), "norm_all": EL_KEYS.get(c), "count": 1, "label": "elrule {0} item on #{1} [raised r{2}]".format(c, u, k),
                   "class": "elrule:" + c, "object": {"kind": "node", "uid": u, "evidence": "tools/elrule.py predict, step_00 -> step_12"}, "raised_by": who})
gate("R every elrule new item ({0}) attributed to an action and has a text key; closed {1}".format(len(raised), ELP["closed_items"]),
     all(x["raised_by"] and x["norm_all"] for x in raised), raised)
unpred = []
for kind, how, acts in (S.get("compile") or {}).get("ops") or []:
    if kind == "connect_term_uid" and how == "register_end_case_border":
        ids = [A[i - 1]["id"] for i in acts]
        pos = [41 + i - 1 for i in acts]
        unpred.append({"action": "UNPREDICTED:A{0} {1}".format(pos[0], ids[0]), "id": ids[0], "op_group": ids, "A": pos,
                       "why": "connect_term_uid register_end_case_border (tunnel + register face through the case border, new SR CS7): on step 2 the same verb "
                              "(A32 / A39) left +2 'Wire has loose ends.' items the read cannot attribute by uid (diag_c162_a1_2_facts.md; PD396(a)(2)); "
                              "whether this group leaves one is not decidable offline - the step-3 scratch measures it"})
gate("U unpredicted op groups (read from the session compile): {0}".format([(u["action"], u["op_group"]) for u in unpred]), len(unpred) == 2, unpred)
CI = set(e["item"] for e in cleared)
pred_rows = [copy.deepcopy(r) for r in ROWS if r.get("item") is None or r.get("item") not in CI] + [copy.deepcopy(x) for x in raised]
c = copy.deepcopy(RI)
_x, mc, _u = EC.compare(c, [r for r in ROWS if r.get("item") in CI])
lic = [it for it in c if it.get("licensed_by") == "explicit"]
rest = [dict((k, v) for k, v in it.items() if k != "licensed_by") for it in c if it.get("licensed_by") != "explicit"]
xf, mf, _u = EC.compare(copy.deepcopy(rest), pred_rows)
T = sum(int(r.get("count") or 1) for r in pred_rows)
gate("F compare(read minus the {0} cleared = {1} items, the {2} predicted entries = {3} items) extra {4} missing {5} (raised rows are synthetic: {6})".format(
     len(lic), len(rest), len(pred_rows), T, len(xf), len(mf), len(raised)), not mc and len(lic) == len(CI) and not xf and (len(mf) == len(raised)), (mc, xf, mf))
C0 = collections.Counter(K.el_class(x) for x in RI)
CC = collections.Counter(K.el_class(x) for x in lic)
RN = collections.Counter("elrule:" + k[0] for k in ELP["new_items"])
RC = collections.Counter("elrule:" + k[0] for k in ELP["closed_items"])
PC = dict((k, C0.get(k, 0) - CC.get(k, 0) + RN.get(k, 0) - RC.get(k, 0)) for k in sorted(set(C0) | set(RN)) if C0.get(k, 0) - CC.get(k, 0) + RN.get(k, 0) - RC.get(k, 0))
gate("PC per-class predicted total {0} == item total {1} (start {2} - cleared {3} + raised {4} - elrule closed {5})".format(
     sum(PC.values()), T, len(RI), len(CI), len(raised), len(ELP["closed_items"])), sum(PC.values()) == T == len(RI) - len(CI) + len(raised) - len(ELP["closed_items"]), PC)
cnt = {"cleared": len(cleared), "raised": len(raised), "unpredicted": len(unpred), "standing": NROW - len(cleared), "stale_step3": len(stale), "total": T,
       "total_if_every_unpredicted_raises_one": T + len(unpred), "base_total": NROW}
print("EL COUNTS cleared {cleared} raised {raised} unpredicted {unpredicted} standing {standing} stale {stale_step3} total {total} (upper {total_if_every_unpredicted_raises_one})".format(**cnt), flush=True)
out = {"schema": "errorlist-expected/1", "kind": "PREDICTED step-3 end (P5-2 step 3, plan_ring_p5s02c.json, group I A41..A52); not a read - the step-3 scratch reads it",
       "bed": None, "bed_note": "the step-3 in-between file does not exist yet; base bed f9ae7751 (" + ex["bed"] + ")",
       "decided_by": "card 163-a1-3 (docs/d1/ring-p5b.md PD396(d)): cleared AND raised items per action; written by tools/bench/prep_c163_a1_3_el.py",
       "base_expected": {"path": rel(EXPF), "md5": md5(EXPF), "total": NROW}, "measured_from": ex["measured_from"], "measured_md5": ex["measured_md5"],
       "plan": {"path": rel(PLAN), "md5": md5(PLAN)}, "session": {"path": rel(SESS), "md5": md5(SESS)}, "total": T, "counts": cnt,
       "cleared": cleared, "stale_step3": stale, "raised": raised, "unpredicted": unpred,
       "elrule": {"module_md5": md5(os.path.join(ROOT, "tools", "elrule.py")), "new_items": ELP["new_items"], "closed_items": ELP["closed_items"],
                  "uncertain_base_newly_unwired_inputs": ELP["uncertain_base_newly_unwired_inputs"], "uncertain_subvi_terminals": ELP["uncertain_subvi_terminals"],
                  "rule": ELP["rule"], "fixed": ELP},
       "per_class": {"start_read": {"path": ex["measured_from"], "md5": md5(READF), "items": len(RI), "classes": dict(sorted(C0.items()))},
                     "cleared": dict(CC), "rule_new": dict(RN), "rule_closed": dict(RC), "predicted": PC, "classifier": "stagekit.el_class"},
       "check": {"compare_baseline": [len(xb), len(mb)], "compare_predicted": [len(xf), len(mf)], "checker": "errorlist_check.compare"},
       "expected": pred_rows,
       "format_note": "same entry form as " + rel(EXPF) + " (norm_all / count / label / cite; checker errorlist_check.compare); cleared / raised / unpredicted / stale_step3 are extra keys"}
json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)
gate("W predicted file written, {0} items == total".format(sum(int(r.get("count") or 1) for r in J(OUT)["expected"])), sum(int(r.get("count") or 1) for r in J(OUT)["expected"]) == T)
print("FACT md5 {0} {1}".format(md5(OUT), rel(OUT)), flush=True)
sys.exit(gate.result([{"path": rel(OUT), "md5": md5(OUT)}]))
