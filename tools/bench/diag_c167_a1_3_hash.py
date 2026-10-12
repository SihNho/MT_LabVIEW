# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_167-a1-3.json
# ---
r"""diag_c167_a1_3_hash - card 167-a1-3 (OFFLINE, bytes only, hashlib): the card inputs and the seven VIs hashed, before / after.
Found before writing: diag_c167_a1_1_hash.py (same job for card 167-a1-1, runs at import with its card hard-coded, so not callable);
this file CALLS the same shared functions (protocol.input_md5_changes, prep_c156_a1_1_lib.md5 / Gate) and holds the same seven VI pins
(data, not logic) as an importable check(), which diag_c167_a1_3_closure.py also calls at its start and end.
PREDICTION CONTRACT: every card input equal (13), the 7 VI pins equal, no LabVIEW process (tasklist).
    py tools/bgrun.py --material --max-min 1 --log tools/bench/diag_c167_a1_3_hash_<mode>.log -- py -u tools/bench/diag_c167_a1_3_hash.py <mode>"""
import json, os, subprocess, sys                                                            # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import protocol as PR                                                                       # noqa: E402
import prep_c156_a1_1_lib as L                                                              # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
CARD = os.path.join(ROOT, "tools", "bench", "cards", "task_167-a1-3.json")
VIS = [("D1_ring_p5_20261010_172913.vi", "75773b0d"), ("D1_ring_p5s01_20261009_124542.vi", "7f2582ae"),
       ("D1_ring_p4s09_20261009_060515.vi", "eb1d0f31"), ("D1_ring_p5s02a_20261010_023239.vi", "94ffff94"),
       ("D1_ring_p5s02b_20261010_105511.vi", "f9ae7751"), ("D1_ring_p5s02c_20261010_125755.vi", "564d8cbe"),
       ("D1_ring_p5s02d_20261010_152518.vi", "6dcd5c3d")]


def check(gate, mode):
    """Gates I (card inputs at their md5), H x7 (VI pins), T (no LabVIEW process) on `gate` (a prep_c156_a1_1_lib.Gate). Returns
    {inputs_bad, vis{name: md5}, labview_running}."""
    card = json.load(open(CARD, encoding="utf-8"))
    bad = PR.input_md5_changes(card)
    gate("I {0} md5-pinned card inputs equal ({1})".format(len(card["inputs"]), mode), not bad, bad or "all equal")
    vis = {}
    for name, pin in VIS:
        m = vis[name] = L.md5(os.path.join(CD, name))
        gate("H {0} md5 {1} vs pin {2} ({3})".format(name, m, pin, mode), m.startswith(pin), "equal" if m.startswith(pin) else "UNEQUAL")
    run = ("lab" + "view") in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()
    gate("T no LabVIEW process in tasklist ({0})".format(mode), not run, "none" if not run else "RUNNING")
    return {"inputs_bad": bad, "vis": vis, "labview_running": run}


if __name__ == "__main__":
    g = L.Gate(fatal_default=False)
    check(g, sys.argv[1] if len(sys.argv) > 1 else "before")
    sys.exit(g.result([]))
