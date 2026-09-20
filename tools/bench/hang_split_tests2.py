"""hang_split_tests2.py - is the OpBuildInvoke_v0 lineage safe to copy and read? (spec §30)"""
import os, sys, time, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 40.0)
CD = g.CLAUDEDEV; S = os.path.join(CD, "SCRATCH_invprobe.vi")
shutil.copyfile(os.path.join(CD, "OpBuildInvoke_v0.vi"), S)
def T(name, fn):
    t0 = time.time()
    try:
        r = fn(); print(f"{name}: OK {str(r)[:90]} ({time.time() - t0:.1f}s)", flush=True); return True
    except Exception as e:
        print(f"{name}: FAIL {str(e)[:70]} ({time.time() - t0:.1f}s)", flush=True); return False
T("T0 health report(OpMove_v0)", lambda: len(g.report(os.path.join(CD, "OpMove_v0.vi"), "SubVI")))
T("TA report(copy of OpBuildInvoke_v0) Traverse", lambda: [(o["uid"], o["pos"]) for o in g.report(S, "SubVI")])
T("TB node_info(OpBuildInvoke_v0 ORIGINAL)", lambda: g.node_info(os.path.join(CD, "OpBuildInvoke_v0.vi"), 20))
T("TC node_info(copy of OpBuildInvoke_v0)", lambda: g.node_info(S, 20))
T("TD open_panel(copy) + report", lambda: (g.open_panel(S), len(g.report(S, "Function"))))
T("TE health again", lambda: len(g.report(os.path.join(CD, "OpMove_v0.vi"), "SubVI")))
try:
    g.close_panel(S); os.remove(S); print("scratch removed", flush=True)
except Exception as e:
    print("cleanup", str(e)[:50], flush=True)
