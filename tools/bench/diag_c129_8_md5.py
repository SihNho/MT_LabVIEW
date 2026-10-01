"""diag_c129_8_md5 - card 129-8: md5 of the card's changed files (read-only)."""
import hashlib, os, sys                                                             # noqa: E401
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(R, "tools"))
import protocol as PR                                                               # noqa: E402
FS = ["recipes/stage_d1_ring_p3b1.py", "recipes/stage_d1_ring_p3b2.py", "bench/stage_d1_ring_p3b1_scratch.py", "card_clock.py",
      "bench/selftest_card_clock.py", "bench/diag_c129_8_mempred.py", "bench/plan_ring_p3b1_pred.json", "bench/plan_ring_p3b2_pred.json",
      "bench/plan_ring_p3b1.json", "bench/plan_ring_p3b2.json"]
for p in FS:
    print(hashlib.md5(open(os.path.join(R, "tools", p), "rb").read()).hexdigest(), "tools/" + p, flush=True)
print(PR.result_line(PR.make_result(len(FS), 0)), flush=True)
