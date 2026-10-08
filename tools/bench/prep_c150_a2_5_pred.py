# ---
# labview: none
# hardware: none
# ---
r"""prep_c150_a2_5_pred - card 150-a2-5 step 3 (OFFLINE, no LabVIEW). Writes plan_ring_p4_s07v18_pred.json for the s07 plan made by
prep_c150_a1_1_mk.py (30 actions, v18 ops 136..165) and rebased by stage_prerun --rebase onto the REAL s06 graph graph_ring_p4s06_20261008_192149.json
(a3ecb92b; prep_c150_a2_5_rebase.log, plan 10a4f59a -> 08c2ad4d).
COPIED from prep_c147_a1_3_pred.py (7fd5654c; the rebased-plan form) with ONLY: s06 -> s07 names (plan / pred / session table
prep_c150_a1_1_session.json); base VI = the ADOPTED s06 file 569ffbf5, graph a3ecb92b; START = stage_prerun.x10_start(569ffbf5..) = 593.8 + op-0 5.9
= 599.7 (gate X1 = the prerun's own x10_plan_start(plan) == START); EL base = the adopted s06 Error List expected file
(errorlist_expected_D1_ring_p4s06_20261008_174730.json b47995c8, total 51) with tools/elrule.py a5ee7d5c UNCHANGED; per-class start read = the measured
s06 read that file was made from (errorlist_D1_ring_p4s06_20261008_174730_20261008_181243.json 899e2656, 51 items); card id strings.
Existing tools checked: prep_c147_a1_3_pred.py (copied), prep_c148_a3_3_pred.py (provisional form, not used: the plan is now rebased); tools/elrule.py
(predict, subvis_from_plan, item_class); stage_prerun.x10_start / x10_plan_start / x10_model_peak / x17_gate / negative_uids_left; census_predict.predict.
PREDICTION CONTRACT: M0 pins; RB plan FINAL, base not provisional, open_rows_match, 30 actions == session table, no negative uid; RB2 base vi
  md5 569ffbf5.., real graph a3ecb92b; V18E-R cdiff 0; C each action once; X1 prerun start == pred start == 599.7; X10 Executor peak 673.7
  <= 680 == table; X17 PASS; EL by the rule on base 51 (printed, not typed); PC start read 51 items; SP pred keyed to the plan md5.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c150_a2_5_pred.log -- py -u tools/bench/prep_c150_a2_5_pred.py"""
import collections, hashlib, json, os, re, sys                                            # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR, census_predict as CPR                        # noqa: E401,E402
import elrule as ELR                                                                        # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
RRP, PP = os.path.join(B, "plan_ring_p4_s07v18.json"), os.path.join(B, "plan_ring_p4_s07v18_pred.json")
V18 = os.path.join(B, "plan_ring_p4_v18.json")
SESS = os.path.join(B, "prep_c150_a1_1_session.json")
GRAPH, GRAPH_MD5 = os.path.join(B, "graph_ring_p4s06_20261008_192149.json"), "a3ecb92b27654c3d85b9ab5ff58aa069"
EXPF, EXPF_MD5 = os.path.join(B, "errorlist_expected_D1_ring_p4s06_20261008_174730.json"), "b47995c8b6cbad7dc6e35771b33e71be"
READF, READF_MD5 = os.path.join(B, "errorlist_D1_ring_p4s06_20261008_174730_20261008_181243.json"), "899e265612a8821ffaa8f0553e1ce5f1"
REQF = os.path.join(B, "subvi_requiredness.json")
V18SUM = os.path.join(B, "sim", "ring_p4_v18", "ring_p4_v3", "summary.json")
S06VI_MD5 = "569ffbf51eb6051bf0fdb58946f9bb02"
LOAD6 = 593.8                                                                               # memory_model load_by_vi s06 (diag_c149_a3_2_graph.log:24)
MODEL = SPR.load_memory_model()
XS0 = SPR.x10_start(S06VI_MD5, MODEL)
START, START_CITE = (XS0[0], XS0[1]) if XS0 else (None, None)
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                 # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []
SS_ = J(SESS)
S6N, LAST = SS_["ops"][0] - 1, SS_["ops"][1]
NEXT = LAST + 1
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


