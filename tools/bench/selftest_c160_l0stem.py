# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_160-e4-1.md
# ---
r"""selftest_c160_l0stem - card 160-e4-1 (gate-fp fp-82, OFFLINE): stagekit.plan_in_matches_stem, the predicate RingSession.gate_l0
calls for its 'plan_in = <stem>_in[N]' clause. Accepts exactly <stem>_in and <stem>_in<digits> (basename, extension dropped);
refuses every looser form. Also replays the finalized.plan_in of the stored p5s01a / p5s01b / p5s02a / p5s02b plans.
PREDICTION CONTRACT: A 3/3 accepted, R 7/7 refused, P 4/4 stored plans match their own stem -> 14 pass / 0 fail.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_c160_l0stem_c160_e4_1.log -- py -u tools/bench/selftest_c160_l0stem.py"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagekit as K  # noqa: E402
import protocol  # noqa: E402

G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, info=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, info), flush=True)


ST = "plan_ring_p5s02b"
for p in ("tools/bench/plan_ring_p5s02b_in.json", "tools\\bench\\plan_ring_p5s02b_in2.json", "plan_ring_p5s02b_in12.json"):
    gate("A accepts {0}".format(p), K.plan_in_matches_stem(p, ST) is True)
for p in ("tools/bench/plan_ring_p5s02b_inx.json", "tools/bench/plan_ring_p5s02b_in_2.json", "tools/bench/plan_ring_p5s02b_in2b.json",
          "tools/bench/plan_ring_p5s02a_in.json", "tools/bench/plan_ring_p5s02b.json", "tools/bench/plan_ring_p5s02b_out.json",
          "tools/bench/xplan_ring_p5s02b_in.json"):
    gate("R refuses {0}".format(p), K.plan_in_matches_stem(p, ST) is False)
for st in ("plan_ring_p5s01a", "plan_ring_p5s01b", "plan_ring_p5s02a", "plan_ring_p5s02b"):
    fz = json.load(open(os.path.join(HERE, st + ".json"), encoding="utf-8"))["finalized"]
    gate("P {0} finalized.plan_in matches its stem".format(st), K.plan_in_matches_stem(fz["plan_in"]["path"], st), fz["plan_in"]["path"])
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
