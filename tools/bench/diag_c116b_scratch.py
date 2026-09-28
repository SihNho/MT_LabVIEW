r"""diag_c116b_scratch - card 116-2 P4 (part 1): SCRATCH VERIFY of L2-R2 BEFORE the one launch. It runs the stage recipe's OWN body
(tools/recipes/stage_d1_l2r2.py, imported, SAVE=True) on the dated byte copy claudeDev\scratch_c116b_bed_<ts>.vi of the R1 bed (md5 f465196b) - the
same Executor, RetireGuardBE, E1/D/CEN/CEN2/ENDS/TD/PB/HF gates, the gui_save of the SCRATCH (so its Error List can be read, part 2) and Remove Bad
Wires on copies. The saved scratch is kept ONLY for diag_c116b_scratch_el.py, which deletes it. No VI is run. PRIOR ART: diag_c115b_scratch.py (this is
its cut; SAVE=True is new because card 116-2 P4 reads the scratch's Error List before the launch). PREDICTION: every recipe gate PASS (PS on the
scratch name); LabVIEW gone. PASS writes tools/bench/scratch_verify/stagexec.op_delete_object_looptunnel_<ts>.json.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/diag_c116b_scratch.log -- py -u tools/bench/diag_c116b_scratch.py"""
import json, os, sys, time                                                          # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recipes"))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_d1_l2r2 as R                                                           # noqa: E402
REC = os.path.join(K.BENCH, "scratch_verify")
PLAN = os.path.join(K.BENCH, "plan_l2r2.json")                                      # the recipe's plan (stage_prerun.plan_files reads it)


def body(s):
    print(__doc__, flush=True)
    return R.body(s)


if __name__ == "__main__":
    st = K.Stage(R.BASE["vi"], R.BASE["md5"], "scratch_c116b_bed", preload=False, deadline_min=40,
                 out_json=os.path.join(K.BENCH, "diag_c116b_scratch.json"), task="card 116-2 P4 scratch")
    rc = K.run(body, st)
    gone = R.DRY or SX.kill_labview_at_exit()
    if rc == 0 and gone and not R.DRY:
        os.makedirs(REC, exist_ok=True)
        fn = "stagexec.op_delete_object_looptunnel"
        json.dump({"function": fn, "status": "PASS", "t": time.time(), "card": "116-2 P4",
                   "op": "stagexec delete_wire + delete_object (LoopTunnel) -> stagekit.delete_wire / delete_object",
                   "fixture": "scratch byte copy of claudeDev\\D1_l2_r1_20260928_055441.vi (saved for the Error List read, then deleted)",
                   "plan": {"path": os.path.relpath(PLAN, K.ROOT), "md5": K.md5(PLAN)},
                   "recipe": {"path": "tools/recipes/stage_d1_l2r2.py", "md5": K.md5(R.__file__)},
                   "facts": st.R.get("l2r2"), "log": "tools/bench/diag_c116b_scratch.log"},
                  open(os.path.join(REC, "{0}_{1}.json".format(fn, st.stamp)), "w", encoding="utf-8"), indent=1, default=str)
    sys.exit(rc if gone else 1)
