r"""stage_d1_ring_p2b_scratch - card 122-6: SCRATCH VERIFY of RING P2b BEFORE the one launch (PD244(d): this run IS the end-to-end
verification of the route "valued donor constant -> NEW labelled indicator" on FS1 frame #4866 with all five objects). Runs the stage recipe's
OWN body (tools/recipes/stage_d1_ring_p2b.py, imported unchanged) on a dated byte copy claudeDev\scratch_c122_p2b_<ts>.vi of the P2a bed
(md5 c22a473f) - same Executor, LVBackend and every recipe gate (G/P/T/V/F per label). No VI is run; the bed is never opened for edit.
MODE (argv[1]):
  nosave : SAVE off - structural verification only, NO GUI; the work copy is dropped by the Stage hygiene.
  pin    : SAVE on (rule-6 gui_save of the SCRATCH) so stage_d1_ring_p2b_el.py scratch can pin its Error List (that script deletes it). NEEDS flags.gui.
PRIOR ART: tools/bench/stage_d1_ring_p2a_scratch.py (card 121-2; this is its cut).
PREDICTION: every recipe gate PASS (PS only in pin mode); LabVIEW gone; PASS writes tools/bench/scratch_verify/stagexec.ring_p2b_constind_<mode>_<ts>.json
and gscript.const_indicator_on_diagram_c122_<ts>.json (the route record PD244(d) asks for).
    py tools/bgrun.py --material --max-min 30 --log tools/bench/stage_d1_ring_p2b_scratch_pin.log -- py -u tools/bench/stage_d1_ring_p2b_scratch.py pin"""
import json, os, sys, time                                                          # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recipes"))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_d1_ring_p2b as R                                                       # noqa: E402
REC = os.path.join(K.BENCH, "scratch_verify")
PLAN = os.path.join(K.BENCH, "plan_ring_p2b.json")                                  # the recipe's plan (stage_prerun.plan_files reads it)
MODE = "pin" if "pin" in sys.argv[1:] else "nosave"                                # stage_prerun passes its own flags in argv
R.SAVE = MODE == "pin"


def body(s):
    print(__doc__, flush=True)
    print("MODE {0} (SAVE {1})".format(MODE, R.SAVE), flush=True)
    return R.body(s)


if __name__ == "__main__":
    st = K.Stage(R.BASE["vi"], R.BASE["md5"], "scratch_c122_p2b", preload=False, deadline_min=25,
                 out_json=os.path.join(K.BENCH, "stage_d1_ring_p2b_scratch_{0}.json".format(MODE)), task="card 122-6 scratch " + MODE)
    rc = K.run(body, st)
    gone = R.DRY or SX.kill_labview_at_exit()
    if rc == 0 and gone and not R.DRY:
        os.makedirs(REC, exist_ok=True)
        common = {"status": "PASS", "t": time.time(), "card": "122-6", "mode": MODE, "frame_diagram": R.FRAME,
                  "fixture": "scratch byte copy of " + R.BASE["vi"] + (" (saved for the Error List read, then deleted)" if R.SAVE else " (not saved)"),
                  "plan": {"path": os.path.relpath(PLAN, K.ROOT), "md5": K.md5(PLAN)},
                  "recipe": {"path": "tools/recipes/stage_d1_ring_p2b.py", "md5": K.md5(R.__file__)},
                  "donor": R.PRED["donor"], "facts": st.R.get("ring_p2b"), "log": "tools/bench/stage_d1_ring_p2b_scratch_{0}.log".format(MODE)}
        for fn, opd in (("stagexec.ring_p2b_constind_" + MODE, "stagexec create primitive const_donor x5 + create indicator born_on constant x5 -> the RING P2b recipe"),
                        ("gscript.const_indicator_on_diagram_c122", "create_primitive_nested(const_donor) + create_indicator_on_const on FS frame #4866, 5 labels")):
            json.dump(dict(common, function=fn.split("_c122")[0], op=opd), open(os.path.join(REC, "{0}_{1}.json".format(fn, st.stamp)), "w", encoding="utf-8"),
                      indent=1, default=str)
    sys.exit(rc if gone else 1)
