r"""stage_d1_qrt_pool_scratch - card 119-4 L2 (part 1): SCRATCH VERIFY of the QRT POOL stage BEFORE the one launch. It runs the stage recipe's OWN
body (tools/recipes/stage_d1_qrt_pool.py, imported unchanged) on the dated byte copy claudeDev\scratch_c119_pool_<ts>.vi of the R2 bed (md5 7dac9f04) -
same Executor, LVBackend, TI/NV/RV/MX/D/TD/FU/PB gates and the rule-6 gui_save of the SCRATCH (so its Error List can be read by part 2,
stage_d1_qrt_pool_el.py scratch, which deletes it). No VI is run. R2 is never opened for edit (byte copy only).
PRIOR ART: tools/bench/diag_c116b_scratch.py (card 116-2 P4; this is its cut for the pool recipe).
PREDICTION: every recipe gate PASS (PS on the scratch name); LabVIEW gone; PASS writes tools/bench/scratch_verify/stagexec.qrt_pool_creates_<ts>.json.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/stage_d1_qrt_pool_scratch.log -- py -u tools/bench/stage_d1_qrt_pool_scratch.py"""
import json, os, sys, time                                                          # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recipes"))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_d1_qrt_pool as R                                                       # noqa: E402
REC = os.path.join(K.BENCH, "scratch_verify")
PLAN = os.path.join(K.BENCH, "plan_qrt_pool.json")                                  # the recipe's plan (stage_prerun.plan_files reads it)


def body(s):
    print(__doc__, flush=True)
    return R.body(s)


if __name__ == "__main__":
    st = K.Stage(R.BASE["vi"], R.BASE["md5"], "scratch_c119_pool", preload=False, deadline_min=40,
                 out_json=os.path.join(K.BENCH, "stage_d1_qrt_pool_scratch.json"), task="card 119-4 L2 scratch")
    rc = K.run(body, st)
    gone = R.DRY or SX.kill_labview_at_exit()
    if rc == 0 and gone and not R.DRY:
        os.makedirs(REC, exist_ok=True)
        fn = "stagexec.qrt_pool_creates"
        json.dump({"function": fn, "status": "PASS", "t": time.time(), "card": "119-4 L2",
                   "op": "stagexec create (for/subvi/primitive/queue) + tunnel + const/nested/cfw connect -> the QRT POOL recipe",
                   "fixture": "scratch byte copy of claudeDev\\D1_l2_r2_20260928_110756.vi (saved for the Error List read, then deleted)",
                   "plan": {"path": os.path.relpath(PLAN, K.ROOT), "md5": K.md5(PLAN)},
                   "recipe": {"path": "tools/recipes/stage_d1_qrt_pool.py", "md5": K.md5(R.__file__)},
                   "facts": st.R.get("qrt_pool"), "log": "tools/bench/stage_d1_qrt_pool_scratch.log"},
                  open(os.path.join(REC, "{0}_{1}.json".format(fn, st.stamp)), "w", encoding="utf-8"), indent=1, default=str)
    sys.exit(rc if gone else 1)
