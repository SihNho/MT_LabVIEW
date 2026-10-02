r"""launch_p3b2_c135_b - child 3 of tools/bench/launch_p3b2_c135.py (card 134-P1, PD290(d)): RING P3b-2 SESSION b, the LAUNCH.
Runs tools/recipes/stage_d1_ring_p3b2b.py's OWN body (imported UNCHANGED, md5 e6636785) on a work copy of the file SESSION a SAVED
IN THIS CHAIN (tools/bench/launch_p3b2_c135_state.json `a_file`/`a_md5`; never the scratch in-between 6cc69221, never the bed)
-> claudeDev\D1_ring_p3b2b_<ts>.vi = step P3b-2's FINAL file + errorlist_expected (recipe's EL gate).
WHY THE INPUT IS NOT R.BASE["vi"]: plan b ae6b6111 was finalized on graph_ring_p3b2a_fs_20261002_102553.json, whose `vi` is the scratch
in-between 6cc69221. The runner only starts this child when the launched a-file's graph read COMPARED EQUAL to that graph (node
classes, terminal rows, wires, fs_measured; PD290(b)(d)) - or after plan b was re-finalized on the new read (then R.BASE["vi"] IS the
a-file). The recipe's gates (FR/D/TD/PB) compare against R.BASE's rows, valid in both cases.
SAME code path as tools/bench/stage_d1_ring_p3b2b_scratch.py (Stage on a given input + R.body); only the input, the Stage name and the
log/summary names differ. SX.MEM_STOP_MB = 690.0. X10 = R.PRED memory_pred.peak_mb (667.0 on ae6b6111).
DRY (stage_prerun --dry, COM stubbed): no state file needed - the input falls back to R.BASE (the dry never opens a VI). LIVE without the
state file: exit 2, nothing opened.
PREDICTION: every recipe gate PASS (L0 L1 E1 NG FR D CEN2 TD PB HB PS EL); peak <= 690 and <= X10 + 10; a-file and bed md5 unchanged;
LabVIEW gone. Writes tools/bench/launch_p3b2_c135_b_sum.json.
    (child of the runner)  py tools/bgrun.py --material --max-min 45 --log tools/bench/launch_p3b2_c135_b.log -- py -u tools/bench/launch_p3b2_c135_b.py"""
import json, os, re, sys                                                            # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recipes"))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_d1_ring_p3b2b as R                                                     # noqa: E402
SX.MEM_STOP_MB = 690.0
PLAN = os.path.join(K.BENCH, "plan_ring_p3b2b.json")                                # the recipe's plan (stage_prerun.plan_files reads it)
LOG = os.path.join(K.BENCH, "launch_p3b2_c135_b.log")
STATE = os.path.join(K.BENCH, "launch_p3b2_c135_state.json")
BED = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_ring_p3b1_20261002_060910.vi"
BED_MD5 = "9d7bf28738b7c154280e5e7c2c9d4961"
X10 = float((R.PRED.get("memory_pred") or {}).get("peak_mb") or 0) or None


def body(s):
    print(__doc__, flush=True)
    print("MEM_STOP_MB {0}; X10 (pred) {1}".format(SX.MEM_STOP_MB, X10), flush=True)
    return R.body(s)


if __name__ == "__main__":
    st_ = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {}
    if not R.DRY and not (st_.get("a_file") and st_.get("a_md5")):
        print("NO STATE: {0} lacks a_file/a_md5 - session b needs session a's launched file; nothing opened".format(STATE), flush=True)
        sys.exit(2)
    IN, IN_MD5 = (st_["a_file"], st_["a_md5"]) if not R.DRY else (R.BASE["vi"], R.BASE["md5"])
    a_md5 = K.md5(IN)
    st = K.Stage(IN, IN_MD5, "D1_ring_p3b2b", preload=False, deadline_min=40,
                 out_json=os.path.join(K.BENCH, "launch_p3b2_c135_b.json"), task="launch_p3b2_c135 session b (card 134-P1 runner)")
    rc = K.run(body, st)
    gone = R.DRY or SX.kill_labview_at_exit()
    if not R.DRY:
        mbs = [float(m) for m in re.findall(r"METER \w+\s+k\s+\d+\s+private ([\d.]+) MB", open(LOG, encoding="utf-8", errors="replace").read())] \
            if os.path.exists(LOG) else []
        peak = max(mbs) if mbs else None
        fin, fmd5 = (st.R.get("ring_p3b2b") or {}).get("final"), (st.R.get("ring_p3b2b") or {}).get("md5")
        ok_mem = peak is not None and X10 is not None and peak <= 690.0 and peak <= X10 + 10.0
        ok_in = K.md5(IN) == a_md5 == IN_MD5 and K.md5(BED) == BED_MD5
        print("LAUNCH-B peak {0} MB (X10 {1}); final {2} md5 {3}; a-file md5 {4} -> {5}; bed md5 {6}".format(
            peak, X10, fin, fmd5, a_md5, K.md5(IN), K.md5(BED)), flush=True)
        print("  {0}  MEM peak <= 690 and peak <= X10 + 10 (PD285(d))".format("PASS" if ok_mem else "FAIL"), flush=True)
        print("  {0}  IN a-file and bed md5 unchanged".format("PASS" if ok_in else "FAIL"), flush=True)
        print("  {0}  GONE LabVIEW gone".format("PASS" if gone else "FAIL"), flush=True)
        json.dump({"card": "134-P1 runner", "step": "b", "rc": rc, "peak_mb": peak, "x10": X10, "input": IN, "input_md5": IN_MD5, "final": fin,
                   "final_md5": fmd5, "inputs_ok": ok_in, "gone": gone}, open(os.path.join(K.BENCH, "launch_p3b2_c135_b_sum.json"), "w", encoding="utf-8"), indent=1)
        rc = rc or (0 if (ok_mem and ok_in and gone) else 1)
    sys.exit(rc if gone else 1)
