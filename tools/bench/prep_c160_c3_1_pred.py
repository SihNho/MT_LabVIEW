# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_160-c3-1.md
# ---
r"""prep_c160_c3_1_pred - card 160-c3-1 (OFFLINE, no LabVIEW): plan_ring_p5s02b_pred.json for P5-2 step 2 (plan_ring_p5s02b.json f4520b10, FINAL
on the REAL 94ffff94 graph 7ac24924, prep_c160_b3_1_mk.py) + the sink-gate census file prep_c160_c3_1_session.json that stagekit.RingSession reads
(`sink_gate_census`, from prep_c156_a1_1_lib.sg_census; the b3-1 session table has no such key). Flow of prep_c156_a1_1_pred.py (27fc52dc, a
top-level script: importing it runs it); Gate / main_of from prep_c156_a1_1_lib; compile / checkpoints from stagexec (compile_plan, checkpoint_ops);
X10 from stage_prerun (x10_start, x10_plan_start, x10_model_peak via main_of); census from census_predict; CEN2 ends from stagekit.cen2_wire_ends;
the Error List block READ from errorlist_predicted_D1_ring_p5s02b_end.json (prep_c160_c3_1_el.py: elrule + item-wise cleared / raised).
Per action (PD391(d), PD389(c)): A28 / A35 MERGE with the expected uid READ from the session table `merge` and checked on the sim end; A32 / A39
stub deleted first + fresh connect, the new wire uid NOT predicted; the delete rows dw_a13 / dw_go / dw_ho each their own entry (present at step
n-1, gone at step n). CEN2 judged by wire ENDS (stagekit.gate_cen2, PD389(b)). PB by POSITION (PD370(b)). MAIN limit 675.
STALE 156 expectations changed, not loosened: X1 (156: plan start == bed start == maker's start) -> the maker's start is START_ASSUMED 603.4 (b3-1,
conservative), x10_start(94ffff94) is 599.7: both recorded, MAIN gated at both; E1 move_in checks (156: three move_in ops) -> none in step 2 (0 move_in).
PREDICTION CONTRACT: M0 pins; RB plan FINAL, 20 actions == session, no negative uid; C 10 ops == session compile (kind, acts); E1 checkpoints ==
  checkpoint_ops == session [0,2,3,5,7,9,10], each a step file with its recorded md5; X1 x10_plan_start == x10_start(94ffff94); X10 MAIN at that start
  <= 675 and at START_ASSUMED == prep_c161_a3_2_x10.json (pins checked); X17 PASS; MG MERGE uids read and on the sim end; ST stub delete before its connect,
  sink unwired after the delete, a fresh sourced wire at the end; DW each delete row present before / gone after; CEN2 ends new pairs counted;
  EL item file keyed to this plan; SG census written; SP pred keyed to the plan md5.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c160_c3_1_pred.log -- py -u tools/bench/prep_c160_c3_1_pred.py"""
import collections, json, os, sys                                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import stagexec as SX, stage_prerun as SPR, census_predict as CPR                        # noqa: E401,E402
import stage_shared as SH                                                                   # noqa: E402  checkpoint_step_table (card 162-a2-3)
import stagekit as K                                                                        # noqa: E402  cen2_wire_ends (shared)
import prep_c156_a1_1_lib as L                                                              # noqa: E402  Gate / main_of / sg_census (shared)
md5, rel, J = L.md5, L.rel, L.J
B, T = os.path.join(ROOT, "tools", "bench"), os.path.join(ROOT, "tools")
RRP, PP = os.path.join(B, "plan_ring_p5s02b.json"), os.path.join(B, "plan_ring_p5s02b_pred.json")
SESS, SGF = os.path.join(B, "prep_c160_b3_1_session.json"), os.path.join(B, "prep_c160_c3_1_session.json")
ELF, LIC = os.path.join(B, "errorlist_predicted_D1_ring_p5s02b_end.json"), os.path.join(B, "plan_ring_p5s02b_licence.json")
GRAPH, VGF = os.path.join(B, "graph_ring_p5s02a_20261010_032547.json"), os.path.join(T, "vigraph.py")
PINS = {RRP: "f4520b10", SESS: "e5279899", GRAPH: "7ac24924", os.path.join(B, "plan_ring_p5s02b_in.json"): "56bfddd3",
        os.path.join(B, "plan_ring_p5s02b_in2.json"): "927b805c", os.path.join(B, "memory_model.json"): "5b87de43", VGF: "a7eb58c7",
        os.path.join(T, "stagesim.py"): "95a162ba", os.path.join(T, "stagexec.py"): "a4df7e15", os.path.join(T, "stagekit.py"): "9b8f82c1",   # re-pinned 161-a3-1 from 0b5bb678
        os.path.join(T, "stage_prerun.py"): "7605116f"}
