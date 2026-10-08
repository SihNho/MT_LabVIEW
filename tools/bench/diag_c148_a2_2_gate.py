# ---
# labview: none
# hardware: none
# ---
"""Card 148-a2-2: dry check of the launch gate (guard_cycle.py + stop_record) for the s06 scratch recipe.

Prediction contract: no LabVIEW is touched; prints the guard_cycle rc and its stderr/stdout for a simulated
bgrun launch of tools/recipes/stage_d1_ring_p4_s06v18_scratch.py, plus priorart_diff.scope() of that recipe.
Before the review: expected BLOCKED (DIFF-ONLY hint). After an ANSWERED `novel` review: expected rc 0, empty.
Existing tools reused: tools/hooks/guard_cycle.py main(), tools/priorart_diff.py scope(); nothing new built.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
REC = "tools/recipes/stage_d1_ring_p4_s06v18_scratch.py"
tag = sys.argv[1] if len(sys.argv) > 1 else "check"

import priorart_diff  # noqa: E402

dsc = priorart_diff.scope(os.path.join(ROOT, REC))
print("SCOPE", json.dumps({k: (v if k != "substantive" else len(v)) for k, v in (dsc or {}).items()}, default=str))
cmd = ("py tools/bgrun.py --material --max-min 30 --log tools/bench/stage_d1_ring_p4_s06v18_scratch.log -- "
       "py -u " + REC)
inp = json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}})
env = dict(os.environ)
env.pop("CYCLE_GUARD_OFF", None)
p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "hooks", "guard_cycle.py")], input=inp,
                   capture_output=True, text=True, cwd=ROOT, env=env, timeout=240)
print("GATE rc=%d" % p.returncode)
print("STDOUT:", p.stdout.strip()[:3000])
print("STDERR:", p.stderr.strip()[:3000])
ok = 1 if p.returncode == 0 else 0
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if ok else "FAIL",
                              "gates": {"pass": ok, "fail": 1 - ok}, "first_fail": None if ok else "gate-" + tag,
                              "artefacts": []}))