print("FACT plan md5 {0}; session table {1} ops {2}..{3}; earlier s07 pred e888ab67 (14-action provisional 148, replaced)".format(
      md5(RRP), md5(SESS), S6N + 1, LAST), flush=True)
gate("M0 graph a3ecb92b, EL expected file b47995c8, start read 899e2656, requiredness 13b0d75f md5 == card",
     md5(GRAPH) == GRAPH_MD5 and md5(EXPF) == EXPF_MD5 and md5(READF) == READF_MD5 and md5(REQF) == "13b0d75f6ac66511e43b3b22c898368d",
     (md5(GRAPH), md5(EXPF), md5(READF), md5(REQF)))
p = J(RRP)
NA = SS_["actions"]
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
gate("RB2 base doc vi md5 569ffbf5.. (adopted s06 file); fs_carried.real_graph md5 == a3ecb92b (the graph file) or base IS the graph; base file md5 == plan's",
     str(base.get("md5") or "") == S06VI_MD5 and (rg.get("md5") == GRAPH_MD5 or (not rg and md5(os.path.join(ROOT, bp["path"])) == GRAPH_MD5))
     and md5(os.path.join(ROOT, bp["path"])) == bp.get("md5"), (base.get("md5"), rg, bp))
V18S = J(V18SUM)
v18n = dict((s["n"], s) for s in V18S["steps"])
v18 = J(V18)
vpos = dict((a["id"], k) for k, a in enumerate(v18["actions"], 1))
n_last = vpos[SS_["last"]]
e7, e18 = set(fz.get("end_cdiff_rows") or []), set(v18n[n_last].get("cdiff_rows") or [])
print("FACT V18E-R rebased s07 end rows {0} vs v18 sim after #{1} ({2}) rows {3}; only s07 {4}; only v18 {5}; v18 summary md5 {6}".format(
      len(e7), n_last, SS_["last"], len(e18), sorted(e7 - e18), sorted(e18 - e7), md5(V18SUM)), flush=True)
gate("V18E-R rebased s07 end cdiff rows == v18 sim rows after the same last action #{0} (cdiff {1})".format(n_last, len(e7 ^ e18)), e7 == e18,
     {"only_s07": sorted(e7 - e18), "only_v18": sorted(e18 - e7)})
ops = SX.compile_plan(p)
gate("C compile: {0} actions -> {1} ops, each action once".format(len(p["actions"]), len(ops)),
     sorted(n for o in ops for n in o["acts"]) == list(range(1, len(p["actions"]) + 1)))
bind = sorted(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS)
cps = sorted(set([0, len(ops)]) | set(bind))
xs = SPR.x10_plan_start(RRP, MODEL)
gate("X1 ONE start: prerun's own x10_plan_start(plan) {0} == pred start x10_start(569ffbf5) {1} == {2} + op-0 {3}".format(
     xs and xs[0], START, LOAD6, MODEL["op0_read_mb"]["value"]), xs is not None and START is not None and xs[0] == START
     and abs(START - round(LOAD6 + float(MODEL["op0_read_mb"]["value"]), 1)) < 0.05, (xs, XS0))
mp = SPR.x10_model_peak([o["kind"] for o in ops], cps, model=MODEL, start_mb=START)
mp2 = SPR.x10_model_peak([o["kind"] for o in ops], cps, model=MODEL, start_mb=xs[0])
print("FACT X10 at start {0}: N {1} R {2} peak {3} fail_above {4} ok {5} margin {6}; MEMSTOP {7} margin {8} | prerun's own start {9} -> peak {10}".format(
      START, mp["N"], mp["R"], mp["peak_mb"], mp["fail_above_mb"], mp["ok"], round(mp["fail_above_mb"] - mp["peak_mb"], 1), SX.MEM_STOP_MB,
      round(SX.MEM_STOP_MB - mp["peak_mb"], 1), xs[0], mp2["peak_mb"]), flush=True)
