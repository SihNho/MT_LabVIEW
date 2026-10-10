# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_160-c3-3.json
# ---
r"""prep_c160_c3_3_hash - card 160-c3-3 (OFFLINE, bytes only): md5 of four claudeDev ring VIs, compared with their pins.
Reads the files with hashlib only; never opens them in LabVIEW. Existing: prep_c160_c3_1_md5.py also pins these VIs (inside a 14-file list);
this card asks for one small separate script, so it calls the shared md5 / Gate from prep_c156_a1_1_lib.
PREDICTION CONTRACT: H each VI's md5 starts with its pin (4/4).
    py tools/bgrun.py --material --max-min 1 --log tools/bench/prep_c160_c3_3_hash.log -- py -u tools/bench/prep_c160_c3_3_hash.py"""
import os, sys                                                                              # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import prep_c156_a1_1_lib as L                                                              # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
PINS = [("D1_ring_p4s09_20261009_060515.vi", "eb1d0f31"), ("D1_ring_p5s01a_20261009_101219.vi", "2482fe7b"),
        ("D1_ring_p5s01_20261009_124542.vi", "7f2582ae"), ("D1_ring_p5s02a_20261010_023239.vi", "94ffff94")]
gate = L.Gate(fatal_default=False)
for name, pin in PINS:
    m = L.md5(os.path.join(CD, name))
    gate("H {0} md5 {1} vs pin {2}".format(name, m, pin), m.startswith(pin), "equal" if m.startswith(pin) else "UNEQUAL")
sys.exit(gate.result([]))
