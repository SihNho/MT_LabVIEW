"""restart LabVIEW (the SPEC copies in memory carry junk Invokes from the wiring reads -> not executable), then the black-box Z comparison."""
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "lv_restart.py")], timeout=400); print("lv_restart rc", r.returncode, flush=True)
r = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "bench", "blackbox_z.py")], timeout=900); print("capture rc", r.returncode, flush=True)
sys.exit(r.returncode)
