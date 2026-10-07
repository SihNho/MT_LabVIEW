# ---
# labview: none
# hardware: none
# ---
r"""prep_c145_a2_6_pred - card 145-a2-6 steps 2+3 (OFFLINE, no LabVIEW). Regenerates plan_ring_p4_s05v18_pred.json for the s05 plan AFTER
stage_prerun --rebase onto the REAL s04 graph (graph_ring_p4s04_20261007_223245.json 094ba298; prep_c145_a2_6_rebase.log).
COPIED from prep_c145_2_pred.py (the post-rebase pred builder of s04) with: s04 -> s05 names; session table prep_c145_a2_6_session.json;
START 605.4 (s04 adopted file's MEASURED fresh load, diag_c145_a2_1_facts.md:15); EL base = errorlist_expected_D1_ring_p4s04_20261007_215031.json
(1a28fe86, MEASURED 58); EL by the FIXED rule = tools/elrule.py predict WITH subvis (PD351(c): created SubVI calls by measured pane rule) -
prep_c145_2_pred.py called the prep_c143_3_elrule re-export without subvis; RB2 pins the s04 file md5 95e408ff and the graph 094ba298;
X10 per-op formula for ops 98..124 and next op 125 at 605.4, reported against fail_above 680 / MEMSTOP 695 (non-fatal, no re-cut);
OLD_* = the provisional pred 6666a718 (EL 57 on base 60 = s04 PRED, start 598.5, peak 678.5).
Existing tools checked: prep_c145_2_pred.py / prep_c145_p1_pred.py (copied); tools/elrule.py (predict, subvis_from_plan).
PREDICTION CONTRACT: RB plan FINAL, base not provisional, open_rows_match, N actions == session table, no negative uid; RB2 base vi md5
  95e408ff.., real graph 094ba298; C each action once; X10 printed (expect ~685.4 > 680, reported); X17 PASS; EL by the rule (printed, not
  typed); SP pred keyed to the plan md5.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c145_a2_6_pred.log -- py -u tools/bench/prep_c145_a2_6_pred.py"""
import collections, hashlib, json, os, sys                                                # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR, census_predict as CPR                        # noqa: E401,E402
import elrule as ELR                                                                        # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
RRP, PP = os.path.join(B, "plan_ring_p4_s05v18.json"), os.path.join(B, "plan_ring_p4_s05v18_pred.json")
V18 = os.path.join(B, "plan_ring_p4_v18.json")
SESS = os.path.join(B, "prep_c145_a2_6_session.json")
GRAPH, GRAPH_MD5 = os.path.join(B, "graph_ring_p4s04_20261007_223245.json"), "094ba298ba7b2c1d69f92c84d8ecb626"
EXPF, EXPF_MD5 = os.path.join(B, "errorlist_expected_D1_ring_p4s04_20261007_215031.json"), "1a28fe86db42a982e6828f5ed8e98da1"
REQF = os.path.join(B, "subvi_requiredness.json")
START, START_CITE = 605.4, "session 4 file D1_ring_p4s04_20261007_215031.vi (95e408ff) measured FRESH load 605.4 MB (card 145-a2-1, diag_c145_a2_1_facts.md:15)"
OLD_PRED_MD5, OLD_EL, OLD_START, OLD_PEAK = "6666a7183fc4a2ca428e62fab5897803", 57, 598.5, 678.5
S4N, LAST, NEXT = 97, 124, 125
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                 # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []


def gate(label, ok, d="", fatal=True):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)
    if not ok and fatal:
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
        sys.exit(1)


print("FACT old pred md5 {0} (on disk {1}); plan md5 {2}".format(OLD_PRED_MD5, md5(PP), md5(RRP)), flush=True)
gate("M0 graph 094ba298, EL expected file 1a28fe86, requiredness 13b0d75f md5 == card",
     md5(GRAPH) == GRAPH_MD5 and md5(EXPF) == EXPF_MD5 and md5(REQF) == "13b0d75f6ac66511e43b3b22c898368d", (md5(GRAPH), md5(EXPF), md5(REQF)))
p = J(RRP)
NA = J(SESS)["actions"]
fz = p.get("finalized") or {}
bp = (fz.get("base") or p.get("base") or {})
neg = SPR.negative_uids_left(p)
gate("RB plan rebased: base {0} not provisional, FINAL, open_rows_match, {1} actions == session table {2}; no negative uid left".format(
     bp.get("path"), len(p["actions"]), NA),
     not (p.get("base") or {}).get("provisional") and p.get("final") is True and fz.get("open_rows_match") is True and len(p["actions"]) == NA and not neg,
     {"base": p.get("base"), "rebase": fz.get("rebase"), "neg": neg[:6]})
