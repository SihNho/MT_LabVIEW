# ---
# labview: build
# hardware: none
# offline-args: --el-advisory --el-advisory-selftest
# evidence: tools/recipes/stage_d1_ring_p4_s07v18_scratch.py:161-167
# ---
r"""stage_d1_ring_p4_s07v18_scratch - card 150-a3-1 (WRITTEN, NOT LAUNCHED): the ONE SCRATCH RUN of RING P4 v18 LabVIEW SESSION 7
(PD364(c), PD365(d)(e), PD366(e)(g)) on the REBASED plan 08c2ad4d. COPIED from stage_d1_ring_p4_s06v18_scratch.py (31009bfc) with
names changed (log, scratch name, work name, out/sum json, card id, recipe) and the sink-gate assertion = R's census count (PD366(e): one
declared gate per s07 census row through wire_indicators, read by R from prep_c150_a1_1_session.json; was "exactly ONE");
launch-memory line MEML 680 kept (PD331(c)); scratch stop = SX.X10_FAIL_MB (680, PD328(a)).
x10() takes the limit from the md5-PINNED pred file (plan_ring_p4_s07v18_pred.json memory_pred.peak_mb, used only when
pred.plan.md5 == md5(plan_ring_p4_s07v18.json)).
Runs tools/recipes/stage_d1_ring_p4_s07v18.py's OWN body (imported UNCHANGED) with plan_ring_p4_s07v18.json on a dated byte copy
claudeDev\D1_ring_p4s07_<ts>.vi of session 6's ADOPTED file 569ffbf5 - same Executor, LVBackend (per-op census + Is Broken? + the
run-time PRIM gate), every recipe gate and the ExecState read. No VI is run; the bed is never edited. SAVE on (rule-6 gui_save of the work
copy) so the Error List can be read next; when every STRUCTURAL gate passes the work copy is ADOPTED as session 7's file by
`py tools/stagexec.py adopt` (PD329(a), PD354(a)).
ADDED (card 147-a1-3, PD354(a)) - the Error List step is ADVISORY, offline, and changes no structural gate: after the scratch's full EL read
(errorlist_check.py --role final on the work copy), run this file with `--el-advisory <read json>`: it prints EL-ADVISORY with the total and
the per-class difference against the pred's errorlist.per_class (classes by elcls(), the same copy as prep_c150_a3_1_pred.py), and exits
NON-ZERO ONLY when a class appears that is in neither the start read nor the prediction, or |total diff| > 3; any other difference is
recorded (rc 0). `--el-advisory-selftest` runs three synthetic reads offline. Neither mode opens LabVIEW (they return before K.Stage).
PREDICTION (numbers in plan_ring_p4_s07v18_pred.json): every recipe gate PASS incl. PRIM; peak private MB <= SX.X10_FAIL_MB (680) and <= X10 + 10 and,
for the launch, <= 680 (PD331(c)); bed md5 unchanged; LabVIEW gone. Error List (next, separate run) -> EL-ADVISORY (recorded; RETURN only by its rc).
    py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c150_p4s07v18_scratch.log -- py -u tools/recipes/stage_d1_ring_p4_s07v18_scratch.py"""
import collections, json, os, re, sys, time                                         # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_d1_ring_p4_s07v18 as R                                                 # noqa: E402
import elrule as ELR                                                                # noqa: E402  card 147-a1-3: item_class for the advisory EL step
SG = SX.check_sink_gates(R.SINK_GATES, R.SINK_FNS)                                  # card 147-a2-1 (PD355(b)): R.body hands R's sink gates to LVBackend
assert len(SG) == len(R.SINK_GATES) == len(R.SG_CENSUS) and [d["sink"] for d in SG] == [d["sink"] for d in R.SGS], \
    ("scratch expects one sink gate per census row", SG)                            # card 150-a3-1 (PD366(e)): declared once each, in R
SX.MEM_STOP_MB = SX.X10_FAIL_MB            # card 143-P2 (PD328(a), prior-art c143-p1 B2; as s02v18_scratch.py:21): the scratch stop = X10 fail threshold (680; was 690)
PLAN = os.path.join(K.BENCH, "plan_ring_p4_s07v18.json")                            # the recipe's plan (stage_prerun.plan_files reads it)
PREDF = os.path.join(K.BENCH, "plan_ring_p4_s07v18_pred.json")
LOG = os.path.join(K.BENCH, "diag_c150_p4s07v18_scratch.log")
OBS = {"snaps": []}
_snap, _cg = K.Stage.census_snapshot, K.Stage.census_gate


def snap_keep(self, target=None):
    d = _snap(self, target); OBS["snaps"].append(dict(d)); return d                 # noqa: E702


