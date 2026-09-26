import hashlib, json, os, glob
R = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop"
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
m = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
for p in [os.path.join(CD, "D1_s1_dispA_20260927_024535.vi"), os.path.join(CD, "D1_s1_copy.vi")]:
    print(m(p), os.path.getsize(p), p)
for p in ["tools/recipes/stage_d1_disp.py", "tools/bench/stage_d1_dispA.json", "tools/bench/sim/disp/plan_disp.json", "tools/stagexec.py"]:
    print(m(os.path.join(R, p)), p)
d = json.load(open(os.path.join(R, "tools/bench/stage_d1_dispA.json"), encoding="utf-8"))["partA"]
print({k: d.get(k) for k in ("file", "md5", "stop_after", "plan_md5")})
for p in ["tools/bench/stage_d1_disp_c104B.log", "tools/bench/stage_d1_disp.json"]:
    print(m(os.path.join(R, p)), p)
import subprocess
print("LABVIEW RUNNING:", "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower())
for p in sorted(glob.glob(os.path.join(CD, "D1_s1_disp_2026092*"))):
    print("EXISTING", m(p), os.path.getsize(p), p)
