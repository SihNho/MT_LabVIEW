"""diag_chain.py - fresh LabVIEW (ini tokens now in place) -> clfn_wire_probe.py -> build_opgeterrors.py"""
import os, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
for tag, args, to in (("lv_restart", [os.path.join(TOOLS, "lv_restart.py")], 400),
                      ("wire_probe", ["-u", os.path.join(TOOLS, "bench", "clfn_wire_probe.py")], 600),
                      ("opgeterrors", ["-u", os.path.join(TOOLS, "recipes", "build_opgeterrors.py")], 900)):
    try:
        rc = subprocess.run([sys.executable] + args, timeout=to, cwd=ROOT).returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"{tag} rc {rc}", flush=True)
