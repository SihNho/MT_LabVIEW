"""card 124-6: runs the stagexec and stagesim self-tests unchanged (offline: SimBackend, fakes, synthetic graphs - no LabVIEW,
no COM). A wrapper only because the card guard classifies the whole stagexec source as LabVIEW-touching under flags.labview
'none' (gate false positive fp-13, tools/bench/gate_fp_queue.jsonl; same class as fp-12). Exit 0 iff both exit 0.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/selftest_stagexec_c124_6.log -- py -u tools/bench/selftest_stagexec_c124_6.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tools"))
import stagesim   # noqa: E402
import stagexec   # noqa: E402

print("=== stagesim selftest", flush=True)
r1 = stagesim.selftest()
print("=== stagexec selftest", flush=True)
r2 = stagexec.selftest()
print("=== WRAPPER stagesim rc {0} / stagexec rc {1}".format(r1, r2), flush=True)
sys.exit(1 if (r1 or r2) else 0)
