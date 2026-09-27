r"""diag_c113c_peek - card 113-2, OFFLINE read-only (no LabVIEW): md5 of the card's artefacts for result_113-2.json."""
import hashlib, os, sys                                                            # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
import protocol                                                                    # noqa: E402
P = ["tools/stagexec.py", "tools/recipes/stage_d1_l2b2b.py", "tools/bench/plan_l2b2b.json", "tools/bench/plan_l2b2b_d4.json",
     "tools/bench/sim/c113c/plan_c113c_bed.json", "tools/bench/scratch_verify/stagexec.ctltun_loop_20260928_012355.json",
     "tools/bench/scratch_verify/stagexec.ctlsink_loop_20260928_012355.json", "tools/bench/diag_c113c_scratch.py", "tools/bench/diag_c113c_plan.py",
     "tools/bench/diag_c113d_errorlist.py", "tools/bench/cards/plan_113-2_l2b2b.md", "archive/peer/2026-09-28-priorart-c113c-l2b2b.md",
     "archive/peer/2026-09-28-c113d-pb.md", r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_l2_b2a_20260928_001426.vi"]
for p in P:
    f = p if os.path.isabs(p) else os.path.join(ROOT, p)
    print("MD5", hashlib.md5(open(f, "rb").read()).hexdigest(), p)
print("B2b files in claudeDev:", [x for x in os.listdir(r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev") if x.startswith(("D1_l2_b2b", "scratch_c113"))])
print(protocol.result_line(protocol.make_result(1, 0, None, [])))
