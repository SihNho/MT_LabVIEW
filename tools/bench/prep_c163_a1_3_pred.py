# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_163-a1-3.md
# ---
r"""prep_c163_a1_3_pred - card 163-a1-3 (OFFLINE, no LabVIEW): plan_ring_p5s02c_pred.json for P5-2 step 3 (plan_ring_p5s02c.json 930699ec, group
I = A41..A52, FINAL on the REAL f9ae7751 graph 431cfd83, prep_c163_a1_2_mk.py) + the sink-gate census file prep_c163_a1_3_session.json that
stagekit.RingSession reads (`sink_gate_census`, prep_c156_a1_1_lib.sg_census). Flow of prep_c160_c3_1_pred.py (a top-level script: importing it runs
it); Gate / main_of / sg_census from prep_c156_a1_1_lib; compile / checkpoints from stagexec; E1 table from stage_shared.checkpoint_step_table;
X10 from stage_prerun (x10_start, x10_plan_start, x17_gate); census from census_predict; CEN2 ends from stagekit.cen2_wire_ends; the Error List
block READ from errorlist_predicted_D1_ring_p5s02c_end.json (prep_c163_a1_3_el.py).
Per action (PD396(d), PD374(b)): the new objects (add_shift_reg CS7 -> CS7L / CS7R, DigitalNumericConstant K07, Increment IN7, case tunnels TC7 /
TD7 through register_end_case_border) are each bound in the sim end's symbol map; the two case_frame_wire rows (w_c7_fi branch on frame #31506,
w_c7_pass new_wire on #31517) each have a sourced wire at the sim end on the frame the session frame_map resolved; every wire row's sink is wired
at the sim end. Group I has no delete_wire / delete_object (those are group J). CEN2 judged by wire ENDS (stagekit.gate_cen2, PD389(b)). PB by
POSITION (PD370(b)). MAIN limit 675; START = stage_prerun.x10_start(f9ae7751) (PD396(c)); the session's start_mb is the same number.
STALE 160 expectations changed, not loosened: MG / ST / DW (MERGE, stub delete + fresh, delete rows) -> none in group I; X10 record
prep_c161_a3_2_x10.json (step 2) -> the 163-a1-2 session x10 {main, exec_peak}; START_ASSUMED -> none (start == x10_start).
PREDICTION CONTRACT: M0 pins; RB plan FINAL, 12 actions == session, no negative uid, base = 431cfd83 with bed f9ae7751; C 8 ops == session compile;
  E1 checkpoints == checkpoint_ops == session [0,1,2,4,5,7,8], each a step file with its recorded md5; X1 x10_plan_start == x10_start(f9ae7751) ==
  session start_mb 607.1; X10 MAIN <= 675 and == session x10 main 658.3, Executor peak == 653.2; X17 PASS; NO no delete rows; OBJ every created / SR /
  tunnel symbol bound at the sim end; CF case_frame_wire rows sourced on their frame; WS every wire row's sink wired at the sim end; CEN2 ends new
  pairs counted; EL item file keyed to this plan; SG census written; SP pred keyed to the plan md5.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c163_a1_3_pred.log -- py -u tools/bench/prep_c163_a1_3_pred.py"""
import collections, json, os, sys                                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import stagexec as SX, stage_prerun as SPR, census_predict as CPR                        # noqa: E401,E402
import stage_shared as SH                                                                   # noqa: E402  checkpoint_step_table (shared)
import stagekit as K                                                                        # noqa: E402  cen2_wire_ends, sim_census_snapshot (shared)
import prep_c156_a1_1_lib as L                                                              # noqa: E402  Gate / main_of / sg_census (shared)
md5, rel, J = L.md5, L.rel, L.J
B, T = os.path.join(ROOT, "tools", "bench"), os.path.join(ROOT, "tools")
RRP, PP = os.path.join(B, "plan_ring_p5s02c.json"), os.path.join(B, "plan_ring_p5s02c_pred.json")
SESS, SGF = os.path.join(B, "prep_c163_a1_2_session.json"), os.path.join(B, "prep_c163_a1_3_session.json")
ELF, LIC = os.path.join(B, "errorlist_predicted_D1_ring_p5s02c_end.json"), os.path.join(B, "plan_ring_p5s02c_licence.json")
GRAPH, VGF = os.path.join(B, "graph_ring_p5s02b_20261010_111905.json"), os.path.join(T, "vigraph.py")
PINS = {RRP: "930699ec", SESS: "e8daf1fe", GRAPH: "431cfd83", os.path.join(B, "plan_ring_p5s02c_in.json"): "eb48fabc",
        os.path.join(B, "memory_model.json"): "def9e640", os.path.join(T, "stagesim.py"): "95a162ba", os.path.join(T, "stagexec.py"): "a4df7e15",
        os.path.join(T, "stagekit.py"): "9b8f82c1", os.path.join(T, "stage_prerun.py"): "7605116f", os.path.join(T, "stage_shared.py"): "b688edd4"}
