r"""stage_d1_ring_p3b2b_scratch - card 133-5 step 3: SCRATCH RUN of RING P3b-2 SESSION b (PD283(d), PD284(f), D-2026-10-01-01).
Runs tools/recipes/stage_d1_ring_p3b2b.py's OWN body (imported UNCHANGED) on a dated byte copy
claudeDev\scratch_c133_5_ring_p3b2b_<ts>.vi of session a's SCRATCH saved file (the plan's base after `--rebase` onto
graph_ring_p3b2a_<ts>.json, step 2) - same Executor, LVBackend and every recipe gate (L0 L1 E1 NG FR D CEN2 TD PB HB PS EL).
No VI is run; neither the bed nor a's scratch file is edited. SAVE on (rule-6 gui_save of the work copy): the saved file is the
scratch FINAL of step P3b-2 that step 4 reads the Error List of (count-only, --role scratch). Deleted at the end of card 133-5.
Only change vs the recipe run: SX.MEM_STOP_MB = 690.0. X10 is read at run time from the newest 'X10 ... predicted peak' FACT of
tools/bench/stage_prerun_c133_5_p3b2b_scr_prerun.log (the prerun of THIS file after the rebase), so the sha256 stays the prerun's.
PRIOR ART: tools/bench/stage_d1_ring_p3b2a_scratch.py (step 1, same card), stage_d1_ring_p3b1_scratch.py.
PREDICTION: L1 18 actions; E1 every checkpoint == sim; NG; FR; D == sim; TD; CEN2 == pred; PB cdiff 16; HB <= +700; PS saved; EL
expected file written; peak private MB <= 690 and <= the prerun's X10 + 10 (one-sided, PD285(d)); bed + a-file md5 unchanged; LabVIEW gone.
CARD 133-6: recipe FR fix (PD285(b)); logs renamed *_c133_6 (meter read + X10 source); scratch name scratch_c133_6_ring_p3b2b.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/stage_d1_ring_p3b2b_scratch_c133_6.log -- py -u tools/bench/stage_d1_ring_p3b2b_scratch.py"""
import json, os, re, sys                                                            # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recipes"))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_d1_ring_p3b2b as R                                                     # noqa: E402
SX.MEM_STOP_MB = 690.0
PLAN = os.path.join(K.BENCH, "plan_ring_p3b2b.json")                                # the recipe's plan (stage_prerun.plan_files reads it)
LOG = os.path.join(K.BENCH, "stage_d1_ring_p3b2b_scratch_c133_6.log")
PRLOG = os.path.join(K.BENCH, "stage_prerun_c133_6_p3b2b_scr_prerun.log")
BED = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_ring_p3b1_20261002_060910.vi"
BED_MD5 = "9d7bf28738b7c154280e5e7c2c9d4961"


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
    st = K.Stage(R.BASE["vi"], R.BASE["md5"], "scratch_c133_6_ring_p3b2b", preload=False, deadline_min=40,
                 out_json=os.path.join(K.BENCH, "stage_d1_ring_p3b2b_scratch.json"), task="card 133-6 scratch b")
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
        json.dump({"card": "133-6", "rc": rc, "peak_mb": peak, "x10": X, "final": fin, "final_md5": (st.R.get("ring_p3b2b") or {}).get("md5"),
                   "inputs_ok": ok_in, "gone": gone}, open(os.path.join(K.BENCH, "stage_d1_ring_p3b2b_scratch_sum.json"), "w", encoding="utf-8"), indent=1)
        rc = rc or (0 if (ok_mem and ok_in and gone) else 1)
    sys.exit(rc if gone else 1)
