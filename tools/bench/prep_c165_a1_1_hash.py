# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_165-1-1.json
# ---
"""Card 165-1-1 step 1: md5 of the card inputs (file reads only; the VI is hashed as bytes, never opened in LabVIEW).

Prediction contract: VI D1_ring_p5s02d_20261010_152518.vi 6dcd5c3d, graph 2a5fa0c4, EL expected c74200f2, memory_model ff0fabca,
step-4 scratch log 388a86d3 (the binding record: its STEPX 'bound' lines), scratch JSON printed. r_in printed (9dadb0c1 before the
edit, 0b895983 after). Each pinned prefix compared."""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
F = [(os.path.join(CD, "D1_ring_p5s02d_20261010_152518.vi"), "6dcd5c3d"),
     (os.path.join(HERE, "graph_ring_p5s02d_20261010_154830.json"), "2a5fa0c4"),
     (os.path.join(HERE, "errorlist_expected_D1_ring_p5s02d_20261010_152518.json"), "c74200f2"),
     (os.path.join(HERE, "memory_model.json"), "ff0fabca"),
     (os.path.join(HERE, "diag_c164_p5s02d_scratch.log"), "388a86d3"),
     (os.path.join(HERE, "diag_c164_p5s02d_scratch.json"), None),
     (os.path.join(HERE, "plan_ring_p5s02r_in.json"), None),
     (os.path.join(ROOT, "tools", "stagexec.py"), None),
     (os.path.join(ROOT, "tools", "stagesim.py"), "95a162ba"),
     (os.path.join(ROOT, "tools", "stagekit.py"), "dd57c1ca")]
G = [0, 0, None]
for p, pin in F:
    h = hashlib.md5(open(p, "rb").read()).hexdigest()
    ok = pin is None or h.startswith(pin)
    G[0 if ok else 1] += 1
    if not ok and G[2] is None:
        G[2] = os.path.basename(p)
    print("  {0}  {1} md5 {2}{3}".format("PASS" if ok else "FAIL", p, h, "" if pin is None else " (pin " + pin + ")"), flush=True)
print(protocol.result_line(protocol.make_result(G[0], G[1], G[2], [])), flush=True)
sys.exit(1 if G[1] else 0)
