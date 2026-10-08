# ---
# labview: none
# hardware: none
# ---
r"""prep_c148_a3_3_pred - card 148-a3-3 step 3 (OFFLINE, no LabVIEW). Writes plan_ring_p4_s07v18_pred.json for the PROVISIONAL s07 plan made by
prep_c148_a3_3_mk.py on session 6's SIMULATED end (sim/ring_p4_s07v18/s06end/base_provisional.json; s06 plan cfbd9823).
COPIED from prep_c147_a1_3_pred.py (7fd5654c; itself a copy of prep_c146_a1_2_pred.py 19270d62) with: s06 -> s07 names (plan / pred / session
table prep_c148_a3_3_session.json); the plan is PROVISIONAL, so (a) gate RB checks base provisional + sim_of == s06 cfbd9823 instead of 'rebased',
RB2 checks the base doc is the s06 sim end (vi md5 3f9ac26b inherited, sym of s06); (b) X1 = the prerun has NO start for it (x10_plan_start None,
stage_prerun.py:2079-2080) and the pred start = the session table's PROVISIONAL start (606.7 + 0.719 x 21 + 5.9 = 627.7, prep_c148_a3_3_mk.py);
(c) EL base = the s06 PREDICTED Error List (plan_ring_p4_s06v18_pred.json c4a6a35a: predicted_total 55, per_class.predicted) - no s06 file, no
measured read exists yet; elrule a5ee7d5c UNCHANGED; per-class start = that predicted per-class table (marked 'predicted', not a read).
Existing tools checked: prep_c147_a1_3_pred.py (copied); tools/elrule.py (predict, subvis_from_plan, item_class); stage_prerun.x10_plan_start /
x10_model_peak / x17_gate / negative_uids_left; census_predict.predict.
PREDICTION CONTRACT: M0 pins; RB plan FINAL, base provisional (sim_of s06 cfbd9823), open_rows_match, 14 actions == session table; RB2 base vi md5
  3f9ac26b.. (inherited), base sym == s06 END sym; V18E-R cdiff 0; C each action once; X1 prerun start None, pred start 627.7; X10 Executor peak
  674.5 <= 680 == table; X17 PASS; EL by the rule on base 55 (printed, not typed); PC start classes sum 55; SP pred keyed to the plan md5.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c148_a3_3_pred.log -- py -u tools/bench/prep_c148_a3_3_pred.py"""
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
S06 = os.path.join(B, "plan_ring_p4_s06v18.json")
SESS = os.path.join(B, "prep_c148_a3_3_session.json")
P6F, P6F_MD5 = os.path.join(B, "plan_ring_p4_s06v18_pred.json"), "c4a6a35aff6f71d508ea2c43c24ec510"
END6F, END6F_MD5 = os.path.join(B, "sim", "ring_p4_s06v18", "step_25_wire.json"), "abe1dd1113d181cbaa0dd723979a4f2e"
REQF = os.path.join(B, "subvi_requiredness.json")
V18SUM = os.path.join(B, "sim", "ring_p4_v18", "ring_p4_v3", "summary.json")
S05VI_MD5 = "3f9ac26b69179eb53c202d90407ce7ee"
MODEL = SPR.load_memory_model()
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                 # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []
SS_ = J(SESS)
S6N, LAST = SS_["ops"][0] - 1, SS_["ops"][1]
NEXT = LAST + 1
START, START_CITE = SS_["start_mb"], SS_["start_cite"]
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


print("FACT plan md5 {0}; session table {1} ops {2}..{3}; no earlier s07 pred (first pred of this plan)".format(md5(RRP), md5(SESS), S6N + 1, LAST), flush=True)
gate("M0 s06 pred c4a6a35a, s06 end step abe1dd11, requiredness 13b0d75f, s06 plan cfbd9823 md5 == card",
     md5(P6F) == P6F_MD5 and md5(END6F) == END6F_MD5 and md5(REQF) == "13b0d75f6ac66511e43b3b22c898368d" and md5(S06) == "cfbd9823d3b47be39de94f2125ad6b66",
     (md5(P6F), md5(END6F), md5(REQF), md5(S06)))
