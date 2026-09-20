"""camera_budget_sweep.py - how much per-frame processing can the rig afford before it loses frames?

This is the measurement the whole loop-multiplication argument rests on, done through `niimaqdx.dll` directly instead
of through NI's `Acquire Every Image.vi`. Same experiment, three advantages: it cannot open a modal dialog (the failure
that killed three earlier attempts), it does not contend for the single COM client while the diagram scan holds
LabVIEW, and it excludes LabVIEW's own per-frame overhead - so the curve it produces is the CAMERA-and-ring-buffer
limit, the floor that no amount of software work can get under.

Method, which is exactly what the NI example does:
  configure `--buffers` ring buffers -> start -> repeatedly fetch the NEXT buffer in sequence, then burn `delay` ms
  pretending to process it. Fetching by `Next` is what makes the loop have to KEEP UP: if the consumer is slower than
  the camera, the ring wraps and buffers are overwritten unread.

`Images Missed` is computed the way IMAQdx does it - from the gaps in the returned buffer numbers, which increase by
exactly 1 when nothing was lost. The delay at which missed frames leave zero IS the per-frame budget.

Reference points to read the table against, all measured earlier on this rig:
  ~2.5 ms  the CPU-parallel tracking kernel          (PARALLEL_kernel_v3)
  ~1.1 ms  the GPU kernel's cost above baseline      (GPU v2)
  6.67 ms  the whole budget at the wanted 150 Hz;  4.03 ms at the camera's 247.95 Hz ceiling

HARDWARE: camera only, and it only acquires - nothing moves. `Width`/`Height` are restored to the full binned frame at
the end, binning is never touched, and the session is always unconfigured and closed in a finally block.
  py tools/bgrun.py --max-min 20 --log tools/bench/camera_budget_sweep.log -- py -u tools/bench/camera_budget_sweep.py
"""
import ctypes as C
import json, os, sys, time

MAXSTR = 512
dx = C.windll.LoadLibrary("niimaqdx.dll")
I64, F64 = 1, 2
IMG = "CameraAttributes::ImageFormatControl::"
TL = "CameraAttributes::TransportLayerControl::"
ACQ = "CameraAttributes::AcquisitionControl::"
NEXT, LAST = 0, 1                      # IMAQdxBufferNumberMode
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "camera_budget_sweep_%s.json" % os.environ.get("SWEEP_MODE", "next").lower())

SECONDS = float(os.environ.get("SWEEP_SECONDS", 4.0))
BUFFERS = int(os.environ.get("SWEEP_BUFFERS", 10))     # NI's example default
DELAYS = [float(x) for x in os.environ.get("SWEEP_DELAYS", "0,1,2,3,4,5,6,7,8,10").split(",")]
# The rig runs at 90 Hz today, the user wants 150 Hz, and 247.95 Hz is the measured ceiling. A budget measured only at
# 90 Hz answers nothing about 150 Hz - the frame period is 11.1 ms there and 6.67 ms at the target - so the rate is
# swept too. It is written as `AcquisitionFrameRateRaw`, the frame PERIOD IN MICROSECONDS, because that attribute is an
# integer: ctypes does not know IMAQdxSetAttribute is variadic, and on x64 Windows a variadic double must be placed in
# both an XMM register and the matching GPR, which ctypes will not do. Integers have no such ambiguity.
RATES = [float(x) for x in os.environ.get("SWEEP_RATES", "90,150,200,247").split(",")]
# Buffer-number mode. `Next` is the DEFAULT on both IMAQdx Get Image and Grab, and it is what makes a consumer have to
# keep up: it hands back the next buffer IN SEQUENCE, so a slow consumer falls behind and the ring overwrites unread
# buffers. `Last` hands back the newest buffer and never waits, so a slow consumer simply skips - it degrades smoothly
# instead of halving. Sweeping both is the measurement behind "can the live display be restored": if a display loop on
# `Last` costs the tracking loop nothing, the view can come back as-is.
MODE = {"next": NEXT, "last": LAST}[os.environ.get("SWEEP_MODE", "next").lower()]


