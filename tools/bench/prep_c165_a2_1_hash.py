# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_165-2-1.md
# ---
r"""prep_c165_a2_1_hash - card 165-2-1 part 1 (OFFLINE, file reads only): md5 of every card input (pins from task_165-2-1.json) plus the VI
claudeDev\D1_ring_p5s02d_20261010_152518.vi (bytes only, never opened in LabVIEW).
PREDICTION: every md5 equals its card pin; VI 6dcd5c3d; judgement-time values stagexec 6ea6637f, r_in 0b895983, graph 2a5fa0c4, EL c74200f2,
memory_model ff0fabca, stagekit dd57c1ca, stagesim 95a162ba, stage_prerun 7605116f all equal. 23 PASS / 0 FAIL.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c165_a2_1_hash.log -- py -u tools/bench/prep_c165_a2_1_hash.py"""
import os, sys                                                                                # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, B)
import prep_c156_a1_1_lib as L                                                               # noqa: E402
ROOT, md5, J = L.ROOT, L.md5, L.J
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
WANT = [(os.path.normpath(os.path.join(ROOT, i["path"])), i["md5"]) for i in J("tools/bench/cards/task_165-2-1.json")["inputs"]]
WANT.append((os.path.join(CD, "D1_ring_p5s02d_20261010_152518.vi"), "6dcd5c3d"))
gate = L.Gate(fatal_default=False)
for p, w in WANT:
    h = md5(p)
    gate("M {0} md5 {1} == pin {2}".format(os.path.relpath(p, ROOT) if p.startswith(ROOT) else p, h, w[:8]), h.startswith(w[:8]) and (len(w) < 32 or h == w), h)
sys.exit(gate.result())