BEDVI_MD5_PREFIX, MAIN_SRC_READS, LIMIT = "f9ae7751", 2, 675.0
gate = L.Gate()
ARTS = gate.ARTS
gate("M0 pins {0}".format(dict((os.path.basename(p), w) for p, w in PINS.items())), all(md5(p).startswith(w) for p, w in PINS.items()),
     dict((os.path.basename(p), md5(p)[:8]) for p in PINS))
p, S = J(RRP), J(SESS)
fz = p.get("finalized") or {}
bp = fz.get("base") or p.get("base") or {}
neg = SPR.negative_uids_left(p)
gate("RB plan FINAL, open_rows_match, {0} actions == session {1}; no negative uid; base not provisional".format(len(p["actions"]), len(S["actions"])),
     p.get("final") is True and fz.get("open_rows_match") is True and [a["id"] for a in p["actions"]] == S["actions"] and not neg
     and not (p.get("base") or {}).get("provisional"), {"base": p.get("base"), "neg": neg[:6]})
base = J(bp["path"])
gate("RB2 base IS the real f9ae7751 graph 431cfd83; its vi md5 {0}".format(str(base.get("md5"))[:8]),
     md5(os.path.join(ROOT, bp["path"])) == md5(GRAPH) == bp.get("md5") and str(base.get("md5") or "").startswith(BEDVI_MD5_PREFIX), (bp, base.get("vi"), base.get("md5")))
A = p["actions"]
APOS = dict((a["id"], 41 + n) for n, a in enumerate(A))                                    # A41..A52 = plan order (163-a1-2 facts, gate IDS)
ops = SX.compile_plan(p)
SC = S["compile"]
gate("C compile: {0} actions -> {1} ops == session compile (kind, acts), each action once".format(len(A), len(ops)),
     [[o["kind"], list(o["acts"])] for o in ops] == [[k, list(a)] for k, _h, a in SC["ops"]] and sorted(n for o in ops for n in o["acts"]) == list(range(1, len(A) + 1)),
     [[o["kind"], o["acts"]] for o in ops])
cps = list(SX.checkpoint_ops(ops))
bind = sorted(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS)
SFN = dict((int(x["n"]), x) for x in fz.get("step_files") or [])
cpe = SH.checkpoint_step_table(ops, cps, SFN, A)
print("FACT E1 checkpoints {0}: {1}".format(cps, [(e["op"], e["kind"], e["action"], e["step_file"]) for e in cpe]), flush=True)
DWK = sorted(k for k, o in enumerate(ops, 1) if o["kind"] == "delete_wire")
gate("E1 checkpoints {0} == stagexec.checkpoint_ops == session {1} | delete_wire ops {2}; each has its simulated step file, md5 == recorded".format(
     cps, SC["checkpoints"], DWK),
     cps == sorted(set(SC["checkpoints"]) | set(DWK)) and all(e["step_file"] and md5(os.path.join(ROOT, e["step_file"])) == e["md5"] for e in cpe), cpe)
MODEL = SPR.load_memory_model()
XS0 = SPR.x10_start(base.get("md5"), MODEL)
START, START_CITE = XS0 if XS0 else (None, None)
xs = SPR.x10_plan_start(RRP, MODEL)
SA = S["start_mb"]
gate("X1 ONE measured start: x10_plan_start(plan) {0} == x10_start(f9ae7751) {1} == session start_mb {2}".format(xs and xs[0], START, SA),
     xs is not None and START is not None and xs[0] == START == SA, (xs, XS0))
