# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_170-a3-1.md
# ---
"""diag_c170_a3_1_rehash - card 170-a3-1 step 0: re-hash the 11 pinned inputs offline (stagekit.md5, the one shared helper).
PREDICTION: all 11 EQUAL to the brief's 8-hex prefixes; any DRIFT = card BLOCKED before LabVIEW.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c170_a3_1_rehash.log -- py -u tools/bench/diag_c170_a3_1_rehash.py"""
import os, sys                                                                           # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagekit as K                                                                     # noqa: E402
import protocol                                                                          # noqa: E402
C, R = K.CLAUDEDEV, os.path.join(K.CLAUDEDEV, "replay")
ROWS = [("bed", os.path.join(C, "D1_ring_p6_20261012_212645.vi"), "c2d9c13c"),
        ("graph", os.path.join(ROOT, "tools", "bench", "graph_ring_p6_20261012_212645.json"), "fbc7b7ee"),
        ("S1", os.path.join(C, "D1_s1_copy.vi"), "3e3d23ce"),
        ("S1 replay", os.path.join(R, "D1_s1_replay_20260925_075422.vi"), "126f8497"),
        ("get-buff", os.path.join(R, "replay_get_buff_image.vi"), "842ecad9"),
        ("cal", os.path.join(R, "replay_get_image_cal.vi"), "afce0d04"),
        ("buf", os.path.join(R, "replay_imaqdx_get_image_buf.vi"), "a89dafc1"),
        ("frame manifest", os.path.join(ROOT, "tools", "bench", "p6_replay_frames_manifest.txt"), "9055d98a"),
        ("compare", os.path.join(ROOT, "tools", "bench", "m8b_replay_compare.py"), "c2efe10d"),
        ("P5", os.path.join(C, "D1_ring_p5_20261010_172913.vi"), "75773b0d"),
        ("P5-1", os.path.join(C, "D1_ring_p5s01_20261009_124542.vi"), "7f2582ae")]
npass = nfail = 0
first = None
for name, path, want in ROWS:
    got = K.md5(path) if os.path.exists(path) else None
    ok = bool(got) and got.startswith(want)
    npass, nfail = npass + ok, nfail + (not ok)
    first = first or (None if ok else "{0} {1} got {2}".format(name, want, got))
    print("{0} {1:15s} want {2} got {3} {4}".format("PASS" if ok else "FAIL", name, want, got, path))
print(protocol.result_line(dict(status="PASS" if not nfail else "FAIL", gates={"pass": npass, "fail": nfail}, first_fail=first)))
