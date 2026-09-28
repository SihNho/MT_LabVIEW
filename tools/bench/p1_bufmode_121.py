"""p1_bufmode_121.py - card 121-1: IMAQdx buffer-number modes via the C API. Reuses camera_budget_sweep.py (cell
loop), camera_contract.py / imaqdx_limits.py (DLL, exposure writer). New: all 5 modes of NIIMAQdx.h:178-185, WAIT-style
delay (sleep, 1 ms timer), duplicates, per-call time, process CPU; BufferNumber asks prev+1. Camera only.
PREDICTION CONTRACT (checked mechanically below):
  P1 every cell's camera rate (StatusInformation::LastBufferNumber delta / wall) is within 3 % of the set rate.
  P2 Last at delay 0: calls/s > 3 x camera rate (re-reads the newest buffer; camera-acquisition-facts.md:79-81).
  P3 LastNew: 0 duplicates in every cell (waits for an unreturned buffer).
  P4 Next/BufferNumber/Every at delay 0 and 1 ms: 0 gaps, 0 duplicates, no rc error.
  P5 after close: LabVIEW absent before open; a fresh open/close succeeds (nobody holds the camera); rate restored.
Recorded only (no prediction): Every/Next at 15 ms (> 11.1 ms period at 90 Hz), rc errors there, CPU ratios.
  py tools/bgrun.py --material --max-min 15 --log tools/bench/p1_bufmode_121.log -- py -u tools/bench/p1_bufmode_121.py
"""
import ctypes as C, json, os, statistics, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import camera_contract as CC, imaqdx_limits as L, protocol
dx, OUT = L.dx, os.path.join(HERE, "p1_bufmode_121.json")
MODES = {"Next": 0, "Last": 1, "BufferNumber": 2, "Every": 3, "LastNew": 4}
DELAYS, RATES, SECONDS = [0, 1, 15], [90.0009, 150.0], 4.0
LBN = "StatusInformation::LastBufferNumber"
TL = "CameraAttributes::TransportLayerControl::"


def cell(sess, buf, size, mode, delay, set_hz):
    dx.IMAQdxConfigureAcquisition(sess, C.c_uint32(1), C.c_uint32(10))
    act, times, nums, errs = C.c_uint32(0), [], [], {}
    try:
        dx.IMAQdxStartAcquisition(sess)
        for _ in range(5):
            dx.IMAQdxGetImageData(sess, buf, C.c_uint32(size), C.c_uint32(0), C.c_uint32(0), C.byref(act))
        prev, lbn0, cpu0, t0 = act.value, L.get(sess, LBN), time.process_time(), time.perf_counter()
        while time.perf_counter() - t0 < SECONDS:
            want = prev + 1 if mode == 2 else 0
            a = time.perf_counter()
            rc = dx.IMAQdxGetImageData(sess, buf, C.c_uint32(size), C.c_uint32(mode), C.c_uint32(want), C.byref(act))
            times.append((time.perf_counter() - a) * 1e3)
            if rc:
                errs[str(rc & 0xFFFFFFFF)] = errs.get(str(rc & 0xFFFFFFFF), 0) + 1
                if sum(errs.values()) > 200: break
            else:
                nums.append(act.value); prev = act.value
            if delay: time.sleep(delay / 1000.0)
        el, cpu, lbn1 = time.perf_counter() - t0, time.process_time() - cpu0, L.get(sess, LBN)
    finally:
        dx.IMAQdxStopAcquisition(sess); dx.IMAQdxUnconfigureAcquisition(sess)
    steps = [b - a for a, b in zip(nums, nums[1:])]
    ts = sorted(times)
    cam = (lbn1 - lbn0) / el if lbn0 is not None and lbn1 is not None else None
    return {"mode": [k for k, v in MODES.items() if v == mode][0], "delay_ms": delay, "set_hz": round(set_hz, 3),
            "wall_s": round(el, 3), "calls": len(times), "calls_per_s": round(len(times) / el, 1),
            "distinct_per_s": round(len(set(nums)) / el, 1), "duplicates": sum(1 for s in steps if s == 0),
            "gaps": sum(1 for s in steps if s > 1), "skipped": sum(s - 1 for s in steps if s > 1),
            "backwards": sum(1 for s in steps if s < 0), "rc_errors": errs,
            "get_ms_median": round(statistics.median(ts), 4) if ts else None,
            "get_ms_p99": round(ts[int(0.99 * (len(ts) - 1))], 4) if ts else None,
            "camera_hz": round(cam, 2) if cam is not None else None, "cpu_per_wall": round(cpu / el, 3)}


