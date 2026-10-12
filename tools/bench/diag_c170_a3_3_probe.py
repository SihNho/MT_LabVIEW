# ---
# labview: none
# hardware: none
# ---
"""diag_c170_a3_3_probe - card 170-a3-3: read-only look at the stored 110-7 legs before writing the init-range and
other-files checks: trans/rot ranges per leg, init boundary, files in each leg --out dir and run dir. No LabVIEW.
PREDICTION: both tra parse; trans/rot all finite on both legs (facts only; one gate: the data parsed)."""
import json, os, sys                                                                    # noqa: E401
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, m8b_replay_compare as C                                           # noqa: E401,E402
LEGS = os.path.join(HERE, "t0_legs", "c110f_replay_20260927_184600")
A = os.path.join(HERE, "m8_out", "replay_s1_20260927_184651")
B = C.run_dirs(os.path.join(LEGS, "B_dispreplay_a1", "leg.json"))[0]
(ia, ta), (ib, tb) = C.tra(A), C.tra(B)
tr = C.trans_rot(ta, tb)
print("TRANSROT", json.dumps({k: v for k, v in tr.items() if k != "envelope"}))
for tag, t in (("A", ta), ("B", tb)):
    print("RANGE %s shape %s trans [%r, %r] rot [%r, %r] finite %s" % (tag, t.shape, float(np.nanmin(t[:, 1])), float(np.nanmax(t[:, 1])),
          float(np.nanmin(t[:, 2])), float(np.nanmax(t[:, 2])), bool(np.isfinite(t[:, 1:3]).all())))
    print("INIT %s rows 0..%d trans %s rot %s" % (tag, tr["boundary"], np.unique(t[:tr["boundary"], 1])[:12].tolist(), np.unique(t[:tr["boundary"], 2])[:12].tolist()))
for d in ("A_S1replay_a1", "B_dispreplay_a1"):
    print("LEGOUT %s %s" % (d, sorted(os.listdir(os.path.join(LEGS, d)))))
print("LEGS top %s" % sorted(os.listdir(LEGS)))
print("RUNDIR A %s B %s" % (sorted(os.listdir(A)), sorted(os.listdir(B))))
lj = json.load(open(os.path.join(LEGS, "A_S1replay_a1", "leg.json")))
print("LEGJSON keys %s facts %s" % (list(lj), sorted(lj["facts"])))
print("FACTS lost %r frames_delta %r m8 files %s" % (lj["facts"].get("lost"), lj["facts"].get("frames_delta"), sorted((lj.get("m8") or {}).get("files") or {})))
ok = bool(ia["parsed"] and ib["parsed"])
print(P.result_line(P.make_result(1 if ok else 0, 0 if ok else 1, None if ok else "tra parse", [])))