BEDVI_MD5_PREFIX, MAIN_SRC_READS, LIMIT = "94ffff94", 2, 675.0
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
gate("RB2 base IS the real 94ffff94 graph 7ac24924; its vi md5 {0}".format(str(base.get("md5"))[:8]),
     md5(os.path.join(ROOT, bp["path"])) == md5(GRAPH) == bp.get("md5") and str(base.get("md5") or "").startswith(BEDVI_MD5_PREFIX), (bp, base.get("vi"), base.get("md5")))
A = p["actions"]
ops = SX.compile_plan(p)
SC = S["compile"]
gate("C compile: {0} actions -> {1} ops == session compile (kind, acts), each action once".format(len(A), len(ops)),
     [[o["kind"], list(o["acts"])] for o in ops] == [[k, list(a)] for k, _h, a in SC["ops"]] and sorted(n for o in ops for n in o["acts"]) == list(range(1, len(A) + 1)),
     [[o["kind"], o["acts"]] for o in ops])
cps = list(SX.checkpoint_ops(ops))
bind = sorted(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS)
SFN = dict((int(x["n"]), x) for x in fz.get("step_files") or [])
cpe = SH.checkpoint_step_table(ops, cps, SFN, A)                                             # card 162-a2-3: tools/stage_shared.py (+ ids), was a copied block
print("FACT E1 checkpoints {0}: {1}".format(cps, [(e["op"], e["kind"], e["action"], e["step_file"]) for e in cpe]), flush=True)
DWK = sorted(k for k, o in enumerate(ops, 1) if o["kind"] == "delete_wire")   # 161-b1-1 (PD393(a), stagexec a4df7e15): + every delete_wire op
gate("E1 checkpoints {0} == stagexec.checkpoint_ops == session {1} | delete_wire ops {2}; each has its simulated step file, md5 == recorded".format(
     cps, SC["checkpoints"], DWK),
     cps == sorted(set(SC["checkpoints"]) | set(DWK)) and all(e["step_file"] and md5(os.path.join(ROOT, e["step_file"])) == e["md5"] for e in cpe), cpe)
MODEL = SPR.load_memory_model()
XS0 = SPR.x10_start(base.get("md5"), MODEL)
START, START_CITE = XS0 if XS0 else (None, None)
xs = SPR.x10_plan_start(RRP, MODEL)
SA = S["start_mb"]
gate("X1 ONE measured start: x10_plan_start(plan) {0} == x10_start(94ffff94) {1}; START_ASSUMED (b3-1, conservative) {2} recorded".format(xs and xs[0], START, SA),
     xs is not None and START is not None and xs[0] == START, (xs, XS0))
KINDS = [o["kind"] for o in ops]
MAIN, mp, _c = L.main_of(len(ops), KINDS, SX, SPR, MODEL, START, MAIN_SRC_READS)
MAINA, mpa, _c = L.main_of(len(ops), KINDS, SX, SPR, MODEL, SA, MAIN_SRC_READS)
print("FACT X10 at start {0}: N {1} R {2} Executor peak {3} MAIN {4}; at START_ASSUMED {5}: peak {6} MAIN {7}; card limit {8}; fail_above {9}; MEMSTOP {10}".format(
      START, mp["N"], mp["R"], mp["peak_mb"], MAIN, SA, mpa["peak_mb"], MAINA, LIMIT, mp["fail_above_mb"], SX.MEM_STOP_MB), flush=True)