class CameraInformation(C.Structure):
    _fields_ = [("Type", C.c_uint32), ("Version", C.c_uint32), ("Flags", C.c_uint32),
                ("SerialNumberHi", C.c_uint32), ("SerialNumberLo", C.c_uint32), ("BusType", C.c_uint32),
                ("InterfaceName", C.c_char * MAXSTR), ("VendorName", C.c_char * MAXSTR),
                ("ModelName", C.c_char * MAXSTR), ("CameraFileName", C.c_char * MAXSTR),
                ("CameraAttributeURL", C.c_char * MAXSTR)]


def geti(sess, name):
    v = C.c_int64()
    return None if dx.IMAQdxGetAttribute(sess, name.encode(), C.c_uint32(I64), C.byref(v)) else v.value


def getf(sess, name):
    v = C.c_double()
    return None if dx.IMAQdxGetAttribute(sess, name.encode(), C.c_uint32(F64), C.byref(v)) else v.value


def seti(sess, name, val):
    return dx.IMAQdxSetAttribute(sess, name.encode(), C.c_uint32(I64), C.c_int64(val))


def spin(ms):
    """Busy-wait. time.sleep() cannot resolve 1 ms on Windows (its timer granularity is ~15 ms unless the process
    raises it), and a sleeping consumer is not what a tracking loop does anyway - it burns CPU."""
    if ms <= 0:
        return
    end = time.perf_counter() + ms / 1000.0
    while time.perf_counter() < end:
        pass


def cell(sess, buf, size, delay_ms, seconds):
    """One delay point: acquire in sequence for `seconds`, counting the gaps in the buffer numbers."""
    if dx.IMAQdxConfigureAcquisition(sess, C.c_uint32(1), C.c_uint32(BUFFERS)):
        raise RuntimeError("ConfigureAcquisition failed")
    try:
        if dx.IMAQdxStartAcquisition(sess):
            raise RuntimeError("StartAcquisition failed")
        actual = C.c_uint32(0)
        # discard the first few frames: the camera and the ring are still filling and the first interval is not a rate
        for _ in range(5):
            dx.IMAQdxGetImageData(sess, buf, C.c_uint32(size), C.c_uint32(MODE), C.c_uint32(0), C.byref(actual))
        prev = actual.value
        first, n, missed, t0 = prev, 0, 0, time.perf_counter()
        while time.perf_counter() - t0 < seconds:
            rc = dx.IMAQdxGetImageData(sess, buf, C.c_uint32(size), C.c_uint32(MODE), C.c_uint32(0), C.byref(actual))
            if rc:
                return {"delay_ms": delay_ms, "error": f"GetImageData rc={rc}"}
            gap = actual.value - prev
            if gap > 1:
                missed += gap - 1          # buffers the camera filled and overwrote before we asked for them
            prev = actual.value
            n += 1
            spin(delay_ms)
        el = time.perf_counter() - t0
        return {"delay_ms": delay_ms, "frames": n, "seconds": round(el, 3),
                "processed_fps": round(n / el, 1),
                "acquired_fps": round((prev - first) / el, 1),
                "images_missed": missed,          # in `last` mode these are buffers DELIBERATELY skipped, not lost work
                "mode": os.environ.get("SWEEP_MODE", "next").lower(),
                "buffers": BUFFERS}
    finally:
        dx.IMAQdxStopAcquisition(sess)
        dx.IMAQdxUnconfigureAcquisition(sess)


