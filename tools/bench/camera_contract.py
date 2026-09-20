"""camera_contract.py - apply and RECORD the decided camera contract (master plan Phase 0.4).

The contract, decided by the user 2026-09-16 (`docs/pre-rig-master-plan.md` "1. Camera"):

    90 Hz  ·  ExposureTime ~= 5 556 us (half the 11.111 ms period)  ·  ExposureAuto OFF
    1280 x 1024, OffsetX/Y = 0  ·  BinningHorizontal is NEVER written

`imaqdx_limits.py` writes only OffsetX/OffsetY/Width/Height (:93-96) - it has no exposure path, which is why the
plan marks the tool as missing. This script adds exactly that, and nothing else: it reuses imaqdx_limits' camera
enumeration and attribute helpers rather than repeating them.

Why fixed exposure matters: with `ExposureAuto = Continuous` a dark field drives the exposure up to its maximum,
and the exposure time then caps the achievable frame rate - a dry run with no sample would "measure" that 90 Hz is
unreachable and blame the software. Fixing exposure at half the period removes that mechanism by the operating
condition instead of arguing about it.

    py tools/bench/camera_contract.py                     # read-only: current values, ranges, and every
                                                          #   Exposure* attribute the camera actually exposes
    py tools/bench/camera_contract.py --apply             # write ExposureAuto=Off then ExposureTime, read back
    py tools/bench/camera_contract.py --apply --batch G:\\Data\\Sihyeong-Developing\\2026-09-16-dryrun1
                                                          # ... and record the read-back as camera_contract.json

A run whose settings are not recorded is not a measurement (master plan 0.2), so --apply always prints the
read-back, and with --batch it writes the same values to <batch>/camera_contract.json.

Nothing is acquired here and no other instrument is touched. Exposure is a camera-side setting; the rig being
disassembled does not change what it means.
"""
import ctypes as C
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import imaqdx_limits as L  # DLL handle, CameraInformation, get(), limits()

ACQ, IMG = L.ACQ, L.IMG
PERIOD_US = 11111.0          # 90.0009 Hz, the rig's configured condition
EXPOSURE_US = PERIOD_US / 2  # the user's decision: expose for half, idle for half

# IMAQdx attribute type codes (IMAQdxAttributeType)
T_U32, T_I64, T_F64, T_STR, T_ENUM, T_BOOL, T_CMD, T_BLOB = range(8)
TYPE_NAME = {T_U32: "U32", T_I64: "I64", T_F64: "F64", T_STR: "String",
             T_ENUM: "Enum", T_BOOL: "Bool", T_CMD: "Command", T_BLOB: "Blob"}
VIS_ADVANCED = 0x00004000


class AttributeInformation(C.Structure):
    _fields_ = [("Type", C.c_uint32), ("Readable", C.c_uint32), ("Writable", C.c_uint32),
                ("Name", C.c_char * L.MAXSTR)]


def enumerate_attributes(sess, root=""):
    """Every attribute under `root`, as (name, type_code, readable, writable)."""
    n = C.c_uint32(0)
    L.dx.IMAQdxEnumerateAttributes2(sess, None, C.byref(n), root.encode(), C.c_uint32(VIS_ADVANCED))
    if not n.value:
        return []
    arr = (AttributeInformation * n.value)()
    L.dx.IMAQdxEnumerateAttributes2(sess, arr, C.byref(n), root.encode(), C.c_uint32(VIS_ADVANCED))
    return [(a.Name.decode(), a.Type, bool(a.Readable), bool(a.Writable)) for a in arr]


def get_string(sess, name):
    buf = C.create_string_buffer(L.MAXSTR)
    rc = L.dx.IMAQdxGetAttribute(sess, name.encode(), C.c_uint32(T_STR), buf)
    return None if rc else buf.value.decode(errors="replace")


def set_string(sess, name, value):
    return L.dx.IMAQdxSetAttribute(sess, name.encode(), C.c_uint32(T_STR), value.encode())


def set_f64(sess, name, value):
    return L.dx.IMAQdxSetAttribute(sess, name.encode(), C.c_uint32(T_F64), C.c_double(value))


def read_value(sess, name, tcode):
    """Read an attribute whatever its type, returning a JSON-safe value."""
    if tcode in (T_F64,):
        return L.get(sess, name, L.F64)
    if tcode in (T_I64, T_U32):
        return L.get(sess, name, L.I64)
    if tcode in (T_STR, T_ENUM):
        return get_string(sess, name)
    if tcode == T_BOOL:
        v = C.c_uint32()
        rc = L.dx.IMAQdxGetAttribute(sess, name.encode(), C.c_uint32(T_BOOL), C.byref(v))
        return None if rc else bool(v.value)
    return None


def snapshot(sess):
    """The values a batch directory must record: geometry, rate, and the whole exposure group."""
    snap = {
        "Width": L.get(sess, IMG + "Width"), "Height": L.get(sess, IMG + "Height"),
        "OffsetX": L.get(sess, IMG + "OffsetX"), "OffsetY": L.get(sess, IMG + "OffsetY"),
        "BinningHorizontal": L.get(sess, IMG + "BinningHorizontal"),
        "BinningVertical": L.get(sess, IMG + "BinningVertical"),
        "AcquisitionFrameRate": L.get(sess, ACQ + "AcquisitionFrameRate", L.F64),
        "AcquisitionFrameRateRaw_us": L.get(sess, ACQ + "AcquisitionFrameRateRaw"),
    }
    for name, tcode, readable, _w in enumerate_attributes(sess, ACQ.rstrip(":")):
        short = name.split("::")[-1]
        if "Exposure" in short and readable:
            snap[short] = read_value(sess, name, tcode)
    return snap


