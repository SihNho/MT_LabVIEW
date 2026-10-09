# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_154-a3-2b.md
# ---
r"""prep_c154_a3_2b_pred - card 154-a3-2b (OFFLINE, no LabVIEW): writes plan_ring_p5s01a_pred.json for P5-1a (plan_ring_p5s01a.json, made by
prep_c154_a3_2b_mk.py on the REAL s09 graph 22f967b5; no rebase - the base IS the real graph).
COPY of prep_c152_b2_1_pred.py (the s09 pred) with these CHANGES, stated before the run:
  (p1) names / pins: plan / pred plan_ring_p5s01a*.json, session table prep_c154_a3_2b_session.json, graph = base = graph_ring_p4s09_20261009_062044.json
       22f967b5 (vi eb1d0f31), START = stage_prerun.x10_start(eb1d0f31) = 596.7 + op-0 5.9; EL base = s09's expected file
       errorlist_expected_D1_ring_p4s09_20261009_060515.json 5146f980 (total printed) and the read it was measured from (its `measured_from`).
  (p2) REMOVED: the V18E-R' block (rebase-log RENAMED-OLD, v18 summary compare) - P5 is not a v18 session and this plan was never rebased; the
       RB/RB2 gates become: plan FINAL, open_rows_match, base == the graph file (md5 22f967b5) whose vi md5 == eb1d0f31, no negative uid.
  (p3) E1 (PD374(f)): every executor checkpoint of the plan has a simulated step file; their md5s are recorded in pred.e1 (the recipe's E1 compares
       each real checkpoint with them). D / TD / PB keys: recorded as the POSITION key of vigraph.py a7eb58c7 (chat-T6), gate VG pins that md5.
  (p4) CARRY: both elrule totals are computed and recorded (no-carry = predicted_total as s09's pred chose, carry = the s09 carry set
       {4538, 29843, 29879, 30002, 2626} = alternative_total); neither gates (PD370(a)). The CARRY-S08 re-run of the copy is dropped (s08 is two
       sessions back; s09's EL file is already the measured base).
  (p5) the per-op formula line uses this plan's own ops (not v18's).
PREDICTION CONTRACT: M0 pins; RB plan FINAL / base / no negative uid; C each action once; X1 prerun start == pred start == 602.6; X10 Executor peak
  == the maker's (session table) and MAIN <= 680; X17 PASS; VG vigraph a7eb58c7; E1 a step file per checkpoint; PC start read items == base total;
  per-class predicted total == rule total; SP pred keyed to the plan md5.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c154_a3_2b_pred.log -- py -u tools/bench/prep_c154_a3_2b_pred.py"""
import collections, hashlib, json, os, re, sys                                            # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR, census_predict as CPR                        # noqa: E401,E402
import elrule as ELR                                                                        # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
RRP, PP = os.path.join(B, "plan_ring_p5s01a.json"), os.path.join(B, "plan_ring_p5s01a_pred.json")
SESS = os.path.join(B, "prep_c154_a3_2b_session.json")
GRAPH, GRAPH_MD5 = os.path.join(B, "graph_ring_p4s09_20261009_062044.json"), "22f967b513726a01c9d8f63269f689e6"
EXPF, EXPF_MD5 = os.path.join(B, "errorlist_expected_D1_ring_p4s09_20261009_060515.json"), "5146f980f5a4b58403ce87afc870f9a9"
REQF = os.path.join(B, "subvi_requiredness.json")
VGF = os.path.join(ROOT, "tools", "vigraph.py")
BEDVI_MD5 = "eb1d0f3107bbba49c9ae67a47c0ee50f"                                             # the s09 adopted file (never opened)
MAIN_SRC_READS = 2
CARRY_SET = (4538, 29843, 29879, 30002, 2626)                                               # == prep_c152_b2_1_pred.py:212
MODEL = SPR.load_memory_model()
XS0 = SPR.x10_start(BEDVI_MD5, MODEL)
START, START_CITE = (XS0[0], XS0[1]) if XS0 else (None, None)
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                 # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []
SS_ = J(SESS)
OCR_ALIASES = (("vl", "vi"), ("v", "y"))                                                    # == errorlist_check.OCR_ALIASES (copied)


def norm_ocr(s):
    k = re.sub(r"[^a-z0-9]", "", (s or "").lower())                                        # == errorlist_check.norm
    for a, b in OCR_ALIASES:
        k = k.replace(a, b)
    return k


