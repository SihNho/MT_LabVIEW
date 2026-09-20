"""restart_probe.py - does OpenFrontPanel work after a restart WITHOUT dismissing the startup window? (spec §30)"""
import os, sys, time, subprocess, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"], capture_output=True)
time.sleep(6)
subprocess.run(["powershell", "-NoProfile", "-Command", "Start-Process '%s'" % r"C:\Program Files\National Instruments\LabVIEW 2026\LabVIEW.exe"], capture_output=True)
import gscript as g
t0 = time.time()
for _ in range(30):
    time.sleep(5)
    try:
        g._lv = None; g.lv().Version; break
    except Exception:
        pass
print("COM answers after %.0f s" % (time.time() - t0), flush=True)
for k in range(4):
    print("  +%ds dialogs: %s | windows: %s" % (k * 15, g._lv_gui("-Action", "dialogs").strip().replace("\n", " / ")[-90:], g._lv_gui("-Action", "windows").strip().replace("\n", " | ")[:80]), flush=True)
    time.sleep(15)
g._run.__defaults__ = (6.0, 60.0)
CD = g.CLAUDEDEV; S = os.path.join(CD, "SCRATCH_invprobe.vi")
shutil.copyfile(os.path.join(CD, "OpBuildInvoke_v0.vi"), S)
t0 = time.time()
try:
    print("report(copy):", len(g.report(S, "SubVI")), "%.1fs" % (time.time() - t0), flush=True)
except Exception as e:
    print("report(copy) FAIL", str(e)[:60], flush=True)
t0 = time.time()
try:
    g._invoke(g.lv().GetVIReference(S, "", False, 0), "OpenFrontPanel", False, 1); print("open_panel(copy) OK %.1fs" % (time.time() - t0), flush=True)
except Exception as e:
    print("open_panel(copy) FAIL", str(e)[:80], "%.1fs" % (time.time() - t0), flush=True)
t0 = time.time()
try:
    print("report(copy) after open:", len(g.report(S, "SubVI")), "%.1fs" % (time.time() - t0), flush=True)
except Exception as e:
    print("report after open FAIL", str(e)[:60], flush=True)
print("dialogs now:", g._lv_gui("-Action", "dialogs").strip().replace("\n", " / ")[-90:], flush=True)
