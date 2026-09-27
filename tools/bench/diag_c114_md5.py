"""card 114-1: md5 of the card's artefacts (read-only) + LabVIEW process check."""
import hashlib
import subprocess
import sys

CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev" + "\\"
for p in ["tools/stage_prerun.py", "tools/bench/selftest_stage_prerun_c114.py", "tools/bench/graph_l2b2b_20260928.json",
          "tools/bench/plan_l2b3.json", "tools/bench/plan_l2b3_d4.json", "tools/bench/namediff_l2b3.json",
          "tools/recipes/stage_d1_l2b3.py", "tools/bench/diag_c114_plan.py", "tools/bench/diag_c114_errorlist.py",
          CD + "D1_l2_b3_20260928_032703.vi", CD + "D1_l2_b2b_20260928_015450.vi"]:
    print(hashlib.md5(open(p, "rb").read()).hexdigest(), p)
print("labview running:", "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower())
sys.exit(0)