p = J(RRP)
NA = SS_["actions"]
fz = p.get("finalized") or {}
pb = p.get("base") or {}
bp = (fz.get("base") or pb or {})
neg = SPR.negative_uids_left(p)
gate("RB plan PROVISIONAL: base {0} provisional, sim_of == s06 plan cfbd9823, FINAL, open_rows_match, {1} actions == session table {2}".format(
     pb.get("path"), len(p["actions"]), NA),
     pb.get("provisional") is True and (pb.get("sim_of") or {}).get("md5") == md5(S06) and p.get("final") is True and fz.get("open_rows_match") is True
     and len(p["actions"]) == NA, {"base": pb, "neg_left": neg[:6]})
print("FACT negative uids left in the plan (bound at --rebase): {0}".format(neg), flush=True)
base = J(bp["path"])
e6 = J(END6F)["state"]
print("FACT base doc vi {0} md5 {1}; base file {2} md5 {3}; sym {4}".format(base.get("vi"), base.get("md5"), bp.get("path"), bp.get("md5"), base.get("sym")), flush=True)
gate("RB2 base doc = s06 sim end: vi md5 3f9ac26b.. (inherited from the s06 input), sym == END6 sym, base file md5 == plan's",
     str(base.get("md5") or "") == S05VI_MD5 and base.get("sym") == e6.get("sym") and md5(os.path.join(ROOT, bp["path"])) == bp.get("md5"),
     (base.get("md5"), base.get("sym"), bp))
V18S = J(V18SUM)
v18n = dict((s["n"], s) for s in V18S["steps"])
v18 = J(V18)
vpos = dict((a["id"], k) for k, a in enumerate(v18["actions"], 1))
n_last = vpos[SS_["last"]]
e7, e18 = set(fz.get("end_cdiff_rows") or []), set(v18n[n_last].get("cdiff_rows") or [])
print("FACT V18E-R s07 end rows {0} vs v18 sim after #{1} ({2}) rows {3}; only s07 {4}; only v18 {5}; v18 summary md5 {6}".format(
      len(e7), n_last, SS_["last"], len(e18), sorted(e7 - e18), sorted(e18 - e7), md5(V18SUM)), flush=True)
gate("V18E-R s07 end cdiff rows == v18 sim rows after the same last action #{0} (cdiff {1})".format(n_last, len(e7 ^ e18)), e7 == e18,
     {"only_s07": sorted(e7 - e18), "only_v18": sorted(e18 - e7)})
ops = SX.compile_plan(p)
gate("C compile: {0} actions -> {1} ops, each action once".format(len(p["actions"]), len(ops)),
     sorted(n for o in ops for n in o["acts"]) == list(range(1, len(p["actions"]) + 1)))
bind = sorted(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS)
cps = sorted(set([0, len(ops)]) | set(bind))
xs = SPR.x10_plan_start(RRP, MODEL)
gate("X1 PROVISIONAL: prerun's own x10_plan_start(plan) is None for a provisional base (stage_prerun.py:2079-2080): {0}; pred start = session table "
     "start {1} = 606.7 + {2} x 21 + op-0 {3}".format(xs, START, MODEL["load_growth_mb_per_op"]["value"], MODEL["op0_read_mb"]["value"]),
     xs is None and START is not None and abs(START - round(606.7 + float(MODEL["load_growth_mb_per_op"]["value"]) * 21 + float(MODEL["op0_read_mb"]["value"]), 1)) < 0.05,
     (xs, START))
mp = SPR.x10_model_peak([o["kind"] for o in ops], cps, model=MODEL, start_mb=START)
print("FACT X10 at start {0}: N {1} R {2} peak {3} fail_above {4} ok {5} margin {6}; MEMSTOP {7} margin {8}".format(
      START, mp["N"], mp["R"], mp["peak_mb"], mp["fail_above_mb"], mp["ok"], round(mp["fail_above_mb"] - mp["peak_mb"], 1), SX.MEM_STOP_MB,
      round(SX.MEM_STOP_MB - mp["peak_mb"], 1)), flush=True)
