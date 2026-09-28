r"""stage_d1_ring_p2a_scratch - card 121-2: SCRATCH VERIFY of RING P2a BEFORE the one launch. Runs the stage recipe's OWN body
(tools/recipes/stage_d1_ring_p2a.py, imported unchanged) on a dated byte copy claudeDev\scratch_c121_p2a_<ts>.vi of the pool bed (md5 93539368) -
same Executor, LVBackend, RetireGuardBE and every recipe gate. No VI is run; the bed is never opened for edit (byte copy only).
MODE (argv[1]):
  nosave : SAVE off - structural verification only, NO GUI (no rule-6 save); the work copy is dropped by the Stage hygiene.
  pin    : SAVE on (rule-6 gui_save of the SCRATCH) so stage_d1_ring_p2a_el.py scratch can pin its Error List (that script deletes it). NEEDS flags.gui.
PRIOR ART: tools/bench/stage_d1_qrt_pool_scratch.py (card 119-4; this is its cut, + the nosave mode).
PREDICTION: every recipe gate PASS (PS only in pin mode); LabVIEW gone; PASS writes tools/bench/scratch_verify/stagexec.ring_p2a_deletes_<mode>_<ts>.json.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/stage_d1_ring_p2a_scratch_nosave.log -- py -u tools/bench/stage_d1_ring_p2a_scratch.py nosave"""
import json, os, sys, time                                                          # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recipes"))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_d1_ring_p2a as R                                                       # noqa: E402
REC = os.path.join(K.BENCH, "scratch_verify")
PLAN = os.path.join(K.BENCH, "plan_ring_p2a.json")                                  # the recipe's plan (stage_prerun.plan_files reads it)
MODE = "pin" if "pin" in sys.argv[1:] else "nosave"                                # stage_prerun passes its own flags in argv
R.SAVE = MODE == "pin"


def body(s):
    print(__doc__, flush=True)
    print("MODE {0} (SAVE {1})".format(MODE, R.SAVE), flush=True)
    return R.body(s)


if __name__ == "__main__":
    st = K.Stage(R.BASE["vi"], R.BASE["md5"], "scratch_c121_p2a", preload=False, deadline_min=25,
                 out_json=os.path.join(K.BENCH, "stage_d1_ring_p2a_scratch_{0}.json".format(MODE)), task="card 121-2 scratch " + MODE)
    rc = K.run(body, st)
    gone = R.DRY or SX.kill_labview_at_exit()
    if rc == 0 and gone and not R.DRY:
        os.makedirs(REC, exist_ok=True)
        fn = "stagexec.ring_p2a_deletes_" + MODE
        json.dump({"function": fn, "status": "PASS", "t": time.time(), "card": "121-2", "mode": MODE,
                   "op": "stagexec delete_wire x4 + delete_object x4 (RetireGuardBE) -> the RING P2a recipe",
                   "fixture": "scratch byte copy of " + R.BASE["vi"] + (" (saved for the Error List read, then deleted)" if R.SAVE else " (not saved)"),
                   "plan": {"path": os.path.relpath(PLAN, K.ROOT), "md5": K.md5(PLAN)},
                   "recipe": {"path": "tools/recipes/stage_d1_ring_p2a.py", "md5": K.md5(R.__file__)},
                   "facts": st.R.get("ring_p2a"), "log": "tools/bench/stage_d1_ring_p2a_scratch_{0}.log".format(MODE)},
                  open(os.path.join(REC, "{0}_{1}.json".format(fn, st.stamp)), "w", encoding="utf-8"), indent=1, default=str)
    sys.exit(rc if gone else 1)
