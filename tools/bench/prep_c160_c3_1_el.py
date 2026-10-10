# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_160-c3-1.md
# ---
r"""prep_c160_c3_1_el - card 160-c3-1 (OFFLINE, json only): the PREDICTED step-2-end Error List of P5-2 step 2 (docs/d1/ring-p5b.md PD389(d),
PD391(d)) -> tools/bench/errorlist_predicted_D1_ring_p5s02b_end.json, item by item from the 56-row expected file of the 94ffff94 bed
(errorlist_expected_D1_ring_p5s02a_20261010_023239.json 1fd016bf, NOT edited):
  CLEARED  = every row whose clears_by.step == 2, mapped to the plan_ring_p5s02b.json action that clears it, READ: a delete_wire row whose wire_uid
             is the row's object uid (dw_a13 / dw_go / dw_ho), else a MERGE row of the session table (prep_c160_b3_1_session.json `merge`, expect uid);
             a 56-row clears_by that names another action is a STALE expectation (PD391(a)(d): A32/A39 no longer merge) - changed and reported;
  RAISED   = tools/elrule.py predict (the FIXED rule, no second classifier) on the plan's step_00 -> step_20 sim states, each new item tied to the action
             that made / wired its owner; UNPREDICTED:<action> for the actions of a NEW STRUCTURE CLASS (PD391(e)): the connect_term_uid
             register_end_case_border groups whose sink is a BASE RightShiftRegister inner face (route read from the session compile + base graph);
  STANDING = the rest, entries unchanged. Classes by stagekit.el_class; the checker form is errorlist_check.compare (shared calls).
PREDICTION CONTRACT: M0 pins (expected 1fd016bf, read == measured_md5, plan f4520b10, session e5279899, graph 7ac24924); B compare(read 56, the 56
  rows) extra 0 missing 0; CL 5 rows with step 2 = items 0,1,2,3,5, each mapped (dw_a13 w10394, dw_go w24264, dw_ho w24300, MERGE w_gl w24285 /
  w_hl w24312), none outside step 2 touched; SIM the deleted wires gone at the sim end, the MERGE uids carry a source and a sink there; R elrule
  new / closed printed, every new item attributed; U unpredicted = w_gr / w_hr; F compare(read minus the cleared 5, predicted) extra 0 missing 0;
  PC per-class predicted total == item total; W file written.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c160_c3_1_el.log -- py -u tools/bench/prep_c160_c3_1_el.py"""
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
PLAN, SESS = os.path.join(B, "plan_ring_p5s02b.json"), os.path.join(B, "prep_c160_b3_1_session.json")
EXPF = os.path.join(B, "errorlist_expected_D1_ring_p5s02a_20261010_023239.json")
OUT = os.path.join(B, "errorlist_predicted_D1_ring_p5s02b_end.json")
PINS = {EXPF: "1fd016bf", PLAN: "f4520b10", SESS: "e5279899", os.path.join(B, "graph_ring_p5s02a_20261010_032547.json"): "7ac24924"}
STEP = 2
EL_KEYS = {"input": ["containsunwiredorbadterminal"], "sr": ["shiftregister", "unwiredfrominside"], "local": ["localvariable", "notconnected"],
           "cond": ["conditionalterminal", "notwired"]}                                    # elrule class -> norm_all of its Error List text (elrule.py:6-13)
gate = L.Gate(width=1000)
ex, P, S = J(EXPF), J(PLAN), J(SESS)
READF = os.path.join(ROOT, ex["measured_from"])
gate("M0 pins {0}; read md5 == expected file's measured_md5".format(dict((os.path.basename(p), w) for p, w in PINS.items())),
     all(md5(p).startswith(w) for p, w in PINS.items()) and md5(READF) == ex["measured_md5"], dict((os.path.basename(p), md5(p)[:8]) for p in PINS))