def open_cam():
    n = C.c_uint32(0); dx.IMAQdxEnumerateCameras(None, C.byref(n), C.c_uint32(1))
    arr = (L.CameraInformation * max(n.value, 1))(); dx.IMAQdxEnumerateCameras(arr, C.byref(n), C.c_uint32(1))
    s = C.c_uint32(0); rc = dx.IMAQdxOpenCamera(arr[0].InterfaceName, C.c_uint32(0), C.byref(s))
    return s, rc, arr[0].InterfaceName.decode()


def main():
    C.windll.winmm.timeBeginPeriod(1)
    lv = subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower().count("labview")
    g, rows, rec = [], [], {"card": "121-1", "when": time.strftime("%Y-%m-%d %H:%M:%S"), "labview_procs_before": lv}
    if lv:
        print("LabVIEW is running - BLOCKED before the camera opens", flush=True)
        print(protocol.result_line(protocol.make_result(0, 1, "LabVIEW running", status="BLOCKED"))); return 2
    sess, rc, name = open_cam()
    print(f"open {name} rc={rc}", flush=True)
    if rc:
        print(protocol.result_line(protocol.make_result(0, 1, "OpenCamera rc=%d" % rc))); return 4
    found_raw = L.get(sess, CC.ACQ + "AcquisitionFrameRateRaw")
    rec["found_hz"] = found_hz = L.get(sess, CC.ACQ + "AcquisitionFrameRate", L.F64)
    try:
        CC.set_string(sess, CC.ACQ + "ExposureAuto", "Off"); CC.set_string(sess, CC.ACQ + "ExposureMode", "Timed")
        CC.set_f64(sess, CC.ACQ + "ExposureTime", CC.EXPOSURE_US)
        rec["contract_readback"] = CC.snapshot(sess); print("contract:", rec["contract_readback"], flush=True)
        size = L.get(sess, TL + "PayloadSize"); buf = C.create_string_buffer(size)
        for hz in RATES:
            L.dx.IMAQdxSetAttribute(sess, (CC.ACQ + "AcquisitionFrameRateRaw").encode(), C.c_uint32(1),
                                    C.c_int64(int(round(1e6 / hz))))
            got = L.get(sess, CC.ACQ + "AcquisitionFrameRate", L.F64); print(f"=== set {hz} Hz -> {got:.3f}", flush=True)
            for mname, m in MODES.items():
                for d in DELAYS:
                    r = cell(sess, buf, size, m, d, got); rows.append(r); print(json.dumps(r), flush=True)
                    rec["rows"] = rows; json.dump(rec, open(OUT, "w"), indent=1)
                    g.append(("P1 %s d%d %g" % (mname, d, hz), r["camera_hz"] and abs(r["camera_hz"] - got) < 0.03 * got))
                    if mname == "Last" and d == 0: g.append(("P2 Last d0 %g" % hz, r["calls_per_s"] > 3 * got))
                    if mname == "LastNew": g.append(("P3 LastNew d%d %g" % (d, hz), r["duplicates"] == 0))
                    if mname in ("Next", "BufferNumber", "Every") and d < 15:
                        g.append(("P4 %s d%d %g" % (mname, d, hz),
                                  r["gaps"] == 0 and r["duplicates"] == 0 and not r["rc_errors"]))
    finally:
        L.dx.IMAQdxSetAttribute(sess, (CC.ACQ + "AcquisitionFrameRateRaw").encode(), C.c_uint32(1),
                                C.c_int64(found_raw))
        rec["restored_hz"] = L.get(sess, CC.ACQ + "AcquisitionFrameRate", L.F64)
        rec["close_rc"] = dx.IMAQdxCloseCamera(sess)
    s2, rc2, _ = open_cam(); rec["reopen"] = {"rc": rc2, "hz": L.get(s2, CC.ACQ + "AcquisitionFrameRate", L.F64),
                                             "w": L.get(s2, CC.IMG + "Width"), "h": L.get(s2, CC.IMG + "Height")}
    rec["reopen"]["close_rc"] = dx.IMAQdxCloseCamera(s2)
    print("restore/reopen:", rec["restored_hz"], rec["reopen"], flush=True)
    g.append(("P5 closed+reopen", rc2 == 0 and rec["reopen"]["close_rc"] == 0 and rec["close_rc"] == 0
              and abs((rec["reopen"]["hz"] or 0) - found_hz) < 0.05))
    rec["gates"] = [[n, bool(ok)] for n, ok in g]; json.dump(rec, open(OUT, "w"), indent=1)
    fails = [n for n, ok in g if not ok]
    for n, ok in g: print(("GATE PASS " if ok else "GATE FAIL ") + n, flush=True)
    md5 = __import__("hashlib").md5(open(OUT, "rb").read()).hexdigest()
    print(protocol.result_line(protocol.make_result(len(g) - len(fails), len(fails), fails[0] if fails else None,
                                                    [{"path": "tools/bench/p1_bufmode_121.json", "md5": md5}])))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
