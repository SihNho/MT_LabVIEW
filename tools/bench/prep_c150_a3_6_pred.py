# ---
# labview: none
# hardware: none
# ---
r"""prep_c150_a3_6_pred - card 150-a3-6 step 4 (OFFLINE). COPY of prep_c150_a3_1_pred.py (2644bdd4) with ONLY s07 -> s08 names: plan / pred
plan_ring_p4_s08v18*.json, session table prep_c150_a3_6_session.json (ops 166..184, 19 actions), real graph = s07's 71935a84, base VI = adopted s07
b3f86b32 (START = x10_start = 589.4 + op-0 5.9 = 595.3), EL base = the adopted s07 Error List expected file 42c5718d (total 50) and its read aa27c138;
V18E-R' (2) reads RENAMED-OLD from BOTH rebase outputs: this card's s08 rebase prep_c150_a3_6_rebase.log (0c298253) and the s07 rebase
prep_c150_a2_5_rebase.log (28341ad1) whose renames END7 / the real s07 graph already carry (prep_c150_a3_6_mk.py docstring (4)); each owner is printed
with the log it came from, and an extra condition (2b) requires every only-v18 row to be an only-v18 row ALREADY at s08 step 0 (inherited, not made
by s08); (3) compares against the real s07 graph. --- original docstring follows ---
prep_c150_a3_1_pred - card 150-a3-1 step 1 (OFFLINE, no LabVIEW). COPY of prep_c150_a2_5_pred.py (85196a77) with ONLY: the V18E-R key-set
compare (its lines 103-107) REPLACED by V18E-R' (docs/d1/ring-p4c.md PD366(c): (1) only-s07 empty; (2) every only-v18 row has before: null in v18's
cdiff_detail at the compared step and its node owns a RENAMED-OLD entry READ from prep_c150_a2_5_rebase.log (28341ad1); (3) per such node the
multiset of sink-terminal names in the real s06 graph a3ecb92b == S1's (stagesim.load_s1); both graphs built by vigraph.build4 the same way);
card id strings 150-a3-1. Everything else unchanged. --- original docstring follows ---
prep_c150_a2_5_pred - card 150-a2-5 step 3 (OFFLINE, no LabVIEW). Writes plan_ring_p4_s07v18_pred.json for the s07 plan made by
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
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c150_a3_6_pred.log -- py -u tools/bench/prep_c150_a3_6_pred.py"""
import collections, hashlib, json, os, re, sys                                            # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR, census_predict as CPR                        # noqa: E401,E402
import elrule as ELR                                                                        # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
RRP, PP = os.path.join(B, "plan_ring_p4_s08v18.json"), os.path.join(B, "plan_ring_p4_s08v18_pred.json")
V18 = os.path.join(B, "plan_ring_p4_v18.json")
SESS = os.path.join(B, "prep_c150_a3_6_session.json")
GRAPH, GRAPH_MD5 = os.path.join(B, "graph_ring_p4s07_20261008_224835.json"), "71935a845efedd8123044aab288cd81c"
EXPF, EXPF_MD5 = os.path.join(B, "errorlist_expected_D1_ring_p4s07_20261008_222709.json"), "42c5718df5f697196419185cc215f4df"
READF, READF_MD5 = os.path.join(B, "errorlist_D1_ring_p4s07_20261008_222709_20261008_223629.json"), "aa27c13844a0bca2be87ead2bff713b3"
REQF = os.path.join(B, "subvi_requiredness.json")
V18SUM = os.path.join(B, "sim", "ring_p4_v18", "ring_p4_v3", "summary.json")
S06VI_MD5 = "b3f86b322292a6ec6c67976a589b5b06"                                            # card 150-a3-6: the ADOPTED s07 file (name kept from the copy)
LOAD6 = 589.4                                                                               # memory_model load_by_vi s07 (diag_c150_a3_2_graph.log:24)
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


print("FACT plan md5 {0}; session table {1} ops {2}..{3}; no earlier s08 pred".format(
      md5(RRP), md5(SESS), S6N + 1, LAST), flush=True)
