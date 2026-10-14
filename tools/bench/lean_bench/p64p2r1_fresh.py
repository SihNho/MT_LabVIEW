"""p64p2r1_fresh - lean task p64p2 retry 1 (copy of p64p2_fresh.py, which stays unchanged): ONE fresh open/close of the camera
through the NI-IMAQdx C API, READ ONLY (no attribute is written, nothing is acquired), after LabVIEW is closed. Reads
AcquisitionFrameRate / Raw / ExposureTime / ExposureAuto and prints one RESULT-style line. Expected: 90.0009 Hz (every open
reloads the .icd, camera-acquisition-facts.md:642-647).
Retry 1 (review c5 cause 2): the raw output goes to a FILE. Run without arguments: the outer process records the `.icd` md5,
starts THIS script once with `--child` (the only camera open), captures its stdout / stderr / exit code, records the `.icd` md5
again and writes `out_p64/p64p2_r1/fresh_open.json`.
    py tools/bench/lean_bench/p64p2r1_fresh.py"""
import ctypes as C
import hashlib
import json
import os
import subprocess
import sys
import time

U32, I64, F64, STR = 0, 1, 2, 3
ACQ = "CameraAttributes::AcquisitionControl::"
CAM = "cam1"
HERE = os.path.dirname(os.path.abspath(__file__))
ICD = r"C:\Users\Public\Documents\National Instruments\NI-IMAQdx\Data\JAI Corporation SP-5000M-USB (#000014FB0067A270).icd"
OUT = os.path.join(HERE, "out_p64", "p64p2_r1", "fresh_open.json")


def get(dx, sess, name, t):
    if t == STR:
        b = C.create_string_buffer(512)
        rc = dx.IMAQdxGetAttribute(sess, name.encode(), C.c_uint32(t), b)
        return (rc, b.value.decode(errors="replace"))
    v = C.c_int64() if t == I64 else C.c_double()
    rc = dx.IMAQdxGetAttribute(sess, name.encode(), C.c_uint32(t), C.byref(v))
    return (rc, v.value)


def child():
    dx = C.windll.LoadLibrary("niimaqdx.dll")
    sess = C.c_uint32(0)
    rc = dx.IMAQdxOpenCamera(CAM.encode(), C.c_uint32(0), C.byref(sess))
    out = {"open_rc": rc}
    if rc:
        print("RESULT %s" % json.dumps(out)); return 4
    try:
        out["AcquisitionFrameRate"] = get(dx, sess, ACQ + "AcquisitionFrameRate", F64)
        out["AcquisitionFrameRateRaw"] = get(dx, sess, ACQ + "AcquisitionFrameRateRaw", I64)
        out["ExposureTime"] = get(dx, sess, ACQ + "ExposureTime", F64)
        out["ExposureAuto"] = get(dx, sess, ACQ + "ExposureAuto", STR)
    finally:
        out["close_rc"] = dx.IMAQdxCloseCamera(sess)
    print("RESULT %s" % json.dumps(out), flush=True)
    rate = out["AcquisitionFrameRate"]
    return 0 if rate[0] == 0 and abs(rate[1] - 90.0009) < 0.001 and out["close_rc"] == 0 else 1


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def outer():
    if os.path.exists(OUT):
        sys.exit("p64p2r1_fresh: %s exists already - run ONCE only; nothing done" % OUT)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    cmd = [sys.executable, "-u", os.path.abspath(__file__), "--child"]
    rec = {"icd": ICD, "icd_md5_before": md5(ICD), "command_line": subprocess.list2cmdline(cmd),
           "run_start": time.strftime("%Y-%m-%d %H:%M:%S")}
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    rec.update(run_end=time.strftime("%Y-%m-%d %H:%M:%S"), exit_code=p.returncode, stdout=p.stdout, stderr=p.stderr,
               icd_md5_after=md5(ICD))
    res = [ln for ln in p.stdout.splitlines() if ln.startswith("RESULT ")]
    if res:
        r = json.loads(res[-1][len("RESULT "):])
        rec.update(open_rc=r.get("open_rc"), AcquisitionFrameRate=r.get("AcquisitionFrameRate"), close_rc=r.get("close_rc"),
                   AcquisitionFrameRateRaw=r.get("AcquisitionFrameRateRaw"), ExposureTime=r.get("ExposureTime"), ExposureAuto=r.get("ExposureAuto"))
    json.dump(rec, open(OUT, "w", encoding="utf-8"), indent=1)
    print(json.dumps(rec, indent=1))
    return p.returncode


if __name__ == "__main__":
    sys.exit(child() if "--child" in sys.argv else outer())
# ---
# labview: none
# hardware: camera
# ---
