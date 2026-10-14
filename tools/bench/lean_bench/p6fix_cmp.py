"""p6fix_cmp - offline: P6-2's full compare (m8b_replay_compare.compare_p6, D = 20, unchanged) of P6-2's S1 leg vs a new P6 leg.
    py tools/bench/lean_bench/p6fix_cmp.py <P6 run dir> <P6 leg dir> <out json>"""
import os, sys                                                                           # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); BENCH = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(BENCH))
sys.path.insert(0, BENCH); sys.path.insert(0, os.path.join(ROOT, "tools"))
import m8b_replay_compare as CMP, motor_gate as MG                                        # noqa: E401,E402
S1_RUN = os.path.join(HERE, "out_20261013d", "run", "replay_s1_20261013_142928")
S1_LEG = os.path.join(HERE, "out_20261013d", "legs", "S1_a1")
R, I = CMP.compare_p6(S1_RUN, sys.argv[1], 20, sys.argv[3], S1_LEG, sys.argv[2], MG.load_limits())
print("RESULT", {k: ("PASS" if v else "FAIL") for k, v in I.items()})
