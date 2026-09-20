"""imaqdx_dirty_exit.py - does a client that dies WITHOUT closing leave the camera's ROI behind?

This resolves a contradiction between two of today's own measurements, which is the reason it exists rather than being
a theory anyone likes:

  * `imaqdx_reset_test.py` showed set-640 -> CloseCamera -> OpenCamera reads 1280. Open/close resets the ROI.
  * but the very first probe of the day (`imaqdx_ctypes.py`) opened a fresh session and read **640**.

Both cannot be true if the reset were unconditional. The obvious candidate for the difference is HOW the previous
session ended: today's earlier attempts left a LabVIEW that had to be killed behind modal dialogs, and the user's own
symptom is about what the FIRST run finds. So: does an un-closed session leave the camera as it was?

  stage 1 (--dirty): open, set the ROI to half, then exit via os._exit() - no CloseCamera, no atexit, no DLL cleanup
                     the interpreter would otherwise run. This is the closest safe stand-in for a killed process.
  stage 2 (default): open, read. 640 means a dirty exit preserves the ROI; 1280 means the driver resets regardless and
                     the contradiction has some other source that still needs finding. Restores the full frame either
                     way.

SAFETY: only Width/Height/offsets are written; binning is never touched, so nm-per-pixel cannot change. Stage 2 always
restores 1280x1024 before it exits. Nothing is acquired and nothing moves.
  py tools/bench/imaqdx_dirty_exit.py --dirty     # then:
  py tools/bench/imaqdx_dirty_exit.py
"""
import ctypes as C
import os, sys

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


def geti(sess, n):
    v = C.c_int64()
    return None if dx.IMAQdxGetAttribute(sess, n.encode(), C.c_uint32(I64), C.byref(v)) else v.value


def seti(sess, n, val):
    return dx.IMAQdxSetAttribute(sess, n.encode(), C.c_uint32(I64), C.c_int64(val))


def open_first():
    n = C.c_uint32(0)
    dx.IMAQdxEnumerateCameras(None, C.byref(n), C.c_uint32(1))
    if not n.value:
        print("no camera", flush=True); sys.exit(3)
    arr = (CameraInformation * n.value)()
    dx.IMAQdxEnumerateCameras(arr, C.byref(n), C.c_uint32(1))
    name = arr[0].InterfaceName.decode()
    sess = C.c_uint32(0)
    if dx.IMAQdxOpenCamera(name.encode(), C.c_uint32(0), C.byref(sess)):
        print(f"OpenCamera({name}) failed", flush=True); sys.exit(4)
    return name, sess


def show(sess, tag):
    print(f"   {tag:<22} {geti(sess, IMG + 'Width')} x {geti(sess, IMG + 'Height')}   "
          f"binning {geti(sess, IMG + 'BinningHorizontal')}x{geti(sess, IMG + 'BinningVertical')}   "
          f"PayloadSize {geti(sess, TL + 'PayloadSize')}", flush=True)


def main():
    name, sess = open_first()
    dirty = "--dirty" in sys.argv
    print(f"camera {name}  ({'STAGE 1: set half then die without closing' if dirty else 'STAGE 2: read what survived'})",
          flush=True)
    show(sess, "on open")
    if dirty:
        bh, bv = geti(sess, IMG + "BinningHorizontal"), geti(sess, IMG + "BinningVertical")
        half_w = geti(sess, IMG + "WidthMax") // bh // 2
        half_h = geti(sess, IMG + "HeightMax") // bv // 2
        seti(sess, IMG + "Width", half_w); seti(sess, IMG + "Height", half_h)
        show(sess, "after writing half")
        print("   exiting WITHOUT CloseCamera (os._exit)", flush=True)
        sys.stdout.flush()
        os._exit(0)                      # no CloseCamera, no atexit, no interpreter cleanup

    bh, bv = geti(sess, IMG + "BinningHorizontal"), geti(sess, IMG + "BinningVertical")
    full_w = geti(sess, IMG + "WidthMax") // bh
    full_h = geti(sess, IMG + "HeightMax") // bv
    w, h = geti(sess, IMG + "Width"), geti(sess, IMG + "Height")
    if (w, h) == (full_w // 2, full_h // 2):
        print("\n   ==> A DIRTY EXIT PRESERVES THE ROI. The two contradictory observations are reconciled: a clean\n"
              "       close resets the frame, a killed client does not. The 640x512 found this morning was left by a\n"
              "       session that died, and 'the first run halves it' means the FIRST run inherits a leftover.", flush=True)
    elif (w, h) == (full_w, full_h):
        print("\n   ==> the driver reset the ROI even after a dirty exit. So the contradiction has another source -\n"
              "       do NOT adopt the leftover-state story; find what else set 640x512 this morning.", flush=True)
    else:
        print(f"\n   ==> unexpected {w} x {h}; measure again rather than theorise.", flush=True)

    for attr, val in ((IMG + "OffsetX", 0), (IMG + "OffsetY", 0),
                      (IMG + "Width", full_w), (IMG + "Height", full_h)):
        seti(sess, attr, val)
    show(sess, "restored")
    dx.IMAQdxCloseCamera(sess)
    return 0


if __name__ == "__main__":
    sys.exit(main())