RI = [dict((k, v) for k, v in it.items() if k != "licensed_by") for it in J(READF).get("items") or []]   # the read's own licensing marks dropped
ROWS = ex["expected"]
xb, mb, _u = EC.compare(copy.deepcopy(RI), ROWS)
gate("B compare(read {0} items, the {1} expected rows) extra {2} missing {3} (baseline)".format(len(RI), len(ROWS), len(xb), len(mb)),
     len(RI) == len(ROWS) == int(ex["total"]) and not xb and not mb, (xb, mb))
A = P["actions"]
pos = dict((e["id"], e["pos"]) for e in (S.get("merge") or []) + (S.get("stubs") or []))
lab = lambda i: ("A{0} {1}".format(pos[i], i) if i in pos else i)                          # noqa: E731  A-number only where the session table holds it
DEL = dict((int(a["wire_uid"]), a["id"]) for a in A if a["op"] == "delete_wire")
MRG = dict((int(m["expect"]), m) for m in S.get("merge") or [])
cleared, stale, bad = [], [], []
for r in ROWS:
    cb, ou = r.get("clears_by") or {}, (r.get("object") or {}).get("uid")
    hit = DEL.get(ou) if ou is not None else None
    m = MRG.get(ou) if ou is not None else None
    if cb.get("step") != STEP:
        if hit or m:
            bad.append(("outside step 2 but touched", r["item"], ou))
        continue
    if hit:
        e = {"item": r["item"], "class": r["class"], "object_uid": ou, "action": hit, "how": "delete_wire {0} (plan action {1})".format(ou, hit)}
    elif m:
        e = {"item": r["item"], "class": r["class"], "object_uid": ou, "action": lab(m["id"]), "how": "MERGE onto t{0}, one ok wire, uid {1} expected".format(m["stub_term"], m["expect"]),
             "assumption": "MERGE (PD388(c), PD391(d)): unmeasured; the step-2 scratch measures it"}
    else:
        bad.append(("step-2 row with no clearing action", r["item"], ou))
        continue
    was = cb.get("action")
    if was and was not in (e["action"], "delete_wire {0}".format(ou) if hit else e["action"]):
        e["changed_from"] = was
        stale.append((r["item"], was, e["action"]))
    cleared.append(e)
for e in cleared:
    print("FACT CLEARED item {item} {class} uid {object_uid} by {action} - {how}{0}".format(" (STALE 56-row clears_by '{0}' changed)".format(e["changed_from"]) if e.get("changed_from") else "", **e), flush=True)
gate("CL {0} step-2 rows (items {1}) each mapped to its clearing action; none outside step 2 touched".format(len(cleared), [e["item"] for e in cleared]),
     not bad and len(cleared) == sum(1 for r in ROWS if (r.get("clears_by") or {}).get("step") == STEP), bad)
print("FACT STALE 56-row clears_by changed (PD391(a)(d): A32/A39 are delete + fresh connect, not MERGE): {0}".format(stale), flush=True)
sf = P["finalized"]["step_files"]
st0, last = J(sf[0]["path"])["state"], J(sf[-1]["path"])["state"]
wires = lambda st: collections.Counter(int(t["wire_uid"]) for t in st["terminals"] if t.get("wire_uid"))   # noqa: E731
objs = lambda st: set(int(o["uid"]) for o in st.get("objs") or [])                         # noqa: E731
W0, W1, O1 = wires(st0), wires(last), objs(last)
simchk = []
for e in cleared:
    u = e["object_uid"]
    if e["action"] in DEL.values():
        simchk.append((e["action"], u, "gone at sim end", u not in W1 and u not in O1))
    else:
        rs = [t for t in last["terminals"] if t.get("wire_uid") == u]
        simchk.append((e["action"], u, "sim end rows {0}".format(sorted((t["term_uid"], bool(t.get("is_source"))) for t in rs)),
                       any(t.get("is_source") for t in rs) and any(not t.get("is_source") for t in rs)))