KINDS = [o["kind"] for o in ops]
MAIN, mp, _c = L.main_of(len(ops), KINDS, SX, SPR, MODEL, START, MAIN_SRC_READS)
SXR = S["x10"]
print("FACT X10 at start {0}: N {1} R {2} Executor peak {3} MAIN {4}; session x10 {5}; card limit {6}; fail_above {7}; MEMSTOP {8}".format(
      START, mp["N"], mp["R"], mp["peak_mb"], MAIN, SXR, LIMIT, mp["fail_above_mb"], SX.MEM_STOP_MB), flush=True)
gate("X10 MAIN {0} (start {1}) <= {2}; Executor peak {3} == session {4}; MAIN == session {5}".format(MAIN, START, LIMIT, mp["peak_mb"], SXR["exec_peak"], SXR["main"]),
     mp["ok"] and MAIN <= LIMIT and mp["peak_mb"] == SXR["exec_peak"] and MAIN == SXR["main"], mp)
ok17, det17 = SPR.x17_gate([p])
gate("X17 over P5-2 step 3", ok17, det17)
st = lambda n: J(SFN[n]["path"])["state"]                                                   # noqa: E731
last, st0 = st(len(A)), st(0)
gate("NO group I has no delete_wire / delete_object action (group J's)", not [a["id"] for a in A if a["op"] in ("delete_wire", "delete_object")], [a["op"] for a in A])
SYM = last.get("sym") or {}
trows = lambda u: [t for t in last["terminals"] if int(t.get("owner_uid") or 0) == int(u)]   # noqa: E731
ent, objs = [], []
for n, a in enumerate(A, 1):
    e = {"n": n, "A": APOS[a["id"]], "id": a["id"], "op": a["op"], "verdict": "PLAN"}
    if a.get("as"):
        syms = sorted(k for k in SYM if k == "new:" + a["as"] or (a["op"] == "add_shift_reg" and k in ("new:" + a["as"] + "L", "new:" + a["as"] + "R")))
        e.update(verdict="NEW", symbols=dict((k, SYM[k]) for k in syms), cls=a.get("class") or a["op"], prim=a.get("prim"),
                 terminals_at_end=dict((k, len(trows(SYM[k]))) for k in syms if isinstance(SYM[k], int)))
        objs.append(e)
    ent.append(e)
gate("OBJ every created / shift-register / tunnel symbol bound at the sim end: {0}".format([(e["id"], e["symbols"]) for e in objs]),
     len(objs) == sum(1 for a in A if a.get("as")) and all(e["symbols"] and all(isinstance(v, int) for v in e["symbols"].values()) for e in objs)
     and all(len(e["symbols"]) == 2 for e in objs if e["op"] == "add_shift_reg"), objs)
FM = S.get("frame_map") or {}
CF = []
for k, o in enumerate(ops, 1):
    if o["kind"] != "case_frame_wire":
        continue
    for n in o["acts"]:
        a = A[n - 1]
        fr = sorted(set(v["real_frame"] for kk, v in FM.items() if kk.startswith(a["id"] + "|")))
        sf = J(SFN[n]["path"])
        eff = sf.get("effect") or {}
        wu = eff.get("wire")                                                                # step file effect key (sim/ring_p5s02c/step_08_wire.json)
        cf = eff.get("case_frame") or {}
        rs = [t for t in last["terminals"] if wu is not None and t.get("wire_uid") == wu]
        e = ent[n - 1]
        e.update(verdict="CASE-FRAME", op_kind=o["kind"], how=SC["ops"][k - 1][1], frames_resolved=fr, wire_sim=wu, effect_how=eff.get("how"), case_frame=cf,
                 checks={"frame_resolved": len(fr) == 1, "effect_frame == resolved": [cf.get("diagram")] == fr, "case_frame.variant == compile how": cf.get("variant") == SC["ops"][k - 1][1],
                         "sourced": any(t.get("is_source") for t in rs), "has_sink": any(not t.get("is_source") for t in rs)})
        CF.append(e)
