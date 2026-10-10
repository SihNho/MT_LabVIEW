# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_156-a1-1.md
# ---
r"""prep_c156_a1_1_pred - card 156-a1-1 (OFFLINE, no LabVIEW): writes plan_ring_p5s02a_pred.json for P5-2 step 1 RE-MADE (plan_ring_p5s02a.json,
prep_c156_a1_1_mk.py, on the REAL P5-1 graph 6716c499; no rebase). Base = prep_c155_a4_1_pred.py (9c587c75) with ONLY: names / pins (plan, pred,
session prep_c156_a1_1_session.json); gate() CALLED from prep_c156_a1_1_lib.Gate; X10 MAIN checked against the card limit 675 (PD379(c));
NEW (PD379(e)): the E1 checkpoints carry the three move_in ops (#376 / #3052 / #3453) explicitly, each with its step file, as scratch-run items.
The E1 / EL / per-class blocks are the 155 pred's (OPEN: copied, no shared function holds them; stagekit pinned).
PREDICTION CONTRACT: M0 pins; RB plan FINAL / base / no negative uid; C each action once; X1 prerun start == pred start == maker's; X10 Executor peak
  == maker's and MAIN <= 675; X17 PASS; VG vigraph a7eb58c7; E1 a step file per checkpoint and per move_in op; PC start read items == base total 45;
  per-class predicted total == rule total; SP pred keyed to the plan md5.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c156_a1_1_pred.log -- py -u tools/bench/prep_c156_a1_1_pred.py"""
import collections, json, os, sys                                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import stagexec as SX, stage_prerun as SPR, census_predict as CPR                        # noqa: E401,E402
import elrule as ELR                                                                        # noqa: E402
import stagekit as SK                                                                       # noqa: E402  el_class (shared)
import stage_shared as SH                                                                   # noqa: E402  checkpoint_step_table (card 162-a2-3)
import prep_c156_a1_1_lib as L                                                              # noqa: E402
md5, rel, J = L.md5, L.rel, L.J
B = os.path.join(ROOT, "tools", "bench")
RRP, PP = os.path.join(B, "plan_ring_p5s02a.json"), os.path.join(B, "plan_ring_p5s02a_pred.json")
SESS = os.path.join(B, "prep_c156_a1_1_session.json")
GRAPH, GRAPH_PIN = os.path.join(B, "graph_ring_p5s01_20261009_125622.json"), "6716c49948f097b8ac0e1780930bfab1"
EXPF, EXPF_PIN = os.path.join(B, "errorlist_expected_D1_ring_p5s01_20261009_124542.json"), "ffc4cf66"
REQF = os.path.join(B, "subvi_requiredness.json")
VGF = os.path.join(ROOT, "tools", "vigraph.py")
BEDVI_MD5 = "7f2582ae54dc5bc42c3df0bdf3c72d2e"
MAIN_SRC_READS, LIMIT = 2, 675.0
CARRY_SET = (4538, 29843, 29879, 30002, 2626)                                               # == prep_c155_a4_1_pred.py:37
P5S01_OFFSETS = {"read_minus_elrule_pred": {"input": -1, "tunnel": -1, "total": -2},
                 "source": "tools/bench/diag_c155_a3_2_facts.md:18 (elcls read 45 vs pred 47 / alternative 47)"}
MODEL = SPR.load_memory_model()
XS0 = SPR.x10_start(BEDVI_MD5, MODEL)
START, START_CITE = (XS0[0], XS0[1]) if XS0 else (None, None)
gate = L.Gate()
ARTS = gate.ARTS
SS_ = J(SESS)
elcls = SK.el_class
ex = J(EXPF)
READF = os.path.join(ROOT, ex["measured_from"]) if not os.path.isabs(ex["measured_from"]) else ex["measured_from"]
print("FACT plan md5 {0}; session {1} ({2} actions, {3} ops); EL expected {4} total {5}, measured_from {6} md5 {7}".format(
      md5(RRP), md5(SESS), SS_["actions"], SS_["ops"], rel(EXPF), ex["total"], rel(READF), md5(READF)), flush=True)