gate("M0 graph 71935a84, EL expected file 42c5718d, start read aa27c138, requiredness 13b0d75f md5 == card",
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
gate("RB2 base doc vi md5 b3f86b32.. (adopted s07 file); fs_carried.real_graph md5 == 71935a84 (the graph file) or base IS the graph; base file md5 == plan's",
     str(base.get("md5") or "") == S06VI_MD5 and (rg.get("md5") == GRAPH_MD5 or (not rg and md5(os.path.join(ROOT, bp["path"])) == GRAPH_MD5))
     and md5(os.path.join(ROOT, bp["path"])) == bp.get("md5"), (base.get("md5"), rg, bp))
V18S = J(V18SUM)
v18n = dict((s["n"], s) for s in V18S["steps"])
v18 = J(V18)
vpos = dict((a["id"], k) for k, a in enumerate(v18["actions"], 1))
n_last = vpos[SS_["last"]]
e7, e18 = set(fz.get("end_cdiff_rows") or []), set(v18n[n_last].get("cdiff_rows") or [])
print("FACT V18E-R rebased s08 end rows {0} vs v18 sim after #{1} ({2}) rows {3}; only s07 {4}; only v18 {5}; v18 summary md5 {6}".format(
      len(e7), n_last, SS_["last"], len(e18), sorted(e7 - e18), sorted(e18 - e7), md5(V18SUM)), flush=True)
# ---- card 150-a3-1 (PD366(c)): V18E-R' replaces the key-set compare. Nothing typed: renamed-old from the rebase log, S1 by stagesim.load_s1.
import ast, stagesim as SSIM, vigraph as VG                                                 # noqa: E401,E402
RBLOGS = [(os.path.join(B, "prep_c150_a3_6_rebase.log"), "0c29825361e7", "s08 rebase (this card)"),
          (os.path.join(B, "prep_c150_a2_5_rebase.log"), "28341ad147b6", "s07 rebase (inherited by END7 / the real s07 graph)")]
only7, only18 = sorted(e7 - e18), sorted(e18 - e7)
DET = dict((str(y["sink"]), y) for y in (v18n[n_last].get("cdiff_detail") or []))
REN_OLD, REN_SRC = [], collections.defaultdict(set)
for RBLOG, RBLOG_MD5, RBWHY in RBLOGS:
    gate("V18E-R' M rebase log {0} md5 == pin {1}".format(rel(RBLOG), RBLOG_MD5), md5(RBLOG).startswith(RBLOG_MD5), md5(RBLOG))
    got = []
    for ln in open(RBLOG, encoding="utf-8", errors="replace").read().splitlines():
        mm = re.match(r"^RENAMED-OLD (-?\d+) #(-?\d+) ('(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")->('(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")\s*$", ln)
        if mm:
            got.append((int(mm.group(1)), int(mm.group(2)), ast.literal_eval(mm.group(3)), ast.literal_eval(mm.group(4))))
    for _u, o, _a, _b in got:
        REN_SRC[o].add(os.path.basename(RBLOG))
    REN_OLD += got
    print("FACT V18E-R' rebase log {0} ({1}) md5 {2}: RENAMED-OLD {3} -> owners {4}".format(rel(RBLOG), RBWHY, md5(RBLOG), got,
          sorted(set(o for _u, o, _a, _b in got))), flush=True)
REN_OWN = set(o for _u, o, _a, _b in REN_OLD)
gate("V18E-R' M RENAMED-OLD lines read over both rebase outputs (>0); owners by log {0}".format(dict((k, sorted(v)) for k, v in REN_SRC.items())), bool(REN_OLD), REN_OLD)
SUMF = os.path.join(B, "sim", "ring_p4_s08v18", "summary.json")                         # the rebased s08 simulation (stage_prerun --rebase)
S0R = set(J(SUMF)["steps"][0].get("cdiff_rows") or [])
v18_177 = set(v18n[vpos[J(os.path.join(B, "prep_c150_a3_6_session.json"))["first"]] - 1].get("cdiff_rows") or [])
inh18 = sorted(v18_177 - S0R)
ok2b = set(only18) <= set(inh18)
print("V18E-R' (2b) s08 step-0 rows {0} ({1} md5 {2}) vs v18 after #{3}: only-v18 at step 0 {4}; every end only-v18 row inherited: {5}".format(
      len(S0R), rel(SUMF), md5(SUMF), vpos[J(os.path.join(B, "prep_c150_a3_6_session.json"))["first"]] - 1, inh18, "PASS" if ok2b else "FAIL"), flush=True)
c2 = [(k, (DET.get(k) or {}).get("node"), "before" in (DET.get(k) or {}) and DET[k]["before"] is None,
       (DET.get(k) or {}).get("node") is not None and int(DET[k]["node"]) in REN_OWN, (DET.get(k) or {}).get("before"), (DET.get(k) or {}).get("after"))
      for k in only18]
ok1, ok2 = not only7, all(x[2] and x[3] for x in c2) and ok2b
print("V18E-R' (1) only-s08 rows {0}: {1}".format(only7, "PASS" if ok1 else "FAIL"), flush=True)
for x in c2:
    print("V18E-R' (2) only-v18 row {0}: node {1}; v18 cdiff_detail before null {2} (before {4}, after {5}); node owns RENAMED-OLD {3}".format(*x), flush=True)
print("V18E-R' (2) {0} only-v18 row(s): {1}".format(len(c2), "PASS" if ok2 else "FAIL"), flush=True)
GR = J(GRAPH)
GRB = VG.build4(GR["terminals"], GR.get("objs"), GR.get("loops"), {}, GR.get("fs_tunnel_pairs"))
S1B = SSIM.load_s1(p)
sinkms = lambda Gx, n: collections.Counter(str(r.get("term_name") or "") for r in (Gx.get("by_node") or {}).get(n, []) if not r.get("is_source"))   # noqa: E731
c3 = []
for n in sorted(set(int(x[1]) for x in c2 if x[1] is not None)):
    a3, b3 = sinkms(GRB, n), sinkms(S1B, n)
    c3.append((n, dict(sorted(a3.items())), dict(sorted(b3.items())), a3 == b3 and bool(a3)))
    print("V18E-R' (3) node #{0}: sink-name multiset real s07 graph {1} vs S1 ({2}) {3}: {4}".format(
          n, dict(sorted(a3.items())), (p.get("context") or {}).get("s1_key"), dict(sorted(b3.items())), "PASS" if c3[-1][3] else "FAIL"), flush=True)
ok3 = bool(c3) and all(x[3] for x in c3) if only18 else True
print("V18E-R' excluded keys (only-v18, name artefacts of v18's bed): {0}".format(only18 if (ok1 and ok2 and ok3) else []), flush=True)
gate("V18E-R' rebased s08 end vs v18 sim after #{0}: (1) only-s08 empty {1}; (2) {2} only-v18 row(s) before:null + RENAMED-OLD owner + inherited at step 0 {3}; (3) sink-name "
     "multiset real s07 == S1 on node(s) {4}: {5}".format(n_last, ok1, len(c2), ok2, [x[0] for x in c3], ok3), ok1 and ok2 and ok3,
     {"only_s08": only7, "only_v18": [list(x) for x in c2], "inherited_step0": inh18, "nodes": [list(x) for x in c3]})
ops = SX.compile_plan(p)
gate("C compile: {0} actions -> {1} ops, each action once".format(len(p["actions"]), len(ops)),
     sorted(n for o in ops for n in o["acts"]) == list(range(1, len(p["actions"]) + 1)))
bind = sorted(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS)
cps = sorted(set([0, len(ops)]) | set(bind))
xs = SPR.x10_plan_start(RRP, MODEL)
gate("X1 ONE start: prerun's own x10_plan_start(plan) {0} == pred start x10_start(b3f86b32) {1} == {2} + op-0 {3}".format(
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
gate("X17 over s08v18", ok17, det17)
rep = CPR.predict(p, {}, J(os.path.join(B, "census_samples.json")))
sf = fz.get("step_files") or []
st0, last = J(sf[0]["path"])["state"], J(sf[-1]["path"])["state"]
madeu = set(int(u) for u in (last.get("sym") or {}).values() if isinstance(u, int)) - set(int(u) for u in (st0.get("sym") or {}).values() if isinstance(u, int))
ex = J(EXPF)
EL_S6 = int(ex["total"])
SUBV = ELR.subvis_from_plan(p, st0, last)
ELP = ELR.predict(st0, last, EL_S6, madeu, extra_owner_states=(base,), subvis=SUBV)
byc = collections.Counter(k[0] for k in ELP["new_items"]), collections.Counter(k[0] for k in ELP["closed_items"])
print("EL FIXED s08: base {0} (MEASURED adopted s07 file) new {1} closed {2} -> {3}; per class new {4} closed {5}; "
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
pred = {"schema": "ring-p3b-pred/1", "card": "150-a3-6", "note": "P4 v18 session 8 (v18 ops {0}..{1}, capped before p4_x_n2_order) as one bed session on session 7's ADOPTED file "
        "D1_ring_p4s07_20261008_222709.vi (b3f86b32, card 150-a3-2); made on s07 plan 08c2ad4d's simulated end (prep_c150_a3_6_mk.py) and rebased onto "
        "its real graph 71935a84 (prep_c150_a3_6_rebase.log); start = the ONE X10 start stage_prerun.x10_start = measured fresh load 589.4 + op-0 read 5.9 "
        "(PD352(b)); Error List by the fixed rule (tools/elrule.py a5ee7d5c, unchanged, PD354(b)) on the adopted s07 Error List (50); the EL is a RECORDED "
        "cross-check (PD354(a)), per_class feeds the scratch recipe's advisory step".format(S6N + 1, LAST),
        "plan": {"path": rel(RRP), "md5": md5(RRP)}, "graph": {"path": bp["path"], "md5": md5(os.path.join(ROOT, bp["path"]))}, "bed": base.get("vi"), "bed_md5": base.get("md5"),
        "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [p["actions"][k - 1]["id"] for k in rep["unpredicted"]],
        "ops": [o["kind"] for o in ops], "cdiff_rows": sorted(fz.get("end_cdiff_rows") or []), "cross_session_refs": "bound by stage_prerun --rebase (finalized.rebase)",
        "errorlist": {"bed_total": EL_S6, "new_items_predicted": len(ELP["new_items"]) - len(ELP["closed_items"]), "predicted_total": ELP["predicted_total"],
                      "alternative_total": None, "fixed": ELP, "rule": ELP["rule"] + "; base = adopted s07 file measured " + str(EL_S6) + " (" + rel(EXPF) + ")",
                      "rule_source": {"module": "tools/elrule.py", "module_md5": md5(os.path.join(ROOT, "tools", "elrule.py")), "requiredness": rel(REQF),
                                      "requiredness_md5": md5(REQF), "pd": "PD349+PD351(c); PD354(a)(b)"},
                      "previous": None, "base_file": rel(EXPF), "checked": False,
                      "per_class": {"start_read": {"path": rel(READF), "md5": READF_MD5, "items": len(RI), "classes": dict(sorted(C0.items()))},
                                    "rule_new": dict(byc[0]), "rule_closed": dict(byc[1]), "predicted": PC,
                                    "classifier": "elcls: elrule.item_class(raw + detail) -> local/cond/sr; norm_ocr(raw) containing 'unwiredorbadterminal' or "
                                                  "'requiredinput'+'notwired' -> input; else 'other:' + norm_ocr(raw) (prep_c147_a1_3_pred.py)",
                                    "advisory": "PD354(a): non-zero only for a class in neither start_read.classes nor predicted, or |total diff| > 3"}},
        "memory_pred": {"card": "150-a3-6", "checkpoints": cps, "R": mp["R"], "N": mp["N"], "bind_ops": bind, "op_kinds": [o["kind"] for o in ops],
                        "start_mb": START, "start_cite": START_CITE, "start_rule": "stage_prerun.x10_start (PD352(b))", "peak_mb": mp["peak_mb"],
                        "fail_above_mb": mp["fail_above_mb"], "below_fail": mp["ok"], "memstop_mb": SX.MEM_STOP_MB, "next_op": NEXT, "next_op_peak_mb": pk(S6N, NEXT),
                        "prerun_start": xs, "prerun_peak_mb": mp2["peak_mb"], "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)}},
        "summary": fz.get("summary")}
json.dump(pred, open(PP, "w", encoding="utf-8"), indent=1)
print("FACT ops", dict(collections.Counter(pred["ops"])), "census", pred["census"], "overall", pred["census_overall"], "unpredicted", len(pred["census_unpredicted"]),
      "| EL", pred["errorlist"]["predicted_total"], "| end rows", len(pred["cdiff_rows"]), "open pairs", len(p.get("open_rows") or []), flush=True)
for x in ("tools/bench/plan_ring_p4_s08v18.json", "tools/bench/plan_ring_p4_s08v18_pred.json", "tools/bench/plan_ring_p4_s08v18_in.json",
          "tools/elrule.py", "tools/bench/memory_model.json", bp["path"]):
    print("FACT md5 {0} {1}".format(md5(os.path.join(ROOT, x)), x), flush=True)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (RRP, PP))
gate("SP pred written, keyed to the plan md5", J(PP)["plan"]["md5"] == md5(RRP))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
sys.exit(1 if G["fail"] else 0)
