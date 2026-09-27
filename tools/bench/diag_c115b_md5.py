"""diag_c115b_md5 - card 115-2: md5 of the card's artefacts and inputs (read-only, no LabVIEW)."""
import hashlib, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = [r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_l2_b3_20260928_032703.vi",
     "tools/stage_prerun.py", "tools/stagexec.py", "tools/stagesim.py", "tools/recipes/stage_d1_l2r1.py", "tools/bench/plan_l2r1.json",
     "tools/bench/plan_l2r1_in.json", "tools/bench/plan_l2r1_d4.json", "tools/bench/diag_c115b_scratch.py", "tools/bench/diag_c115b_errorlist.py",
     "tools/bench/diag_c115b_r1.py", "tools/bench/cards/plan_115-2_l2r1.md"]
for f in F:
    p = f if os.path.isabs(f) else os.path.join(R, f)
    print(f, hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "MISSING")
cd = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
print("claudeDev l2_r1/scratch_c115:", [n for n in os.listdir(cd) if "l2_r1" in n or "scratch_c115" in n])
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":0,"fail":0},"first_fail":null,"artefacts":[]}')
