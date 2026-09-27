"""diag_c113f_md5 - card 113-4: md5 of the card's artefacts + claudeDev leftovers + LabVIEW process check (offline, read-only)."""
import glob, hashlib, os, subprocess                                                 # noqa: E401
R = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop"
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                         # noqa: E731
for rel in ("tools/recipes/stage_d1_l2b2b.py", "tools/bench/diag_c113f_plan.py", "tools/bench/diag_c113d_errorlist.py",
            "tools/bench/errorlist_expected_D1_l2_b2b_20260928_015450.json", "tools/bench/plan_l2b2b.json", "tools/bench/plan_l2b2b_in.json",
            "tools/bench/plan_l2b2b_d4.json", "tools/bench/cards/plan_113-4_l2b2b.md", "archive/peer/2026-09-28-priorart-c113f-l2b2b.md"):
    p = os.path.join(R, rel)
    print("MD5", rel, md5(p), os.path.getsize(p))
for p in sorted(glob.glob(os.path.join(CD, "*b2b*")) + glob.glob(os.path.join(CD, "_elc_*")) + [os.path.join(CD, "D1_l2_b2a_20260928_001426.vi")]):
    print("CD", os.path.basename(p), md5(p), os.path.getsize(p))
print("LABVIEW", "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower())
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":0,"fail":0},"first_fail":null,"artefacts":[]}')
