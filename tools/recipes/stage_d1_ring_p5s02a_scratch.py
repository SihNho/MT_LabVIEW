# ---
# labview: build
# hardware: none
# offline-args: --el-advisory --el-advisory-selftest
# evidence: tools/recipes/stage_d1_ring_p5s02a_scratch.py:43-45
# ---
r"""stage_d1_ring_p5s02a_scratch - card 156-a1-1 (WRITTEN, NOT LAUNCHED): the ONE SCRATCH RUN of RING P5-2 step 1 RE-MADE (docs/d1/ring-p5.md
PD374(b)(d), PD376(d), PD379) on plan_ring_p5s02a.json. Shape = tools/recipes/stage_template_ring_scratch.py (INPUTS + CALLS - stagekit
census_all_install, pred_x10, scratch_offline_modes / el_advisory, scratch_tail), the pair shape of stage_d1_ring_p5s02_scratch.py: only names,
plan / pred paths and the log differ (docs/script-writing.md rules 1-2).
Runs tools/recipes/stage_d1_ring_p5s02a.py's OWN body (imported unchanged) on a dated byte copy claudeDev\D1_ring_p5s02a_<ts>.vi of the ADOPTED
P5-1 file 7f2582ae. No VI is run; the bed is never edited. SAVE on (rule-6 gui_save of the work copy); when every STRUCTURAL gate passes the copy is
ADOPTED by `py tools/stagexec.py adopt` (PD329(a), PD354(a)). The E1 graph == sim result after each move_in op (#376 / #3052 / #3453) is quoted
from this run's log (PD379(e), prior-art A4). Error List (next, separate run): `--el-advisory <read json>`; `--el-advisory-selftest`.
PREDICTION (numbers in plan_ring_p5s02a_pred.json): every recipe gate PASS incl. PRIM; peak private MB <= SX.X10_FAIL_MB (680) and <= X10 + 10;
bed md5 unchanged; LabVIEW gone.
card 158-a3-1 (PD386(c)(e)): the retry writes its OWN log / json / summary (diag_c158_p5s02a_*; the c156 LOG constant made scratch_tail's
METER parse read the whole appended file) and prints one OPCENSUS line per op 16 / 17 (stagekit.op_class_census_install, printing only,
no extra read). The retry's `retry_of` card ("retry_of": "stage_d1_ring_p5s02a_scratch.py") is carried as written:
    py tools/bgrun.py --material --max-min 50 --retry-card <task card> --log tools/bench/diag_c158_p5s02a_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s02a_scratch.py"""
import os, sys, time                                                                # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_d1_ring_p5s02a as R                                                    # noqa: E402

# ---- INPUTS -------------------------------------------------------------------------------------------------------------------------
PLAN = os.path.join(K.BENCH, "plan_ring_p5s02a.json")                               # == R.PLAN (stage_prerun.plan_files reads the literal)
PREDF = os.path.join(K.BENCH, "plan_ring_p5s02a_pred.json")
LOG = os.path.join(K.BENCH, "diag_c158_p5s02a_scratch.log")                         # the bgrun --log of this run (METER lines); card 158-a3-1
SCRATCH, WORK, TAG = "scratch_c156_p5s02a", "D1_ring_p5s02a", "P5S02A"
CARD = "card 158 retry (PD386(e))"
OUT_JSON, SUM_JSON = os.path.join(K.BENCH, "diag_c158_p5s02a_scratch.json"), os.path.join(K.BENCH, "diag_c158_p5s02a_scratch_sum.json")
OPS_CENSUS = (16, 17)                                                               # PD386(c): the per-op class census owed by PD385(b)

# ---- CALLS --------------------------------------------------------------------------------------------------------------------------
SG = SX.check_sink_gates(R.SINK_GATES, R.SINK_FNS)                                  # R.body hands R's sink gates to LVBackend (PD355(b))
assert len(SG) == len(R.SINK_GATES) == len(R.SG_CENSUS) and [d["sink"] for d in SG] == [d["sink"] for d in R.SGS], \
    ("scratch expects one sink gate per census row", SG)                            # PD366(e): declared once each, in R
SX.MEM_STOP_MB = SX.X10_FAIL_MB            # PD328(a): the scratch stop = X10 fail threshold (680)
K.census_all_install()
OPC = K.op_class_census_install(R.RS, OPS_CENSUS)                                   # printing only: keeps reads the run takes anyway


def body(s):
    print(__doc__, flush=True)
    print("MEM_STOP_MB {0}; X10 from the md5-pinned pred {1}; declared sink gates {2}; retry card {3}".format(
        SX.MEM_STOP_MB, K.pred_x10(PREDF, PLAN), SG, K.retry_card_arg(sys.argv, __file__)), flush=True)
    try:
        return R.body(s)
    finally:
        K.op_class_census_print(OPC)


if __name__ == "__main__":
    off = K.scratch_offline_modes(sys.argv[1:], PREDF, PLAN)                       # OFFLINE: returns before K.Stage, no LabVIEW
    if off is not None:
        sys.exit(off)
    st = K.Stage(R.BASE["vi"], R.BASE["md5"], SCRATCH, preload=False, deadline_min=45,
                 work_name="{0}_{1}.vi".format(WORK, time.strftime("%Y%m%d_%H%M%S")), out_json=OUT_JSON, task="{0} scratch".format(CARD))
    rc = K.run(body, st)
    gone = R.DRY or SX.kill_labview_at_exit()
    if not R.DRY:
        rc = K.scratch_tail(st, rc, gone, R.KEY, TAG, LOG, R.BASE["vi"], R.BASE["md5"], PREDF, PLAN, CARD, SUM_JSON, SX.X10_FAIL_MB)
    sys.exit(rc if gone else 1)