gate("SIM deleted wires gone at the sim end; each MERGE uid carries a source and a sink there", all(x[3] for x in simchk), simchk)
sym0 = set(v for v in (st0.get("sym") or {}).values() if isinstance(v, int))
SYMR = dict((int(u), s) for s, u in (last.get("sym") or {}).items() if isinstance(u, int))
madeu = set(SYMR) - sym0
base = J(P["finalized"]["base"]["path"])
ELP = ELR.predict(st0, last, int(ex["total"]), madeu, carry=(), extra_owner_states=(base,), subvis=ELR.subvis_from_plan(P, st0, last))
print("FACT ELRULE new {0} closed {1} uncertain base {2} uncertain subvi {3}".format(ELP["new_items"], ELP["closed_items"],
      ELP["uncertain_base_newly_unwired_inputs"], ELP["uncertain_subvi_terminals"]), flush=True)


def owner_action(u):
    """The plan action that made owner u (its 'as' symbol) or that wires one of its terminals (dict end with that uid); None if none."""
    s = SYMR.get(int(u))
    if s and s.startswith("new:"):
        a = next((a for a in A if a.get("as") == s[4:].split(".")[0]), None)
        if a:
            return a["id"]
    return next((a["id"] for a in A for k in ("src", "dst") if isinstance(a.get(k), dict) and a[k].get("uid") == u), None)


raised = []
for k, (c, u) in enumerate(ELP["new_items"]):
    raised.append({"item": "r{0}".format(k), "norm_all": EL_KEYS.get(c), "count": 1, "label": "elrule {0} item on #{1} [raised r{2}]".format(c, u, k),
                   "class": "elrule:" + c, "object": {"kind": "node", "uid": u, "evidence": "tools/elrule.py predict, step_00 -> step_20"},
                   "raised_by": owner_action(u), "cite": "tools/elrule.py:" + {"local": "6", "cond": "7", "sr": "9", "input": "13"}.get(c, "5")})
gate("R every elrule new item ({0}) attributed to an action and has a text key; closed {1}".format(len(raised), ELP["closed_items"]),
     all(x["raised_by"] and x["norm_all"] for x in raised), raised)
opsS = (S.get("compile") or {}).get("ops") or []
bcls = dict((int(t["term_uid"]), str(t.get("owner_class") or "")) for t in base["terminals"])
unpred = []
for kind, how, acts in opsS:
    if kind != "connect_term_uid" or how != "register_end_case_border":
        continue
    for n in acts:
        a = A[n - 1]
        ends = [a.get(k) for k in ("src", "dst") if isinstance(a.get(k), dict) and a[k].get("term_uid") is not None]
        if a["op"] == "wire" and any(bcls.get(int(d["term_uid"])) == "RightShiftRegister" for d in ends):
            unpred.append({"action": "UNPREDICTED:{0}".format(lab(a["id"])), "id": a["id"], "op_group": [A[i - 1]["id"] for i in acts],
                           "why": "PD391(c)(e) new structure class: a BASE RightShiftRegister inner face (t{0}) through connect_term_uid register_end_case_border; "
                                  "whether the verb's SelectorTunnel / purged Invokes leave an Error List item (tunnel, wire, missing assignment) is not decidable "
                                  "offline - the step-2 scratch measures it".format([d["term_uid"] for d in ends if bcls.get(int(d["term_uid"])) == "RightShiftRegister"][0])})
gate("U unpredicted actions (new structure class, read from the session compile + base graph): {0}".format([u["action"] for u in unpred]),
     sorted(u["id"] for u in unpred) == sorted(e["id"] for e in S.get("stubs") or []), unpred)
CI = set(e["item"] for e in cleared)
pred_rows = [copy.deepcopy(r) for r in ROWS if r["item"] not in CI] + [copy.deepcopy(x) for x in raised]
c = copy.deepcopy(RI)
_x, mc, _u = EC.compare(c, [r for r in ROWS if r["item"] in CI])
lic = [it for it in c if it.get("licensed_by") == "explicit"]
rest = [dict((k, v) for k, v in it.items() if k != "licensed_by") for it in c if it.get("licensed_by") != "explicit"]
xf, mf, _u = EC.compare(copy.deepcopy(rest), pred_rows)
gate("F compare(read minus the {0} cleared = {1} items, the {2} predicted rows) extra {3} missing {4} (raised rows are synthetic: {5})".format(
     len(lic), len(rest), len(pred_rows), len(xf), len(mf), len(raised)), not mc and len(lic) == len(CI) and not xf and (len(mf) == len(raised)), (mc, xf, mf))
