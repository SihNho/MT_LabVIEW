# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_170-a2-2.md
# ---
r"""diag_c170_a2_2_hygiene - card 170-a2-2 brief step 4: end-of-card checks. Offline, no LabVIEW call.
Found before writing (CALLED): prep_c156_a1_1_lib.Gate / .md5 (as diag_c170_a2_1_cal.py uses them); pins as in diag_c170_a2_1_hash.log:5,8,9.
PREDICTION: P1-P3 the three pinned VIs hash unchanged; J p6_replay_facts.json parses with f4 carrying layout of 9. (Process check: plain tasklist, outside this script.)
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c170_a2_2_hygiene.log -- py -u tools/bench/diag_c170_a2_2_hygiene.py"""
import json, os, sys                                                           # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
for _p in (ROOT, os.path.join(ROOT, "tools"), HERE):
    _p in sys.path or sys.path.insert(0, _p)                                                 # noqa: E701
import prep_c156_a1_1_lib as L                                                               # noqa: E402

CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
PINS = {"D1_ring_p6_20261012_212645.vi": "c2d9c13c", "D1_s1_copy.vi": "3e3d23ce", r"replay\D1_s1_replay_20260925_075422.vi": "126f8497"}
gate = L.Gate(fatal_default=False)
for name, pin in PINS.items():
    m = L.md5(os.path.join(CD, name))
    gate("P %s md5 starts with pin %s" % (name, pin), m.startswith(pin), m)
d = json.load(open(os.path.join(HERE, "p6_replay_facts.json"), encoding="utf-8"))
gate("J p6_replay_facts.json parses; f4 layout has 9 elements, element 6 'Date and time'",
     len(d["f4"]["layout"]) == 9 and d["f4"]["layout"][6]["label"] == "Date and time", d["f4"]["verdict"])
sys.exit(gate.result([{"path": "tools/bench/p6_replay_facts.json", "md5": L.md5(os.path.join(HERE, "p6_replay_facts.json"))},
                      {"path": "tools/bench/p6_replay_facts.md", "md5": L.md5(os.path.join(HERE, "p6_replay_facts.md"))}]))
