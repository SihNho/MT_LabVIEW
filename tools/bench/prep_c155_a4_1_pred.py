# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_155-a4-1.md
# ---
r"""prep_c155_a4_1_pred - card 155-a4-1 (OFFLINE, no LabVIEW): writes plan_ring_p5s02_pred.json for P5-2 step 1 (plan_ring_p5s02.json, made by
prep_c155_a4_1_mk.py on the REAL P5-1 graph 6716c499; no rebase).
COPY of prep_c155_a2_1_pred.py (20726b40; OPEN: its gate / E1 / EL / per-class blocks are copied, not extracted - outside this card's write globs)
with these CHANGES, stated before the run:
  (p1) names / pins: plan / pred plan_ring_p5s02*.json, session table prep_c155_a4_1_session.json, graph = base = graph_ring_p5s01_20261009_125622.json
       6716c499 (vi 7f2582ae), START = stage_prerun.x10_start(7f2582ae); EL base = P5-1's expected file errorlist_expected_D1_ring_p5s01_20261009_124542.json
       ffc4cf66 (total 45) and the read it was measured from.
  (p2) no brief hand prediction (brief_155-a4-1.md gives none); the P5-1 measured offsets (read 45 vs pred 47: input -1, tunnel -1;
       diag_c155_a3_2_facts.md:18) are recorded, non-gating.
PREDICTION CONTRACT: M0 pins; RB plan FINAL / base / no negative uid; C each action once; X1 prerun start == pred start == maker's; X10 Executor peak
  == the maker's and MAIN <= 680; X17 PASS; VG vigraph a7eb58c7; E1 a step file per checkpoint; PC start read items == base total 45;
  per-class predicted total == rule total; SP pred keyed to the plan md5.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c155_a4_1_pred.log -- py -u tools/bench/prep_c155_a4_1_pred.py"""
import collections, hashlib, json, os, sys                                                # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR, census_predict as CPR                        # noqa: E401,E402
import stage_shared as SH                                                                   # noqa: E402  checkpoint_step_table (card 162-a2-3)
import elrule as ELR                                                                        # noqa: E402
import stagekit as SK                                                                       # noqa: E402  el_class (shared)
B = os.path.join(ROOT, "tools", "bench")
RRP, PP = os.path.join(B, "plan_ring_p5s02.json"), os.path.join(B, "plan_ring_p5s02_pred.json")
SESS = os.path.join(B, "prep_c155_a4_1_session.json")
GRAPH, GRAPH_PIN = os.path.join(B, "graph_ring_p5s01_20261009_125622.json"), "6716c49948f097b8ac0e1780930bfab1"
EXPF, EXPF_PIN = os.path.join(B, "errorlist_expected_D1_ring_p5s01_20261009_124542.json"), "ffc4cf66"
REQF = os.path.join(B, "subvi_requiredness.json")
VGF = os.path.join(ROOT, "tools", "vigraph.py")
BEDVI_MD5 = "7f2582ae54dc5bc42c3df0bdf3c72d2e"                                             # the adopted P5-1 file (never opened)
MAIN_SRC_READS = 2
CARRY_SET = (4538, 29843, 29879, 30002, 2626)                                               # == prep_c155_a2_1_pred.py:38
P5S01_OFFSETS = {"read_minus_elrule_pred": {"input": -1, "tunnel": -1, "total": -2},
                 "source": "tools/bench/diag_c155_a3_2_facts.md:18 (elcls read 45 vs pred 47 / alternative 47)"}
MODEL = SPR.load_memory_model()
XS0 = SPR.x10_start(BEDVI_MD5, MODEL)
START, START_CITE = (XS0[0], XS0[1]) if XS0 else (None, None)
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                 # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []
SS_ = J(SESS)
elcls = SK.el_class


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
gate("M0 graph 6716c499, EL expected file ffc4cf66, its read == its measured_md5, vigraph a7eb58c7, plan == session table's",
     md5(GRAPH) == GRAPH_PIN and md5(EXPF).startswith(EXPF_PIN) and md5(READF) == ex.get("measured_md5") and md5(VGF).startswith("a7eb58c7")
     and md5(RRP) == SS_["plan"]["md5"], (md5(GRAPH), md5(EXPF), md5(READF), md5(VGF)))
p = J(RRP)
fz = p.get("finalized") or {}
bp = (fz.get("base") or p.get("base") or {})
neg = SPR.negative_uids_left(p)
gate("RB plan FINAL, open_rows_match, {0} actions == session table {1}; no negative uid left".format(len(p["actions"]), SS_["actions"]),
     p.get("final") is True and fz.get("open_rows_match") is True and len(p["actions"]) == SS_["actions"] and not neg and not (p.get("base") or {}).get("provisional"),
     {"base": p.get("base"), "neg": neg[:6]})
