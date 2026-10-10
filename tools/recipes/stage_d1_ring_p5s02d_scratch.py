# ---
# labview: build
# hardware: none
# offline-args: --el-advisory --el-advisory-selftest
# evidence: tools/recipes/stage_d1_ring_p5s02d_scratch.py:58-61
# ---
r"""stage_d1_ring_p5s02d_scratch - card 164-3-4 (WRITTEN, NOT LAUNCHED; re-made from card 164-a2-3's scratch for the re-made plan): the ONE
SCRATCH RUN of RING P5-2 step 4 (docs/d1/ring-p5c.md PD397(d), PD399, D-2026-10-01-01: a full scratch before every ring step) on
plan_ring_p5s02d.json 97837e2a (groups J in the P4 delete form + K3, A53..A71). Pair shape of stage_d1_ring_p5s02c_scratch.py on the shared
stagekit calls (census_all_install, op_class_census_install, pred_x10, scratch_offline_modes / el_advisory, scratch_tail): only names, plan /
pred paths, the log and the census ops differ (docs/script-writing.md rules 1-2).
Runs tools/recipes/stage_d1_ring_p5s02d.py's OWN body (imported unchanged) on a dated byte copy claudeDev\D1_ring_p5s02d_<ts>.vi of the saved
p5s02c file 564d8cbe. No VI is run; the bed is never edited. SAVE on (rule-6 gui_save of the work copy). First actions measured: dw_cond and
dw_23460 (delete_wire #23489 / #23460, each a checkpoint). The two delete_object rows (ops 3 / 4: #23042, #23501), wire_remove_loose_ends
#23519 (op 5), the case-frame connect w_eq7_x (op 8) and the two connect_term_uid register_end_case_border groups (ops 14 / 15: OK3 / IK3 onto
the new SR SK3) are judged by wire ENDS (PD389(b)); PD399(a) expectations in the pred key `pd399a` (w23460 0 rows; w23519 sinks
{t23450, t23241, t7606}). OPCENSUS ops 3 / 4 / 5 / 8 / 14 / 15 (printing only, reads the run takes anyway); an op whose previous op is not a
checkpoint prints "not measured".
Error List (next, separate run): `--el-advisory <read json>` against the pred (predicted 53, UNPREDICTED groups A66 t_k3o / A69 t_k3i and
delete row A56 do_23501, upper 56); `--el-advisory-selftest`.
PREDICTION (numbers in plan_ring_p5s02d_pred.json): every recipe gate PASS incl. PRIM; peak private MB <= SX.X10_FAIL_MB (680) and <= X10 + 10;
bed md5 unchanged; LabVIEW gone.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c164_p5s02d_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s02d_scratch.py"""
import os, sys, time                                                                # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_d1_ring_p5s02d as R                                                    # noqa: E402

# ---- INPUTS -------------------------------------------------------------------------------------------------------------------------
PLAN = os.path.join(K.BENCH, "plan_ring_p5s02d.json")                               # == R.PLAN (stage_prerun.plan_files reads the literal)
PREDF = os.path.join(K.BENCH, "plan_ring_p5s02d_pred.json")
LOG = os.path.join(K.BENCH, "diag_c164_p5s02d_scratch.log")                         # the bgrun --log of this run (METER lines)
SCRATCH, WORK, TAG = "scratch_c164_p5s02d", "D1_ring_p5s02d", "P5S02D"
CARD = "card 164-3-4 (P5-2 step 4 scratch)"
OUT_JSON, SUM_JSON = os.path.join(K.BENCH, "diag_c164_p5s02d_scratch.json"), os.path.join(K.BENCH, "diag_c164_p5s02d_scratch_sum.json")
OPS_CENSUS = (3, 4, 5, 8, 14, 15)                                                   # delete_object 3 / 4, rle 5, case-frame connect 8, reb 14 / 15

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