VOPS = SX.compile_plan(v18)
VB = set(k for k, o in enumerate(VOPS, 1) if o["kind"] in SX.BIND_KINDS)
v = lambda k: float(MODEL[k]["value"])                                                      # noqa: E731
pk = lambda a, b: round(START + len({a, b} | set(k for k in VB if a < k <= b)) * v("read_mb") + (b - a) * (v("edit_mb") + v("other_mb")) + v("final_read_mb"), 1)   # noqa: E731
first_over = next((b for b in range(S6N + 1, len(VOPS) + 1) if pk(S6N, b) > SPR.X10_FAIL_MB), None)
print("FACT X10 per-op formula (Executor) at {0}: ops {1}..{2} peak {3}; next op {4} peak {5}; first op over {6} = {7}".format(
      START, S6N + 1, LAST, pk(S6N, LAST), NEXT, pk(S6N, NEXT), SPR.X10_FAIL_MB, first_over), flush=True)
gate("X10 Executor peak {0} at start {1} <= fail threshold {2} (memory_model.json); == per-op table {3}".format(mp["peak_mb"], START, mp["fail_above_mb"], pk(S6N, LAST)),
     mp["ok"] and abs(mp["peak_mb"] - pk(S6N, LAST)) < 0.05, mp)
ok17, det17 = SPR.x17_gate([p])
gate("X17 over s07v18", ok17, det17)
rep = CPR.predict(p, {}, J(os.path.join(B, "census_samples.json")))
sf = fz.get("step_files") or []
st0, last = J(sf[0]["path"])["state"], J(sf[-1]["path"])["state"]
madeu = set(int(u) for u in (last.get("sym") or {}).values() if isinstance(u, int)) - set(int(u) for u in (st0.get("sym") or {}).values() if isinstance(u, int))
P6 = J(P6F)
EL_S6 = int(P6["errorlist"]["predicted_total"])
SUBV = ELR.subvis_from_plan(p, st0, last)
ELP = ELR.predict(st0, last, EL_S6, madeu, extra_owner_states=(base,), subvis=SUBV)
byc = collections.Counter(k[0] for k in ELP["new_items"]), collections.Counter(k[0] for k in ELP["closed_items"])
print("EL FIXED s07: base {0} (PREDICTED s06 total, plan_ring_p4_s06v18_pred.json) new {1} closed {2} -> {3}; per class new {4} closed {5}; "
      "open at start {6}; open at end {7}; uncertain base {8}; uncertain subvi {9}; subvis {10}; detail_end {11}; created {12}; steps {13} -> {14}".format(
          EL_S6, ELP["new_items"], ELP["closed_items"], ELP["predicted_total"], dict(byc[0]), dict(byc[1]), ELP["open_at_start"], ELP["open_at_end"],
          ELP["uncertain_base_newly_unwired_inputs"], ELP["uncertain_subvi_terminals"], SUBV, ELP["detail_end"], sorted(madeu), sf[0]["path"], sf[-1]["path"]), flush=True)
print("FACT EL rule: {0}".format(ELP.get("rule")), flush=True)
C0 = dict(P6["errorlist"]["per_class"]["predicted"])
PC = dict((c, C0.get(c, 0) + byc[0].get(c, 0) - byc[1].get(c, 0)) for c in sorted(set(C0) | set(byc[0]) | set(byc[1])))
print("EL PER-CLASS start = s06 PREDICTED per class ({0} items): {1}".format(sum(C0.values()), dict(sorted(C0.items()))), flush=True)
print("EL PER-CLASS predicted end (start + new - closed): {0}; total {1}".format(PC, sum(PC.values())), flush=True)
gate("PC start classes (s06 predicted) sum {0} == s06 predicted total {1}; per-class predicted total {2} == rule predicted_total {3}".format(
     sum(C0.values()), EL_S6, sum(PC.values()), ELP["predicted_total"]),
     sum(C0.values()) == EL_S6 and sum(PC.values()) == ELP["predicted_total"], PC)
