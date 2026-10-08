# ---
# labview: none
# hardware: none
# ---
"""Card 153-a2-1 invariant md5 check (offline, hashes files only; re-cut of diag_c153_a1_1_md5.py with
stagesim pinned at 78b8d5a1 per PD371(e) and the original + its census added).
Prediction: every file hashes to its pinned prefix; RESULT pass 13 fail 0."""
import hashlib, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
PINS = [
    ("604529e8", "tools/stagekit.py"), ("207beb0d", "tools/addrcheck.py"), ("1bab9cf9", "tools/stagexec.py"),
    ("1a80236e", "tools/gscript.py"), ("c739eb86", "tools/stage_prerun.py"), ("78b8d5a1", "tools/stagesim.py"),
    ("13be0847", "tools/vigraph.py"), ("eb1d0f31", os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi")),
    ("22f967b5", "tools/bench/graph_ring_p4s09_20261009_062044.json"), ("6f2b5687", "tools/bench/memory_model.json"),
    ("c39f36e0", os.path.join(os.path.dirname(ROOT), "Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi")),
    ("b9e6849f", "tools/bench/orig_3state_nodeterms.json"), ("3e3d23ce", "docs/wiki/subvi/D1_s1_copy.json"),
]
ok = 0
first = None
for pin, p in PINS:
    full = p if os.path.isabs(p) else os.path.join(ROOT, p)
    h = hashlib.md5(open(full, "rb").read()).hexdigest()
    good = h.startswith(pin)
    ok += good
    if not good and first is None:
        first = p
    print("OK  " if good else "FAIL", h, pin, p)
print(protocol.result_line({"status": "PASS" if first is None else "FAIL",
                            "gates": {"pass": ok, "fail": len(PINS) - ok}, "first_fail": first, "artefacts": []}))