def elcls(it):
    """card 147-a1-3: one Error List item -> its class (rule classes local / cond / sr / input; else other:<norm_ocr(raw)>)."""
    c = ELR.item_class("{0} {1}".format(it.get("raw", ""), it.get("detail", "")))
    if c:
        return c
    k = norm_ocr(it.get("raw"))
    if "unwiredorbadterminal" in k or ("requiredinput" in k and "notwired" in k):
        return "input"
    return "other:" + k


def gate(label, ok, d="", fatal=True):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)
    if not ok and fatal:
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
        sys.exit(1)


ex = J(EXPF)
READF = os.path.join(ROOT, ex["measured_from"]) if not os.path.isabs(ex["measured_from"]) else ex["measured_from"]
print("FACT plan md5 {0}; session table {1} ({2} actions, {3} ops); EL expected {4} total {5}, measured_from {6} md5 {7} (expected-file pin {8})".format(
      md5(RRP), md5(SESS), SS_["actions"], SS_["ops"], rel(EXPF), ex["total"], rel(READF), md5(READF), ex.get("measured_md5")), flush=True)
gate("M0 graph 22f967b5, EL expected file 5146f980, its read == its measured_md5, vigraph a7eb58c7, plan == session table's",
     md5(GRAPH) == GRAPH_MD5 and md5(EXPF) == EXPF_MD5 and md5(READF) == ex.get("measured_md5") and md5(VGF).startswith("a7eb58c7")
     and md5(RRP) == SS_["plan"]["md5"], (md5(GRAPH), md5(EXPF), md5(READF), md5(VGF)))
p = J(RRP)
fz = p.get("finalized") or {}
bp = (fz.get("base") or p.get("base") or {})
neg = SPR.negative_uids_left(p)
gate("RB plan FINAL, open_rows_match, {0} actions == session table {1}; no negative uid left".format(len(p["actions"]), SS_["actions"]),
     p.get("final") is True and fz.get("open_rows_match") is True and len(p["actions"]) == SS_["actions"] and not neg and not (p.get("base") or {}).get("provisional"),
     {"base": p.get("base"), "neg": neg[:6]})
base = J(bp["path"])
gate("RB2 base IS the real s09 graph: path md5 == 22f967b5 == plan's base md5; its vi md5 == eb1d0f31 (the bed)",
     md5(os.path.join(ROOT, bp["path"])) == GRAPH_MD5 == bp.get("md5") and str(base.get("md5") or "") == BEDVI_MD5, (bp, base.get("vi"), base.get("md5")))
ops = SX.compile_plan(p)
gate("C compile: {0} actions -> {1} ops, each action once".format(len(p["actions"]), len(ops)),
     sorted(n for o in ops for n in o["acts"]) == list(range(1, len(p["actions"]) + 1)) and len(ops) == SS_["ops"])
bind = sorted(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS)
cps = sorted(set([0, len(ops)]) | set(bind))
xs = SPR.x10_plan_start(RRP, MODEL)
gate("X1 ONE start: prerun's own x10_plan_start(plan) {0} == pred start x10_start(eb1d0f31) {1} == maker's {2}".format(xs and xs[0], START, SS_["start_mb"]),
     xs is not None and START is not None and xs[0] == START == SS_["start_mb"], (xs, XS0))
mp = SPR.x10_model_peak([o["kind"] for o in ops], cps, model=MODEL, start_mb=START)
v = lambda k: float(MODEL[k]["value"])                                                      # noqa: E731
MAIN = round(mp["peak_mb"] + MAIN_SRC_READS * v("read_mb"), 1)
print("FACT X10 at start {0}: N {1} R {2} Executor peak {3} MAIN {4} fail_above {5} margin {6}; MEMSTOP {7} margin {8}; next op of P5-1 MAIN {9}".format(
      START, mp["N"], mp["R"], mp["peak_mb"], MAIN, mp["fail_above_mb"], round(mp["fail_above_mb"] - MAIN, 1), SX.MEM_STOP_MB,
      round(SX.MEM_STOP_MB - MAIN, 1), (SS_["cut"]["per_prefix_main"][len(ops)] if len(SS_["cut"]["per_prefix_main"]) > len(ops) else None)), flush=True)
gate("X10 Executor peak {0} == maker's {1}; MAIN {2} == maker's {3} <= {4}".format(mp["peak_mb"], SS_["exec_peak_mb"], MAIN, SS_["main_peak_mb"], SPR.X10_FAIL_MB),
     mp["ok"] and mp["peak_mb"] == SS_["exec_peak_mb"] and MAIN == SS_["main_peak_mb"] and MAIN <= SPR.X10_FAIL_MB, mp)
