"""imaqdx_reset_test.py - does opening a camera session by itself restore the full frame?

This is the discriminating test for the second half of the user's report. The first half is already settled: the camera
really was at 640x512 (PayloadSize read 327680, not 1310720, so it was a genuine ROI and not an Image Display zoom -
the alternative a peer review correctly pushed back with). What is NOT settled is the mechanism behind
"두 번 작동하면 사이즈 원상복구되" - the second run restoring it.

Between the only two observations available, the camera went 640x512 -> 1280x1024, and the ONLY thing that happened in
between was a close and a re-open. If a plain open/close cycle resets the ROI, then the user's "second run" is not
doing anything clever: `IMAQdx Open Camera` hands every run a full frame, and the halving is something the first run
does to it afterwards. That converts an unexplained intermittent symptom into a deterministic one.

The test, in three phases:
  1. open, read  - the state as found.
  2. write Width/Height to half, read back, close.   (proves the write lands, and reproduces the symptom on purpose)
  3. re-open, read - if it reads FULL again, open/close resets the ROI. If it still reads half, the camera persists
     the ROI and the restoring mechanism is somewhere else entirely.
  4. finally: leave the camera at the full binned frame regardless of how the test ended.

SAFETY. Only Width, Height, OffsetX and OffsetY are ever written - exactly the attributes the main VI writes on every
single run - and **Binning is never touched**, so nanometres-per-pixel cannot change and the calibration is untouched.
Phase 4 runs in a finally block, so an exception still leaves the camera at 1280x1024. Nothing is acquired; no other
instrument is involved. Camera operation is covered by the user's 2026-09-12 clearance while the rig is disassembled.

  py tools/bench/imaqdx_reset_test.py
"""
import ctypes as C
import sys

MAXSTR = 512
dx = C.windll.LoadLibrary("niimaqdx.dll")
I64 = 1
IMG = "CameraAttributes::ImageFormatControl::"
TL = "CameraAttributes::TransportLayerControl::"


class CameraInformation(C.Structure):
    _fields_ = [("Type", C.c_uint32), ("Version", C.c_uint32), ("Flags", C.c_uint32),
                ("SerialNumberHi", C.c_uint32), ("SerialNumberLo", C.c_uint32), ("BusType", C.c_uint32),
                ("InterfaceName", C.c_char * MAXSTR), ("VendorName", C.c_char * MAXSTR),
                ("ModelName", C.c_char * MAXSTR), ("CameraFileName", C.c_char * MAXSTR),
                ("CameraAttributeURL", C.c_char * MAXSTR)]


def geti(sess, name):
    v = C.c_int64()
    rc = dx.IMAQdxGetAttribute(sess, name.encode(), C.c_uint32(I64), C.byref(v))
    return None if rc else v.value


def seti(sess, name, val):
    return dx.IMAQdxSetAttribute(sess, name.encode(), C.c_uint32(I64), C.c_int64(val))


def state(sess, tag):
    w, h = geti(sess, IMG + "Width"), geti(sess, IMG + "Height")
    bh, bv = geti(sess, IMG + "BinningHorizontal"), geti(sess, IMG + "BinningVertical")
    ox, oy = geti(sess, IMG + "OffsetX"), geti(sess, IMG + "OffsetY")
    pay = geti(sess, TL + "PayloadSize")
    print(f"   {tag:<28} {w} x {h}   binning {bh}x{bv}   offset {ox},{oy}   PayloadSize {pay}", flush=True)
    return w, h, bh, bv


def open_cam(name):
    sess = C.c_uint32(0)
    rc = dx.IMAQdxOpenCamera(name.encode(), C.c_uint32(0), C.byref(sess))
    if rc:
        raise RuntimeError(f"OpenCamera({name}) failed rc={rc}")
    return sess


def main():
    n = C.c_uint32(0)
    dx.IMAQdxEnumerateCameras(None, C.byref(n), C.c_uint32(1))
    if not n.value:
        print("no camera", flush=True); return 3
    arr = (CameraInformation * n.value)()
    dx.IMAQdxEnumerateCameras(arr, C.byref(n), C.c_uint32(1))
    name = arr[0].InterfaceName.decode()
    print(f"camera {name}\n", flush=True)

    sess = open_cam(name)
    full_w = full_h = None
    try:
        print("phase 1 - as found", flush=True)
        w, h, bh, bv = state(sess, "open #1")
        full_w, full_h = geti(sess, IMG + "WidthMax") // bh, geti(sess, IMG + "HeightMax") // bv
        print(f"   (full binned frame at this binning = {full_w} x {full_h})\n", flush=True)

        print(f"phase 2 - deliberately write half ({full_w // 2} x {full_h // 2}); binning untouched", flush=True)
        for attr, val in ((IMG + "Width", full_w // 2), (IMG + "Height", full_h // 2)):
            rc = seti(sess, attr, val)
            print(f"      set {attr.split('::')[-1]:<8} = {val:<6} rc={rc}", flush=True)
        halved = state(sess, "after writing half")[:2] == (full_w // 2, full_h // 2)
        print(f"   the write {'LANDED' if halved else 'did NOT land'}\n", flush=True)
    finally:
        dx.IMAQdxCloseCamera(sess)
        print("   closed session #1\n", flush=True)

    print("phase 3 - re-open and look. THIS is the question.", flush=True)
    sess = open_cam(name)
    try:
        w2, h2, _, _ = state(sess, "open #2")
        if (w2, h2) == (full_w, full_h):
            print("\n   ==> OPEN/CLOSE RESETS THE ROI. Every run of the main VI therefore starts from a FULL frame,\n"
                  "       so the user's 'second run restores it' is the driver, not the VI. The halving is something\n"
                  "       the first run does AFTER opening - and it must be deterministic, not intermittent.", flush=True)
        elif (w2, h2) == (full_w // 2, full_h // 2):
            print("\n   ==> THE CAMERA PERSISTS THE ROI across sessions. Then open/close is NOT the restorer, and the\n"
                  "       earlier 640->1280 transition had some other cause that still needs finding.", flush=True)
        else:
            print(f"\n   ==> neither full nor half: {w2} x {h2}. Unexpected - do not theorise, measure again.", flush=True)
    finally:
        print("\nphase 4 - leaving the camera at the full binned frame", flush=True)
        for attr, val in ((IMG + "OffsetX", 0), (IMG + "OffsetY", 0),
                          (IMG + "Width", full_w), (IMG + "Height", full_h)):
            rc = seti(sess, attr, val)
            print(f"      set {attr.split('::')[-1]:<8} = {val:<6} rc={rc}", flush=True)
        state(sess, "final")
        dx.IMAQdxCloseCamera(sess)
        print("   closed session #2", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
