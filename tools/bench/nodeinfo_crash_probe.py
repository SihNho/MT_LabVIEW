"""nodeinfo_crash_probe.py - why did LabVIEW die during the motion-VI inspection?

Observed 2026-09-12: `inspect_motion_vis.py` read counts and ActiveX properties from a copy of `Mercury_comm.vi`
(a 2009-vintage PI driver VI) and then LabVIEW vanished at the `node_info` call; every later call returned
RPC_S_SERVER_UNAVAILABLE and the whole batch was void.

Two candidate triggers, and a third possibility that it was transient:
  A  the op itself is broken or LabVIEW is in a bad state    -> a modern VI would crash too
  B  the 17-year-old VI is the trigger                       -> only the old VI crashes
  C  the ActiveX property probe `props()` destabilised the connection, and node_info was merely the next call
     -> the old VI is fine WITHOUT the probe and dies WITH it

Three cells, each in its OWN process behind its OWN fresh LabVIEW, so one crash cannot void the others:
  cell 1  node_info on PARALLEL_kernel_v3.vi          (modern control)          predict: OK
  cell 2  node_info on a copy of Mercury_comm.vi, NO property probe             predict: decides B vs C
  cell 3  property probe THEN node_info on the same copy                        predict: decides C
  py tools/bgrun.py --max-min 20 --log tools/bench/nodeinfo_crash_probe.log -- py -u tools/bench/nodeinfo_crash_probe.py
"""
import os, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
LAB = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI"
MERC = os.path.join(LAB, "PI Trans", "Mercury_comm.vi")

CELL = r'''
import os, shutil, sys, time
sys.path.insert(0, r"{tools}")
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 45.0)
src = r"{src}"
probe = {probe}
if r"{copy}" == "yes":
    dst = os.path.join(g.CLAUDEDEV, "INSPECT_probe.vi")
    if os.path.exists(dst):
        os.remove(dst)
    shutil.copyfile(src, dst)
else:
    dst = src
print("target:", os.path.basename(dst), flush=True)
print("counts:", {{c: g.count(dst, c) for c in ("Node", "Diagram", "SubVI", "Wire")}}, flush=True)
if probe:
    vi = g.lv().GetVIReference(dst, "", False, 0)
    got = {{}}
    for n in ("ReentrantExecution", "Reentrant", "ExecutionPriority", "PreferredExecSystem", "ExecSystem", "VIType"):
        try:
            got[n] = vi.__getattr__(n)
        except Exception:
            pass
    print("props:", got, flush=True)
    del vi
info = g.node_info(dst, max_n=60)
print("node_info OK, nodes:", len(info), flush=True)
for i, style, text in info:
    print("   [%d] %r %r" % (i, style, text), flush=True)
if r"{copy}" == "yes":
    try:
        g.close_panel(dst); time.sleep(0.3); os.remove(dst)
    except Exception:
        pass
print("CELL OK", flush=True)
'''

CELLS = [
    ("1 control: modern VI, no probe",
     os.path.join(r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev", "PARALLEL_kernel_v3.vi"), "no", "False"),
    ("2 old VI, NO property probe", MERC, "yes", "False"),
    ("3 old VI, WITH property probe", MERC, "yes", "True"),
]

for name, src, copy, probe in CELLS:
    print(f"\n{'#' * 70}\n#### cell {name}", flush=True)
    try:
        rc = subprocess.run([sys.executable, os.path.join(TOOLS, "lv_restart.py")], timeout=400, cwd=ROOT).returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"   lv_restart rc {rc}", flush=True)
    code = CELL.format(tools=TOOLS, src=src, copy=copy, probe=probe)
    try:
        p = subprocess.run([sys.executable, "-u", "-c", code], timeout=600, cwd=ROOT,
                           capture_output=True, text=True)
        print(p.stdout, flush=True)
        if p.stderr.strip():
            print("   STDERR:", p.stderr.strip()[-600:], flush=True)
        print(f"   cell rc {p.returncode}", flush=True)
    except subprocess.TimeoutExpired:
        print("   cell TIMEOUT", flush=True)
    alive = subprocess.run(["powershell", "-NoProfile", "-Command",
                            "if (Get-Process -Name LabVIEW -ErrorAction SilentlyContinue) {'alive'} else {'DEAD'}"],
                           capture_output=True, text=True, timeout=60).stdout.strip()
    print(f"   LabVIEW after the cell: {alive}", flush=True)
print("\nDONE", flush=True)
