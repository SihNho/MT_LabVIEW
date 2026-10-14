"""p64p2_fresh - lean task p64p2: ONE fresh open/close of the camera through the NI-IMAQdx C API, READ ONLY (no attribute is
written, nothing is acquired), after LabVIEW is closed. Reads AcquisitionFrameRate / Raw / ExposureTime / ExposureAuto and
prints one RESULT-style line. Expected: 90.0009 Hz (every open reloads the .icd, camera-acquisition-facts.md:642-647).
    py tools/bench/lean_bench/p64p2_fresh.py"""
import ctypes as C
import json
import os
import sys

dx = C.windll.LoadLibrary("niimaqdx.dll")
U32, I64, F64, STR = 0, 1, 2, 3
ACQ = "CameraAttributes::AcquisitionControl::"
CAM = "cam1"


def get(sess, name, t):
    if t == STR:
        b = C.create_string_buffer(512)
        rc = dx.IMAQdxGetAttribute(sess, name.encode(), C.c_uint32(t), b)
        return (rc, b.value.decode(errors="replace"))
    v = C.c_int64() if t == I64 else C.c_double()
    rc = dx.IMAQdxGetAttribute(sess, name.encode(), C.c_uint32(t), C.byref(v))
    return (rc, v.value)


def main():
    sess = C.c_uint32(0)
    rc = dx.IMAQdxOpenCamera(CAM.encode(), C.c_uint32(0), C.byref(sess))
    out = {"open_rc": rc}
    if rc:
        print("RESULT %s" % json.dumps(out)); return 4
    try:
        out["AcquisitionFrameRate"] = get(sess, ACQ + "AcquisitionFrameRate", F64)
        out["AcquisitionFrameRateRaw"] = get(sess, ACQ + "AcquisitionFrameRateRaw", I64)
        out["ExposureTime"] = get(sess, ACQ + "ExposureTime", F64)
        out["ExposureAuto"] = get(sess, ACQ + "ExposureAuto", STR)
    finally:
        out["close_rc"] = dx.IMAQdxCloseCamera(sess)
    print("RESULT %s" % json.dumps(out), flush=True)
    rate = out["AcquisitionFrameRate"]
    return 0 if rate[0] == 0 and abs(rate[1] - 90.0009) < 0.001 and out["close_rc"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
# ---
# labview: none
# hardware: camera
# ---