def main():
    apply_it = "--apply" in sys.argv
    batch = None
    if "--batch" in sys.argv:
        batch = sys.argv[sys.argv.index("--batch") + 1]

    n = C.c_uint32(0)
    L.dx.IMAQdxEnumerateCameras(None, C.byref(n), C.c_uint32(1))
    if not n.value:
        print("no camera", flush=True)
        return 3
    arr = (L.CameraInformation * n.value)()
    L.dx.IMAQdxEnumerateCameras(arr, C.byref(n), C.c_uint32(1))
    name = arr[0].InterfaceName.decode()
    sess = C.c_uint32(0)
    rc = L.dx.IMAQdxOpenCamera(name.encode(), C.c_uint32(0), C.byref(sess))
    if rc:
        print(f"OpenCamera({name}) failed: {rc}", flush=True)
        return 4

    try:
        print(f"--- {name}: every Exposure* attribute the camera exposes", flush=True)
        exposure_attrs = [a for a in enumerate_attributes(sess, ACQ.rstrip(":")) if "Exposure" in a[0]]
        for attr, tcode, readable, writable in exposure_attrs:
            val = read_value(sess, attr, tcode) if readable else "(write-only)"
            flags = ("r" if readable else "-") + ("w" if writable else "-")
            print(f"    {attr.split('::')[-1]:<22} {TYPE_NAME.get(tcode, tcode):<8} {flags}  = {val}", flush=True)
        if not exposure_attrs:
            print("    NONE - this camera exposes no Exposure* attribute under AcquisitionControl", flush=True)

        emin, emax, einc = L.limits(sess, ACQ + "ExposureTime", L.F64)
        print(f"\n    ExposureTime range min/max/inc = {emin} / {emax} / {einc}", flush=True)
        print(f"    contract wants {EXPOSURE_US:.1f} us (half of the {PERIOD_US:.0f} us period)", flush=True)

        before = snapshot(sess)
        print(f"\n--- BEFORE: {json.dumps(before, indent=2, default=str)}", flush=True)

        after = before
        if apply_it:
            print("\n--- applying the contract (ExposureAuto first, then ExposureTime)", flush=True)
            writable = {a[0].split("::")[-1] for a in exposure_attrs if a[3]}

            if "ExposureAuto" in writable:
                rc = set_string(sess, ACQ + "ExposureAuto", "Off")
                print(f"    set ExposureAuto = Off        rc={rc}", flush=True)
            else:
                print("    ExposureAuto is NOT writable - skipped (recorded as found)", flush=True)

            if "ExposureMode" in writable:
                rc = set_string(sess, ACQ + "ExposureMode", "Timed")
                print(f"    set ExposureMode = Timed      rc={rc}", flush=True)

            want = EXPOSURE_US
            if emin is not None and want < emin:
                want = emin
            if emax is not None and want > emax:
                want = emax
            if want != EXPOSURE_US:
                print(f"    clamped {EXPOSURE_US:.1f} -> {want:.1f} us by the camera's own range", flush=True)
            rc = set_f64(sess, ACQ + "ExposureTime", want)
            print(f"    set ExposureTime = {want:.1f} us  rc={rc}", flush=True)

            time.sleep(0.2)
            after = snapshot(sess)
            print(f"\n--- AFTER (read back from the camera): {json.dumps(after, indent=2, default=str)}", flush=True)

            got = after.get("ExposureTime")
            if got is None:
                print("\n    !! ExposureTime could not be read back - the contract is NOT verified", flush=True)
            elif abs(got - want) > max(1.0, (einc or 1.0)):
                print(f"\n    !! read-back {got} differs from the written {want} - NOT verified", flush=True)
            else:
                print(f"\n    OK ExposureTime = {got} us, ExposureAuto = {after.get('ExposureAuto')}", flush=True)

            fr = after.get("AcquisitionFrameRate")
            if fr is not None and abs(fr - 1e6 / PERIOD_US) > 0.5:
                print(f"    !! AcquisitionFrameRate is {fr:.3f} Hz, not the contract's "
                      f"{1e6 / PERIOD_US:.3f} Hz - exposure may be capping the rate", flush=True)

        if batch:
            os.makedirs(batch, exist_ok=True)
            out = os.path.join(batch, "camera_contract.json")
            with open(out, "w", encoding="utf-8") as f:
                json.dump({"camera": name, "when": time.strftime("%Y-%m-%d %H:%M:%S"),
                           "contract": {"frame_rate_hz": 1e6 / PERIOD_US, "exposure_us": EXPOSURE_US,
                                        "exposure_auto": "Off", "width": 1280, "height": 1024},
                           "before": before, "after": after,
                           "exposure_attributes": [{"name": a[0], "type": TYPE_NAME.get(a[1], a[1]),
                                                    "readable": a[2], "writable": a[3]} for a in exposure_attrs],
                           "exposure_range": {"min": emin, "max": emax, "inc": einc}},
                          f, indent=2, default=str)
            print(f"\nrecorded -> {out}", flush=True)
    finally:
        L.dx.IMAQdxCloseCamera(sess)
        print("\nclosed the camera session", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
