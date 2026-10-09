# ---
# labview: build
# hardware: none
# offline-args: --el-advisory --el-advisory-selftest
# evidence: tools/recipes/stage_d1_ring_p5s01b_scratch.py:43-45
# ---
r"""stage_d1_ring_p5s01b_scratch - card 155-a2-1 (WRITTEN, NOT LAUNCHED): the ONE SCRATCH RUN of RING P5-1b (docs/d1/ring-p5.md PD374(e),
PD378(b); 12 actions / 8 ops, the remainder of P5-1 form S) on plan_ring_p5s01b.json. Shape = tools/recipes/stage_template_ring_scratch.py
(card chat-T7: INPUTS + CALLS - stagekit census_all_install, pred_x10, scratch_offline_modes / el_advisory, scratch_tail) instead of a copy of
stage_d1_ring_p5s01a_scratch.py (3b02d9a7), whose inline blocks those calls replace (docs/script-writing.md rule 1; brief_155-a2-1.md item 6).
Runs tools/recipes/stage_d1_ring_p5s01b.py's OWN body (imported unchanged) on a dated byte copy claudeDev\D1_ring_p5s01b_<ts>.vi of the ADOPTED
P5-1a file 2482fe7b - same Executor, LVBackend (per-op census + Is Broken? + the run-time PRIM gate), every recipe gate and the ExecState read.
No VI is run; the bed is never edited. SAVE on (rule-6 gui_save of the work copy); when every STRUCTURAL gate passes the copy is ADOPTED by
`py tools/stagexec.py adopt` (PD329(a), PD354(a)). Error List (next, separate run): `--el-advisory <read json>`; `--el-advisory-selftest`.
Neither opens LabVIEW.
PREDICTION (numbers in plan_ring_p5s01b_pred.json): every recipe gate PASS incl. PRIM; peak private MB <= SX.X10_FAIL_MB (680) and <= X10 + 10
and <= 680 for the launch (PD331(c)); bed md5 unchanged; LabVIEW gone.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c155_p5s01b_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s01b_scratch.py"""
import os, sys, time                                                                # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_d1_ring_p5s01b as R                                                    # noqa: E402

# ---- INPUTS -------------------------------------------------------------------------------------------------------------------------
PLAN = os.path.join(K.BENCH, "plan_ring_p5s01b.json")                               # == R.PLAN (stage_prerun.plan_files reads the literal)
PREDF = os.path.join(K.BENCH, "plan_ring_p5s01b_pred.json")
LOG = os.path.join(K.BENCH, "diag_c155_p5s01b_scratch.log")                         # the bgrun --log of this run (METER lines)
SCRATCH, WORK, TAG = "scratch_c155_p5s01b", "D1_ring_p5s01b", "P5S01B"
CARD = "card 155-a2-1"
OUT_JSON, SUM_JSON = os.path.join(K.BENCH, "diag_c155_p5s01b_scratch.json"), os.path.join(K.BENCH, "diag_c155_p5s01b_scratch_sum.json")

# ---- CALLS --------------------------------------------------------------------------------------------------------------------------
SG = SX.check_sink_gates(R.SINK_GATES, R.SINK_FNS)                                  # R.body hands R's sink gates to LVBackend (PD355(b))
assert len(SG) == len(R.SINK_GATES) == len(R.SG_CENSUS) and [d["sink"] for d in SG] == [d["sink"] for d in R.SGS], \
    ("scratch expects one sink gate per census row", SG)                            # PD366(e): declared once each, in R
SX.MEM_STOP_MB = SX.X10_FAIL_MB            # PD328(a): the scratch stop = X10 fail threshold (680)
K.census_all_install()


def body(s):
    print(__doc__, flush=True)
    print("MEM_STOP_MB {0}; X10 from the md5-pinned pred {1}; declared sink gates {2}".format(SX.MEM_STOP_MB, K.pred_x10(PREDF, PLAN), SG), flush=True)
    return R.body(s)


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