ok17, det17 = SPR.x17_gate([p])
gate("X17 over P5-1a", ok17, det17)
sf = fz.get("step_files") or []
SFN = dict((int(x["n"]), x) for x in sf)
# E1: the action number at the end of each checkpoint op -> its step file
cpe = []
for k in cps:
    an = max(ops[k - 1]["acts"]) if k else 0
    x = SFN.get(an)
    cpe.append({"op": k, "kind": ops[k - 1]["kind"] if k else "base", "action": an, "step_file": x and x["path"], "md5": x and x.get("md5")})
gate("E1 every checkpoint ({0}) has a simulated step file with md5".format(len(cpe)), all(e["step_file"] and e["md5"] for e in cpe), cpe)
gate("VG D / TD / PB keys under vigraph.py a7eb58c7 (position key, chat-T6)", md5(VGF).startswith("a7eb58c7"), md5(VGF))
rep = CPR.predict(p, {}, J(os.path.join(B, "census_samples.json")))
print("FACT CENSUS derived {0}; overall {1}; unpredicted rows {2}".format(rep["derived"], rep["overall"], [p["actions"][k - 1]["id"] for k in rep["unpredicted"]]), flush=True)
st0, last = J(sf[0]["path"])["state"], J(sf[-1]["path"])["state"]
madeu = set(int(u) for u in (last.get("sym") or {}).values() if isinstance(u, int)) - set(int(u) for u in (st0.get("sym") or {}).values() if isinstance(u, int))
OPENNEW = sorted((int(r["owner_uid"]), r.get("owner_class"), r.get("term_name"), bool(r.get("is_source"))) for r in last["terminals"]
                 if int(r["owner_uid"]) in madeu and not r.get("wire_uid"))
SYMR = dict((int(u), s) for s, u in (last.get("sym") or {}).items() if isinstance(u, int))
print("FACT OPEN-NEW {0} unwired terminal(s) of P5-1a-created objects at the sim end (owner, sym, class, name, is_source): {1}".format(
      len(OPENNEW), [(o, SYMR.get(o), c, n, s) for o, c, n, s in OPENNEW]), flush=True)
EL0 = int(ex["total"])
SUBV = ELR.subvis_from_plan(p, st0, last)
ELP = ELR.predict(st0, last, EL0, madeu, carry=(), extra_owner_states=(base,), subvis=SUBV)
ELALT = ELR.predict(st0, last, EL0, madeu, carry=CARRY_SET, extra_owner_states=(base,), subvis=SUBV)
print("EL BOTH TOTALS base {0}: no carry -> {1} (new {2} closed {3}); carry {4} -> {5} (new {6} closed {7})".format(
      EL0, ELP["predicted_total"], ELP["new_items"], ELP["closed_items"], list(CARRY_SET), ELALT["predicted_total"], ELALT["new_items"], ELALT["closed_items"]), flush=True)
byc = collections.Counter(k[0] for k in ELP["new_items"]), collections.Counter(k[0] for k in ELP["closed_items"])
print("EL FIXED P5-1a: base {0} new {1} closed {2} -> {3}; per class new {4} closed {5}; open at start {6}; open at end {7}; uncertain base {8}; "
      "uncertain subvi {9}; subvis {10}; created {11}".format(EL0, len(ELP["new_items"]), len(ELP["closed_items"]), ELP["predicted_total"], dict(byc[0]), dict(byc[1]),
                                                             ELP["open_at_start"], ELP["open_at_end"], ELP["uncertain_base_newly_unwired_inputs"],
                                                             ELP["uncertain_subvi_terminals"], SUBV, sorted(madeu)), flush=True)
print("FACT EL rule: {0}".format(ELP.get("rule")), flush=True)
RI = J(READF).get("items") or []
C0 = collections.Counter(elcls(x) for x in RI)
PC = dict((c, C0.get(c, 0) + byc[0].get(c, 0) - byc[1].get(c, 0)) for c in sorted(set(C0) | set(byc[0]) | set(byc[1])))
print("EL PER-CLASS start read {0} ({1} items): {2}".format(rel(READF), len(RI), dict(sorted(C0.items()))), flush=True)
print("EL PER-CLASS predicted end (start + new - closed): {0}; total {1}".format(PC, sum(PC.values())), flush=True)
gate("PC start read {0} items == expected total {1}; per-class predicted total {2} == rule predicted_total {3}".format(len(RI), EL0, sum(PC.values()), ELP["predicted_total"]),
     len(RI) == EL0 and sum(PC.values()) == ELP["predicted_total"], PC)