VOPS = SX.compile_plan(v18)
VB = set(k for k, o in enumerate(VOPS, 1) if o["kind"] in SX.BIND_KINDS)
v = lambda k: float(MODEL[k]["value"])                                                      # noqa: E731
pk = lambda a, b: round(START + len({a, b} | set(k for k in VB if a < k <= b)) * v("read_mb") + (b - a) * (v("edit_mb") + v("other_mb")) + v("final_read_mb"), 1)   # noqa: E731
first_over = next((b for b in range(S6N + 1, len(VOPS) + 1) if pk(S6N, b) > SPR.X10_FAIL_MB), None)
print("FACT X10 per-op formula (Executor) at {0}: ops {1}..{2} peak {3}; next op {4} peak {5}; first op over {6} = {7}".format(
      START, S6N + 1, LAST, pk(S6N, LAST), NEXT, pk(S6N, NEXT), SPR.X10_FAIL_MB, first_over), flush=True)
gate("X10 Executor peak {0} at start {1} <= fail threshold {2} (memory_model.json); == per-op table {3}".format(mp["peak_mb"], START, mp["fail_above_mb"], pk(S6N, LAST)),
     mp["ok"] and mp2["ok"] and abs(mp["peak_mb"] - pk(S6N, LAST)) < 0.05, mp)
ok17, det17 = SPR.x17_gate([p])
gate("X17 over s07v18", ok17, det17)
rep = CPR.predict(p, {}, J(os.path.join(B, "census_samples.json")))
sf = fz.get("step_files") or []
st0, last = J(sf[0]["path"])["state"], J(sf[-1]["path"])["state"]
madeu = set(int(u) for u in (last.get("sym") or {}).values() if isinstance(u, int)) - set(int(u) for u in (st0.get("sym") or {}).values() if isinstance(u, int))
ex = J(EXPF)
EL_S6 = int(ex["total"])
SUBV = ELR.subvis_from_plan(p, st0, last)
ELP = ELR.predict(st0, last, EL_S6, madeu, extra_owner_states=(base,), subvis=SUBV)
byc = collections.Counter(k[0] for k in ELP["new_items"]), collections.Counter(k[0] for k in ELP["closed_items"])
print("EL FIXED s07: base {0} (MEASURED adopted s06 file) new {1} closed {2} -> {3}; per class new {4} closed {5}; "
      "open at start {6}; open at end {7}; uncertain base {8}; uncertain subvi {9}; subvis {10}; detail_end {11}; created {12}; steps {13} -> {14}".format(
          EL_S6, ELP["new_items"], ELP["closed_items"], ELP["predicted_total"], dict(byc[0]), dict(byc[1]), ELP["open_at_start"], ELP["open_at_end"],
          ELP["uncertain_base_newly_unwired_inputs"], ELP["uncertain_subvi_terminals"], SUBV, ELP["detail_end"], sorted(madeu), sf[0]["path"], sf[-1]["path"]), flush=True)
print("FACT EL rule: {0}".format(ELP.get("rule")), flush=True)
RI = J(READF).get("items") or []
C0 = collections.Counter(elcls(x) for x in RI)
PC = dict((c, C0.get(c, 0) + byc[0].get(c, 0) - byc[1].get(c, 0)) for c in sorted(set(C0) | set(byc[0]) | set(byc[1])))
print("EL PER-CLASS start read {0} ({1} items): {2}".format(rel(READF), len(RI), dict(sorted(C0.items()))), flush=True)
print("EL PER-CLASS predicted end (start + new - closed): {0}; total {1}".format(PC, sum(PC.values())), flush=True)
gate("PC start read {0} items == expected total {1}; per-class predicted total {2} == rule predicted_total {3}".format(len(RI), EL_S6, sum(PC.values()), ELP["predicted_total"]),
     len(RI) == EL_S6 and sum(PC.values()) == ELP["predicted_total"], PC)
