import os, sys
ROOT = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop"
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
os.chdir(ROOT)
import guard_peer as gp, protocol as P
for s in ["tools/bench/ring_p2a_md5.py", "tools/bench/selftest_launch_gate.py", "tools/bench/selftest_census_hookin_c123.py",
          "tools/bench/selftest_case_frame_c124.py", "tools/stagexec.py", "tools/protocol.py", "tools/stage_prerun.py",
          "tools/stagesim.py", "tools/census_predict.py", "tools/gate_fp.py"]:
    src = P._src(os.path.join(ROOT, s))
    print("%-45s gp_touch=%s  P_LVIMPORT=%s" % (s, gp.script_touches_labview(os.path.join(ROOT, s)),
          [m.group(0).strip() for m in P.LV_IMPORT_RE.finditer(P.code_only(src))][:4]))
cmd = "py tools/bgrun.py --material --max-min 2 --log tools/bench/ring_p2a_md5.log -- py -u tools/bench/ring_p2a_md5.py"
print("offline_command fp10:", gp.offline_command(cmd))
print("selftest_exempt fp11:", gp.selftest_exempt("BGRUN START x limit 5.0 min: py -u tools/bench/selftest_case_frame_c124.py"))
