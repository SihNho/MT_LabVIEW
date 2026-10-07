# ---
# labview: none
# hardware: none
# ---
r"""prep_c144_a2_2_pred - card 144-a2-2 steps 2+3 (OFFLINE, no LabVIEW). Regenerates plan_ring_p4_s04v18_pred.json for the s04 plan AFTER
stage_prerun --rebase onto the REAL s03 graph (graph_ring_p4s03_20261007_205535.json 5638469b; prep_c144_a2_2_rebase.log, plan 9ff46b0e).
COPIED from prep_c144_1_pred.py (bbf12f62: the post-rebase pred builder, RB/RB2 gates, EL base = a MEASURED expected file) with the s04 names
of prep_c144_p1_pred.py (session table prep_c144_p1_session.json). No gate loosened. Changes: s03 -> s04 names; START 598.5 (fresh load of the
s03 file, card 144-a2-1, brief step 2); EL base = errorlist_expected_D1_ring_p4s03_20261007_202957.json (2b8f9f25, measured 55); RB2 pins
the s03 file md5 prefix 282301ca and the real graph 5638469b; X10 also reported by the mk script's per-op formula (prep_c144_p1_mk.py:75)
for ops 79..97 and the next op 98 at 598.5 (report only, no re-cut).
Existing tools checked: prep_c144_1_pred.py / prep_c144_p1_pred.py / prep_c144_p1_mk.py (reused by copy); tools/elrule.py via
prep_c143_3_elrule.py (the PD349 rule).
PREDICTION CONTRACT: RB plan FINAL, base not provisional, open_rows_match, 23 actions, no negative uid; RB2 base vi md5 282301ca.., real graph
  5638469b; C each action once; X10 peak at 598.5 printed (provisional 677.6 at 596.0 -> expect ~680.1; the gate is the model's own fail
  threshold, a FAIL is reported, not adjusted); X17 PASS; EL total by the rule (number printed, not typed; p1 said 60 on base 55 = s03 PRED);
  SP pred keyed to the plan md5.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c144_a2_2_pred.log -- py -u tools/bench/prep_c144_a2_2_pred.py"""