base = J(bp["path"])
gate("RB2 base IS the real P5-1 graph: path md5 == 6716c499 == plan's base md5; its vi md5 == 7f2582ae (the bed)",
     md5(os.path.join(ROOT, bp["path"])) == GRAPH_PIN == bp.get("md5") and str(base.get("md5") or "") == BEDVI_MD5, (bp, base.get("vi"), base.get("md5")))
ops = SX.compile_plan(p)
gate("C compile: {0} actions -> {1} ops, each action once".format(len(p["actions"]), len(ops)),
     sorted(n for o in ops for n in o["acts"]) == list(range(1, len(p["actions"]) + 1)) and len(ops) == SS_["ops"])
bind = sorted(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS)
cps = sorted(set([0, len(ops)]) | set(bind))
xs = SPR.x10_plan_start(RRP, MODEL)
gate("X1 ONE start: prerun's own x10_plan_start(plan) {0} == pred start x10_start(7f2582ae) {1} == maker's {2}".format(xs and xs[0], START, SS_["start_mb"]),
     xs is not None and START is not None and xs[0] == START == SS_["start_mb"], (xs, XS0))
mp = SPR.x10_model_peak([o["kind"] for o in ops], cps, model=MODEL, start_mb=START)
v = lambda k: float(MODEL[k]["value"])                                                      # noqa: E731
MAIN = round(mp["peak_mb"] + MAIN_SRC_READS * v("read_mb"), 1)
print("FACT X10 at start {0}: N {1} R {2} Executor peak {3} MAIN {4} fail_above {5} margin {6}; MEMSTOP {7} margin {8}".format(
      START, mp["N"], mp["R"], mp["peak_mb"], MAIN, mp["fail_above_mb"], round(mp["fail_above_mb"] - MAIN, 1), SX.MEM_STOP_MB,
      round(SX.MEM_STOP_MB - MAIN, 1)), flush=True)
gate("X10 Executor peak {0} == maker's {1}; MAIN {2} == maker's {3} <= {4}".format(mp["peak_mb"], SS_["exec_peak_mb"], MAIN, SS_["main_peak_mb"], SPR.X10_FAIL_MB),
     mp["ok"] and mp["peak_mb"] == SS_["exec_peak_mb"] and MAIN == SS_["main_peak_mb"] and MAIN <= SPR.X10_FAIL_MB, mp)
ok17, det17 = SPR.x17_gate([p])
gate("X17 over P5-2 step 1", ok17, det17)
sf = fz.get("step_files") or []
SFN = dict((int(x["n"]), x) for x in sf)
cpe = SH.checkpoint_step_table(ops, cps, SFN)                                                # card 162-a2-3: tools/stage_shared.py, was a copied block
gate("E1 every checkpoint ({0}) has a simulated step file with md5".format(len(cpe)), all(e["step_file"] and e["md5"] for e in cpe), cpe)
gate("VG D / TD / PB keys under vigraph.py a7eb58c7 (position key, chat-T6)", md5(VGF).startswith("a7eb58c7"), md5(VGF))
rep = CPR.predict(p, {}, J(os.path.join(B, "census_samples.json")))
print("FACT CENSUS derived {0}; overall {1}; unpredicted rows {2}".format(rep["derived"], rep["overall"], [p["actions"][k - 1]["id"] for k in rep["unpredicted"]]), flush=True)
st0, last = J(sf[0]["path"])["state"], J(sf[-1]["path"])["state"]
madeu = set(int(u) for u in (last.get("sym") or {}).values() if isinstance(u, int)) - set(int(u) for u in (st0.get("sym") or {}).values() if isinstance(u, int))
OPENNEW = sorted((int(r["owner_uid"]), r.get("owner_class"), r.get("term_name"), bool(r.get("is_source"))) for r in last["terminals"]
                 if int(r["owner_uid"]) in madeu and not r.get("wire_uid"))
SYMR = dict((int(u), s) for s, u in (last.get("sym") or {}).items() if isinstance(u, int))
print("FACT OPEN-NEW {0} unwired terminal(s) of P5-2-created objects at the sim end (owner, sym, class, name, is_source): {1}".format(
      len(OPENNEW), [(o, SYMR.get(o), c, n, s) for o, c, n, s in OPENNEW]), flush=True)
EL0 = int(ex["total"])
SUBV = ELR.subvis_from_plan(p, st0, last)
ELP = ELR.predict(st0, last, EL0, madeu, carry=(), extra_owner_states=(base,), subvis=SUBV)
ELALT = ELR.predict(st0, last, EL0, madeu, carry=CARRY_SET, extra_owner_states=(base,), subvis=SUBV)
print("EL BOTH TOTALS base {0}: no carry -> {1} (new {2} closed {3}); carry {4} -> {5} (new {6} closed {7})".format(
      EL0, ELP["predicted_total"], ELP["new_items"], ELP["closed_items"], list(CARRY_SET), ELALT["predicted_total"], ELALT["new_items"], ELALT["closed_items"]), flush=True)
