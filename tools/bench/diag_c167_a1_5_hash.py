# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_167-a1-5.json
# ---
r"""diag_c167_a1_5_hash - card 167-a1-5 (OFFLINE, bytes only, hashlib). Found before writing: diag_c166_a1_1_hash.py (same job, card
166-a1-1); this script CALLS the same shared functions (protocol.input_md5_changes, prep_c156_a1_1_lib.md5 / Gate) and copies only its
seven-VI name list (brief_167-a1-5.md:29). No logic of its own.
argv[1] = before | after. 'after' drops the card inputs this card is allowed to edit (stagekit.py, selftest_c147_b1_2.py,
errorlist_check.py) from the pinned inputs and prints their md5 as FACT.
PREDICTION CONTRACT: before: every card input equal, 7 VI pins equal. after: same, except the named editable files.
    py tools/bgrun.py --material --max-min 1 --log tools/bench/diag_c167_a1_5_hash_<mode>.log -- py -u tools/bench/diag_c167_a1_5_hash.py <mode>"""
import json, os, sys                                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import protocol as PR                                                                       # noqa: E402
import prep_c156_a1_1_lib as L                                                              # noqa: E402
MODE = sys.argv[1] if len(sys.argv) > 1 else "before"
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
CARD = os.path.join(ROOT, "tools", "bench", "cards", "task_167-a1-5.json")
MUTABLE = ("tools/stagekit.py", "tools/errorlist_check.py", "tools/bench/selftest_c147_b1_2.py")
VIS = [("D1_ring_p5_20261010_172913.vi", "75773b0d"), ("D1_ring_p5s01_20261009_124542.vi", "7f2582ae"),
       ("D1_ring_p4s09_20261009_060515.vi", "eb1d0f31"), ("D1_ring_p5s02a_20261010_023239.vi", "94ffff94"),
       ("D1_ring_p5s02b_20261010_105511.vi", "f9ae7751"), ("D1_ring_p5s02c_20261010_125755.vi", "564d8cbe"),
       ("D1_ring_p5s02d_20261010_152518.vi", "6dcd5c3d")]
gate = L.Gate(fatal_default=False)
card = json.load(open(CARD, encoding="utf-8"))
if MODE == "after":
    card["inputs"] = [i for i in card["inputs"] if i["path"] not in MUTABLE]
bad = PR.input_md5_changes(card)
gate("I {0} md5-pinned card inputs equal in the main tree".format(len(card["inputs"])), not bad, bad or "all equal")
for p in MUTABLE:
    print("FACT {0} md5 {1}".format(p, L.md5(os.path.join(ROOT, p))), flush=True)
for name, pin in VIS:
    m = L.md5(os.path.join(CD, name))
    gate("H {0} md5 {1} vs pin {2}".format(name, m, pin), m.startswith(pin), "equal" if m.startswith(pin) else "UNEQUAL")
sys.exit(gate.result([]))
