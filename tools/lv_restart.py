"""lv_restart.py - restart LabVIEW 2026 (standing permission, CLAUDE.md 3) and wait until COM answers.

  py tools/bgrun.py --max-min 6 --log tools/bench/fixture_probe.log -- py -u tools/lv_restart.py
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
LV_EXE = r"C:\Program Files\National Instruments\LabVIEW 2026\LabVIEW.exe"

subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"],
               capture_output=True)
time.sleep(6)
subprocess.run(["powershell", "-NoProfile", "-Command", "Start-Process '%s'" % LV_EXE], capture_output=True)
t0 = time.time()
import gscript as g  # noqa: E402

for _ in range(30):
    time.sleep(5)
    try:
        g._lv = None
        v = g.lv().Version
        print("LabVIEW up after %.0f s, version %s" % (time.time() - t0, v), flush=True)
        # NEVER 'dismiss' anything at startup: the small untitled window lv_gui reports as a modal right after
        # launch is LabVIEW's own startup window; posting WM_CLOSE to it (2026-09-07 03:3x-04:5x) left the root
        # loop in a state where every later OpenFrontPanel/Run hung 60-180 s. Waiting 45 s is enough (restart_probe).
        time.sleep(45)
        print("dialogs:", g._lv_gui("-Action", "dialogs").strip().replace("\n", " / ")[-80:], flush=True)
        break
    except Exception:
        pass
else:
    print("LabVIEW did not answer within 150 s", flush=True)
    sys.exit(1)