byc = collections.Counter(k[0] for k in ELP["new_items"]), collections.Counter(k[0] for k in ELP["closed_items"])
print("EL FIXED P5-2: base {0} new {1} closed {2} -> {3}; per class new {4} closed {5}; open at start {6}; open at end {7}; uncertain base {8}; "
      "uncertain subvi {9}; subvis {10}; created {11}".format(EL0, len(ELP["new_items"]), len(ELP["closed_items"]), ELP["predicted_total"], dict(byc[0]), dict(byc[1]),
                                                             ELP["open_at_start"], ELP["open_at_end"], ELP["uncertain_base_newly_unwired_inputs"],
                                                             ELP["uncertain_subvi_terminals"], SUBV, sorted(madeu)), flush=True)
print("FACT EL rule: {0}".format(ELP.get("rule")), flush=True)
print("FACT EL P5-1 measured offsets (non-gating): {0}".format(json.dumps(P5S01_OFFSETS)), flush=True)
RI = J(READF).get("items") or []
C0 = collections.Counter(elcls(x) for x in RI)
PC = dict((c, C0.get(c, 0) + byc[0].get(c, 0) - byc[1].get(c, 0)) for c in sorted(set(C0) | set(byc[0]) | set(byc[1])))
print("EL PER-CLASS start read {0} ({1} items): {2}".format(rel(READF), len(RI), dict(sorted(C0.items()))), flush=True)
print("EL PER-CLASS predicted end (start + new - closed): {0}; total {1}".format(PC, sum(PC.values())), flush=True)
gate("PC start read {0} items == expected total {1}; per-class predicted total {2} == rule predicted_total {3}".format(len(RI), EL0, sum(PC.values()), ELP["predicted_total"]),
     len(RI) == EL0 and sum(PC.values()) == ELP["predicted_total"], PC)
pred = {"schema": "ring-p3b-pred/1", "card": "155-a4-1",
        "note": "RING P5-2 step 1 (PD374(b)(d), PD376(d), PD378(c)) as one bed session on the ADOPTED P5-1 file D1_ring_p5s01_20261009_124542.vi (7f2582ae), "
                "planned directly on its real graph 6716c499 (prep_c155_a4_1_mk.py, no rebase); start = stage_prerun.x10_start = measured load + op-0 read "
                "(PD352(b)); Error List by the fixed rule (tools/elrule.py) on the P5-1 expected file (total {0}), BOTH totals recorded, neither gating "
                "(PD370(a))".format(EL0),
        "plan": {"path": rel(RRP), "md5": md5(RRP)}, "graph": {"path": bp["path"], "md5": md5(os.path.join(ROOT, bp["path"]))}, "bed": base.get("vi"), "bed_md5": base.get("md5"),
        "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [p["actions"][k - 1]["id"] for k in rep["unpredicted"]],
        "ops": [o["kind"] for o in ops], "cdiff_rows": sorted(fz.get("end_cdiff_rows") or []), "cross_session_refs": "none: planned on the real graph (no rebase)",
        "e1": {"rule": "PD374(f): graph == sim at every executor checkpoint", "checkpoints": cpe},
        "keys": {"d_td_pb": "position key (chat-T6, PD366)", "vigraph": {"path": "tools/vigraph.py", "md5": md5(VGF)}},
        "errorlist": {"bed_total": EL0, "new_items_predicted": len(ELP["new_items"]) - len(ELP["closed_items"]), "predicted_total": ELP["predicted_total"],
                      "alternative_total": ELALT["predicted_total"], "fixed": ELP, "alternative": ELALT,
                      "rule": ELP["rule"] + "; base = P5-1 expected file " + str(EL0) + " (" + rel(EXPF) + "); no carry (alternative: carry " + json.dumps(list(CARRY_SET)) + ")",
                      "rule_source": {"module": "tools/elrule.py", "module_md5": md5(os.path.join(ROOT, "tools", "elrule.py")), "requiredness": rel(REQF),
                                      "requiredness_md5": md5(REQF), "pd": "PD349+PD351(c); PD354(a)(b); PD370(a); PD374(f); PD378(c)"},
                      "p5s01_measured_offsets": P5S01_OFFSETS,
                      "previous": None, "base_file": rel(EXPF), "checked": False,
                      "per_class": {"start_read": {"path": rel(READF), "md5": md5(READF), "items": len(RI), "classes": dict(sorted(C0.items()))},
                                    "rule_new": dict(byc[0]), "rule_closed": dict(byc[1]), "predicted": PC,
                                    "classifier": "stagekit.el_class (== elcls of prep_c147_a1_3_pred.py)",
                                    "advisory": "PD354(a): non-zero only for a class in neither start_read.classes nor predicted, or |total diff| > 3"}},
        "memory_pred": {"card": "155-a4-1", "checkpoints": cps, "R": mp["R"], "N": mp["N"], "bind_ops": bind, "op_kinds": [o["kind"] for o in ops],
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