def cg_print(self, label, before, after, declared):
    got = _cg(self, label, before, after, declared)
    if isinstance(before, dict) and isinstance(after, dict) and len(OBS["snaps"]) >= 2:
        b, a = OBS["snaps"][0], OBS["snaps"][-1]
        cnt = lambda d: dict((c, sum(1 for v in d.values() if v == c)) for c in set(d.values()))   # noqa: E731
        cb, ca = cnt(b), cnt(a)
        delta = dict((c, ca.get(c, 0) - cb.get(c, 0)) for c in sorted(set(cb) | set(ca)) if ca.get(c, 0) != cb.get(c, 0))
        nb = {}
        for u in set(a) - set(b):
            nb[a[u]] = nb.get(a[u], 0) + 1
        print("  CENSUS-ALL net delta (every class) {0}".format(json.dumps(delta, sort_keys=True)), flush=True)
        print("  CENSUS-ALL new uids by class (every class) {0}".format(json.dumps(nb, sort_keys=True)), flush=True)
        print("  CENSUS-ALL lost uids {0}".format(len(set(b) - set(a))), flush=True)
        self.R["census_all"] = {"net_delta": delta, "new_by_class": nb, "lost": len(set(b) - set(a))}
    return got


K.Stage.census_snapshot, K.Stage.census_gate = snap_keep, cg_print


def x10():
    """The X10 prediction of THIS plan: the pred file's memory_pred.peak_mb, only when the pred is keyed to the plan's md5."""
    try:
        pr = json.load(open(PREDF, encoding="utf-8"))
        if (pr.get("plan") or {}).get("md5") != K.md5(PLAN):
            return None
        v = (pr.get("memory_pred") or {}).get("peak_mb")
        return float(v) if v is not None else None
    except (OSError, ValueError):
        return None


def body(s):
    print(__doc__, flush=True)
    print("MEM_STOP_MB {0}; X10 from the md5-pinned pred {1}; declared sink gates {2}".format(SX.MEM_STOP_MB, x10(), SG), flush=True)
    return R.body(s)


# ---- card 147-a1-3 (PD354(a)): the ADVISORY Error List step - offline, after the scratch's EL read; no structural gate is touched
OCR_ALIASES = (("vl", "vi"), ("v", "y"))                                            # == errorlist_check.OCR_ALIASES (copied)
EL_TOTAL_TOL = 3                                                                    # PD354(a): RETURN when |total diff| > 3


def norm_ocr(s):
    k = re.sub(r"[^a-z0-9]", "", (s or "").lower())                                # == errorlist_check.norm
    for a, b in OCR_ALIASES:
        k = k.replace(a, b)
    return k


def elcls(it):
    """One Error List item -> its class (== prep_c150_a3_1_pred.py elcls): local / cond / sr / input / other:<norm_ocr(raw)>."""
    c = ELR.item_class("{0} {1}".format(it.get("raw", ""), it.get("detail", "")))
    if c:
        return c
    k = norm_ocr(it.get("raw"))
    if "unwiredorbadterminal" in k or ("requiredinput" in k and "notwired" in k):
        return "input"
    return "other:" + k


def el_advisory(items, pred=None):
    """(rc, report) for one EL read (its items) against the pred: rc 1 only for an unseen class or |total diff| > EL_TOTAL_TOL; rc 2 when
    the pred is not keyed to this plan or has no per_class block; else 0 (the difference is recorded, not a gate)."""
    pr = pred if pred is not None else json.load(open(PREDF, encoding="utf-8"))
    el = pr.get("errorlist") or {}
    pc = el.get("per_class") or {}
    if pred is None and (pr.get("plan") or {}).get("md5") != K.md5(PLAN):
        return 2, {"why": "pred not keyed to plan md5"}
    if not pc.get("predicted"):
        return 2, {"why": "pred has no errorlist.per_class"}
    start, want = pc["start_read"]["classes"], pc["predicted"]
    got = collections.Counter(elcls(x) for x in items or [])
    diff = dict((c, got.get(c, 0) - want.get(c, 0)) for c in sorted(set(got) | set(want)) if got.get(c, 0) != want.get(c, 0))
    unseen = sorted(c for c in got if c not in start and c not in want)
    td = len(items or []) - int(el["predicted_total"])
    rc = 1 if (unseen or abs(td) > EL_TOTAL_TOL) else 0
    return rc, {"read_total": len(items or []), "pred_total": el["predicted_total"], "total_diff": td, "per_class_diff": diff, "unseen": unseen,
                "verdict": "RETURN" if rc else "RECORDED"}


def el_advisory_print(rc, rep):
    print("EL-ADVISORY total read {0} pred {1} diff {2:+}; per-class diff (read - pred) {3}; unseen classes {4}; verdict {5} rc {6}".format(
        rep.get("read_total"), rep.get("pred_total"), rep.get("total_diff", 0), json.dumps(rep.get("per_class_diff"), sort_keys=True),
        rep.get("unseen"), rep.get("verdict", rep.get("why")), rc), flush=True)


