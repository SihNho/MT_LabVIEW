r"""launch_p3b2_c135_a - child 1 of tools/bench/launch_p3b2_c135.py (card 134-P1, PD290(d)): RING P3b-2 SESSION a, the LAUNCH.
Runs tools/recipes/stage_d1_ring_p3b2a.py's OWN body (imported UNCHANGED, md5 bb5ba064) on a work copy of the BED
D1_ring_p3b1_20261002_060910.vi (R.BASE, md5 9d7bf287; the bed itself is never saved) -> claudeDev\D1_ring_p3b2a_<ts>.vi (the
recipe's rule-6 gui_save of the work copy; never a bed). SAME code path as tools/bench/stage_d1_ring_p3b2a_scratch.py (card 133-6,
PASS 20/0 at 650.9 MB): only the Stage name (D1_ring_p3b2a, not scratch_), the log/summary names and the card text differ.
Only change vs the recipe run: SX.MEM_STOP_MB = 690.0 (PD272(b)/PD275(b)).
PREDICTION: every recipe gate PASS (L0 L1 E1 NG FR D CEN2 TD PB HB PS); peak private MB <= 690 and <= X10 671.8 + 10 (scratch a measured
650.9); bed md5 unchanged; LabVIEW gone. Writes tools/bench/launch_p3b2_c135_a_sum.json for the runner.
    (child of the runner)  py tools/bgrun.py --material --max-min 45 --log tools/bench/launch_p3b2_c135_a.log -- py -u tools/bench/launch_p3b2_c135_a.py"""
import json, os, re, sys                                                            # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recipes"))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_d1_ring_p3b2a as R                                                     # noqa: E402
SX.MEM_STOP_MB = 690.0
X10 = 671.8
PLAN = os.path.join(K.BENCH, "plan_ring_p3b2a.json")                                # the recipe's plan (stage_prerun.plan_files reads it)
LOG = os.path.join(K.BENCH, "launch_p3b2_c135_a.log")


def body(s):
    print(__doc__, flush=True)
    print("MEM_STOP_MB {0}".format(SX.MEM_STOP_MB), flush=True)
    return R.body(s)


if __name__ == "__main__":
    bed_md5 = K.md5(R.BASE["vi"])
    st = K.Stage(R.BASE["vi"], R.BASE["md5"], "D1_ring_p3b2a", preload=False, deadline_min=40,
                 out_json=os.path.join(K.BENCH, "launch_p3b2_c135_a.json"), task="launch_p3b2_c135 session a (card 134-P1 runner)")
    rc = K.run(body, st)
    gone = R.DRY or SX.kill_labview_at_exit()
    if not R.DRY:
        mbs = [float(m) for m in re.findall(r"METER \w+\s+k\s+\d+\s+private ([\d.]+) MB", open(LOG, encoding="utf-8", errors="replace").read())] \
            if os.path.exists(LOG) else []
        peak = max(mbs) if mbs else None
        fin, fmd5 = (st.R.get("ring_p3b2a") or {}).get("final"), (st.R.get("ring_p3b2a") or {}).get("md5")
        ok_mem = peak is not None and peak <= 690.0 and peak <= X10 + 10.0
        ok_bed = K.md5(R.BASE["vi"]) == bed_md5 == R.BASE["md5"]
        print("LAUNCH-A peak {0} MB (X10 {1}); final {2} md5 {3}; bed md5 {4} -> {5}".format(peak, X10, fin, fmd5, bed_md5, K.md5(R.BASE["vi"])), flush=True)
        print("  {0}  MEM peak <= 690 and peak <= X10 + 10 (PD285(d))".format("PASS" if ok_mem else "FAIL"), flush=True)
        print("  {0}  BED bed md5 unchanged".format("PASS" if ok_bed else "FAIL"), flush=True)
        print("  {0}  GONE LabVIEW gone".format("PASS" if gone else "FAIL"), flush=True)
        json.dump({"card": "134-P1 runner", "step": "a", "rc": rc, "peak_mb": peak, "x10": X10, "final": fin, "final_md5": fmd5,
                   "bed_md5_ok": ok_bed, "gone": gone}, open(os.path.join(K.BENCH, "launch_p3b2_c135_a_sum.json"), "w", encoding="utf-8"), indent=1)
        rc = rc or (0 if (ok_mem and ok_bed and gone) else 1)
    sys.exit(rc if gone else 1)