XR = (lambda q: J(q) if os.path.exists(q) else {})(os.path.join(B, "prep_c161_a3_2_x10.json")); XOK = bool(XR) and all(md5(os.path.join(ROOT, q)) == w for q, w in XR["pins"].items())  # noqa: E702  161-a3-2 (PD394(b)): X10 record on the shared checkpoint rule, pins checked
gate("X10 MAIN {0} (start {1}) <= {2}; at START_ASSUMED {3}: Executor peak {4} == x10 record {5}, MAIN {6} == x10 record {7} <= {2}; record present + pins match {8}".format(MAIN, START, LIMIT, SA, mpa["peak_mb"], XR.get("exec_peak"), MAINA, XR.get("main"), XOK),
     mp["ok"] and MAIN <= LIMIT and XOK and XR["start_assumed_mb"] == SA and mpa["peak_mb"] == XR["exec_peak"] and MAINA == XR["main"] and MAINA <= LIMIT, (mp, mpa, XR.get("pins")))
ok17, det17 = SPR.x17_gate([p])
gate("X17 over P5-2 step 2", ok17, det17)
sf = fz.get("step_files") or []
st = lambda n: J(SFN[n]["path"])["state"]                                                   # noqa: E731
wires_of = lambda s: set(int(t["wire_uid"]) for t in s["terminals"] if t.get("wire_uid"))   # noqa: E731
objs_of = lambda s: set(int(o["uid"]) for o in s.get("objs") or [])                         # noqa: E731
term_rows = lambda s, tu: [t for t in s["terminals"] if int(t["term_uid"]) == int(tu)]      # noqa: E731
last = st(len(A))
idx = dict((a["id"], n) for n, a in enumerate(A, 1))
pos = dict((e["id"], e["pos"]) for e in (S.get("merge") or []) + (S.get("stubs") or []))
ent = []
for n, a in enumerate(A, 1):
    e = {"n": n, "id": a["id"], "op": a["op"], "A": pos.get(a["id"]), "verdict": "PLAN"}
    if a["op"] == "delete_wire":
        u = int(a["wire_uid"])
        pre, post = st(n - 1), st(n)
        e.update(verdict="DELETE", wire_uid=u, present_before=u in wires_of(pre) or u in objs_of(pre), gone_after=u not in wires_of(post) and u not in objs_of(post),
                 why=a.get("why"))
    ent.append(e)
MG = []
for m in S.get("merge") or []:
    e = ent[idx[m["id"]] - 1]
    rs = term_rows(last, m["stub_term"])
    e.update(verdict="MERGE", stub_term=m["stub_term"], expect_uid=m["expect"], sim_end_wires=sorted(set(t.get("wire_uid") for t in rs)),
             cen2="judged by wire ENDS (stagekit.gate_cen2 / cen2_wire_ends, PD389(b)); the uid is printed as UID-REUSE, not judged",
             assumption="MERGE (PD388(c), PD391(d)): unmeasured; the step-2 scratch measures it")
    MG.append(e)
gate("MG A28/A35 MERGE: expected uid read from the session table == the stub-term wire at the sim end: {0}".format([(e["id"], e["stub_term"], e["expect_uid"], e["sim_end_wires"]) for e in MG]),
     len(MG) == 2 and all(e["sim_end_wires"] == [e["expect_uid"]] for e in MG), MG)
STB = []
for sb in S.get("stubs") or []:
    e = ent[idx[sb["id"]] - 1]
    dn = next(k for k, a in enumerate(A, 1) if a["op"] == "delete_wire" and int(a["wire_uid"]) == int(sb["wire"]))
    rs_pre, rs_del, rs_end = term_rows(st(dn - 1), sb["sink_term"]), term_rows(st(dn), sb["sink_term"]), term_rows(last, sb["sink_term"])
    endw = sorted(set(t.get("wire_uid") for t in rs_end))
    srcd = [t for t in last["terminals"] if t.get("wire_uid") in endw and t.get("is_source")]
    e.update(verdict="DELETE+FRESH", sink_term=sb["sink_term"], stub_wire=sb["wire"], stub_deleted_by=A[dn - 1]["id"], delete_n=dn, new_uid=None, uid_predicted=False,
             cen2="judged by wire ENDS (PD389(b)); the new wire uid is NOT predicted (PD391(d))",
             checks={"delete_before_connect": dn < idx[sb["id"]], "stub_on_sink_before_delete": [t.get("wire_uid") for t in rs_pre] == [sb["wire"]],
                     "sink_unwired_after_delete": all(not t.get("wire_uid") for t in rs_del), "end_wire_not_stub": len(endw) == 1 and endw[0] != sb["wire"],
                     "end_wire_has_source": len(srcd) == 1})
    STB.append(e)