def el_selftest():
    """Three synthetic reads built from the pred's predicted per-class counts (offline): unseen class -> 1; total +4 -> 1; total +2 known -> 0."""
    pr = json.load(open(PREDF, encoding="utf-8"))
    want = pr["errorlist"]["per_class"]["predicted"]
    txt = {"local": "Local Variable: This variable is not connected to anything.", "sr": "Shift Register: unwired from inside the loop",
           "cond": "While Loop: Conditional terminal is not wired", "input": "Index Array 'Index Array': Contains unwired or bad terminal"}
    mk = lambda c: {"raw": txt[c] if c in txt else c.split(":", 1)[1], "detail": ""}   # noqa: E731
    base = [mk(c) for c, n in sorted(want.items()) for _ in range(n)]
    rt = all(elcls(mk(c)) == c for c in want)
    known = sorted(c for c in want if c.startswith("other:"))[0]
    cases = [("A unseen class (+1 'Feedback Node: Initializer terminal is not wired')", base + [{"raw": "Feedback Node: Initializer terminal is not wired", "detail": ""}], 1),
             ("B total +4 of a known class ({0})".format(known), base + [mk(known)] * 4, 1),
             ("C total +2 of a known class ({0})".format(known), base + [mk(known)] * 2, 0),
             ("D the prediction itself", base, 0)]
    ok = rt
    print("EL-SELFTEST synthetic classes round-trip through elcls: {0} ({1} classes, {2} items)".format(rt, len(want), len(base)), flush=True)
    for name, items, exp in cases:
        rc, rep = el_advisory(items, pr)
        el_advisory_print(rc, rep)
        print("EL-SELFTEST case {0}: rc {1} expected {2} -> {3}".format(name, rc, exp, "PASS" if rc == exp else "FAIL"), flush=True)
        ok = ok and rc == exp
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if ok else "FAIL", "gates": {"pass": 5 if ok else 0, "fail": 0 if ok else 1},
                                  "first_fail": None if ok else "EL-SELFTEST", "artefacts": []}), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    if "--el-advisory-selftest" in sys.argv[1:]:                                   # OFFLINE: returns before K.Stage, no LabVIEW
        sys.exit(el_selftest())
    if "--el-advisory" in sys.argv[1:]:                                             # OFFLINE: <read json> -> EL-ADVISORY, no LabVIEW
        _rc, _rep = el_advisory(json.load(open(sys.argv[sys.argv.index("--el-advisory") + 1], encoding="utf-8")).get("items") or [])
        el_advisory_print(_rc, _rep)
        sys.exit(_rc)
    st = K.Stage(R.BASE["vi"], R.BASE["md5"], "scratch_c150_p4s07v18", preload=False, deadline_min=45,
                 work_name="D1_ring_p4s07_{0}.vi".format(time.strftime("%Y%m%d_%H%M%S")),
                 out_json=os.path.join(K.BENCH, "diag_c150_p4s07v18_scratch.json"), task="card 150-a3-1 scratch P4 v18 session 7")
    rc = K.run(body, st)
    gone = R.DRY or SX.kill_labview_at_exit()
    if not R.DRY:
        mbs = [float(m) for m in re.findall(r"METER \w+\s+k\s+\d+\s+private ([\d.]+) MB", open(LOG, encoding="utf-8", errors="replace").read())] \
            if os.path.exists(LOG) else []
        peak, X = (max(mbs) if mbs else None), x10()
        fin = (st.R.get("ring_p4_s07v18") or {}).get("final")
        print("SCRATCH-P4S07V18 peak {0} MB (X10 {1}, d {2}); final {3} md5 {4}; bed md5 {5}".format(
            peak, X, None if peak is None or X is None else round(peak - X, 1), fin, (st.R.get("ring_p4_s07v18") or {}).get("md5"), K.md5(R.BASE["vi"])), flush=True)
        ok_mem = peak is not None and X is not None and peak <= SX.X10_FAIL_MB and peak <= X + 10.0
        ok_in = K.md5(R.BASE["vi"]) == R.BASE["md5"]
        print("GATE MEM peak <= {1} and peak <= X10 + 10 (PD285(d), PD328(a)): {0}".format("PASS" if ok_mem else "FAIL", SX.X10_FAIL_MB), flush=True)
        print("GATE MEML peak <= 680 (launch condition, PD331(c)): {0}".format("PASS" if peak is not None and peak <= 680.0 else "FAIL"), flush=True)
        print("GATE IN bed md5 unchanged: {0}".format("PASS" if ok_in else "FAIL"), flush=True)
        print("GATE GONE LabVIEW gone: {0}".format("PASS" if gone else "FAIL"), flush=True)
        json.dump({"card": "150-a3-1", "rc": rc, "peak_mb": peak, "x10": X, "final": fin, "final_md5": (st.R.get("ring_p4_s07v18") or {}).get("md5"),
                   "inputs_ok": ok_in, "gone": gone, "census_all": st.R.get("census_all")},
                  open(os.path.join(K.BENCH, "diag_c150_p4s07v18_scratch_sum.json"), "w", encoding="utf-8"), indent=1)
        rc = rc or (0 if (ok_mem and ok_in and gone) else 1)
    sys.exit(rc if gone else 1)