pred = {"schema": "ring-p3b-pred/1", "card": "154-a3-2b",
        "note": "RING P5-1a (PD374(e) cut of P5-1 form S: ops 1..{0} of 22, actions 1..{1} of 32) as one bed session on the ADOPTED s09 file "
                "D1_ring_p4s09_20261009_060515.vi (eb1d0f31), planned directly on its real graph 22f967b5 (prep_c154_a3_2b_mk.py, no rebase); start = "
                "stage_prerun.x10_start = measured load + op-0 read (PD352(b)); Error List by the fixed rule (tools/elrule.py) on the s09 expected file "
                "(total {2}), BOTH totals recorded (no carry = predicted_total, carry = alternative_total), neither gating (PD370(a))".format(len(ops), len(p["actions"]), EL0),
        "plan": {"path": rel(RRP), "md5": md5(RRP)}, "graph": {"path": bp["path"], "md5": md5(os.path.join(ROOT, bp["path"]))}, "bed": base.get("vi"), "bed_md5": base.get("md5"),
        "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [p["actions"][k - 1]["id"] for k in rep["unpredicted"]],
        "ops": [o["kind"] for o in ops], "cdiff_rows": sorted(fz.get("end_cdiff_rows") or []), "cross_session_refs": "none: planned on the real graph (no rebase)",
        "e1": {"rule": "PD374(f): graph == sim at every executor checkpoint", "checkpoints": cpe},
        "keys": {"d_td_pb": "position key (chat-T6, PD366)", "vigraph": {"path": "tools/vigraph.py", "md5": md5(VGF)}},
        "errorlist": {"bed_total": EL0, "new_items_predicted": len(ELP["new_items"]) - len(ELP["closed_items"]), "predicted_total": ELP["predicted_total"],
                      "alternative_total": ELALT["predicted_total"], "fixed": ELP, "alternative": ELALT,
                      "rule": ELP["rule"] + "; base = s09 expected file " + str(EL0) + " (" + rel(EXPF) + "); no carry (alternative: carry " + json.dumps(list(CARRY_SET)) + ")",
                      "rule_source": {"module": "tools/elrule.py", "module_md5": md5(os.path.join(ROOT, "tools", "elrule.py")), "requiredness": rel(REQF),
                                      "requiredness_md5": md5(REQF), "pd": "PD349+PD351(c); PD354(a)(b); PD370(a); PD374(f)"},
                      "previous": None, "base_file": rel(EXPF), "checked": False,
                      "per_class": {"start_read": {"path": rel(READF), "md5": md5(READF), "items": len(RI), "classes": dict(sorted(C0.items()))},
                                    "rule_new": dict(byc[0]), "rule_closed": dict(byc[1]), "predicted": PC,
                                    "classifier": "elcls: elrule.item_class(raw + detail) -> local/cond/sr; norm_ocr(raw) containing 'unwiredorbadterminal' or "
                                                  "'requiredinput'+'notwired' -> input; else 'other:' + norm_ocr(raw) (prep_c147_a1_3_pred.py)",
                                    "advisory": "PD354(a): non-zero only for a class in neither start_read.classes nor predicted, or |total diff| > 3"}},
        "memory_pred": {"card": "154-a3-2b", "checkpoints": cps, "R": mp["R"], "N": mp["N"], "bind_ops": bind, "op_kinds": [o["kind"] for o in ops],
                        "start_mb": START, "start_cite": START_CITE, "start_rule": "stage_prerun.x10_start (PD352(b))", "peak_mb": mp["peak_mb"], "main_peak_mb": MAIN,
                        "fail_above_mb": mp["fail_above_mb"], "below_fail": mp["ok"], "memstop_mb": SX.MEM_STOP_MB, "prerun_start": xs,
                        "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)}},
        "summary": fz.get("summary")}
json.dump(pred, open(PP, "w", encoding="utf-8"), indent=1)
print("FACT ops", dict(collections.Counter(pred["ops"])), "census", pred["census"], "overall", pred["census_overall"], "unpredicted", len(pred["census_unpredicted"]),
      "| EL", pred["errorlist"]["predicted_total"], "alt", pred["errorlist"]["alternative_total"], "| end rows", len(pred["cdiff_rows"]),
      "open pairs", len(p.get("open_rows") or []), flush=True)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (RRP, PP))
gate("SP pred written, keyed to the plan md5", J(PP)["plan"]["md5"] == md5(RRP))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
sys.exit(1 if G["fail"] else 0)
