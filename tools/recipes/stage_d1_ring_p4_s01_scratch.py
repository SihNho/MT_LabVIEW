r"""stage_d1_ring_p4_s01_scratch - card 140-3 item 4 (was 140-2 item 3; card 140-3 changed ONLY names: log, prerun log, scratch name,
out/sum json, card id; plan_ring_p4_s01.json re-made from v15, PD321(b)): the ONE SCRATCH RUN of RING P4 LabVIEW SESSION 1 (PD320(e), D-2026-10-01-01).
COPIED from tools/recipes/stage_d1_ring_p4s1_scratch.py (card 139-7) with ONLY names changed (recipe module, plan, log, prerun log,
scratch name, out json, result key, card id). Runs tools/recipes/stage_d1_ring_p4_s01.py's OWN body (imported UNCHANGED) with
plan_ring_p4_s01.json on a dated byte copy claudeDev\scratch_c140_2_ring_p4s01_<ts>.vi of the P3b-2b bed D1_ring_p3b2b_20261002_130007.vi
(395118775a52) - same Executor, LVBackend (per-op census + Is Broken?), every recipe gate (L0 L1 E1 NG FR D CEN2 TD PB HB PS) and the
ExecState read. No VI is run; the bed is never edited. SAVE on (rule-6 gui_save of the work copy) so the Error List can be read
count-only (--role scratch) next; the scratch file is deleted after that read.
PREDICTION: L1 16 ops; E1 every checkpoint == sim; NG; FR; D == sim; TD; CEN2 == pred; PB cdiff == pred rows; HB <= +700; PS saved;
peak private MB <= 690 and <= X10 (673.4) + 10; bed md5 unchanged; LabVIEW gone. Error List (next, separate run) 51 (alt. 53).
    py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c140_3_scratch.log -- py -u tools/recipes/stage_d1_ring_p4_s01_scratch.py"""
import json, os, re, sys                                                            # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_d1_ring_p4_s01 as R                                                    # noqa: E402
SX.MEM_STOP_MB = 690.0
PLAN = os.path.join(K.BENCH, "plan_ring_p4_s01.json")                               # the recipe's plan (stage_prerun.plan_files reads it)
LOG = os.path.join(K.BENCH, "diag_c140_3_scratch.log")
PRLOG = os.path.join(K.BENCH, "prep_c140_3_scr_prerun.log")
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
    if not os.path.exists(PRLOG):
        return None
    v = re.findall(r"X10 \S+plan_ring_p4_s01\.json: .*predicted peak ([\d.]+) MB", open(PRLOG, encoding="utf-8", errors="replace").read())
    return float(v[-1]) if v else None


def body(s):
    print(__doc__, flush=True)
    print("MEM_STOP_MB {0}; X10 from prerun {1}".format(SX.MEM_STOP_MB, x10()), flush=True)
    return R.body(s)


if __name__ == "__main__":
    st = K.Stage(R.BASE["vi"], R.BASE["md5"], "scratch_c140_3_ring_p4s01", preload=False, deadline_min=45,
                 out_json=os.path.join(K.BENCH, "diag_c140_3_scratch.json"), task="card 140-3 scratch P4 session 1")
    rc = K.run(body, st)
    gone = R.DRY or SX.kill_labview_at_exit()
    if not R.DRY:
        mbs = [float(m) for m in re.findall(r"METER \w+\s+k\s+\d+\s+private ([\d.]+) MB", open(LOG, encoding="utf-8", errors="replace").read())] \
            if os.path.exists(LOG) else []
        peak, X = (max(mbs) if mbs else None), x10()
        fin = (st.R.get("ring_p4_s01") or {}).get("final")
        print("SCRATCH-P4S01 peak {0} MB (X10 {1}, d {2}); final {3} md5 {4}; bed md5 {5}".format(
            peak, X, None if peak is None or X is None else round(peak - X, 1), fin, (st.R.get("ring_p4_s01") or {}).get("md5"), K.md5(R.BASE["vi"])), flush=True)
        ok_mem = peak is not None and X is not None and peak <= 690.0 and peak <= X + 10.0
        ok_in = K.md5(R.BASE["vi"]) == R.BASE["md5"]
        print("GATE MEM peak <= 690 and peak <= X10 + 10 (PD285(d)): {0}".format("PASS" if ok_mem else "FAIL"), flush=True)
        print("GATE IN bed md5 unchanged: {0}".format("PASS" if ok_in else "FAIL"), flush=True)
        print("GATE GONE LabVIEW gone: {0}".format("PASS" if gone else "FAIL"), flush=True)
        json.dump({"card": "140-3", "rc": rc, "peak_mb": peak, "x10": X, "final": fin, "final_md5": (st.R.get("ring_p4_s01") or {}).get("md5"),
                   "inputs_ok": ok_in, "gone": gone, "census_all": st.R.get("census_all")},
                  open(os.path.join(K.BENCH, "diag_c140_3_scratch_sum.json"), "w", encoding="utf-8"), indent=1)
        rc = rc or (0 if (ok_mem and ok_in and gone) else 1)
    sys.exit(rc if gone else 1)
