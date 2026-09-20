"""gpu_base_smoke.py - does the copied CLFN in GPU_kernel_base.vi find claudeDev\Debug\GPU Tracking.dll and call it?
Placeholder (donor-typed) controls are fed small dummies; the DLL is expected to answer with a size-mismatch message in
'Error Message 2' (not a crash / not a missing-DLL error)."""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
T = os.path.join(g.CLAUDEDEV, "GPU_kernel_base.vi")
print("ExecState", g.exec_state(T), flush=True)
vi = g.op(T)
labs = g.fp_labels(T); print("labels:", [(l, i) for _, l, i in labs], flush=True)
vi.SetControlValue("Error Message", " " * 64); vi.SetControlValue("Cross Size", 120)
try:
    vi.SetControlValue("X Array", [1, 2, 3]); vi.SetControlValue("Y Array", [1]); vi.SetControlValue("Test Array", [0.0] * 120)
except Exception as e:
    print("set:", str(e)[:120], flush=True)
t0 = time.time()
try:
    g._run(vi); print(f"run ok {time.time() - t0:.1f}s", flush=True)
except Exception as e:
    print("run raised:", str(e)[:300], flush=True)
for l in ("Error Message 2", "error out", "X Array 2", "Y Array 2"):
    try:
        print(f"  {l!r} = {str(vi.GetControlValue(l))[:120]}", flush=True)
    except Exception as e:
        print(f"  {l!r} read err {str(e)[:80]}", flush=True)
