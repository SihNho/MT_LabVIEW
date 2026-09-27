r"""diag_c115b_scratch - card 115-2 R2: SCRATCH VERIFY of the shift-register-pair delete (both halves and their wires) BEFORE the one L2-R1
launch. It runs the stage recipe's OWN body (tools/recipes/stage_d1_l2r1.py, imported, SAVE=False) on the dated byte copy
claudeDev\scratch_c115b_bed_<ts>.vi of the B3 bed (md5 1b5c12d7) - the same Executor, RetireGuardBE (live-consumer re-read before each delete),
E1/D/CEN/ENDS/PB/HF gates, and Remove Bad Wires on the work copy vs a copy of the bed. Nothing saved, no VI run; the copies are deleted at close.
PRIOR ART: diag_c113c_scratch.py (scratch Stage + record write). PREDICTION: every gate of the recipe PASS except PS (not run: SAVE=False);
LabVIEW gone. PASS writes tools/bench/scratch_verify/stagexec.op_delete_object_srpair_<ts>.json.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/diag_c115b_scratch.log -- py -u tools/bench/diag_c115b_scratch.py"""
import json, os, sys, time                                                          # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recipes"))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_d1_l2r1 as R                                                           # noqa: E402
REC = os.path.join(K.BENCH, "scratch_verify")
PLAN = os.path.join(K.BENCH, "plan_l2r1.json")                                      # the recipe's plan (stage_prerun.plan_files reads it)
R.SAVE = False


def body(s):
    print(__doc__, flush=True)
    return R.body(s)


if __name__ == "__main__":
    st = K.Stage(R.BASE["vi"], R.BASE["md5"], "scratch_c115b_bed", preload=False, deadline_min=35,
                 out_json=os.path.join(K.BENCH, "diag_c115b_scratch.json"), task="card 115-2 R2")
    rc = K.run(body, st)
    gone = R.DRY or SX.kill_labview_at_exit()
    if rc == 0 and gone and not R.DRY:
        os.makedirs(REC, exist_ok=True)
        fn = "stagexec.op_delete_object_srpair"
        json.dump({"function": fn, "status": "PASS", "t": time.time(), "card": "115-2 R2",
                   "op": "stagexec delete_object -> stagekit.delete_object -> build_opfsinnertunnelconnect_v0.del_node (RightShiftRegister; pair)",
                   "fixture": "scratch byte copy of claudeDev\\D1_l2_b3_20260928_032703.vi (deleted)",
                   "plan": {"path": os.path.relpath(PLAN, K.ROOT), "md5": K.md5(PLAN)},
                   "recipe": {"path": "tools/recipes/stage_d1_l2r1.py", "md5": K.md5(R.__file__)},
                   "facts": st.R.get("l2r1"), "log": "tools/bench/diag_c115b_scratch.log"},
                  open(os.path.join(REC, "{0}_{1}.json".format(fn, st.stamp)), "w", encoding="utf-8"), indent=1, default=str)
    sys.exit(rc if gone else 1)
