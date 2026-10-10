# ---
# labview: build
# hardware: none
# offline-args: --el-advisory --el-advisory-selftest
# evidence: tools/recipes/stage_d1_ring_p5s02b_scratch.py:54-57
# ---
r"""stage_d1_ring_p5s02b_scratch - card 160-c3-1 (WRITTEN, NOT LAUNCHED): the ONE SCRATCH RUN of RING P5-2 step 2 (docs/d1/ring-p5b.md PD390(f),
PD391(e): new structure class, the scratch is not skipped) on plan_ring_p5s02b.json. Pair shape of stage_d1_ring_p5s02a_scratch.py on the shared
stagekit calls (census_all_install, op_class_census_install, pred_x10, scratch_offline_modes / el_advisory, scratch_tail): only names, plan / pred
paths, the log and the census ops differ (docs/script-writing.md rules 1-2).
Runs tools/recipes/stage_d1_ring_p5s02b.py's OWN body (imported unchanged) on a dated byte copy claudeDev\D1_ring_p5s02b_<ts>.vi of the saved
p5s02a file 94ffff94. No VI is run; the bed is never edited. SAVE on (rule-6 gui_save of the work copy). First action measured: dw_a13 (the
termless delete, PD390(a)); MERGE A28 / A35 and the stub delete + fresh connect A32 / A39 are judged by wire ENDS (PD389(b), PD391(d)).
OPCENSUS ops 3 / 5 / 7 / 9 (printing only, reads the run takes anyway): 3 = group t_gi (A28 MERGE), 7 = group t_hi (A35 MERGE), 5 / 9 = the base
register connect_term_uid groups (A32 / A39); an op whose previous op is not a checkpoint prints "not measured".
Error List (next, separate run): `--el-advisory <read json>` against the pred (predicted 51, UNPREDICTED A32 / A39); `--el-advisory-selftest`.
PREDICTION (numbers in plan_ring_p5s02b_pred.json): every recipe gate PASS incl. PRIM; peak private MB <= SX.X10_FAIL_MB (680) and <= X10 + 10;
bed md5 unchanged; LabVIEW gone.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c161_p5s02b_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s02b_scratch.py"""
import os, sys, time                                                                # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_d1_ring_p5s02b as R                                                    # noqa: E402

# ---- INPUTS -------------------------------------------------------------------------------------------------------------------------
PLAN = os.path.join(K.BENCH, "plan_ring_p5s02b.json")                               # == R.PLAN (stage_prerun.plan_files reads the literal)
PREDF = os.path.join(K.BENCH, "plan_ring_p5s02b_pred.json")
LOG = os.path.join(K.BENCH, "diag_c161_p5s02b_scratch.log")                         # the bgrun --log of this run (METER lines)
SCRATCH, WORK, TAG = "scratch_c161_p5s02b", "D1_ring_p5s02b", "P5S02B"
CARD = "card 160-c3-1 (P5-2 step 2 scratch)"
OUT_JSON, SUM_JSON = os.path.join(K.BENCH, "diag_c161_p5s02b_scratch.json"), os.path.join(K.BENCH, "diag_c161_p5s02b_scratch_sum.json")
OPS_CENSUS = (3, 5, 7, 9)                                                           # MERGE groups 3 / 7, base-register connects 5 / 9 (PD391(e))

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
