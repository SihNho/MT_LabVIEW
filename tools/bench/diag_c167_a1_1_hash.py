# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_167-a1-1.json
# ---
r"""diag_c167_a1_1_hash - card 167-a1-1 (OFFLINE, bytes only, hashlib). Found before writing: diag_c166_a1_1_hash.py (same job for
card 166-a1-1, a script that runs at import, so not importable as a function); this script CALLS the same shared functions
(protocol.input_md5_changes, prep_c156_a1_1_lib.md5 / Gate) with this card and the same seven VI pins (data, not logic).
argv[1] = before | after (same checks both times: this card writes none of its pinned inputs).
PREDICTION CONTRACT: every card input equal (13), the 7 VI pins equal.
    py tools/bgrun.py --material --max-min 1 --log tools/bench/diag_c167_a1_1_hash_<mode>.log -- py -u tools/bench/diag_c167_a1_1_hash.py <mode>"""
import json, os, sys                                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import protocol as PR                                                                       # noqa: E402
import prep_c156_a1_1_lib as L                                                              # noqa: E402
MODE = sys.argv[1] if len(sys.argv) > 1 else "before"
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
CARD = os.path.join(ROOT, "tools", "bench", "cards", "task_167-a1-1.json")
VIS = [("D1_ring_p5_20261010_172913.vi", "75773b0d"), ("D1_ring_p5s01_20261009_124542.vi", "7f2582ae"),
       ("D1_ring_p4s09_20261009_060515.vi", "eb1d0f31"), ("D1_ring_p5s02a_20261010_023239.vi", "94ffff94"),
       ("D1_ring_p5s02b_20261010_105511.vi", "f9ae7751"), ("D1_ring_p5s02c_20261010_125755.vi", "564d8cbe"),
       ("D1_ring_p5s02d_20261010_152518.vi", "6dcd5c3d")]
gate = L.Gate(fatal_default=False)
card = json.load(open(CARD, encoding="utf-8"))
bad = PR.input_md5_changes(card)
gate("I {0} md5-pinned card inputs equal ({1})".format(len(card["inputs"]), MODE), not bad, bad or "all equal")
for name, pin in VIS:
    m = L.md5(os.path.join(CD, name))
    gate("H {0} md5 {1} vs pin {2}".format(name, m, pin), m.startswith(pin), "equal" if m.startswith(pin) else "UNEQUAL")
sys.exit(gate.result([]))