gate("M0 graph 6716c499, EL expected ffc4cf66, its read == measured_md5, vigraph a7eb58c7, plan == session table's",
     md5(GRAPH) == GRAPH_PIN and md5(EXPF).startswith(EXPF_PIN) and md5(READF) == ex.get("measured_md5") and md5(VGF).startswith("a7eb58c7")
     and md5(RRP) == SS_["plan"]["md5"], (md5(GRAPH), md5(EXPF), md5(READF), md5(VGF)))
p = J(RRP)
fz = p.get("finalized") or {}
bp = (fz.get("base") or p.get("base") or {})
neg = SPR.negative_uids_left(p)
gate("RB plan FINAL, open_rows_match, {0} actions == session {1}; no negative uid".format(len(p["actions"]), SS_["actions"]),
     p.get("final") is True and fz.get("open_rows_match") is True and len(p["actions"]) == SS_["actions"] and not neg and not (p.get("base") or {}).get("provisional"),
     {"base": p.get("base"), "neg": neg[:6]})
base = J(bp["path"])
gate("RB2 base IS the real P5-1 graph 6716c499; its vi md5 == 7f2582ae", md5(os.path.join(ROOT, bp["path"])) == GRAPH_PIN == bp.get("md5") and str(base.get("md5") or "") == BEDVI_MD5,
     (bp, base.get("vi"), base.get("md5")))
ops = SX.compile_plan(p)
gate("C compile: {0} actions -> {1} ops, each action once".format(len(p["actions"]), len(ops)),
     sorted(n for o in ops for n in o["acts"]) == list(range(1, len(p["actions"]) + 1)) and len(ops) == SS_["ops"])
bind = sorted(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS)
cps = sorted(set([0, len(ops)]) | set(bind))
xs = SPR.x10_plan_start(RRP, MODEL)
gate("X1 ONE start: x10_plan_start(plan) {0} == x10_start(7f2582ae) {1} == maker's {2}".format(xs and xs[0], START, SS_["start_mb"]),
     xs is not None and START is not None and xs[0] == START == SS_["start_mb"], (xs, XS0))
MAIN, mp, _c = L.main_of(len(ops), [o["kind"] for o in ops], SX, SPR, MODEL, START, MAIN_SRC_READS)
print("FACT X10 at start {0}: N {1} R {2} Executor peak {3} MAIN {4}; card limit {5} margin {6}; stage_prerun fail_above {7}; MEMSTOP {8}".format(
      START, mp["N"], mp["R"], mp["peak_mb"], MAIN, LIMIT, round(LIMIT - MAIN, 1), mp["fail_above_mb"], SX.MEM_STOP_MB), flush=True)
gate("X10 Executor peak {0} == maker's {1}; MAIN {2} == maker's {3} <= {4} (card)".format(mp["peak_mb"], SS_["exec_peak_mb"], MAIN, SS_["main_peak_mb"], LIMIT),
     mp["ok"] and mp["peak_mb"] == SS_["exec_peak_mb"] and MAIN == SS_["main_peak_mb"] and MAIN <= LIMIT, mp)
ok17, det17 = SPR.x17_gate([p])
gate("X17 over P5-2 step 1", ok17, det17)
sf = fz.get("step_files") or []
SFN = dict((int(x["n"]), x) for x in sf)
cpe = SH.checkpoint_step_table(ops, cps, SFN)                                                # card 162-a2-3: tools/stage_shared.py, was a copied block
gate("E1 every checkpoint ({0}) has a simulated step file with md5".format(len(cpe)), all(e["step_file"] and e["md5"] for e in cpe), cpe)
MV = []
for k, o in enumerate(ops, 1):
    if o["kind"] == "move_in":
        an = o["acts"][0]
        x = SFN.get(an)
        MV.append({"op": k, "action": an, "id": p["actions"][an - 1]["id"], "node": p["actions"][an - 1]["nodes"], "step_file": x and x["path"], "md5": x and x.get("md5"),
                   "check": "PD379(e)/prior-art A4: the scratch quotes graph == sim (E1) after this op (cycles 97/98 left case-frame moves termless)"})