gate("CF case_frame_wire rows ({0}): frame resolved by the session frame_map, the sim-end wire sourced and sunk: {1}".format(
     len(CF), [(e["id"], e["how"], e["frames_resolved"], e["checks"]) for e in CF]), len(CF) == 2 and all(all(e["checks"].values()) for e in CF), CF)
WS = []
for n, a in enumerate(A, 1):
    if a["op"] != "wire":
        continue
    eff = J(SFN[n]["path"]).get("effect") or {}
    du = eff.get("dst_term_uid")
    row = next((t for t in last["terminals"] if du is not None and t["term_uid"] == du), None)
    WS.append((a["id"], du, bool(row and row.get("wire_uid"))))
gate("WS every wire row's sink terminal wired at the sim end ({0} rows)".format(len(WS)), WS and all(x[2] for x in WS), WS)
c2 = K.cen2_wire_ends(base["terminals"], last["terminals"], last["terminals"], (base.get("owners") or {}).keys())
print("FACT CEN2 by ends on the sim end: new pairs {0} (key {1}); stubs {2}".format(c2["new_sim"], c2["key"], c2["stubs"]), flush=True)
rep = CPR.predict(p, {}, J(os.path.join(B, "census_samples.json")))
print("FACT CENSUS derived {0}; overall {1}; unpredicted rows {2}".format(rep["derived"], rep["overall"], [A[k - 1]["id"] for k in rep["unpredicted"]]), flush=True)
csim = collections.Counter(K.sim_census_snapshot(last).values()) - collections.Counter(K.sim_census_snapshot(st0).values())
print("FACT CENSUS sim end - step 0 by class (information only, NOT a census verdict, PD387(e)) {0}".format(dict(csim)), flush=True)
EL = J(ELF)
gate("EL item file {0} keyed to this plan md5; total {1} (cleared {2}, raised {3}, unpredicted {4})".format(rel(ELF), EL["total"], EL["counts"]["cleared"],
     EL["counts"]["raised"], EL["counts"]["unpredicted"]), EL["plan"]["md5"] == md5(RRP) and sum(EL["per_class"]["predicted"].values()) == EL["total"], EL["counts"])
SGC = L.sg_census(p, SX)
sgf = {"schema": "ring-session-census/1", "card": "163-a1-3", "plan": {"path": rel(RRP), "md5": md5(RRP)}, "from_session": {"path": rel(SESS), "md5": md5(SESS)},
       "sink_gate_census": SGC, "actions": len(A), "ops": len(ops), "checkpoints": cps, "start_mb": START, "main_peak_mb": MAIN,
       "note": "stagekit.RingSession reads `sink_gate_census`; prep_c163_a1_2_session.json carries none (computed here by prep_c156_a1_1_lib.sg_census)"}
json.dump(sgf, open(SGF, "w", encoding="utf-8"), indent=1)
gate("SG census file written: {0} wire row(s) onto a ControlTerminal, {1} need a sink gate".format(len(SGC), sum(1 for e in SGC if e["needs_sink_gate"])),
     J(SGF)["plan"]["md5"] == md5(RRP), SGC)
