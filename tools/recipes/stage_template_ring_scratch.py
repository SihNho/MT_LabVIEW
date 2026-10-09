# ---
# labview: build
# hardware: none
# offline-args: --el-advisory --el-advisory-selftest
# evidence: tools/recipes/stage_template_ring_scratch.py:49-51
# ---
r"""stage_template_ring_scratch - TEMPLATE of a ring batch's ONE SCRATCH RUN as INPUTS + CALLS (card chat-T7, docs/script-writing.md,
docs/d1/result-gates.md PD377). A new batch writes tools/recipes/stage_d1_ring_<batch>_scratch.py with this shape: its INPUTS block, `import
<its recipe> as R`, the same calls. Logic lives in tools/stagekit.py: census_all_install (CENSUS-ALL lines), pred_x10 (X10 from the md5-pinned
pred), scratch_offline_modes / el_advisory / el_class (the ADVISORY Error List step, PD354(a)), scratch_tail (MEM / MEML / IN / GONE + sum json).
Worked example = P5-1a's inputs (== tools/recipes/stage_d1_ring_p5s01a_scratch.py, which ran in cycle 154 and is kept as the record).
Runs R's OWN body (imported unchanged) on a dated byte copy claudeDev\<WORK>_<ts>.vi of R's base - same Executor, LVBackend (per-op census
+ Is Broken? + the run-time PRIM gate), every recipe gate and the ExecState read. No VI is run; the bed is never edited. SAVE on (rule-6
gui_save of the work copy); when every STRUCTURAL gate passes the copy is ADOPTED by `py tools/stagexec.py adopt` (PD329(a), PD354(a)).
Error List (next, separate run): `--el-advisory <read json>` prints EL-ADVISORY and exits non-zero only for an unseen class or |total diff| > 3;
`--el-advisory-selftest` runs synthetic reads. Neither opens LabVIEW. The TEMPLATE itself refuses a real launch.
PREDICTION (numbers in R.PRED): every recipe gate PASS incl. PRIM; peak private MB <= SX.X10_FAIL_MB (680) and <= X10 + 10 and <= 680 for the
launch (PD331(c)); bed md5 unchanged; LabVIEW gone.
    py tools/stage_prerun.py --dry tools/recipes/stage_template_ring_scratch.py"""
import os, sys, time                                                                # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_template_ring as R                                                     # noqa: E402  a batch imports ITS recipe here

# ---- INPUTS: the only lines a new batch changes -------------------------------------------------------------------------------------
PLAN = os.path.join(K.BENCH, "plan_ring_p5s01a.json")                               # == R.PLAN (stage_prerun.plan_files reads the literal)
PREDF = os.path.join(K.BENCH, "plan_ring_p5s01a_pred.json")
LOG = os.path.join(K.BENCH, "diag_template_ring_scratch.log")                       # the bgrun --log of this run (METER lines)
SCRATCH, WORK, TAG = "scratch_template_ring", "D1_ring_p5s01a", "P5S01A"
CARD = "chat-T7 template"
OUT_JSON, SUM_JSON = os.path.join(K.BENCH, "diag_template_ring_scratch.json"), os.path.join(K.BENCH, "diag_template_ring_scratch_sum.json")

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
    if not R.DRY and os.path.basename(__file__).startswith("stage_template_"):
        sys.exit("stage_template_ring_scratch is a TEMPLATE: write tools/recipes/stage_d1_ring_<batch>_scratch.py and launch that")
    st = K.Stage(R.BASE["vi"], R.BASE["md5"], SCRATCH, preload=False, deadline_min=45,
                 work_name="{0}_{1}.vi".format(WORK, time.strftime("%Y%m%d_%H%M%S")), out_json=OUT_JSON, task="{0} scratch".format(CARD))
    rc = K.run(body, st)
    gone = R.DRY or SX.kill_labview_at_exit()
    if not R.DRY:
        rc = K.scratch_tail(st, rc, gone, R.KEY, TAG, LOG, R.BASE["vi"], R.BASE["md5"], PREDF, PLAN, CARD, SUM_JSON, SX.X10_FAIL_MB)
    sys.exit(rc if gone else 1)
