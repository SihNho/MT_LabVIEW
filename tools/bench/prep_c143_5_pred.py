r"""prep_c143_5_pred - card 143-5 step 3 (OFFLINE, no LabVIEW; PD335(b)). After prep_c143_5_fix.py (s03 action 1 src #-20 'value' -> base row
name 'StopAll') and `stage_prerun.py --rebase plan_ring_p4_s03v18.json --graph graph_ring_p4s02_20261003_112505.json` (prep_c143_5_rebase2.log,
REBASED final=True): the md5-pinned pred file plan_ring_p4_s03v18_pred.json for stage_d1_ring_p4_s03v18.py / _scratch.py.
COPIED from prep_c143_3_pred.py (card 143-3) with ONE gate changed: RB2. The rebase CARRIED the provisional FS map (FS-CARRY line), so the plan's
base is the augmented copy tools/bench/sim/ring_p4_s03v18_base_real_fsmap.json (stage_prerun.py:3916-3926), not the graph file itself; RB2 now
checks its fs_carried.real_graph md5 == eda9db40 and its vi md5 == the s02 file 84cac487 (prep_c143_5_probe.log). EL: the FIXED predictor
prep_c143_3_elrule.py (selftest_elpred.log 7/0) on the s02 file's measured 53 - unchanged rule.
PREDICTION CONTRACT: RB plan rebased (not provisional, FINAL, open_rows_match, 20 actions, no negative uid left in actions); RB2 base doc vi md5
  84cac487, fs_carried.real_graph md5 eda9db40; C compile each action once; X10 peak at 596.0 <= 680 (else re-cut, PD320(c)); X17 PASS;
  EL fixed predictor: closed items include cond 23166 and local 6902 (s03 action 1 p4_w_stop12, src now #6902.'StopAll'); SP pred keyed to the plan md5.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c143_5_pred.log -- py -u tools/bench/prep_c143_5_pred.py"""
import collections, hashlib, json, os, sys                                                # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR, census_predict as CPR                        # noqa: E401,E402
import prep_c143_3_elrule as ELR                                                            # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
RRP, PP = os.path.join(B, "plan_ring_p4_s03v18.json"), os.path.join(B, "plan_ring_p4_s03v18_pred.json")
EXPF = os.path.join(B, "errorlist_expected_D1_ring_p4s02_20261003_110001.json")
START, START_CITE = 596.0, "session 2 file D1_ring_p4s02_20261003_110001.vi measured load 596.0 MB (diag_c143_2_facts.md; diag_c143_1_graph.log:24; PD333(c))"
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                 # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)
    if not ok:
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
        sys.exit(1)


p = J(RRP)
fz = p.get("finalized") or {}
bp = (fz.get("base") or p.get("base") or {})
neg = [v for a in p["actions"] for v in json.dumps(a).replace(",", " ").replace("}", " ").split() if v.lstrip("-").isdigit() and v.startswith("-")]
gate("RB plan rebased: base {0} not provisional, FINAL, open_rows_match, {1} actions; no negative uid left".format(bp.get("path"), len(p["actions"])),
     not (p.get("base") or {}).get("provisional") and p.get("final") is True and fz.get("open_rows_match") is True and len(p["actions"]) == 20 and not neg,
     {"base": p.get("base"), "rebase": fz.get("rebase"), "neg": neg[:6]})
base = J(bp["path"])
rg = (base.get("fs_carried") or {}).get("real_graph") or {}
gate("RB2 base doc vi md5 == s02 file 84cac487; fs_carried.real_graph md5 eda9db40 (== the graph file); base file md5 == plan's",
     base.get("md5") == "84cac48781c7c915c8f0d7e8fb079341" and rg.get("md5") == "eda9db4088d1be89623e6333268e09ff"
     and md5(os.path.join(ROOT, rg["path"])) == rg["md5"] and md5(os.path.join(ROOT, bp["path"])) == bp.get("md5"),
     (base.get("md5"), rg, bp))
a1 = p["actions"][0]
gate("A1 action 1 p4_w_stop12 src = #6902.'StopAll' (the -20 Local bound; name from the base row)",
     a1["id"] == "p4_w_stop12" and a1["src"] == {"uid": 6902, "term": "StopAll"}, a1.get("src"))
ops = SX.compile_plan(p)
gate("C compile: {0} actions -> {1} ops, each action once".format(len(p["actions"]), len(ops)),
     sorted(n for o in ops for n in o["acts"]) == list(range(1, len(p["actions"]) + 1)))
