# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-a2-3.md
# ---
r"""prep_c164_a2_3_md5 - card 164-a2-3 (OFFLINE, read-only): the md5-UNCHANGED pass item (brief_164-a2-3.md:46-47) and the md5 of every output.
Inputs only; the check is prep_c164_a2_3_lib.unchanged. PREDICTION CONTRACT: U every pinned file's md5 starts with its pin.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c164_a2_3_md5.log -- py -u tools/bench/prep_c164_a2_3_md5.py"""
import os, sys                                                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep_c164_a2_3_lib as LB                                                             # noqa: E402
B, T, ROOT = LB.B, LB.T, LB.ROOT
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
PINS = {os.path.join(T, "stagesim.py"): "95a162ba", os.path.join(T, "stagexec.py"): "a4df7e15", os.path.join(T, "stagekit.py"): "dd57c1ca",
        os.path.join(T, "stage_prerun.py"): "7605116f", os.path.join(T, "stage_shared.py"): "b688edd4", os.path.join(B, "memory_model.json"): "8fb432e4",
        os.path.join(B, "plan_ring_p5s02d.json"): "872822f3", os.path.join(B, "graph_ring_p5s02c_20261010_131658.json"): "3d5196ab",
        os.path.join(B, "errorlist_expected_D1_ring_p5s02c_20261010_125755.json"): "26d45c71",
        os.path.join(CD, "D1_ring_p5s02c_20261010_125755.vi"): "564d8cbe", os.path.join(CD, "D1_ring_p5s02b_20261010_105511.vi"): "f9ae7751",
        os.path.join(CD, "D1_ring_p5s02a_20261010_023239.vi"): "94ffff94", os.path.join(CD, "D1_ring_p5s01_20261009_124542.vi"): "7f2582ae",
        os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi"): "eb1d0f31"}
OUTS = [os.path.join(B, x) for x in ("plan_ring_p5s02d_pred.json", "plan_ring_p5s02d_licence.json", "errorlist_predicted_D1_ring_p5s02d_end.json",
                                     "prep_c164_a2_3_session.json")] + [os.path.join(ROOT, "tools", "recipes", x) for x in ("stage_d1_ring_p5s02d.py", "stage_d1_ring_p5s02d_scratch.py")]
sys.exit(LB.unchanged(PINS, OUTS))
