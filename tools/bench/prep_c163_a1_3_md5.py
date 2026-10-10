# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_163-a1-3.md
# ---
r"""prep_c163_a1_3_md5 - card 163-a1-3 (OFFLINE, read-only): the md5-UNCHANGED pass item - tools (stagesim 95a162ba, stagexec a4df7e15, stagekit
9b8f82c1, stage_prerun 7605116f, stage_shared b688edd4), memory_model def9e640, plan_ring_p5s02c.json 930699ec, graph 431cfd83, the 53-item expected
file 60e02787, VIs f9ae7751 / 94ffff94 / 7f2582ae / eb1d0f31 - and prints the md5 of every output. Gate / md5 from prep_c156_a1_1_lib. Flow of
prep_c160_c3_1_md5.py (names only differ).
PREDICTION CONTRACT: U every pinned file's md5 starts with its pin.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c163_a1_3_md5.log -- py -u tools/bench/prep_c163_a1_3_md5.py"""
import os, sys                                                                              # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import prep_c156_a1_1_lib as L                                                              # noqa: E402
B, T, CD = os.path.join(ROOT, "tools", "bench"), os.path.join(ROOT, "tools"), r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
PINS = {os.path.join(T, "stagesim.py"): "95a162ba", os.path.join(T, "stagexec.py"): "a4df7e15", os.path.join(T, "stagekit.py"): "9b8f82c1",
        os.path.join(T, "stage_prerun.py"): "7605116f", os.path.join(T, "stage_shared.py"): "b688edd4", os.path.join(B, "memory_model.json"): "def9e640",
        os.path.join(B, "plan_ring_p5s02c.json"): "930699ec", os.path.join(B, "graph_ring_p5s02b_20261010_111905.json"): "431cfd83",
        os.path.join(B, "errorlist_expected_D1_ring_p5s02b_20261010_105511.json"): "60e02787",
        os.path.join(CD, "D1_ring_p5s02b_20261010_105511.vi"): "f9ae7751", os.path.join(CD, "D1_ring_p5s02a_20261010_023239.vi"): "94ffff94",
        os.path.join(CD, "D1_ring_p5s01_20261009_124542.vi"): "7f2582ae", os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi"): "eb1d0f31"}
OUTS = [os.path.join(B, x) for x in ("plan_ring_p5s02c_pred.json", "plan_ring_p5s02c_licence.json", "errorlist_predicted_D1_ring_p5s02c_end.json",
                                     "prep_c163_a1_3_session.json")] + [os.path.join(ROOT, "tools", "recipes", x) for x in ("stage_d1_ring_p5s02c.py", "stage_d1_ring_p5s02c_scratch.py")]
gate = L.Gate(fatal_default=False)
got = dict((p, L.md5(p)) for p in PINS)
for p in PINS:
    print("FACT PIN {0} {1} (pin {2})".format(os.path.basename(p), got[p], PINS[p]), flush=True)
gate("U {0} pinned files unchanged".format(len(PINS)), all(got[p].startswith(w) for p, w in PINS.items()),
     [os.path.basename(p) for p, w in PINS.items() if not got[p].startswith(w)])
for p in OUTS:
    print("FACT OUT {0} {1}".format(L.rel(p), L.md5(p)), flush=True)
sys.exit(gate.result([{"path": L.rel(p), "md5": L.md5(p)} for p in OUTS]))
