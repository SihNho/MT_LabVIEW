r"""stage_d1_ring_p3b2a_scratch - card 133-5 step 1: SCRATCH RUN of RING P3b-2 SESSION a (PD283(d), PD284(f), D-2026-10-01-01).
Runs tools/recipes/stage_d1_ring_p3b2a.py's OWN body (imported UNCHANGED) on a dated byte copy
claudeDev\scratch_c133_5_ring_p3b2a_<ts>.vi of the P3b-1 bed (D1_ring_p3b1_20261002_060910.vi, md5 9d7bf287) - same Executor,
LVBackend and every recipe gate (L0 L1 E1 NG FR D CEN2 TD PB HB PS). No VI is run; the bed is never opened for edit.
SAVE on: the recipe's rule-6 gui_save of the SCRATCH work copy (stagekit.save broken_ok, -Exception Approved); the saved scratch is
the in-between file that step 2 reads into a graph and step 3 (session b scratch) edits. Deleted at the end of card 133-5.
Only change vs the recipe run: SX.MEM_STOP_MB = 690.0 (the card's peak ceiling, PD272(b)/PD275(b)) instead of the recipe's 700.
PRIOR ART: tools/bench/stage_d1_ring_p3b1_scratch.py (card 129-2/130-6/131-3; this is its cut without the NEWOBJ observation).
PREDICTION: L1 21 actions; E1 every checkpoint == sim; NG names == step files; FR on base frames; D == sim; TD; CEN2 == pred;
PB cdiff 16; HB <= +700; PS saved; peak private MB <= 690 and <= X10 671.8 + 10 (one-sided, PD285(d)); bed md5 unchanged; LabVIEW gone.
CARD 133-6 (2nd run, retry_of 133-5): the recipe's FR gate now takes base frames from the FS frame lists too (PD285(b)); log
renamed *_c133_6.log so the meter read covers only this run; scratch name scratch_c133_6_ring_p3b2a.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/stage_d1_ring_p3b2a_scratch_c133_6.log -- py -u tools/bench/stage_d1_ring_p3b2a_scratch.py"""
import json, os, re, sys                                                            # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recipes"))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_d1_ring_p3b2a as R                                                     # noqa: E402
SX.MEM_STOP_MB = 690.0
X10 = 671.8
PLAN = os.path.join(K.BENCH, "plan_ring_p3b2a.json")                                # the recipe's plan (stage_prerun.plan_files reads it)
LOG = os.path.join(K.BENCH, "stage_d1_ring_p3b2a_scratch_c133_6.log")


def body(s):
    print(__doc__, flush=True)
    print("MEM_STOP_MB {0}".format(SX.MEM_STOP_MB), flush=True)
    return R.body(s)


if __name__ == "__main__":
    bed_md5 = K.md5(R.BASE["vi"])
    st = K.Stage(R.BASE["vi"], R.BASE["md5"], "scratch_c133_6_ring_p3b2a", preload=False, deadline_min=40,
                 out_json=os.path.join(K.BENCH, "stage_d1_ring_p3b2a_scratch.json"), task="card 133-6 scratch a")
    rc = K.run(body, st)
    gone = R.DRY or SX.kill_labview_at_exit()
    if not R.DRY:
        mbs = [float(m) for m in re.findall(r"METER \w+\s+k\s+\d+\s+private ([\d.]+) MB", open(LOG, encoding="utf-8", errors="replace").read())] \
            if os.path.exists(LOG) else []
        peak = max(mbs) if mbs else None
        fin = (st.R.get("ring_p3b2a") or {}).get("final")
        print("SCRATCH-A peak {0} MB (X10 {1}, d {2}); final {3} md5 {4}; bed md5 {5} -> {6}".format(
            peak, X10, None if peak is None else round(peak - X10, 1), fin, (st.R.get("ring_p3b2a") or {}).get("md5"),
            bed_md5, K.md5(R.BASE["vi"])), flush=True)
        ok_mem = peak is not None and peak <= 690.0 and peak <= X10 + 10.0
        ok_bed = K.md5(R.BASE["vi"]) == bed_md5 == R.BASE["md5"]
        print("GATE MEM peak <= 690 and peak <= X10 + 10 (PD285(d)): {0}".format("PASS" if ok_mem else "FAIL"), flush=True)
        print("GATE BED bed md5 unchanged: {0}".format("PASS" if ok_bed else "FAIL"), flush=True)
        print("GATE GONE LabVIEW gone: {0}".format("PASS" if gone else "FAIL"), flush=True)
        json.dump({"card": "133-6", "rc": rc, "peak_mb": peak, "x10": X10, "final": fin, "final_md5": (st.R.get("ring_p3b2a") or {}).get("md5"),
                   "bed_md5_ok": ok_bed, "gone": gone}, open(os.path.join(K.BENCH, "stage_d1_ring_p3b2a_scratch_sum.json"), "w", encoding="utf-8"), indent=1)
        rc = rc or (0 if (ok_mem and ok_bed and gone) else 1)
    sys.exit(rc if gone else 1)