gate("ST A32/A39 stub deleted first, sink unwired after the delete, a fresh sourced wire at the end (uid not predicted): {0}".format(
     [(e["id"], e["stub_deleted_by"], e["checks"]) for e in STB]), len(STB) == 2 and all(all(e["checks"].values()) for e in STB), STB)
DW = [e for e in ent if e["verdict"] == "DELETE"]
gate("DW delete rows {0}: each present at step n-1 and gone at step n".format([(e["id"], e["wire_uid"]) for e in DW]),
     len(DW) == 3 and all(e["present_before"] and e["gone_after"] for e in DW), DW)
c2 = K.cen2_wire_ends(base["terminals"], last["terminals"], last["terminals"], (base.get("owners") or {}).keys())
print("FACT CEN2 by ends on the sim end: new pairs {0} (key {1}); stubs {2}".format(c2["new_sim"], c2["key"], c2["stubs"]), flush=True)
rep = CPR.predict(p, {}, J(os.path.join(B, "census_samples.json")))
print("FACT CENSUS derived {0}; overall {1}; unpredicted rows {2}".format(rep["derived"], rep["overall"], [A[k - 1]["id"] for k in rep["unpredicted"]]), flush=True)
csim = collections.Counter(K.sim_census_snapshot(last).values()) - collections.Counter(K.sim_census_snapshot(st(0)).values())
print("FACT CENSUS sim end - step 0 by class (information only, NOT a census verdict, PD387(e)) {0}".format(dict(csim)), flush=True)
EL = J(ELF)
gate("EL item file {0} keyed to this plan md5; total {1} (cleared {2}, raised {3}, unpredicted {4})".format(rel(ELF), EL["total"], EL["counts"]["cleared"],
     EL["counts"]["raised"], EL["counts"]["unpredicted"]), EL["plan"]["md5"] == md5(RRP) and sum(EL["per_class"]["predicted"].values()) == EL["total"], EL["counts"])
SGC = L.sg_census(p, SX)
sgf = {"schema": "ring-session-census/1", "card": "160-c3-1", "plan": {"path": rel(RRP), "md5": md5(RRP)}, "from_session": {"path": rel(SESS), "md5": md5(SESS)},
       "sink_gate_census": SGC, "actions": len(A), "ops": len(ops), "checkpoints": cps, "start_mb": START, "start_assumed_mb": SA, "main_peak_mb": MAIN,
       "main_peak_at_start_assumed_mb": MAINA, "note": "stagekit.RingSession reads `sink_gate_census`; prep_c160_b3_1_session.json carries none (computed here by prep_c156_a1_1_lib.sg_census)"}
json.dump(sgf, open(SGF, "w", encoding="utf-8"), indent=1)
gate("SG census file written: {0} wire row(s) onto a ControlTerminal, {1} need a sink gate".format(len(SGC), sum(1 for e in SGC if e["needs_sink_gate"])),
     J(SGF)["plan"]["md5"] == md5(RRP), SGC)
