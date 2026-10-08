# ---
# labview: none
# hardware: none
# ---
"""card 152-b1-3 step 6: pin md5 check after the edit (offline hashlib only, no LabVIEW).
PRIOR ART: the same pin list as diag_c152_b1_2_cross.py:24-30; this re-hashes without stagekit (no LabVIEW import).
PREDICTION: every pinned file equals its brief md5 prefix; only stagesim / naming table / naming selftest differ (edited)."""
import hashlib, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(HERE, "..")
sys.path.insert(0, T)
import protocol
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
PIN = [("stagekit", os.path.join(T, "stagekit.py"), "604529e8"), ("addrcheck", os.path.join(T, "addrcheck.py"), "207beb0d"),
       ("stagexec", os.path.join(T, "stagexec.py"), "1bab9cf9"), ("gscript", os.path.join(T, "gscript.py"), "1a80236e"),
       ("stage_prerun", os.path.join(T, "stage_prerun.py"), "c739eb86"), ("vigraph", os.path.join(T, "vigraph.py"), "13be0847"),
       ("memory_model", os.path.join(HERE, "memory_model.json"), "a28b6dd7"),
       ("s08", os.path.join(CD, "D1_ring_p4s08_20261009_031503.vi"), "f99e8414"),
       ("graph", os.path.join(HERE, "graph_ring_p4s08_20261009_033522.json"), "44858dbf"),
       ("derived", os.path.join(HERE, "graph_ring_p4s08_20261009_033522_fsowner.json"), "e26b4d90"),
       ("fsowner_selftest", os.path.join(HERE, "selftest_c152_fsowner.py"), "64918ff7"),
       ("owners_selftest", os.path.join(HERE, "selftest_c134_4_owners.py"), "2d04ba97")]
gates = []
for k, p, want in PIN:
    got = hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "MISSING"
    gates.append((k, got.startswith(want)))
    print("  {0}  PIN {1} {2} (want {3})".format("PASS" if got.startswith(want) else "FAIL", k, got, want))
n_pass = sum(1 for _k, ok in gates if ok)
first = next((k for k, ok in gates if not ok), None)
print("=== GATES: {0} pass / {1} fail".format(n_pass, len(gates) - n_pass))
print(protocol.result_line(protocol.make_result(n_pass, len(gates) - n_pass, first)))
