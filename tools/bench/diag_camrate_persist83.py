r"""diag_camrate_persist83.py - separator for the cycle-83 failed prediction (m8_load_83.log T5): the camera read 150 Hz
before each 150 Hz leg and 90.0009 Hz after the VI ran. Two explanations: (A) any IMAQdx session open reloads the
camera file's 90 Hz, so a C-API close + reopen also reads 90; (B) only the VI's own open/attribute path resets it, so
a C-API reopen still reads 150. No LabVIEW is touched; the camera is restored to 90 Hz at the end.
PREDICTION: was (B) in run 1 (tools/bench/diag_camrate_persist83.log 17:3x: reopen #1 and #2 read 90.0009 -> (B) REFUTED,
the review archive/peer/2026-09-25-hyp-camrate83.md predicted exactly that from NI's IMAQdxOpenCamera reference and the
.icd on this machine). Run 2 carries the review's prediction (A): P1 set 150 reads back 150 in the same session;
P2 reopen #1 reads 90 (file reloaded); P3 reopen #2 (after 3 s) reads 90; P4 restore 90 reads back 90.
"""
import ctypes as C, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools"))
import imaqdx_limits as L, protocol as P                                        # noqa: E402

def session(hz=None):
    n = C.c_uint32(0); L.dx.IMAQdxEnumerateCameras(None, C.byref(n), C.c_uint32(1))
    arr = (L.CameraInformation * n.value)(); L.dx.IMAQdxEnumerateCameras(arr, C.byref(n), C.c_uint32(1))
    sess = C.c_uint32(0); name = arr[0].InterfaceName.decode()
    assert L.dx.IMAQdxOpenCamera(name.encode(), C.c_uint32(0), C.byref(sess)) == 0, "open failed"
    try:
        rc = None
        if hz is not None:
            rc = L.dx.IMAQdxSetAttribute(sess, (L.ACQ + "AcquisitionFrameRate").encode(), C.c_uint32(L.F64), C.c_double(float(hz)))
            time.sleep(0.2)
        return {"set_rc": rc, "hz": L.get(sess, L.ACQ + "AcquisitionFrameRate", L.F64), "period_us": L.get(sess, L.ACQ + "AcquisitionFrameRateRaw")}
    finally:
        L.dx.IMAQdxCloseCamera(sess)

G = {}
a = session(150); print("set 150 in session:", a, flush=True); G["P1 set 150 reads 150"] = abs((a["hz"] or 0) - 150) <= 0.5
b = session(); print("reopen #1:", b, flush=True); G["P2 reopen #1 reads 90 (file reloaded)"] = abs((b["hz"] or 0) - 90) <= 0.5
time.sleep(3.0)
c = session(); print("reopen #2 after 3 s:", c, flush=True); G["P3 reopen #2 reads 90"] = abs((c["hz"] or 0) - 90) <= 0.5
d = session(90); print("restore 90:", d, flush=True); G["P4 restored 90"] = abs((d["hz"] or 0) - 90) <= 0.5
for k, v in G.items(): print("GATE %-36s %s" % (k, "PASS" if v else "FAIL"), flush=True)
bad = [k for k, v in G.items() if not v]
jp = os.path.join(HERE, "diag_camrate_persist83.json"); json.dump({"a": a, "b": b, "c": c, "d": d, "gates": G}, open(jp, "w"), indent=1)
import hashlib
print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None,
                                  [{"path": "tools/bench/diag_camrate_persist83.json", "md5": hashlib.md5(open(jp, "rb").read()).hexdigest()}])), flush=True)
sys.exit(1 if bad else 0)
