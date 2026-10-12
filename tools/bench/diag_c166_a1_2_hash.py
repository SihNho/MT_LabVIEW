# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_166-a1-2.json
# ---
r"""diag_c166_a1_2_hash - card 166-a1-2 (OFFLINE, bytes only, hashlib; no LabVIEW). Found before writing: diag_c166_a1_1_hash.py (same job for
card 166-a1-1; a module-level script, so it cannot be imported). This script CALLS the same shared functions (protocol.input_md5_changes,
prep_c156_a1_1_lib.md5 / Gate) and copies only the seven-VI pin list (data) from diag_c166_a1_1_hash.py:24-27. No logic of its own except:
argv[1] = before | after. 'after' drops docs/d1/INDEX.md (the one card input this card edits) from the pinned inputs and prints its md5, and
runs the machine key check: errorlist_check.current_bed_text(STATUS.md text) (tools/errorlist_check.py:164, pure; LabVIEW imports are lazy).
PREDICTION CONTRACT: before: every card input equal, 7 VI pins equal. after: same (INDEX excluded), and current_bed_text names
D1_ring_p5_20261010_172913.vi.
    py tools/bgrun.py --material --max-min 1 --log tools/bench/diag_c166_a1_2_hash_<mode>.log -- py -u tools/bench/diag_c166_a1_2_hash.py <mode>"""
import json, os, sys                                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import protocol as PR                                                                       # noqa: E402
import prep_c156_a1_1_lib as L                                                              # noqa: E402
MODE = sys.argv[1] if len(sys.argv) > 1 else "before"
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
CARD = os.path.join(ROOT, "tools", "bench", "cards", "task_166-a1-2.json")
MUTABLE = ("docs/d1/INDEX.md",)
P5 = "D1_ring_p5_20261010_172913.vi"
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
if MODE == "after":
    import errorlist_check as EC                                                            # noqa: E402
    st = os.path.join(ROOT, "STATUS.md")
    print("FACT STATUS.md md5 {0}".format(L.md5(st)), flush=True)
    got = EC.current_bed_text(open(st, encoding="utf-8").read())
    print("FACT current_bed_text(STATUS.md) -> {0!r}".format(got), flush=True)
    gate("K current_bed_text names {0}".format(P5), bool(got) and os.path.basename(got) == P5, got)
    gate("L errorlist_check imported no LabVIEW module (gscript/lv_errorlist not loaded)",
         EC.g is None and "gscript" not in sys.modules and "lv_errorlist" not in sys.modules, sorted(m for m in sys.modules if "gscript" in m))
sys.exit(gate.result([]))