pred = {"schema": "ring-p3b-pred/1", "card": "148-a3-3", "note": "P4 v18 session 7 (v18 ops {0}..{1}) PROVISIONAL: made on s06 plan cfbd9823's simulated end "
        "(prep_c148_a3_3_mk.py), to be rebased onto the adopted s06 file's real graph; start = PROVISIONAL predicted s06 load + op-0 read "
        "(606.7 + 0.719 x 21 + 5.9; the prerun has no start for a provisional base); Error List by the fixed rule (tools/elrule.py a5ee7d5c, unchanged) "
        "on the s06 PREDICTED Error List (55, plan_ring_p4_s06v18_pred.json c4a6a35a); per_class start = s06 predicted per-class; redo both after the "
        "s06 file is adopted and read".format(S6N + 1, LAST),
        "provisional": True,
        "plan": {"path": rel(RRP), "md5": md5(RRP)}, "graph": {"path": bp["path"], "md5": md5(os.path.join(ROOT, bp["path"]))}, "bed": base.get("vi"), "bed_md5": base.get("md5"),
        "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [p["actions"][k - 1]["id"] for k in rep["unpredicted"]],
        "ops": [o["kind"] for o in ops], "cdiff_rows": sorted(fz.get("end_cdiff_rows") or []), "cross_session_refs": "s01..s05 real (creation maps), s06 negative (provisional base); bound at --rebase",
        "errorlist": {"bed_total": EL_S6, "new_items_predicted": len(ELP["new_items"]) - len(ELP["closed_items"]), "predicted_total": ELP["predicted_total"],
                      "alternative_total": None, "fixed": ELP, "rule": ELP["rule"] + "; base = s06 PREDICTED total " + str(EL_S6) + " (" + rel(P6F) + ")",
                      "rule_source": {"module": "tools/elrule.py", "module_md5": md5(os.path.join(ROOT, "tools", "elrule.py")), "requiredness": rel(REQF),
                                      "requiredness_md5": md5(REQF), "pd": "PD349+PD351(c); PD354(a)(b); PD358(f)"},
                      "previous": None, "base_file": rel(P6F), "checked": False,
                      "per_class": {"start_read": {"path": rel(P6F), "md5": P6F_MD5, "items": sum(C0.values()), "classes": dict(sorted(C0.items())),
                                                   "kind": "PREDICTED s06 per-class (errorlist.per_class.predicted), not a measured read"},
                                    "rule_new": dict(byc[0]), "rule_closed": dict(byc[1]), "predicted": PC,
                                    "classifier": "elcls: elrule.item_class(raw + detail) -> local/cond/sr; norm_ocr(raw) containing 'unwiredorbadterminal' or "
                                                  "'requiredinput'+'notwired' -> input; else 'other:' + norm_ocr(raw) (prep_c147_a1_3_pred.py)",
                                    "advisory": "PD354(a): non-zero only for a class in neither start_read.classes nor predicted, or |total diff| > 3"}},
        "memory_pred": {"card": "148-a3-3", "checkpoints": cps, "R": mp["R"], "N": mp["N"], "bind_ops": bind, "op_kinds": [o["kind"] for o in ops],
                        "start_mb": START, "start_cite": START_CITE, "start_rule": "PROVISIONAL predicted s06 load + op0 (prep_c147_a1_2_mk.py rule)", "peak_mb": mp["peak_mb"],
                        "fail_above_mb": mp["fail_above_mb"], "below_fail": mp["ok"], "memstop_mb": SX.MEM_STOP_MB, "next_op": NEXT, "next_op_peak_mb": pk(S6N, NEXT),
                        "prerun_start": xs, "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)}},
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
