r"""stage_d1_ring_p3b2b_scratch - card 134-5 (PD290(d)): SCRATCH RUN of RING P3b-2 SESSION b (PD283(d), PD287(e), D-2026-10-01-01).
Runs tools/recipes/stage_d1_ring_p3b2b.py's OWN body (imported UNCHANGED, e6636785) with plan_ring_p3b2b.json ae6b6111 (finalized
on the MEASURED graph graph_ring_p3b2a_fs_20261002_102553.json, PD290(a)) on a dated byte copy claudeDev\scratch_c134_5_ring_p3b2b_<ts>.vi
of session a's KEPT in-between file (R.BASE["vi"] = scratch_c133_6_ring_p3b2a_20261002_093837.vi, md5 6cc69221) - same Executor,
LVBackend and every recipe gate (L0 L1 E1 NG FR D CEN2 TD PB HB PS EL). No VI is run; neither the bed nor the in-between file is
edited (stagekit.Stage edits only its work copy). SAVE on (rule-6 gui_save of the work copy): the saved file is the scratch FINAL of
step P3b-2 whose Error List is read count-only (--role scratch) next, then deleted.
Changes vs the recipe run: SX.MEM_STOP_MB = 690.0; X10 is read at run time from the newest 'X10 ... predicted peak' FACT of
tools/bench/stage_prerun_c134_5_p3b2b_scr_prerun.log (the prerun of THIS file). Observation only (wrapper side, recipe untouched): the
FULL-class census before/after is printed (CENSUS-ALL lines, cut of stage_d1_ring_p3b1_scratch.py:28-64) - the pred's census is EMPTY
(all 18 rows CENSUS-UNPREDICTED), so these lines are the measurement PD264(c) writes into plan_ring_p3b2b_pred.json.
PRIOR ART: this file's card-133-6 version (a1e3b5d2); stage_d1_ring_p3b2a_scratch.py; stage_d1_ring_p3b1_scratch.py (CENSUS-ALL).
PREDICTION: L1 18 actions; E1 every checkpoint == sim; NG; FR; D == sim; TD; CEN2 UNPREDICTED (measured printed); PB cdiff 16; HB <= +700;
PS saved; EL expected file written; peak private MB <= 690 and <= X10 667.0 + 10 (one-sided, PD285(d)); in-between + bed md5 unchanged;
LabVIEW gone.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/stage_d1_ring_p3b2b_scratch_c134_5.log -- py -u tools/bench/stage_d1_ring_p3b2b_scratch.py"""
import json, os, re, sys                                                            # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recipes"))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_d1_ring_p3b2b as R                                                     # noqa: E402
SX.MEM_STOP_MB = 690.0
PLAN = os.path.join(K.BENCH, "plan_ring_p3b2b.json")                                # the recipe's plan (stage_prerun.plan_files reads it)
LOG = os.path.join(K.BENCH, "stage_d1_ring_p3b2b_scratch_c134_5.log")
PRLOG = os.path.join(K.BENCH, "stage_prerun_c134_5_p3b2b_scr_prerun.log")
BED = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_ring_p3b1_20261002_060910.vi"
BED_MD5 = "9d7bf28738b7c154280e5e7c2c9d4961"
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
    v = re.findall(r"X10 \S+plan_ring_p3b2b\.json: .*predicted peak ([\d.]+) MB", open(PRLOG, encoding="utf-8", errors="replace").read())
    return float(v[-1]) if v else None


def body(s):
    print(__doc__, flush=True)
    print("MEM_STOP_MB {0}; X10 from prerun {1}".format(SX.MEM_STOP_MB, x10()), flush=True)
    return R.body(s)


if __name__ == "__main__":
    a_md5 = K.md5(R.BASE["vi"])
    st = K.Stage(R.BASE["vi"], R.BASE["md5"], "scratch_c134_5_ring_p3b2b", preload=False, deadline_min=40,
                 out_json=os.path.join(K.BENCH, "stage_d1_ring_p3b2b_scratch.json"), task="card 134-5 scratch b")
    rc = K.run(body, st)
    gone = R.DRY or SX.kill_labview_at_exit()
    if not R.DRY:
        mbs = [float(m) for m in re.findall(r"METER \w+\s+k\s+\d+\s+private ([\d.]+) MB", open(LOG, encoding="utf-8", errors="replace").read())] \
            if os.path.exists(LOG) else []
        peak, X = (max(mbs) if mbs else None), x10()
        fin = (st.R.get("ring_p3b2b") or {}).get("final")
        print("SCRATCH-B peak {0} MB (X10 {1}, d {2}); final {3} md5 {4}; a-file md5 {5} -> {6}; bed md5 {7}".format(
            peak, X, None if peak is None or X is None else round(peak - X, 1), fin, (st.R.get("ring_p3b2b") or {}).get("md5"),
            a_md5, K.md5(R.BASE["vi"]), K.md5(BED)), flush=True)
        ok_mem = peak is not None and X is not None and peak <= 690.0 and peak <= X + 10.0
        ok_in = K.md5(R.BASE["vi"]) == a_md5 == R.BASE["md5"] and K.md5(BED) == BED_MD5
        print("GATE MEM peak <= 690 and peak <= X10 + 10 (PD285(d)): {0}".format("PASS" if ok_mem else "FAIL"), flush=True)
        print("GATE IN a-file and bed md5 unchanged: {0}".format("PASS" if ok_in else "FAIL"), flush=True)
        print("GATE GONE LabVIEW gone: {0}".format("PASS" if gone else "FAIL"), flush=True)
        json.dump({"card": "134-5", "rc": rc, "peak_mb": peak, "x10": X, "final": fin, "final_md5": (st.R.get("ring_p3b2b") or {}).get("md5"),
                   "inputs_ok": ok_in, "gone": gone, "census_all": st.R.get("census_all")},
                  open(os.path.join(K.BENCH, "stage_d1_ring_p3b2b_scratch_sum.json"), "w", encoding="utf-8"), indent=1)
        rc = rc or (0 if (ok_mem and ok_in and gone) else 1)
    sys.exit(rc if gone else 1)
