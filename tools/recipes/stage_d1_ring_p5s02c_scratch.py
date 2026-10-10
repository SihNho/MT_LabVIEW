# ---
# labview: build
# hardware: none
# offline-args: --el-advisory --el-advisory-selftest
# evidence: tools/recipes/stage_d1_ring_p5s02c_scratch.py:56-59
# ---
r"""stage_d1_ring_p5s02c_scratch - card 163-a1-3 (WRITTEN, NOT LAUNCHED): the ONE SCRATCH RUN of RING P5-2 step 3 (docs/d1/ring-p5b.md PD396(d)(e),
D-2026-10-01-01: a full scratch before every ring step) on plan_ring_p5s02c.json (group I A41..A52). Pair shape of stage_d1_ring_p5s02b_scratch.py
on the shared stagekit calls (census_all_install, op_class_census_install, pred_x10, scratch_offline_modes / el_advisory, scratch_tail): only names,
plan / pred paths, the log and the census ops differ (docs/script-writing.md rules 1-2).
Runs tools/recipes/stage_d1_ring_p5s02c.py's OWN body (imported unchanged) on a dated byte copy claudeDev\D1_ring_p5s02c_<ts>.vi of the saved
p5s02b file f9ae7751. No VI is run; the bed is never edited. SAVE on (rule-6 gui_save of the work copy). First action measured: sr_c7 (add_sr on
loop #23041). The two connect_term_uid register_end_case_border groups (ops 5 / 7: TC7 / TD7 onto the new SR CS7) and the two case_frame_wire
rows (ops 6 / 8) are judged by wire ENDS (PD389(b)).
OPCENSUS ops 5 / 6 / 7 / 8 (printing only, reads the run takes anyway): 5 / 7 = the register_end_case_border groups, 6 / 8 = case_frame_wire
branch / new_wire; an op whose previous op is not a checkpoint prints "not measured".
Error List (next, separate run): `--el-advisory <read json>` against the pred (predicted 53, UNPREDICTED groups A45 t_ci7 / A49 t_co7, upper 55);
`--el-advisory-selftest`.
PREDICTION (numbers in plan_ring_p5s02c_pred.json): every recipe gate PASS incl. PRIM; peak private MB <= SX.X10_FAIL_MB (680) and <= X10 + 10;
bed md5 unchanged; LabVIEW gone.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c163_p5s02c_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s02c_scratch.py"""
import os, sys, time                                                                # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_d1_ring_p5s02c as R                                                    # noqa: E402

# ---- INPUTS -------------------------------------------------------------------------------------------------------------------------
PLAN = os.path.join(K.BENCH, "plan_ring_p5s02c.json")                               # == R.PLAN (stage_prerun.plan_files reads the literal)
PREDF = os.path.join(K.BENCH, "plan_ring_p5s02c_pred.json")
LOG = os.path.join(K.BENCH, "diag_c163_p5s02c_scratch.log")                         # the bgrun --log of this run (METER lines)
SCRATCH, WORK, TAG = "scratch_c163_p5s02c", "D1_ring_p5s02c", "P5S02C"
CARD = "card 163-a1-3 (P5-2 step 3 scratch)"
OUT_JSON, SUM_JSON = os.path.join(K.BENCH, "diag_c163_p5s02c_scratch.json"), os.path.join(K.BENCH, "diag_c163_p5s02c_scratch_sum.json")
OPS_CENSUS = (5, 6, 7, 8)                                                           # register_end_case_border 5 / 7, case_frame_wire 6 / 8

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