print("FACT E1-MOVE {0}".format(MV), flush=True)
gate("E1M the three move_in ops (#376 / #3052 / #3453) each have a step file ({0})".format([m["node"] for m in MV]),
     sorted(n for m in MV for n in m["node"]) == [376, 3052, 3453] and all(m["step_file"] and m["md5"] for m in MV), MV)
gate("VG D / TD / PB keys under vigraph.py a7eb58c7", md5(VGF).startswith("a7eb58c7"), md5(VGF))
rep = CPR.predict(p, {}, J(os.path.join(B, "census_samples.json")))
print("FACT CENSUS derived {0}; overall {1}; unpredicted rows {2}".format(rep["derived"], rep["overall"], [p["actions"][k - 1]["id"] for k in rep["unpredicted"]]), flush=True)
st0, last = J(sf[0]["path"])["state"], J(sf[-1]["path"])["state"]
madeu = set(int(u) for u in (last.get("sym") or {}).values() if isinstance(u, int)) - set(int(u) for u in (st0.get("sym") or {}).values() if isinstance(u, int))
OPENNEW = sorted((int(r["owner_uid"]), r.get("owner_class"), r.get("term_name"), bool(r.get("is_source"))) for r in last["terminals"] if int(r["owner_uid"]) in madeu and not r.get("wire_uid"))
SYMR = dict((int(u), s) for s, u in (last.get("sym") or {}).items() if isinstance(u, int))
print("FACT OPEN-NEW {0} unwired terminal(s) of P5-2-created objects at the sim end: {1}".format(len(OPENNEW), [(o, SYMR.get(o), c, n, s) for o, c, n, s in OPENNEW]), flush=True)
EL0 = int(ex["total"])
SUBV = ELR.subvis_from_plan(p, st0, last)
ELP = ELR.predict(st0, last, EL0, madeu, carry=(), extra_owner_states=(base,), subvis=SUBV)
ELALT = ELR.predict(st0, last, EL0, madeu, carry=CARRY_SET, extra_owner_states=(base,), subvis=SUBV)
print("EL BOTH TOTALS base {0}: no carry -> {1} (new {2} closed {3}); carry -> {4}".format(EL0, ELP["predicted_total"], ELP["new_items"], ELP["closed_items"], ELALT["predicted_total"]), flush=True)
byc = collections.Counter(k[0] for k in ELP["new_items"]), collections.Counter(k[0] for k in ELP["closed_items"])
RI = J(READF).get("items") or []
C0 = collections.Counter(elcls(x) for x in RI)
PC = dict((c, C0.get(c, 0) + byc[0].get(c, 0) - byc[1].get(c, 0)) for c in sorted(set(C0) | set(byc[0]) | set(byc[1])))
print("EL PER-CLASS start {0}; predicted end {1}; total {2}; P5-1 offsets (non-gating) {3}".format(dict(sorted(C0.items())), PC, sum(PC.values()), json.dumps(P5S01_OFFSETS)), flush=True)
gate("PC start read {0} items == expected total {1}; per-class predicted total {2} == rule total {3}".format(len(RI), EL0, sum(PC.values()), ELP["predicted_total"]),
     len(RI) == EL0 and sum(PC.values()) == ELP["predicted_total"], PC)
