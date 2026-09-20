"""imaqdx_limits.py - read the camera's LIMITS, not just its current values.

`imaqdx_ctypes.py` showed the camera sitting at 640x512, 2x2 binning, 90.0009 Hz. Current values do not answer the two
open questions, so this reads the attribute RANGES instead:

  * the maximum AcquisitionFrameRate at the geometry currently loaded, and (with --restore) at the full binned frame.
    `AcquisitionFrameRateRaw` is the frame PERIOD in microseconds - 11111 us = 90.0009 Hz - so its MINIMUM is the
    ceiling. This is the number that decides whether the user's wanted 150 Hz is physically reachable before any
    software work is justified.
  * the legal range of Width/Height, which tells us what the configuration step is allowed to ask for.

WRITES, and why they are safe: with `--restore` the script sets Width/Height back to the full binned frame
(WidthMax/BinningHorizontal x HeightMax/BinningVertical). That is not an experiment on the rig - the camera is
currently stuck in the halved state the user reported, the main VI rewrites both attributes at every startup, and the
value written is the one the VI is trying to reach anyway. Binning is never touched, so nm-per-pixel cannot change.
Nothing is acquired and no other instrument is involved.

  py tools/bench/imaqdx_limits.py            # read-only
  py tools/bench/imaqdx_limits.py --restore  # also put the frame back to full size
"""
import ctypes as C
import sys

MAXSTR = 512
dx = C.windll.LoadLibrary("niimaqdx.dll")
U32, I64, F64, STR, ENUM, BOOL = 0, 1, 2, 3, 4, 5
A = "CameraAttributes::"
IMG, ACQ = A + "ImageFormatControl::", A + "AcquisitionControl::"


class CameraInformation(C.Structure):
    _fields_ = [("Type", C.c_uint32), ("Version", C.c_uint32), ("Flags", C.c_uint32),
                ("SerialNumberHi", C.c_uint32), ("SerialNumberLo", C.c_uint32), ("BusType", C.c_uint32),
                ("InterfaceName", C.c_char * MAXSTR), ("VendorName", C.c_char * MAXSTR),
                ("ModelName", C.c_char * MAXSTR), ("CameraFileName", C.c_char * MAXSTR),
                ("CameraAttributeURL", C.c_char * MAXSTR)]


def get(sess, name, t=I64):
    v = C.c_int64() if t == I64 else C.c_double()
    rc = dx.IMAQdxGetAttribute(sess, name.encode(), C.c_uint32(t), C.byref(v))
    return None if rc else v.value


def limits(sess, name, t=I64):
    """(minimum, maximum, increment) - the range the camera will actually accept right now."""
    out = []
    for fn in ("IMAQdxGetAttributeMinimum", "IMAQdxGetAttributeMaximum", "IMAQdxGetAttributeIncrement"):
        v = C.c_int64() if t == I64 else C.c_double()
        rc = getattr(dx, fn)(sess, name.encode(), C.c_uint32(t), C.byref(v))
        out.append(None if rc else v.value)
    return tuple(out)


def report(sess, tag):
    w, h = get(sess, IMG + "Width"), get(sess, IMG + "Height")
    bh, bv = get(sess, IMG + "BinningHorizontal"), get(sess, IMG + "BinningVertical")
    fr = get(sess, ACQ + "AcquisitionFrameRate", F64)
    rmin, rmax, rinc = limits(sess, ACQ + "AcquisitionFrameRateRaw")
    fmin, fmax, finc = limits(sess, ACQ + "AcquisitionFrameRate", F64)
    print(f"\n--- {tag}: {w} x {h}, binning {bh}x{bv}, now {fr:.2f} Hz" if fr else f"\n--- {tag}: {w} x {h}", flush=True)
    print(f"    Width  range {limits(sess, IMG + 'Width')}", flush=True)
    print(f"    Height range {limits(sess, IMG + 'Height')}", flush=True)
    print(f"    FrameRateRaw (period us) min/max/inc = {rmin} / {rmax} / {rinc}", flush=True)
    if rmin:
        print(f"    ==> CEILING = {1e6 / rmin:.1f} Hz   (floor {1e6 / rmax:.2f} Hz)" if rmax else "", flush=True)
    print(f"    AcquisitionFrameRate min/max/inc = {fmin} / {fmax} / {finc}", flush=True)
    return w, h, bh, bv


def main():
    n = C.c_uint32(0)
    dx.IMAQdxEnumerateCameras(None, C.byref(n), C.c_uint32(1))
    if not n.value:
        print("no camera", flush=True); return 3
    arr = (CameraInformation * n.value)()
    dx.IMAQdxEnumerateCameras(arr, C.byref(n), C.c_uint32(1))
    name = arr[0].InterfaceName.decode()
    sess = C.c_uint32(0)
    rc = dx.IMAQdxOpenCamera(name.encode(), C.c_uint32(0), C.byref(sess))
    if rc:
        print(f"OpenCamera({name}) failed: {rc}", flush=True); return 4
    try:
        w, h, bh, bv = report(sess, f"{name} AS FOUND")
        wmax, hmax = get(sess, IMG + "WidthMax"), get(sess, IMG + "HeightMax")
        full_w, full_h = wmax // (bh or 1), hmax // (bv or 1)
        print(f"\n    WidthMax {wmax} / binning {bh} = {full_w};  HeightMax {hmax} / binning {bv} = {full_h}", flush=True)
        print(f"    the frame is {'HALVED' if (w, h) == (full_w // 2, full_h // 2) else 'not exactly halved'}"
              f" relative to the full binned frame", flush=True)

        if "--restore" in sys.argv and (w, h) != (full_w, full_h):
            print(f"\n--- restoring the frame to {full_w} x {full_h} (binning untouched)", flush=True)
            for attr, val in ((IMG + "OffsetX", 0), (IMG + "OffsetY", 0),
                              (IMG + "Width", full_w), (IMG + "Height", full_h)):
                rc = dx.IMAQdxSetAttribute(sess, attr.encode(), C.c_uint32(I64), C.c_int64(val))
                print(f"    set {attr.split('::')[-1]:<10} = {val:<6} rc={rc}", flush=True)
            report(sess, "AFTER RESTORE")
    finally:
        dx.IMAQdxCloseCamera(sess)
        print("\nclosed the camera session", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