def main():
    n = C.c_uint32(0)
    dx.IMAQdxEnumerateCameras(None, C.byref(n), C.c_uint32(1))
    if not n.value:
        print("no camera", flush=True); return 3
    arr = (CameraInformation * n.value)()
    dx.IMAQdxEnumerateCameras(arr, C.byref(n), C.c_uint32(1))
    name = arr[0].InterfaceName.decode()
    sess = C.c_uint32(0)
    if dx.IMAQdxOpenCamera(name.encode(), C.c_uint32(0), C.byref(sess)):
        print(f"OpenCamera({name}) failed", flush=True); return 4

    rows = []
    full_w = full_h = None
    as_found_period = geti(sess, ACQ + "AcquisitionFrameRateRaw")     # read BEFORE anything is changed
    try:
        w, h = geti(sess, IMG + "Width"), geti(sess, IMG + "Height")
        bh, bv = geti(sess, IMG + "BinningHorizontal"), geti(sess, IMG + "BinningVertical")
        full_w = geti(sess, IMG + "WidthMax") // bh
        full_h = geti(sess, IMG + "HeightMax") // bv
        if (w, h) != (full_w, full_h):          # start from the frame the rig is meant to run
            seti(sess, IMG + "Width", full_w); seti(sess, IMG + "Height", full_h)
            w, h = geti(sess, IMG + "Width"), geti(sess, IMG + "Height")
        size = geti(sess, TL + "PayloadSize")
        rate = getf(sess, ACQ + "AcquisitionFrameRate")
        print(f"{name}: {w} x {h}, binning {bh}x{bv}, payload {size} B, camera set to {rate:.2f} Hz, "
              f"{BUFFERS} ring buffers, {SECONDS:g} s per point\n", flush=True)
        buf = C.create_string_buffer(size)

        budgets = {}
        for want in RATES:
            seti(sess, ACQ + "AcquisitionFrameRateRaw", int(round(1e6 / want)))
            got = getf(sess, ACQ + "AcquisitionFrameRate")
            period = 1000.0 / got
            print(f"\n=== camera set to {got:.2f} Hz (asked {want:g}); frame period {period:.2f} ms", flush=True)
            print(f"   {'delay':>6} | {'acquired':>9} | {'processed':>9} | {'missed':>7} | frames", flush=True)
            print(f"   {'-' * 6} + {'-' * 9} + {'-' * 9} + {'-' * 7} + ------", flush=True)
            for d in DELAYS:
                if d > period + 4:            # far past the frame period; the answer is already known to be "loses frames"
                    continue
                r = cell(sess, buf, size, d, SECONDS)
                r["set_fps"] = round(got, 2)
                rows.append(r)
                json.dump(rows, open(OUT, "w", encoding="utf-8"), indent=1)
                if "error" in r:
                    print(f"   {d:>5g}  | {r['error']}", flush=True)
                    continue
                flag = "   <== losing frames" if r["images_missed"] else ""
                print(f"   {d:>5g}  | {r['acquired_fps']:>9} | {r['processed_fps']:>9} | "
                      f"{r['images_missed']:>7} | {r['frames']}{flag}", flush=True)
            clean = [r["delay_ms"] for r in rows
                     if r.get("set_fps") == round(got, 2) and not r.get("images_missed") and "error" not in r]
            budgets[round(got, 1)] = (max(clean) if clean else None, period)

        print(f"\n{'=' * 70}\nPER-FRAME BUDGET ({BUFFERS} ring buffers, {int(w)}x{int(h)})", flush=True)
        print(f"   {'rate':>8} | {'period':>8} | {'budget':>8} | headroom the tracking loop has", flush=True)
        for r_hz, (b, period) in sorted(budgets.items()):
            b_s = f"{b:g} ms" if b is not None else "0 ms"
            print(f"   {r_hz:>6g} Hz | {period:>5.2f} ms | {b_s:>8} |", flush=True)
    finally:
        # Put the camera back exactly as found - full binned frame AND the rig's own 90 Hz - so the next person to run
        # the main VI is not handed a camera this benchmark left at 247 Hz. Binning was never touched.
        try:
            seti(sess, IMG + "Width", full_w); seti(sess, IMG + "Height", full_h)
            seti(sess, ACQ + "AcquisitionFrameRateRaw", as_found_period)
            print(f"\nrestored: {geti(sess, IMG + 'Width')} x {geti(sess, IMG + 'Height')} at "
                  f"{getf(sess, ACQ + 'AcquisitionFrameRate'):.2f} Hz", flush=True)
        except Exception as e:
            print("   RESTORE FAILED:", str(e)[:140], flush=True)
        dx.IMAQdxCloseCamera(sess)
        print("\nclosed the camera session; results ->", OUT, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