pred = {"schema": "ring-p3b-pred/1", "card": "156-a1-1",
        "note": "RING P5-2 step 1 RE-MADE (PD374(b)(d), PD376(d), PD379) as one bed session on the ADOPTED P5-1 file D1_ring_p5s01_20261009_124542.vi (7f2582ae), planned on "
                "its real graph 6716c499 (prep_c156_a1_1_mk.py, no rebase); start = stage_prerun.x10_start; MAIN <= 675 (PD379(c)); Error List by tools/elrule.py on the P5-1 "
                "expected file (total {0}), BOTH totals recorded, neither gating (PD370(a))".format(EL0),
        "plan": {"path": rel(RRP), "md5": md5(RRP)}, "graph": {"path": bp["path"], "md5": md5(os.path.join(ROOT, bp["path"]))}, "bed": base.get("vi"), "bed_md5": base.get("md5"),
        "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [p["actions"][k - 1]["id"] for k in rep["unpredicted"]],
        "ops": [o["kind"] for o in ops], "cdiff_rows": sorted(fz.get("end_cdiff_rows") or []), "cross_session_refs": "none: planned on the real graph (no rebase)",
        "e1": {"rule": "PD374(f): graph == sim at every executor checkpoint; PD379(e): quoted for each move_in op", "checkpoints": cpe, "move_in_checks": MV},
        "keys": {"d_td_pb": "position key (chat-T6, PD366)", "vigraph": {"path": "tools/vigraph.py", "md5": md5(VGF)}},
        "errorlist": {"bed_total": EL0, "new_items_predicted": len(ELP["new_items"]) - len(ELP["closed_items"]), "predicted_total": ELP["predicted_total"],
                      "alternative_total": ELALT["predicted_total"], "fixed": ELP, "alternative": ELALT,
                      "rule": ELP["rule"] + "; base = P5-1 expected file " + str(EL0) + " (" + rel(EXPF) + "); no carry (alternative: carry " + json.dumps(list(CARRY_SET)) + ")",
                      "rule_source": {"module": "tools/elrule.py", "module_md5": md5(os.path.join(ROOT, "tools", "elrule.py")), "requiredness": rel(REQF),
                                      "requiredness_md5": md5(REQF), "pd": "PD349+PD351(c); PD354(a)(b); PD370(a); PD374(f); PD379"},
                      "p5s01_measured_offsets": P5S01_OFFSETS, "previous": None, "base_file": rel(EXPF), "checked": False,
                      "per_class": {"start_read": {"path": rel(READF), "md5": md5(READF), "items": len(RI), "classes": dict(sorted(C0.items()))},
                                    "rule_new": dict(byc[0]), "rule_closed": dict(byc[1]), "predicted": PC, "classifier": "stagekit.el_class",
                                    "advisory": "PD354(a): non-zero only for a class in neither start_read.classes nor predicted, or |total diff| > 3"}},
        "memory_pred": {"card": "156-a1-1", "checkpoints": cps, "R": mp["R"], "N": mp["N"], "bind_ops": bind, "op_kinds": [o["kind"] for o in ops],
                        "start_mb": START, "start_cite": START_CITE, "start_rule": "stage_prerun.x10_start (PD352(b))", "peak_mb": mp["peak_mb"], "main_peak_mb": MAIN,
                        "card_limit_mb": LIMIT, "fail_above_mb": mp["fail_above_mb"], "below_fail": mp["ok"], "memstop_mb": SX.MEM_STOP_MB, "prerun_start": xs,
                        "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)}},
        "summary": fz.get("summary")}
json.dump(pred, open(PP, "w", encoding="utf-8"), indent=1)
print("FACT ops", dict(collections.Counter(pred["ops"])), "census", pred["census"], "unpredicted", len(pred["census_unpredicted"]),
      "| EL", pred["errorlist"]["predicted_total"], "alt", pred["errorlist"]["alternative_total"], "| end rows", len(pred["cdiff_rows"]), "open pairs", len(p.get("open_rows") or []), flush=True)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (RRP, PP))
gate("SP pred written, keyed to the plan md5", J(PP)["plan"]["md5"] == md5(RRP))
sys.exit(gate.result())
