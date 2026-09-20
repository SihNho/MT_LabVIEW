import os, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
for tag, args, to in (("lv_restart", [os.path.join(TOOLS, "lv_restart.py")], 400),
                      ("read_case_panes", ["-u", os.path.join(TOOLS, "bench", "read_case_panes.py")], 1100)):
    try:
        rc = subprocess.run([sys.executable] + args, timeout=to, cwd=ROOT).returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"{tag} rc {rc}", flush=True)
