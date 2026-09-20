"""camera_copy_cost.py - what does ACQUIRING one frame cost, separately from processing it?

The budget sweep measured how much *processing* fits in a frame period, but it never separated the acquisition itself.
That term matters for the loop design: it is paid in every architecture, so it is the part of the per-frame cost that
splitting loops cannot remove. In the t0 plan's A+B+W decomposition this is term A.

The `Last`-mode sweep appeared to answer it - 23 795 calls/s at delay 0 implies 42 us per call - but that figure is not
trustworthy: with nothing new to wait for, `Last` hands back the SAME buffer over and over, and 1.31 MB in 42 us would
be 31 GB/s, well above what a real memcpy does on this class of machine. So that number almost certainly measures a
call that copied nothing, or copied from cache.

This measures only calls that returned a **new** buffer number, timing each one individually:

  * `Last` mode, so the call never blocks waiting for the camera - what is left is the copy;
  * a pace slightly slower than the frame rate, so a fresh buffer is always ready and every timed call does real work;
  * the buffer number is checked, and a call that returned the same buffer as last time is discarded rather than
    averaged in - that is precisely the mistake the 42 us figure makes.

Reported as a distribution, not a mean: the tail is what drops frames.

HARDWARE: camera only, acquisition only, nothing moves. Frame rate and geometry are read, restored, and never changed.
  py tools/bench/camera_copy_cost.py
"""
import ctypes as C
import os, statistics as st, sys, time

MAXSTR = 512
dx = C.windll.LoadLibrary("niimaqdx.dll")
I64, F64 = 1, 2
IMG = "CameraAttributes::ImageFormatControl::"
TL = "CameraAttributes::TransportLayerControl::"
ACQ = "CameraAttributes::AcquisitionControl::"
LAST = 1
N_WANT = int(os.environ.get("COPY_N", 300))


class CameraInformation(C.Structure):
    _fields_ = [("Type", C.c_uint32), ("Version", C.c_uint32), ("Flags", C.c_uint32),
                ("SerialNumberHi", C.c_uint32), ("SerialNumberLo", C.c_uint32), ("BusType", C.c_uint32),
                ("InterfaceName", C.c_char * MAXSTR), ("VendorName", C.c_char * MAXSTR),
                ("ModelName", C.c_char * MAXSTR), ("CameraFileName", C.c_char * MAXSTR),
                ("CameraAttributeURL", C.c_char * MAXSTR)]


def geti(sess, n):
    v = C.c_int64()
    return None if dx.IMAQdxGetAttribute(sess, n.encode(), C.c_uint32(I64), C.byref(v)) else v.value


def getf(sess, n):
    v = C.c_double()
    return None if dx.IMAQdxGetAttribute(sess, n.encode(), C.c_uint32(F64), C.byref(v)) else v.value


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
    try:
        w, h = geti(sess, IMG + "Width"), geti(sess, IMG + "Height")
        size = geti(sess, TL + "PayloadSize")
        rate = getf(sess, ACQ + "AcquisitionFrameRate")
        period = 1.0 / rate
        print(f"{name}: {w} x {h}, payload {size:,} B, {rate:.2f} Hz (period {period * 1e3:.2f} ms)\n", flush=True)
        buf = C.create_string_buffer(size)

        if dx.IMAQdxConfigureAcquisition(sess, C.c_uint32(1), C.c_uint32(10)):
            print("ConfigureAcquisition failed", flush=True); return 5
        try:
            if dx.IMAQdxStartAcquisition(sess):
                print("StartAcquisition failed", flush=True); return 6
            actual = C.c_uint32(0)
            for _ in range(10):
                dx.IMAQdxGetImageData(sess, buf, C.c_uint32(size), C.c_uint32(LAST), C.c_uint32(0), C.byref(actual))
            prev = actual.value
            fresh, stale = [], 0
            deadline = time.perf_counter() + 20.0
            while len(fresh) < N_WANT and time.perf_counter() < deadline:
                # pace just slower than the camera so a NEW buffer is always waiting when we ask
                t_wait = time.perf_counter() + period * 1.2
                while time.perf_counter() < t_wait:
                    pass
                t0 = time.perf_counter()
                rc = dx.IMAQdxGetImageData(sess, buf, C.c_uint32(size), C.c_uint32(LAST), C.c_uint32(0), C.byref(actual))
                dt = (time.perf_counter() - t0) * 1e6
                if rc:
                    print(f"   GetImageData rc={rc}", flush=True); break
                if actual.value == prev:
                    stale += 1                 # same buffer as last time: copied nothing new, discard
                else:
                    fresh.append(dt)
                prev = actual.value
        finally:
            dx.IMAQdxStopAcquisition(sess)
            dx.IMAQdxUnconfigureAcquisition(sess)

        if not fresh:
            print("no fresh-buffer samples", flush=True); return 7
        fresh.sort()
        med = st.median(fresh)
        print(f"   {len(fresh)} calls that returned a NEW buffer ({stale} discarded as same-buffer)\n", flush=True)
        print(f"      min    {fresh[0]:8.1f} us", flush=True)
        print(f"      median {med:8.1f} us   -> {size / med * 1e6 / 1e9:5.2f} GB/s", flush=True)
        print(f"      p90    {fresh[int(len(fresh) * 0.90)]:8.1f} us", flush=True)
        print(f"      p99    {fresh[min(len(fresh) - 1, int(len(fresh) * 0.99))]:8.1f} us", flush=True)
        print(f"      max    {fresh[-1]:8.1f} us", flush=True)
        print(f"\n   ACQUISITION COST = {med / 1000:.2f} ms per frame at {w}x{h}. "
              f"At 150 Hz that is {med / 1000 / 6.67 * 100:.0f}% of the 6.00 ms budget, paid in every design.", flush=True)
    finally:
        dx.IMAQdxCloseCamera(sess)
        print("\nclosed the camera session", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