el = EL["per_class"]
pred = {"schema": "ring-p3b-pred/1", "card": "160-c3-1",
        "note": "RING P5-2 step 2 (PD388(a), PD390(c), PD391) on the saved p5s02a file D1_ring_p5s02a_20261010_023239.vi (94ffff94), planned on its real graph "
                "7ac24924 (prep_c160_b3_1_mk.py); start = stage_prerun.x10_start; MAIN <= 675; Error List item-wise (cleared / raised / UNPREDICTED) in " + rel(ELF),
        "plan": {"path": rel(RRP), "md5": md5(RRP)}, "graph": {"path": bp["path"], "md5": md5(os.path.join(ROOT, bp["path"]))}, "bed": base.get("vi"), "bed_md5": base.get("md5"),
        "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [A[k - 1]["id"] for k in rep["unpredicted"]],
        "census_sim_info": {"by_class": dict(csim), "note": "sim end - step 0 (stagekit.sim_census_snapshot); information only - census_predict has no sample "
                                                            "for these rows, so the census is UNPREDICTED (PD387(e)); the step-2 scratch measures it"},
        "ops": KINDS, "cdiff_rows": sorted(fz.get("end_cdiff_rows") or []), "cross_session_refs": "none: planned on the real graph (no rebase)",
        "actions": ent,
        "merge": [dict((k, e[k]) for k in ("id", "A", "stub_term", "expect_uid", "cen2", "assumption")) for e in MG],
        "delete_fresh": [dict((k, e[k]) for k in ("id", "A", "sink_term", "stub_wire", "stub_deleted_by", "new_uid", "uid_predicted", "cen2")) for e in STB],
        "deletes": [dict((k, e[k]) for k in ("id", "wire_uid", "present_before", "gone_after")) for e in DW],
        "cen2": {"judged_by": "Wire class by wire ENDS (source key, sink key, frame) - stagekit.gate_cen2 / cen2_wire_ends (PD389(b)); other classes uid census",
                 "new_pairs_sim": c2["new_sim"], "key": c2["key"], "stubs_sim": c2["stubs"]},
        "e1": {"rule": "PD374(f): graph == sim at every executor checkpoint (stagexec.checkpoint_ops)", "checkpoints": cpe, "move_in_checks": []},
        "keys": {"d_td_pb": "position key (chat-T6, PD366, PD370(b))", "vigraph": {"path": "tools/vigraph.py", "md5": md5(VGF)}},
        "errorlist": {"bed_total": EL["base_expected"]["total"], "new_items_predicted": EL["counts"]["raised"] - EL["counts"]["cleared"], "predicted_total": EL["total"],
                      "alternative_total": EL["counts"]["total_if_every_unpredicted_raises_one"], "fixed": EL["elrule"]["fixed"],
                      "item_file": {"path": rel(ELF), "md5": md5(ELF)}, "counts": EL["counts"], "cleared": EL["cleared"], "unpredicted": EL["unpredicted"],
                      "rule": "PD389(d): item-wise from the 56-row expected file (cleared by action) + tools/elrule.py new items (raised); alternative = every "
                              "UNPREDICTED action raises one item",
                      "rule_source": {"module": "tools/elrule.py", "module_md5": EL["elrule"]["module_md5"], "pd": "PD389(d); PD391(d)(e); PD354(a)"},
                      "base_file": EL["base_expected"]["path"], "checked": False,
                      "per_class": {"start_read": el["start_read"], "cleared": el["cleared"], "rule_new": el["rule_new"], "rule_closed": el["rule_closed"],
                                    "predicted": el["predicted"], "classifier": el["classifier"],
                                    "advisory": "PD354(a): non-zero only for a class in neither start_read.classes nor predicted, or |total diff| > 3"}},
        "memory_pred": {"card": "160-c3-1", "checkpoints": cps, "R": mp["R"], "N": mp["N"], "bind_ops": bind, "op_kinds": KINDS,
                        "start_mb": START, "start_cite": START_CITE, "start_rule": "stage_prerun.x10_start (PD352(b))", "peak_mb": mp["peak_mb"], "main_peak_mb": MAIN,
                        "start_assumed_mb": SA, "peak_at_start_assumed_mb": mpa["peak_mb"], "main_peak_at_start_assumed_mb": MAINA,
                        "card_limit_mb": LIMIT, "fail_above_mb": mp["fail_above_mb"], "below_fail": mp["ok"], "memstop_mb": SX.MEM_STOP_MB, "prerun_start": xs,
                        "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)}},
        "licence": {"path": rel(LIC), "md5": md5(LIC)}, "sg_census_file": {"path": rel(SGF), "md5": md5(SGF)},
        "summary": fz.get("summary")}
json.dump(pred, open(PP, "w", encoding="utf-8"), indent=1)
print("FACT ops", dict(collections.Counter(KINDS)), "census", pred["census"], pred["census_overall"], "unpredicted", len(pred["census_unpredicted"]),
      "| EL", pred["errorlist"]["predicted_total"], "alt", pred["errorlist"]["alternative_total"], "| end rows", len(pred["cdiff_rows"]), "open pairs", len(p.get("open_rows") or []), flush=True)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (PP, SGF))
gate("SP pred written, keyed to the plan md5", J(PP)["plan"]["md5"] == md5(RRP))
sys.exit(gate.result())
