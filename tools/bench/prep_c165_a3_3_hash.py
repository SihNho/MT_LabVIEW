# ---
# labview: none
# hardware: none
# offline-args: pre
# evidence: tools/bench/cards/brief_165-3-3.md
# ---
r"""prep_c165_a3_3_hash - card 165-3-3 step 1 / step 6 (OFFLINE, file reads only, bytes only; the VI is never opened).
pre : md5 of every card input == its pin (task_165-3-3.json) + VI claudeDev\D1_ring_p5s02d_20261010_152518.vi 6dcd5c3d + stagexec 1d5309f4.
post: the brief's UNCHANGED list (prep_c164_a2_3_lib.unchanged, called) + md5 of every output of this card.
PREDICTION (pre): 34 inputs equal + VI + stagexec -> 36/0. (post): U PASS.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c165_a3_3_hash.log -- py -u tools/bench/prep_c165_a3_3_hash.py pre"""
import os, sys                                                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep_c164_a2_3_lib as LB                                                             # noqa: E402
L, B, T, ROOT, md5, J = LB.L, LB.B, LB.T, LB.ROOT, LB.md5, LB.J
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
VI = os.path.join(CD, "D1_ring_p5s02d_20261010_152518.vi")
MODE = (sys.argv[1:] or ["pre"])[0]
if MODE == "pre":
    gate = L.Gate(fatal_default=False)
    for i in J(os.path.join(B, "cards", "task_165-3-3.json"))["inputs"]:
        h = md5(os.path.join(ROOT, i["path"]))
        gate("M {0} md5 {1} == pin {2}".format(i["path"], h, i["md5"][:8]), h == i["md5"], h)
    h = md5(VI)
    gate("M VI {0} md5 {1} == 6dcd5c3d".format(os.path.basename(VI), h), h.startswith("6dcd5c3d"), h)
    h = md5(os.path.join(T, "stagexec.py"))
    gate("M stagexec.py md5 {0} == 1d5309f4".format(h), h.startswith("1d5309f4"), h)
    sys.exit(gate.result())
PINS = {os.path.join(T, "stagexec.py"): "1d5309f4", os.path.join(T, "stagesim.py"): "95a162ba", os.path.join(T, "stagekit.py"): "dd57c1ca",
        os.path.join(T, "stage_prerun.py"): "7605116f", os.path.join(T, "stage_shared.py"): "b688edd4", os.path.join(B, "memory_model.json"): "ff0fabca",
        os.path.join(B, "plan_ring_p5s02e.json"): "fd23974e", os.path.join(B, "plan_ring_p5s02r_in.json"): "0b895983",
        os.path.join(B, "graph_ring_p5s02d_20261010_154830.json"): "2a5fa0c4",
        os.path.join(B, "errorlist_expected_D1_ring_p5s02d_20261010_152518.json"): "c74200f2",
        VI: "6dcd5c3d", os.path.join(CD, "D1_ring_p5s02c_20261010_125755.vi"): "564d8cbe", os.path.join(CD, "D1_ring_p5s02b_20261010_105511.vi"): "f9ae7751",
        os.path.join(CD, "D1_ring_p5s02a_20261010_023239.vi"): "94ffff94", os.path.join(CD, "D1_ring_p5s01b_20261009_123319.vi"): "7f2582ae",
        os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi"): "eb1d0f31"}
OUTS = [os.path.join(B, x) for x in ("plan_ring_p5s02e_pred.json", "plan_ring_p5s02e_licence.json", "errorlist_predicted_D1_ring_p5s02e_end.json",
                                     "prep_c165_a3_3_sg.json")] \
    + [os.path.join(ROOT, "tools", "recipes", x) for x in ("stage_d1_ring_p5s02e.py", "stage_d1_ring_p5s02e_scratch.py")]
sys.exit(LB.unchanged(PINS, [p for p in OUTS if os.path.exists(p)]))