base = J(bp["path"])
rg = (base.get("fs_carried") or {}).get("real_graph") or {}
print("FACT base doc vi {0} md5 {1}; real_graph {2}; base file {3} md5 {4}".format(base.get("vi"), base.get("md5"), rg, bp.get("path"), bp.get("md5")), flush=True)
gate("RB2 base doc vi md5 95e408ff.. (s04 file); fs_carried.real_graph md5 == 094ba298 (the graph file) or base IS the graph; base file md5 == plan's",
     str(base.get("md5") or "").startswith("95e408ff") and (rg.get("md5") == GRAPH_MD5 or (not rg and md5(os.path.join(ROOT, bp["path"])) == GRAPH_MD5))
     and md5(os.path.join(ROOT, bp["path"])) == bp.get("md5"), (base.get("md5"), rg, bp))
ops = SX.compile_plan(p)
gate("C compile: {0} actions -> {1} ops, each action once".format(len(p["actions"]), len(ops)),
     sorted(n for o in ops for n in o["acts"]) == list(range(1, len(p["actions"]) + 1)))
bind = sorted(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS)
cps = sorted(set([0, len(ops)]) | set(bind))
MODEL = SPR.load_memory_model()
mp = SPR.x10_model_peak([o["kind"] for o in ops], cps, model=MODEL, start_mb=START)
xs = SPR.x10_plan_start(RRP, MODEL)
mp2 = SPR.x10_model_peak([o["kind"] for o in ops], cps, model=MODEL, start_mb=xs[0]) if xs else None
print("FACT X10 at start {0}: N {1} R {2} peak {3} fail_above {4} ok {5} margin {6}; MEMSTOP {7} margin {8} | prerun's own start {9} -> peak {10} | provisional {11} at {12}".format(
      START, mp["N"], mp["R"], mp["peak_mb"], mp["fail_above_mb"], mp["ok"], round(mp["fail_above_mb"] - mp["peak_mb"], 1), SX.MEM_STOP_MB,
      round(SX.MEM_STOP_MB - mp["peak_mb"], 1), xs, mp2 and mp2["peak_mb"], OLD_PEAK, OLD_START), flush=True)
v18 = J(V18)
VOPS = SX.compile_plan(v18)
VB = set(k for k, o in enumerate(VOPS, 1) if o["kind"] in SX.BIND_KINDS)
v = lambda k: float(MODEL[k]["value"])                                                      # noqa: E731
pk = lambda a, b: round(START + len({a, b} | set(k for k in VB if a < k <= b)) * v("read_mb") + (b - a) * (v("edit_mb") + v("other_mb")) + v("final_read_mb"), 1)   # noqa: E731
first_over = next((b for b in range(S4N + 1, len(VOPS) + 1) if pk(S4N, b) > SPR.X10_FAIL_MB), None)
print("FACT X10 per-op formula at {0}: ops {1}..{2} peak {3}; next op {4} peak {5}; first op over {6} = {7}".format(
      START, S4N + 1, LAST, pk(S4N, LAST), NEXT, pk(S4N, NEXT), SPR.X10_FAIL_MB, first_over), flush=True)
gate("X10 peak {0} at start {1} <= fail threshold {2} (memory_model.json)".format(mp["peak_mb"], START, mp["fail_above_mb"]), mp["ok"], mp, fatal=False)   # brief step 3: report only
ok17, det17 = SPR.x17_gate([p])
gate("X17 over s05v18", ok17, det17)
rep = CPR.predict(p, {}, J(os.path.join(B, "census_samples.json")))
sf = fz.get("step_files") or []
st0, last = J(sf[0]["path"])["state"], J(sf[-1]["path"])["state"]
madeu = set(int(u) for u in (last.get("sym") or {}).values() if isinstance(u, int)) - set(int(u) for u in (st0.get("sym") or {}).values() if isinstance(u, int))
ex = J(EXPF)
EL_S4 = int(ex["total"])
SUBV = ELR.subvis_from_plan(p, st0, last)
ELP = ELR.predict(st0, last, EL_S4, madeu, extra_owner_states=(base,), subvis=SUBV)
byc = collections.Counter(k[0] for k in ELP["new_items"]), collections.Counter(k[0] for k in ELP["closed_items"])
print("EL FIXED s05: base {0} (MEASURED s04 file) new {1} closed {2} -> {3} (provisional pred {4}); per class new {5} closed {6}; "
      "open at start {7}; open at end {8}; uncertain base {9}; uncertain subvi {10}; subvis {11}; detail_end {12}; created {13}; steps {14} -> {15}".format(
          EL_S4, ELP["new_items"], ELP["closed_items"], ELP["predicted_total"], OLD_EL, dict(byc[0]), dict(byc[1]), ELP["open_at_start"], ELP["open_at_end"],
          ELP["uncertain_base_newly_unwired_inputs"], ELP["uncertain_subvi_terminals"], SUBV, ELP["detail_end"], sorted(madeu), sf[0]["path"], sf[-1]["path"]), flush=True)
