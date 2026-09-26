"""diag_c104_ladder - card 104-1: run the Jev review ladder (tools/bench/jev_gate.jev_ladder, the function guard_peer calls)
on the failed Part-B log so the NEXT-ACTION line exists for the caller. Touches no LabVIEW. Prints the ladder result."""
import os, sys, json   # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import jev_gate  # noqa: E402
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stage_d1_disp_c104B.log")
txt = open(LOG, encoding="utf-8", errors="replace").read()
fail = "\n".join(ln for ln in txt.splitlines() if "FAIL " in ln or "TypeError" in ln or "BGRUN END" in ln)
r = jev_gate.jev_ladder(LOG, fail, write=True)
print(json.dumps(r, default=str)[:3000])
print("NEWEST", jev_gate.newest_ladder_line(os.path.basename(LOG)))
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
