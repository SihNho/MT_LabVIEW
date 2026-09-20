"""hang_split_tests.py - which target/op combination hangs the reporter? (spec §30, codex-recommended split)
Each call has its own watchdog; a hang is recorded and the script continues (the stuck OpReport run is left
behind - LabVIEW is restarted at the end if any test hung)."""
import os, sys, time, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 40.0)
CD = g.CLAUDEDEV; S = os.path.join(CD, "SCRATCH_pnprobe.vi")
if not os.path.exists(S):
    shutil.copyfile(os.path.join(CD, "OpBuildPN_v0.vi"), S)
def T(name, fn):
    t0 = time.time()
    try:
        r = fn(); print(f"{name}: OK {str(r)[:80]} ({time.time() - t0:.1f}s)", flush=True); return True
    except Exception as e:
        print(f"{name}: HANG/ERR {str(e)[:70]} ({time.time() - t0:.1f}s)", flush=True); return False
ok = []
ok.append(T("T0 health report(OpMove_v0)", lambda: len(g.report(os.path.join(CD, "OpMove_v0.vi"), "SubVI"))))
ok.append(T("T4 report(OpBuildPN_v0 ORIGINAL)", lambda: len(g.report(os.path.join(CD, "OpBuildPN_v0.vi"), "SubVI"))))
ok.append(T("T5 node_info(copy) [Nodes[]-based, no Traverse]", lambda: g.node_info(S, 30)))
ok.append(T("T6 fp_labels(copy)", lambda: g.fp_labels(S, 30)))
ok.append(T("T7 report(OpBuildInvoke_v0 ORIGINAL)", lambda: len(g.report(os.path.join(CD, "OpBuildInvoke_v0.vi"), "SubVI"))))
ok.append(T("T8 report(copy) LAST (may poison the instance)", lambda: len(g.report(S, "SubVI"))))
print("RESULTS", ok, flush=True)
