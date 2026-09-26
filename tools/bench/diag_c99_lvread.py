r"""diag_c99_lvread.py - card 99-1 F1b: READ-ONLY COM read of saved panel DEFAULT values on a unique scratch BYTE COPY
of D1_s1_copy.vi (claudeDev\scratch_c99_<ts>.vi, deleted by close()). Template: diag_c97_gatefacts.py (same Stage,
same hygiene). Existing call only: the COM VI's GetControlValue (gscript.vi_ref). Offline prior (diag_c99_files*.log):
#8323 <- BuildArray #11261 (array = ForLoop #1359 tunnel #11363 of Bundler #11310 {Filtered X, second subarray};
element = Bundler #11608 of WLC #1114 'F-x out'); ring = Initialize Array #8953 dims (x-1 of size, const #8984,
'# FD points'). Files carry no data type and no panel values, hence this read.
PREDICTION CONTRACT: V1 '# FD points' reads as a number; V2 'Force (pN) vs Extension (nm) ' reads without COM error
(its Python shape is a FACT, not predicted); V3 'Z/dZ' reads; input md5 unchanged; nothing saved; no VI run.
"""
import json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagekit as K
g = K.g

S1 = os.path.join(g.CLAUDEDEV, "D1_s1_copy.vi"); S1_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"
NAMES = ["# FD points", "# DT points", "Force (pN) vs Extension (nm) ", "Z/dZ", "Frame rate",
         "Force\nsmoothing\nhalf-width", "Extension\nmedian filter\nhalf-width", "Extension (nm) vs Time (Frame #)"]
s = K.Stage(S1, S1_MD5, "diag_c99_lvread", work_name="scratch_c99_%s.vi" % time.strftime("%Y%m%d_%H%M%S"),
            deadline_min=15, reserve_s=120, task="99-1")


def shape(v, d=0):
    if isinstance(v, (tuple, list)):
        return "seq[%d]%s" % (len(v), ("(" + shape(v[0], d + 1) + ")") if v and d < 4 else "")
    return type(v).__name__ + ("=%r" % (v,) if not isinstance(v, (tuple, list)) and d == 0 else "")


def body(_):
    s.start(); s.scratches.append(s.work)
    bp = K.mod("bench_prep"); h0 = bp.labview_handles(); s.fact("HANDLES before reads: %r" % h0)
    vals = {}
    for n in NAMES:   # run 1 (diag_c99_lvread.log:24) used vi_ref as a plain call; it is a context manager
        def rd(n=n):
            with g.vi_ref(s.work) as vi:
                return vi.GetControlValue(n)
        v, err = s.safe("GetControlValue(%r)" % n, rd)
        vals[n] = {"err": err[:160] if err else "", "shape": shape(v) if not err else None,
                   "value": v if (not err and not isinstance(v, (tuple, list))) else None}
        s.fact("VALUE %r -> %s" % (n, vals[n]))
    s.R["values"] = vals
    s.gate("V1 '# FD points' is a number", isinstance(vals["# FD points"]["value"], (int, float)), repr(vals["# FD points"]))
    s.gate("V2 Force graph read without COM error", not vals["Force (pN) vs Extension (nm) "]["err"], repr(vals["Force (pN) vs Extension (nm) "]))
    s.gate("V3 'Z/dZ' read", not vals["Z/dZ"]["err"], repr(vals["Z/dZ"]))
    h1 = bp.labview_handles(); s.fact("HANDLES after reads: %r" % h1); s.R["handles"] = [h0, h1]


rc = K.run(body, s)
subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"],
               capture_output=True)
time.sleep(4)
gone = "LabVIEW.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True).stdout
s.gate("Z LabVIEW gone after the run", gone); s.dump(); rc = s.summary()
sys.exit(rc)