bind = sorted(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS)
cps = sorted(set([0, len(ops)]) | set(bind))
MODEL = SPR.load_memory_model()
mp = SPR.x10_model_peak([o["kind"] for o in ops], cps, model=MODEL, start_mb=START)
xs = SPR.x10_plan_start(RRP, MODEL)
mp2 = SPR.x10_model_peak([o["kind"] for o in ops], cps, model=MODEL, start_mb=xs[0]) if xs else None
print("FACT X10 at start {0}: N {1} R {2} peak {3} fail_above {4} ok {5} | prerun's own start {6} -> peak {7}".format(
      START, mp["N"], mp["R"], mp["peak_mb"], mp["fail_above_mb"], mp["ok"], xs, mp2 and mp2["peak_mb"]), flush=True)
gate("X10 peak {0} at start {1} <= fail threshold {2} (memory_model.json)".format(mp["peak_mb"], START, mp["fail_above_mb"]), mp["ok"], mp)
ok17, det17 = SPR.x17_gate([p])
gate("X17 over s03v18", ok17, det17)
rep = CPR.predict(p, {}, J(os.path.join(B, "census_samples.json")))
sf = fz.get("step_files") or []
st0, last = J(sf[0]["path"])["state"], J(sf[-1]["path"])["state"]
madeu = set(int(u) for u in (last.get("sym") or {}).values() if isinstance(u, int)) - set(int(u) for u in (st0.get("sym") or {}).values() if isinstance(u, int))
ex = J(EXPF)
EL_S2 = int(ex["total"])
ELP = ELR.predict(st0, last, EL_S2, madeu, extra_owner_states=(base,))
print("EL FIXED s03: base {0} new {1} closed {2} -> {3}; open at start {4}; uncertain {5}; detail_end {6}; created {7}".format(
      EL_S2, ELP["new_items"], ELP["closed_items"], ELP["predicted_total"], ELP["open_at_start"], ELP["uncertain_base_newly_unwired_inputs"],
      ELP["detail_end"], sorted(madeu)), flush=True)
gate("EL closed items include cond 23166 and local 6902 (s03 action 1 p4_w_stop12)",
     ["cond", 23166] in ELP["closed_items"] and ["local", 6902] in ELP["closed_items"], ELP["closed_items"])
pred = {"schema": "ring-p3b-pred/1", "card": "143-5", "note": "P4 v18 session 3 (v18 ops 59..78) as one bed session on session 2's ADOPTED file "
        "(PD333(a)); action 1 src term address corrected to the base row name 'StopAll' (PD335(b), prep_c143_5_fix.log); rebased onto its real graph "
        "eda9db40 (fs map carried); start = its MEASURED load 596.0 (PD333(c))",
        "plan": {"path": rel(RRP), "md5": md5(RRP)}, "graph": {"path": bp["path"], "md5": md5(os.path.join(ROOT, bp["path"]))}, "bed": base.get("vi"), "bed_md5": base.get("md5"),
        "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [p["actions"][k - 1]["id"] for k in rep["unpredicted"]],
        "ops": [o["kind"] for o in ops], "cdiff_rows": sorted(fz.get("end_cdiff_rows") or []), "cross_session_refs": "bound by stage_prerun --rebase (finalized.rebase)",
        "errorlist": {"bed_total": EL_S2, "new_items_predicted": len(ELP["new_items"]) - len(ELP["closed_items"]), "predicted_total": ELP["predicted_total"],
                      "alternative_total": None, "fixed": ELP, "rule": ELP["rule"] + "; base = s02 file measured 53 (" + rel(EXPF) + ")",
                      "base_file": rel(EXPF), "checked": False},
        "memory_pred": {"card": "143-5", "checkpoints": cps, "R": mp["R"], "N": mp["N"], "bind_ops": bind, "op_kinds": [o["kind"] for o in ops],
                        "start_mb": START, "start_cite": START_CITE, "peak_mb": mp["peak_mb"], "fail_above_mb": mp["fail_above_mb"], "below_fail": mp["ok"],
                        "prerun_start": xs, "prerun_peak_mb": mp2 and mp2["peak_mb"], "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)}},
        "summary": fz.get("summary")}
json.dump(pred, open(PP, "w", encoding="utf-8"), indent=1)
print("FACT ops", dict(collections.Counter(pred["ops"])), "census", pred["census"], "overall", pred["census_overall"], "unpredicted", pred["census_unpredicted"],
      "| EL", pred["errorlist"]["predicted_total"], "| end rows", len(pred["cdiff_rows"]), "open pairs", len(p.get("open_rows") or []), flush=True)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (RRP, PP))
gate("SP pred written, keyed to the plan md5", J(PP)["plan"]["md5"] == md5(RRP))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