C0 = collections.Counter(K.el_class(x) for x in RI)
CC = collections.Counter(K.el_class(x) for x in lic)
RN = collections.Counter("elrule:" + k[0] for k in ELP["new_items"])
RC = collections.Counter("elrule:" + k[0] for k in ELP["closed_items"])
PC = dict((k, C0.get(k, 0) - CC.get(k, 0) + RN.get(k, 0) - RC.get(k, 0)) for k in sorted(set(C0) | set(RN)) if C0.get(k, 0) - CC.get(k, 0) + RN.get(k, 0) - RC.get(k, 0))
T = len(pred_rows)
gate("PC per-class predicted total {0} == item total {1} (start {2} - cleared {3} + raised {4} - elrule closed {5})".format(
     sum(PC.values()), T, len(RI), len(CI), len(raised), len(ELP["closed_items"])), sum(PC.values()) == T == len(RI) - len(CI) + len(raised) - len(ELP["closed_items"]), PC)
cnt = {"cleared": len(cleared), "raised": len(raised), "unpredicted": len(unpred), "standing": len(ROWS) - len(cleared), "total": T,
       "total_if_every_unpredicted_raises_one": T + len(unpred), "base_total": len(ROWS)}
print("EL COUNTS cleared {cleared} raised {raised} unpredicted {unpredicted} standing {standing} total {total} (upper {total_if_every_unpredicted_raises_one})".format(**cnt), flush=True)
out = {"schema": "errorlist-expected/1", "kind": "PREDICTED step-2 end (P5-2 step 2, plan_ring_p5s02b.json); not a read - the step-2 scratch reads it",
       "bed": None, "bed_note": "the step-2 in-between file does not exist yet; base bed 94ffff94 (" + ex["bed"] + ")",
       "decided_by": "card 160-c3-1 (docs/d1/ring-p5b.md PD389(d), PD391(d)(e)): cleared AND raised items per action; written by tools/bench/prep_c160_c3_1_el.py",
       "base_expected": {"path": rel(EXPF), "md5": md5(EXPF), "total": len(ROWS)}, "measured_from": ex["measured_from"], "measured_md5": ex["measured_md5"],
       "plan": {"path": rel(PLAN), "md5": md5(PLAN)}, "session": {"path": rel(SESS), "md5": md5(SESS)}, "total": T, "counts": cnt,
       "cleared": cleared, "stale_changed": [{"item": i, "was": w, "now": n, "why": "PD391(a)(d)"} for i, w, n in stale], "raised": raised, "unpredicted": unpred,
       "elrule": {"module_md5": md5(os.path.join(ROOT, "tools", "elrule.py")), "new_items": ELP["new_items"], "closed_items": ELP["closed_items"],
                  "uncertain_base_newly_unwired_inputs": ELP["uncertain_base_newly_unwired_inputs"], "uncertain_subvi_terminals": ELP["uncertain_subvi_terminals"],
                  "rule": ELP["rule"], "fixed": ELP},
       "per_class": {"start_read": {"path": ex["measured_from"], "md5": md5(READF), "items": len(RI), "classes": dict(sorted(C0.items()))},
                     "cleared": dict(CC), "rule_new": dict(RN), "rule_closed": dict(RC), "predicted": PC, "classifier": "stagekit.el_class"},
       "check": {"compare_baseline": [len(xb), len(mb)], "compare_predicted": [len(xf), len(mf)], "checker": "errorlist_check.compare"},
       "expected": pred_rows,
       "format_note": "same entry form as " + rel(EXPF) + " (norm_all / count / label / cite; checker errorlist_check.compare); cleared / raised / unpredicted are extra keys"}
json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)
gate("W predicted file written, {0} rows == total".format(len(J(OUT)["expected"])), len(J(OUT)["expected"]) == T)
print("FACT md5 {0} {1}".format(md5(OUT), rel(OUT)), flush=True)
sys.exit(gate.result([{"path": rel(OUT), "md5": md5(OUT)}]))
