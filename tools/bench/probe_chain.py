"""probe_chain.py - fresh LabVIEW (a client was killed) -> clfn_break_probe.py <selection>"""
import os, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
sel = sys.argv[1] if len(sys.argv) > 1 else "L"
r = subprocess.run([sys.executable, os.path.join(TOOLS, "lv_restart.py")], timeout=400, cwd=ROOT); print("lv_restart rc", r.returncode, flush=True)
r = subprocess.run([sys.executable, "-u", os.path.join(TOOLS, "bench", "clfn_break_probe.py"), sel], timeout=1200, cwd=ROOT); print("probe rc", r.returncode, flush=True)
