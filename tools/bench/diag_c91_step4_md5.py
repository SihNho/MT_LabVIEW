r"""diag_c91_step4_md5.py - md5 of the card 91-3 artefacts (no LabVIEW)."""
import hashlib, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = ["tools/bench/t0_step4_91.json", "tools/bench/diag_c91_step4.py", "tools/bench/diag_c91_step4_leg.py", "tools/bench/diag_c91_step4_stats.py",
     "tools/bench/diag_c91_step4_click1.py", "tools/bench/diag_c91_step4_summary.py", "tools/bench/diag_c91_step4.log", "tools/bench/diag_c91_step4_b.log",
     "tools/bench/diag_c91_step4_click1.log", "tools/bench/diag_c91_step4_summary.log", "archive/peer/2026-09-26-c91-smoke-k1.md",
     "archive/peer/2026-09-26-c91-step4-t12.md", "archive/benchmarks/INDEX.md",
     r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_s1_t0_20260926_055551.vi", r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_s1_copy.vi"]
for f in F + sys.argv[1:]:
    p = f if os.path.isabs(f) else os.path.join(ROOT, f)
    print("%s %s" % (hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else "MISSING", f))
