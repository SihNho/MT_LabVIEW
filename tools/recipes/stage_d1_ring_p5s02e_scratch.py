# ---
# labview: build
# hardware: none
# offline-args: --el-advisory --el-advisory-selftest
# evidence: tools/recipes/stage_d1_ring_p5s02e_scratch.py:58-61
# ---
r"""stage_d1_ring_p5s02e_scratch - card 165-3-3 (WRITTEN, NOT LAUNCHED): the ONE SCRATCH RUN of RING P5-2 step 5 (docs/d1/ring-p5c.md PD400,
PD401, PD402, D-2026-10-01-01: a full scratch before every ring step) on plan_ring_p5s02e.json fd23974e (K3f A72-73, K4 A74-82, K4f A83-84).
Pair shape of stage_d1_ring_p5s02d_scratch.py on the shared stagekit calls (census_all_install, op_class_census_install, pred_x10,
scratch_offline_modes / el_advisory, scratch_tail): only names, plan / pred paths, the log and the census ops differ (docs/script-writing.md
rules 1-2).
Runs tools/recipes/stage_d1_ring_p5s02e.py's OWN body (imported unchanged) on a dated byte copy claudeDev\D1_ring_p5s02e_<ts>.vi of the saved
p5s02d file 6dcd5c3d. No VI is run; the bed is never edited. SAVE on (rule-6 gui_save of the work copy). PRIME-SKIP lines expected for #8776
and #24342 (stagexec 1d5309f4). The two stub-delete + connect pairs (ops 1 -> 2: dw_10362 / w_k3f; ops 8 -> 9: dw_25232 / w_k4f, each delete a
checkpoint) carry the PD401(b) / PD402 expectations in the pred keys `pd401b` / `pd402` (face wire 0 after the delete, census in [{}, {'Wire': 1}],
Is Broken? False). The two connect_term_uid register_end_case_border groups (ops 6 / 7: OK4 / IK4 onto the new SR SK4, pass wire on frame #31517)
are judged by wire ENDS (PD389(b)). OPCENSUS ops 2 / 6 / 7 / 9 (printing only, reads the run takes anyway); an op whose previous op is not a
checkpoint prints "not measured".
Error List (next, separate run): `--el-advisory <read json>` against the pred (predicted 49, UNPREDICTED groups A77 t_k4o / A80 t_k4i, upper 51);
`--el-advisory-selftest`.
PREDICTION (numbers in plan_ring_p5s02e_pred.json): every recipe gate PASS incl. PRIM; peak private MB <= SX.X10_FAIL_MB (680) and <= X10 + 10
(X10 peak 659.9, MAIN 665.0 <= 675); bed md5 unchanged; LabVIEW gone.
    py tools/bgrun.py --material --max-min 50 --unverified-card tools/bench/cards/task_165-3-4.json --log tools/bench/diag_c165_p5s02e_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s02e_scratch.py"""
import os, sys, time                                                                # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_d1_ring_p5s02e as R                                                    # noqa: E402

# ---- INPUTS -------------------------------------------------------------------------------------------------------------------------
PLAN = os.path.join(K.BENCH, "plan_ring_p5s02e.json")                               # == R.PLAN (stage_prerun.plan_files reads the literal)
PREDF = os.path.join(K.BENCH, "plan_ring_p5s02e_pred.json")
LOG = os.path.join(K.BENCH, "diag_c165_p5s02e_scratch.log")                         # the bgrun --log of this run (METER lines)
SCRATCH, WORK, TAG = "scratch_c165_p5s02e", "D1_ring_p5s02e", "P5S02E"
CARD = "card 165-3-3 (P5-2 step 5 scratch)"
OUT_JSON, SUM_JSON = os.path.join(K.BENCH, "diag_c165_p5s02e_scratch.json"), os.path.join(K.BENCH, "diag_c165_p5s02e_scratch_sum.json")
OPS_CENSUS = (2, 6, 7, 9)                                                           # connect w_k3f 2, reb 6 / 7, branch w_k4f 9

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
