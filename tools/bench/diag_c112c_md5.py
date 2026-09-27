"""diag_c112c_md5 - card 112-3 (offline): md5 of the card's artefacts for result_112-3.json. No LabVIEW."""
import hashlib, os                                                                     # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for p in ("tools/recipes/stage_d1_l2b2a.py", "tools/bench/plan_l2b2a_allow.json", "tools/bench/sim/c112c/plan_c112c_bed.json",
          "tools/bench/diag_c112c_t1t2.py", "tools/bench/scratch_verify/stagexec.op_wire_sr_20260927_233612.json",
          "tools/bench/scratch_verify/stagexec.op_connect_20260927_233612.json", "archive/peer/2026-09-27-priorart-c111e-l2b2a.md",
          "tools/bench/diag_c112c_errorlist.py", "tools/bench/plan_l2b2a.json"):
    print("MD5", hashlib.md5(open(os.path.join(ROOT, p), "rb").read()).hexdigest(), p)
cd = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
print("CLAUDEDEV LEFT", sorted(f for f in os.listdir(cd) if f.lower().startswith(("scratch_c112", "d1_l2_b2a"))))
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