el = EL["per_class"]
pred = {"schema": "ring-p3b-pred/1", "card": "163-a1-3",
        "note": "RING P5-2 step 3 (PD396, group I A41..A52 alone) on the saved p5s02b file D1_ring_p5s02b_20261010_105511.vi (f9ae7751), planned on its real "
                "graph 431cfd83 (prep_c163_a1_2_mk.py); start = stage_prerun.x10_start; MAIN <= 675; Error List item-wise (cleared / raised / UNPREDICTED) in " + rel(ELF),
        "plan": {"path": rel(RRP), "md5": md5(RRP)}, "graph": {"path": bp["path"], "md5": md5(os.path.join(ROOT, bp["path"]))}, "bed": base.get("vi"), "bed_md5": base.get("md5"),
        "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [A[k - 1]["id"] for k in rep["unpredicted"]],
        "census_sim_info": {"by_class": dict(csim), "note": "sim end - step 0 (stagekit.sim_census_snapshot); information only - census_predict has no sample "
                                                            "for these rows, so the census is UNPREDICTED (PD387(e)); the step-3 scratch measures it"},
        "ops": KINDS, "cdiff_rows": sorted(fz.get("end_cdiff_rows") or []), "cross_session_refs": "none: planned on the real graph (no rebase)",
        "actions": ent, "new_objects": objs, "case_frame_wires": CF, "wire_sinks": WS, "deletes": [],
        "cen2": {"judged_by": "Wire class by wire ENDS (source key, sink key, frame) - stagekit.gate_cen2 / cen2_wire_ends (PD389(b)); other classes uid census",
                 "new_pairs_sim": c2["new_sim"], "key": c2["key"], "stubs_sim": c2["stubs"]},
        "e1": {"rule": "PD374(f): graph == sim at every executor checkpoint (stagexec.checkpoint_ops)", "checkpoints": cpe, "move_in_checks": []},
        "keys": {"d_td_pb": "position key (chat-T6, PD366, PD370(b))", "vigraph": {"path": "tools/vigraph.py", "md5": md5(VGF)}},
        "errorlist": {"bed_total": EL["base_expected"]["total"], "new_items_predicted": EL["counts"]["raised"] - EL["counts"]["cleared"], "predicted_total": EL["total"],
                      "alternative_total": EL["counts"]["total_if_every_unpredicted_raises_one"], "fixed": EL["elrule"]["fixed"],
                      "item_file": {"path": rel(ELF), "md5": md5(ELF)}, "counts": EL["counts"], "cleared": EL["cleared"], "unpredicted": EL["unpredicted"],
                      "stale_step3": EL["stale_step3"],
                      "rule": "PD396(d): item-wise from the 53-item expected file (cleared by action) + tools/elrule.py new items (raised); alternative = every "
                              "UNPREDICTED op group raises one item",
                      "rule_source": {"module": "tools/elrule.py", "module_md5": EL["elrule"]["module_md5"], "pd": "PD396(d); PD389(d); PD354(a)"},
                      "base_file": EL["base_expected"]["path"], "checked": False,
                      "per_class": {"start_read": el["start_read"], "cleared": el["cleared"], "rule_new": el["rule_new"], "rule_closed": el["rule_closed"],
                                    "predicted": el["predicted"], "classifier": el["classifier"],
                                    "advisory": "PD354(a): non-zero only for a class in neither start_read.classes nor predicted, or |total diff| > 3"}},
        "memory_pred": {"card": "163-a1-3", "checkpoints": cps, "R": mp["R"], "N": mp["N"], "bind_ops": bind, "op_kinds": KINDS,
                        "start_mb": START, "start_cite": START_CITE, "start_rule": "stage_prerun.x10_start (PD352(b), PD396(c))", "peak_mb": mp["peak_mb"], "main_peak_mb": MAIN,
                        "card_limit_mb": LIMIT, "fail_above_mb": mp["fail_above_mb"], "below_fail": mp["ok"], "memstop_mb": SX.MEM_STOP_MB, "prerun_start": xs,
                        "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)}},
        "licence": {"path": rel(LIC), "md5": md5(LIC)}, "sg_census_file": {"path": rel(SGF), "md5": md5(SGF)},
        "summary": fz.get("summary")}
json.dump(pred, open(PP, "w", encoding="utf-8"), indent=1)
print("FACT ops", dict(collections.Counter(KINDS)), "census", pred["census"], pred["census_overall"], "unpredicted", len(pred["census_unpredicted"]),
      "| EL", pred["errorlist"]["predicted_total"], "alt", pred["errorlist"]["alternative_total"], "| end rows", len(pred["cdiff_rows"]), "open pairs", len(p.get("open_rows") or []), flush=True)
for e in ent:
    print("FACT PRED A{A} {id} {op} {verdict} {0}".format(e.get("symbols") or e.get("frames_resolved") or "", **e), flush=True)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (PP, SGF))
gate("SP pred written, keyed to the plan md5", J(PP)["plan"]["md5"] == md5(RRP))
sys.exit(gate.result())
