r"""stage_d1_ring_p4_s02_scratch - card 141-P1 (WRITTEN, NOT LAUNCHED): the ONE SCRATCH RUN of RING P4 v17 LabVIEW SESSION 2
(PD320(e), PD323(d), PD324(d), D-2026-10-01-01). COPIED from stage_d1_ring_p4_s01_scratch.py (card 141-1) with names changed only
(recipe module, plan, pred, log, scratch name, out/sum json, card id). x10() takes the limit from the md5-PINNED pred file
(plan_ring_p4_s02_pred.json memory_pred.peak_mb, used only when pred.plan.md5 == md5(plan_ring_p4_s02.json)).
Runs tools/recipes/stage_d1_ring_p4_s02.py's OWN body (imported UNCHANGED) with plan_ring_p4_s02.json on a dated byte copy
claudeDev\scratch_c141_p4s02_<ts>.vi of session 1's in-between file (the plan's base after `stage_prerun --rebase`) - same Executor,
LVBackend (per-op census + Is Broken? + the run-time PRIM gate), every recipe gate and the ExecState read. No VI is run; the input
file is never edited. SAVE on (rule-6 gui_save of the work copy) so the Error List can be read count-only next; the scratch file is
deleted after that read. Until the rebase the plan's base is PROVISIONAL and the launch gate refuses this file.
PREDICTION (numbers in plan_ring_p4_s02_pred.json): every recipe gate PASS incl. PRIM; peak private MB <= 690 and <= X10 + 10 and,
for the launch, <= 675 (PD321(c)); input md5 unchanged; LabVIEW gone. Error List (next, separate run) == pred predicted_total.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c141_p4s02_scratch.log -- py -u tools/recipes/stage_d1_ring_p4_s02_scratch.py"""
import json, os, re, sys                                                            # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_d1_ring_p4_s02 as R                                                    # noqa: E402
SX.MEM_STOP_MB = 690.0
PLAN = os.path.join(K.BENCH, "plan_ring_p4_s02.json")                               # the recipe's plan (stage_prerun.plan_files reads it)
PREDF = os.path.join(K.BENCH, "plan_ring_p4_s02_pred.json")
LOG = os.path.join(K.BENCH, "diag_c141_p4s02_scratch.log")
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
    st = K.Stage(R.BASE["vi"], R.BASE["md5"], "scratch_c141_p4s02", preload=False, deadline_min=45,
                 out_json=os.path.join(K.BENCH, "diag_c141_p4s02_scratch.json"), task="card 141-P1 scratch P4 v17 session 2")
    rc = K.run(body, st)
    gone = R.DRY or SX.kill_labview_at_exit()
    if not R.DRY:
        mbs = [float(m) for m in re.findall(r"METER \w+\s+k\s+\d+\s+private ([\d.]+) MB", open(LOG, encoding="utf-8", errors="replace").read())] \
            if os.path.exists(LOG) else []
        peak, X = (max(mbs) if mbs else None), x10()
        fin = (st.R.get("ring_p4_s02") or {}).get("final")
        print("SCRATCH-P4S02 peak {0} MB (X10 {1}, d {2}); final {3} md5 {4}; input md5 {5}".format(
            peak, X, None if peak is None or X is None else round(peak - X, 1), fin, (st.R.get("ring_p4_s02") or {}).get("md5"), K.md5(R.BASE["vi"])), flush=True)
        ok_mem = peak is not None and X is not None and peak <= 690.0 and peak <= X + 10.0
        ok_in = K.md5(R.BASE["vi"]) == R.BASE["md5"]
        print("GATE MEM peak <= 690 and peak <= X10 + 10 (PD285(d)): {0}".format("PASS" if ok_mem else "FAIL"), flush=True)
        print("GATE MEML peak <= 675 (launch condition, PD321(c)): {0}".format("PASS" if peak is not None and peak <= 675.0 else "FAIL"), flush=True)
        print("GATE IN input md5 unchanged: {0}".format("PASS" if ok_in else "FAIL"), flush=True)
        print("GATE GONE LabVIEW gone: {0}".format("PASS" if gone else "FAIL"), flush=True)
        json.dump({"card": "141-P1", "rc": rc, "peak_mb": peak, "x10": X, "final": fin, "final_md5": (st.R.get("ring_p4_s02") or {}).get("md5"),
                   "inputs_ok": ok_in, "gone": gone, "census_all": st.R.get("census_all")},
                  open(os.path.join(K.BENCH, "diag_c141_p4s02_scratch_sum.json"), "w", encoding="utf-8"), indent=1)
        rc = rc or (0 if (ok_mem and ok_in and gone) else 1)
    sys.exit(rc if gone else 1)