print("FACT EL rule: {0}".format(ELP.get("rule")), flush=True)
pred = {"schema": "ring-p3b-pred/1", "card": "145-a2-6", "note": "P4 v18 session 5 (v18 ops 98..124) as one bed session on session 4's ADOPTED file "
        "D1_ring_p4s04_20261007_215031.vi (95e408ff, card 145-a2-1); re-made on s04 plan f349c39a's simulated end (prep_c145_a2_6_mk.py) and rebased onto "
        "its real graph 094ba298 (prep_c145_a2_6_rebase.log); start = its MEASURED fresh load 605.4 (PD320(d)); Error List by the FIXED rule "
        "(tools/elrule.py, PD349 + PD351(c)) on the MEASURED s04 Error List (58); replaces provisional pred " + OLD_PRED_MD5,
        "plan": {"path": rel(RRP), "md5": md5(RRP)}, "graph": {"path": bp["path"], "md5": md5(os.path.join(ROOT, bp["path"]))}, "bed": base.get("vi"), "bed_md5": base.get("md5"),
        "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [p["actions"][k - 1]["id"] for k in rep["unpredicted"]],
        "ops": [o["kind"] for o in ops], "cdiff_rows": sorted(fz.get("end_cdiff_rows") or []), "cross_session_refs": "bound by stage_prerun --rebase (finalized.rebase)",
        "errorlist": {"bed_total": EL_S4, "new_items_predicted": len(ELP["new_items"]) - len(ELP["closed_items"]), "predicted_total": ELP["predicted_total"],
                      "alternative_total": None, "fixed": ELP, "rule": ELP["rule"] + "; base = s04 file measured " + str(EL_S4) + " (" + rel(EXPF) + ")",
                      "rule_source": {"module": "tools/elrule.py", "module_md5": md5(os.path.join(ROOT, "tools", "elrule.py")), "requiredness": rel(REQF),
                                      "requiredness_md5": md5(REQF), "pd": "PD349+PD351(c)"},
                      "previous": {"pred_md5": OLD_PRED_MD5, "predicted_total": OLD_EL, "rule": "PD349 on base 60 = s04 PREDICTED, provisional base (card 145-a1-P1)"},
                      "base_file": rel(EXPF), "checked": False},
        "memory_pred": {"card": "145-a2-6", "checkpoints": cps, "R": mp["R"], "N": mp["N"], "bind_ops": bind, "op_kinds": [o["kind"] for o in ops],
                        "start_mb": START, "start_cite": START_CITE, "peak_mb": mp["peak_mb"], "fail_above_mb": mp["fail_above_mb"], "below_fail": mp["ok"],
                        "memstop_mb": SX.MEM_STOP_MB, "next_op": NEXT, "next_op_peak_mb": pk(S4N, NEXT),
                        "prerun_start": xs, "prerun_peak_mb": mp2 and mp2["peak_mb"], "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)}},
        "summary": fz.get("summary")}
json.dump(pred, open(PP, "w", encoding="utf-8"), indent=1)
print("FACT ops", dict(collections.Counter(pred["ops"])), "census", pred["census"], "overall", pred["census_overall"], "unpredicted", len(pred["census_unpredicted"]),
      "| EL", pred["errorlist"]["predicted_total"], "| end rows", len(pred["cdiff_rows"]), "open pairs", len(p.get("open_rows") or []), flush=True)
for x in ("tools/bench/plan_ring_p4_s05v18.json", "tools/bench/plan_ring_p4_s05v18_pred.json", "tools/recipes/stage_d1_ring_p4_s05v18.py",
          "tools/recipes/stage_d1_ring_p4_s05v18_scratch.py", "tools/elrule.py", bp["path"]):
    print("FACT md5 {0} {1}".format(md5(os.path.join(ROOT, x)), x), flush=True)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (RRP, PP))
gate("SP pred written, keyed to the plan md5", J(PP)["plan"]["md5"] == md5(RRP))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
sys.exit(1 if G["fail"] else 0)
