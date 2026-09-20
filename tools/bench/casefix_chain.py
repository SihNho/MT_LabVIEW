import os, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
for tag, args, to in (("lv_restart", [os.path.join(TOOLS, "lv_restart.py")], 400),
                      ("patch_opbuildcase", ["-u", os.path.join(TOOLS, "recipes", "patch_opbuildcase.py")], 700),
                      ("lv_restart2", [os.path.join(TOOLS, "lv_restart.py")], 400),
                      ("case_out_probe", ["-u", os.path.join(TOOLS, "bench", "case_out_probe.py")], 700)):
    try:
        rc = subprocess.run([sys.executable] + args, timeout=to, cwd=ROOT).returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"{tag} rc {rc}", flush=True)
