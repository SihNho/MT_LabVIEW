# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_160-c3-1.json
# ---
r"""prep_c160_c3_1_md5 - card 160-c3-1 (OFFLINE, read-only): the md5-UNCHANGED pass item - tools (stagesim 95a162ba, stagexec ddf23a31, stagekit
1441bb4c, stage_prerun 7605116f), plan f4520b10, in / in2, graph 7ac24924, the 56-row expected file 1fd016bf, the b3-1 session e5279899, VIs s09
eb1d0f31 / P5-1a 2482fe7b / P5-1 7f2582ae / 94ffff94 - and prints the md5 of every output. Gate / md5 from prep_c156_a1_1_lib.
PREDICTION CONTRACT: U every pinned file's md5 starts with its pin.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c160_c3_1_md5.log -- py -u tools/bench/prep_c160_c3_1_md5.py"""
import os, sys                                                                              # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import prep_c156_a1_1_lib as L                                                              # noqa: E402
B, T, CD = os.path.join(ROOT, "tools", "bench"), os.path.join(ROOT, "tools"), r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
PINS = {os.path.join(T, "stagesim.py"): "95a162ba", os.path.join(T, "stagexec.py"): "a4df7e15", os.path.join(T, "stagekit.py"): "9b8f82c1",
        os.path.join(T, "stage_prerun.py"): "7605116f", os.path.join(B, "plan_ring_p5s02b.json"): "f4520b10", os.path.join(B, "plan_ring_p5s02b_in.json"): "56bfddd3",
        os.path.join(B, "plan_ring_p5s02b_in2.json"): "927b805c", os.path.join(B, "graph_ring_p5s02a_20261010_032547.json"): "7ac24924",
        os.path.join(B, "errorlist_expected_D1_ring_p5s02a_20261010_023239.json"): "1fd016bf", os.path.join(B, "prep_c160_b3_1_session.json"): "e5279899",
        os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi"): "eb1d0f31", os.path.join(CD, "D1_ring_p5s01a_20261009_101219.vi"): "2482fe7b",
        os.path.join(CD, "D1_ring_p5s01_20261009_124542.vi"): "7f2582ae", os.path.join(CD, "D1_ring_p5s02a_20261010_023239.vi"): "94ffff94"}
OUTS = [os.path.join(B, x) for x in ("plan_ring_p5s02b_pred.json", "plan_ring_p5s02b_licence.json", "errorlist_predicted_D1_ring_p5s02b_end.json",
                                     "prep_c160_c3_1_session.json")] + [os.path.join(ROOT, "tools", "recipes", x) for x in ("stage_d1_ring_p5s02b.py", "stage_d1_ring_p5s02b_scratch.py")]
gate = L.Gate(fatal_default=False)
got = dict((p, L.md5(p)) for p in PINS)
for p in PINS:
    print("FACT PIN {0} {1} (pin {2})".format(os.path.basename(p), got[p], PINS[p]), flush=True)
gate("U {0} pinned files unchanged".format(len(PINS)), all(got[p].startswith(w) for p, w in PINS.items()),
     [os.path.basename(p) for p, w in PINS.items() if not got[p].startswith(w)])
for p in OUTS:
    print("FACT OUT {0} {1}".format(L.rel(p), L.md5(p)), flush=True)
sys.exit(gate.result([{"path": L.rel(p), "md5": L.md5(p)} for p in OUTS]))
