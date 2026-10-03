r"""stage_d1_ring_p4_s02v18_scratch - card 142-5 (WRITTEN, NOT LAUNCHED): the ONE SCRATCH RUN of RING P4 v18 LabVIEW SESSION 2
(PD331(c)(d), D-2026-10-01-01). COPIED from stage_d1_ring_p4_s01_scratch.py (card 141-3) with names changed (log, scratch name,
out/sum json, card id, recipe) and the launch-memory line MEML 675 -> 680 (PD331(c): the X10 cut limit is memory_model.json's 680,
superseding PD326(e)'s 675; scratch MEM_STOP_MB 690 -> SX.X10_FAIL_MB 680 in card 143-1 per PD328(a)). x10() takes the limit from the md5-PINNED pred file
(plan_ring_p4_s02v18_pred.json memory_pred.peak_mb, used only when pred.plan.md5 == md5(plan_ring_p4_s02v18.json)).
Runs tools/recipes/stage_d1_ring_p4_s02v18.py's OWN body (imported UNCHANGED) with plan_ring_p4_s02v18.json on a dated byte copy
claudeDev\D1_ring_p4s02_<ts>.vi (card 143-1; was scratch_c142_p4s02v18_<ts>.vi) of session 1's file D1_ring_p4s01_20261002_232547.vi (dc61e193) - same Executor, LVBackend
(per-op census + Is Broken? + the run-time PRIM gate), every recipe gate and the ExecState read. No VI is run; the bed is never
edited. SAVE on (rule-6 gui_save of the work copy) so the Error List can be read count-only next.
PREDICTION (numbers in plan_ring_p4_s02v18_pred.json): every recipe gate PASS incl. PRIM; peak private MB <= SX.X10_FAIL_MB (680) and <= X10 + 10 and,
for the launch, <= 680 (PD331(c)); bed md5 unchanged; LabVIEW gone. Error List (next, separate run) == pred predicted_total.
CARD 143-1 EDIT (PD329(a), PD332(d)) - names only: log/out/sum -> diag_c143_1_scratch*, card id 143-1, and the work copy is SAVED
under the stage's normal name claudeDev\D1_ring_p4s02_<ts>.vi (Stage(work_name=...)) so that, when every gate passes, it is ADOPTED
as session 2's file by `py tools/stagexec.py adopt` (no second run on the s01 file). Edits, gates and limits unchanged.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c143_1_scratch.log -- py -u tools/recipes/stage_d1_ring_p4_s02v18_scratch.py"""
import json, os, re, sys, time                                                      # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_d1_ring_p4_s02v18 as R                                                 # noqa: E402
SX.MEM_STOP_MB = SX.X10_FAIL_MB            # card 143-1 (PD328(a), prior-art c143-1 A3/B3): the scratch stop = X10 fail threshold (memory_model.json, 680; was 690)
PLAN = os.path.join(K.BENCH, "plan_ring_p4_s02v18.json")                            # the recipe's plan (stage_prerun.plan_files reads it)
PREDF = os.path.join(K.BENCH, "plan_ring_p4_s02v18_pred.json")
LOG = os.path.join(K.BENCH, "diag_c143_1_scratch.log")
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
    print("MEM_STOP_MB {0}; X10 from the md5-pinned pred {1}".format(SX.MEM_STOP_MB, x10()), flush=True)
    return R.body(s)


if __name__ == "__main__":
    st = K.Stage(R.BASE["vi"], R.BASE["md5"], "scratch_c143_p4s02v18", preload=False, deadline_min=45,
                 work_name="D1_ring_p4s02_{0}.vi".format(time.strftime("%Y%m%d_%H%M%S")),
                 out_json=os.path.join(K.BENCH, "diag_c143_1_scratch.json"), task="card 143-1 scratch P4 v18 session 2 (adopt on all-PASS)")
    rc = K.run(body, st)
    gone = R.DRY or SX.kill_labview_at_exit()
    if not R.DRY:
        mbs = [float(m) for m in re.findall(r"METER \w+\s+k\s+\d+\s+private ([\d.]+) MB", open(LOG, encoding="utf-8", errors="replace").read())] \
            if os.path.exists(LOG) else []
        peak, X = (max(mbs) if mbs else None), x10()
        fin = (st.R.get("ring_p4_s02v18") or {}).get("final")
        print("SCRATCH-P4S02V18 peak {0} MB (X10 {1}, d {2}); final {3} md5 {4}; bed md5 {5}".format(
            peak, X, None if peak is None or X is None else round(peak - X, 1), fin, (st.R.get("ring_p4_s02v18") or {}).get("md5"), K.md5(R.BASE["vi"])), flush=True)
        ok_mem = peak is not None and X is not None and peak <= SX.X10_FAIL_MB and peak <= X + 10.0
        ok_in = K.md5(R.BASE["vi"]) == R.BASE["md5"]
        print("GATE MEM peak <= {1} and peak <= X10 + 10 (PD285(d), PD328(a)): {0}".format("PASS" if ok_mem else "FAIL", SX.X10_FAIL_MB), flush=True)
        print("GATE MEML peak <= 680 (launch condition, PD331(c)): {0}".format("PASS" if peak is not None and peak <= 680.0 else "FAIL"), flush=True)
        print("GATE IN bed md5 unchanged: {0}".format("PASS" if ok_in else "FAIL"), flush=True)
        print("GATE GONE LabVIEW gone: {0}".format("PASS" if gone else "FAIL"), flush=True)
        json.dump({"card": "143-1", "rc": rc, "peak_mb": peak, "x10": X, "final": fin, "final_md5": (st.R.get("ring_p4_s02v18") or {}).get("md5"),
                   "inputs_ok": ok_in, "gone": gone, "census_all": st.R.get("census_all")},
                  open(os.path.join(K.BENCH, "diag_c143_1_scratch_sum.json"), "w", encoding="utf-8"), indent=1)
        rc = rc or (0 if (ok_mem and ok_in and gone) else 1)
    sys.exit(rc if gone else 1)