pred = {"schema": "ring-p3b-pred/1", "card": "150-a2-5", "note": "P4 v18 session 7 (v18 ops {0}..{1}) as one bed session on session 6's ADOPTED file "
        "D1_ring_p4s06_20261008_174730.vi (569ffbf5, card 149-a3-1); made on s06 plan cfbd9823's simulated end (prep_c150_a1_1_mk.py) and rebased onto "
        "its real graph a3ecb92b (prep_c150_a2_5_rebase.log); start = the ONE X10 start stage_prerun.x10_start = measured fresh load 593.8 + op-0 read 5.9 "
        "(PD352(b)); Error List by the fixed rule (tools/elrule.py a5ee7d5c, unchanged, PD354(b)) on the adopted s06 Error List (51); the EL is a RECORDED "
        "cross-check (PD354(a)), per_class feeds the scratch recipe's advisory step".format(S6N + 1, LAST),
        "plan": {"path": rel(RRP), "md5": md5(RRP)}, "graph": {"path": bp["path"], "md5": md5(os.path.join(ROOT, bp["path"]))}, "bed": base.get("vi"), "bed_md5": base.get("md5"),
        "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [p["actions"][k - 1]["id"] for k in rep["unpredicted"]],
        "ops": [o["kind"] for o in ops], "cdiff_rows": sorted(fz.get("end_cdiff_rows") or []), "cross_session_refs": "bound by stage_prerun --rebase (finalized.rebase)",
        "errorlist": {"bed_total": EL_S6, "new_items_predicted": len(ELP["new_items"]) - len(ELP["closed_items"]), "predicted_total": ELP["predicted_total"],
                      "alternative_total": None, "fixed": ELP, "rule": ELP["rule"] + "; base = adopted s06 file measured " + str(EL_S6) + " (" + rel(EXPF) + ")",
                      "rule_source": {"module": "tools/elrule.py", "module_md5": md5(os.path.join(ROOT, "tools", "elrule.py")), "requiredness": rel(REQF),
                                      "requiredness_md5": md5(REQF), "pd": "PD349+PD351(c); PD354(a)(b)"},
                      "previous": None, "base_file": rel(EXPF), "checked": False,
                      "per_class": {"start_read": {"path": rel(READF), "md5": READF_MD5, "items": len(RI), "classes": dict(sorted(C0.items()))},
                                    "rule_new": dict(byc[0]), "rule_closed": dict(byc[1]), "predicted": PC,
                                    "classifier": "elcls: elrule.item_class(raw + detail) -> local/cond/sr; norm_ocr(raw) containing 'unwiredorbadterminal' or "
                                                  "'requiredinput'+'notwired' -> input; else 'other:' + norm_ocr(raw) (prep_c147_a1_3_pred.py)",
                                    "advisory": "PD354(a): non-zero only for a class in neither start_read.classes nor predicted, or |total diff| > 3"}},
        "memory_pred": {"card": "150-a2-5", "checkpoints": cps, "R": mp["R"], "N": mp["N"], "bind_ops": bind, "op_kinds": [o["kind"] for o in ops],
                        "start_mb": START, "start_cite": START_CITE, "start_rule": "stage_prerun.x10_start (PD352(b))", "peak_mb": mp["peak_mb"],
                        "fail_above_mb": mp["fail_above_mb"], "below_fail": mp["ok"], "memstop_mb": SX.MEM_STOP_MB, "next_op": NEXT, "next_op_peak_mb": pk(S6N, NEXT),
                        "prerun_start": xs, "prerun_peak_mb": mp2["peak_mb"], "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)}},
        "summary": fz.get("summary")}
json.dump(pred, open(PP, "w", encoding="utf-8"), indent=1)
print("FACT ops", dict(collections.Counter(pred["ops"])), "census", pred["census"], "overall", pred["census_overall"], "unpredicted", len(pred["census_unpredicted"]),
      "| EL", pred["errorlist"]["predicted_total"], "| end rows", len(pred["cdiff_rows"]), "open pairs", len(p.get("open_rows") or []), flush=True)
for x in ("tools/bench/plan_ring_p4_s07v18.json", "tools/bench/plan_ring_p4_s07v18_pred.json", "tools/bench/plan_ring_p4_s07v18_in.json",
          "tools/elrule.py", "tools/bench/memory_model.json", bp["path"]):
    print("FACT md5 {0} {1}".format(md5(os.path.join(ROOT, x)), x), flush=True)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (RRP, PP))
gate("SP pred written, keyed to the plan md5", J(PP)["plan"]["md5"] == md5(RRP))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
sys.exit(1 if G["fail"] else 0)