import collections, hashlib, json, os, sys                                                # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR, census_predict as CPR                        # noqa: E401,E402
import prep_c143_3_elrule as ELR                                                            # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
RRP, PP = os.path.join(B, "plan_ring_p4_s04v18.json"), os.path.join(B, "plan_ring_p4_s04v18_pred.json")
V18 = os.path.join(B, "plan_ring_p4_v18.json")
SESS = os.path.join(B, "prep_c144_p1_session.json")
GRAPH, GRAPH_MD5 = os.path.join(B, "graph_ring_p4s03_20261007_205535.json"), "5638469b4ea6c259de9802f81e91abd5"
EXPF, EXPF_MD5 = os.path.join(B, "errorlist_expected_D1_ring_p4s03_20261007_202957.json"), "2b8f9f25e662ef72bf90b61e9463f1fa"
START, START_CITE = 598.5, "session 3 file D1_ring_p4s03_20261007_202957.vi (282301ca) measured FRESH load 598.5 MB (card 144-a2-1; 610.0 after reads = the reads' own cost, already in the model; brief 144-a2-2 step 2)"
OLD_PRED_MD5, OLD_EL, OLD_START, OLD_PEAK = "f325cdc95f6531500915031e7dabf9ec", 60, 596.0, 677.6
S3N, NEXT = 78, 98
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
gate("M0 graph 5638469b and EL expected file 2b8f9f25 md5 == card", md5(GRAPH) == GRAPH_MD5 and md5(EXPF) == EXPF_MD5, (md5(GRAPH), md5(EXPF)))
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
gate("RB2 base doc vi md5 282301ca.. (s03 file); fs_carried.real_graph md5 == 5638469b (the graph file); base file md5 == plan's",
     str(base.get("md5") or "").startswith("282301ca") and rg.get("md5") == GRAPH_MD5 and md5(os.path.join(ROOT, rg["path"])) == rg["md5"]
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
print("FACT X10 at start {0}: N {1} R {2} peak {3} fail_above {4} ok {5} margin {6} | prerun's own start {7} -> peak {8} | provisional {9} at {10}".format(
      START, mp["N"], mp["R"], mp["peak_mb"], mp["fail_above_mb"], mp["ok"], round(mp["fail_above_mb"] - mp["peak_mb"], 1), xs, mp2 and mp2["peak_mb"],
      OLD_PEAK, OLD_START), flush=True)
# the mk script's per-op formula on v18 (prep_c144_p1_mk.py:75), for the next op's peak (report only)
v18 = J(V18)
VOPS = SX.compile_plan(v18)
VB = set(k for k, o in enumerate(VOPS, 1) if o["kind"] in SX.BIND_KINDS)
v = lambda k: float(MODEL[k]["value"])                                                      # noqa: E731
pk = lambda a, b: round(START + len({a, b} | set(k for k in VB if a < k <= b)) * v("read_mb") + (b - a) * (v("edit_mb") + v("other_mb")) + v("final_read_mb"), 1)   # noqa: E731
first_over = next((b for b in range(S3N + 1, len(VOPS) + 1) if pk(S3N, b) > SPR.X10_FAIL_MB), None)
print("FACT X10 per-op formula at {0}: ops {1}..97 peak {2}; next op {3} peak {4}; first op over {5} = {6}; limit {7}".format(
      START, S3N + 1, pk(S3N, 97), NEXT, pk(S3N, NEXT), SPR.X10_FAIL_MB, first_over, SPR.X10_FAIL_MB), flush=True)
gate("X10 peak {0} at start {1} <= fail threshold {2} (memory_model.json)".format(mp["peak_mb"], START, mp["fail_above_mb"]), mp["ok"], mp, fatal=False)   # brief step 2: report only, no re-cut; the pred records below_fail
ok17, det17 = SPR.x17_gate([p])
gate("X17 over s04v18", ok17, det17)
rep = CPR.predict(p, {}, J(os.path.join(B, "census_samples.json")))
sf = fz.get("step_files") or []
st0, last = J(sf[0]["path"])["state"], J(sf[-1]["path"])["state"]
madeu = set(int(u) for u in (last.get("sym") or {}).values() if isinstance(u, int)) - set(int(u) for u in (st0.get("sym") or {}).values() if isinstance(u, int))
ex = J(EXPF)
EL_S3 = int(ex["total"])
ELP = ELR.predict(st0, last, EL_S3, madeu, extra_owner_states=(base,))
byc = collections.Counter(k[0] for k in ELP["new_items"]), collections.Counter(k[0] for k in ELP["closed_items"])
print("EL PD349 s04: base {0} (MEASURED s03 file) new {1} closed {2} -> {3} (provisional pred {4} on base 55 = s03 PRED); per class new {5} closed {6}; "
      "open at start {7}; uncertain {8}; detail_end {9}; created {10}; steps {11} -> {12}".format(
          EL_S3, ELP["new_items"], ELP["closed_items"], ELP["predicted_total"], OLD_EL, dict(byc[0]), dict(byc[1]), ELP["open_at_start"],
          ELP["uncertain_base_newly_unwired_inputs"], ELP["detail_end"], sorted(madeu), sf[0]["path"], sf[-1]["path"]), flush=True)
print("FACT EL rule: {0}".format(ELP.get("rule")), flush=True)
pred = {"schema": "ring-p3b-pred/1", "card": "144-a2-2", "note": "P4 v18 session 4 (v18 ops 79..97) as one bed session on session 3's ADOPTED file "
        "D1_ring_p4s03_20261007_202957.vi (card 144-a2-1); rebased onto its real graph 5638469b (prep_c144_a2_2_rebase.log); start = its MEASURED "
        "fresh load 598.5 (PD320(d)); Error List by the PD349 rule on the MEASURED s03 Error List (55); replaces provisional pred " + OLD_PRED_MD5,
        "plan": {"path": rel(RRP), "md5": md5(RRP)}, "graph": {"path": bp["path"], "md5": md5(os.path.join(ROOT, bp["path"]))}, "bed": base.get("vi"), "bed_md5": base.get("md5"),
        "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [p["actions"][k - 1]["id"] for k in rep["unpredicted"]],
        "ops": [o["kind"] for o in ops], "cdiff_rows": sorted(fz.get("end_cdiff_rows") or []), "cross_session_refs": "bound by stage_prerun --rebase (finalized.rebase)",
        "errorlist": {"bed_total": EL_S3, "new_items_predicted": len(ELP["new_items"]) - len(ELP["closed_items"]), "predicted_total": ELP["predicted_total"],
                      "alternative_total": None, "fixed": ELP, "rule": ELP["rule"] + "; base = s03 file measured " + str(EL_S3) + " (" + rel(EXPF) + ")",
                      "rule_source": {"path": "tools/bench/prep_c143_3_elrule.py", "md5": md5(os.path.join(B, "prep_c143_3_elrule.py")),
                                      "module": "tools/elrule.py", "module_md5": md5(os.path.join(ROOT, "tools", "elrule.py")), "pd": "PD349"},
                      "previous": {"pred_md5": OLD_PRED_MD5, "predicted_total": OLD_EL, "rule": "PD349 on base 55 = s03 PREDICTED, provisional base (card 144-P1)"},
                      "base_file": rel(EXPF), "checked": False},
        "memory_pred": {"card": "144-a2-2", "checkpoints": cps, "R": mp["R"], "N": mp["N"], "bind_ops": bind, "op_kinds": [o["kind"] for o in ops],
                        "start_mb": START, "start_cite": START_CITE, "peak_mb": mp["peak_mb"], "fail_above_mb": mp["fail_above_mb"], "below_fail": mp["ok"],
                        "next_op": NEXT, "next_op_peak_mb": pk(S3N, NEXT),
                        "prerun_start": xs, "prerun_peak_mb": mp2 and mp2["peak_mb"], "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)}},
        "summary": fz.get("summary")}
json.dump(pred, open(PP, "w", encoding="utf-8"), indent=1)
print("FACT ops", dict(collections.Counter(pred["ops"])), "census", pred["census"], "overall", pred["census_overall"], "unpredicted", len(pred["census_unpredicted"]),
      "| EL", pred["errorlist"]["predicted_total"], "| end rows", len(pred["cdiff_rows"]), "open pairs", len(p.get("open_rows") or []), flush=True)
for x in ("tools/bench/plan_ring_p4_s04v18.json", "tools/bench/plan_ring_p4_s04v18_pred.json", "tools/recipes/stage_d1_ring_p4_s04v18.py",
          "tools/recipes/stage_d1_ring_p4_s04v18_scratch.py", "tools/bench/termclass_table.json", "tools/bench/prep_c143_3_elrule.py", "tools/elrule.py",
          bp["path"]):
    print("FACT md5 {0} {1}".format(md5(os.path.join(ROOT, x)), x), flush=True)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (RRP, PP))
gate("SP pred written, keyed to the plan md5", J(PP)["plan"]["md5"] == md5(RRP))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
sys.exit(1 if G["fail"] else 0)
