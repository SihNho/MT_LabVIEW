r"""selftest.py - card 90-1 step 1: build + self-test t0stamp.dll OUTSIDE LabVIEW (ctypes), then --install to claudeDev.

FOUND FIRST: no t0stamp/* existed; MSVC BuildTools 2022 at the path tools/gpu/cuda/build.bat uses; no other C compiler on PATH.
PREDICTION CONTRACT (card pass lines, gated):
  S0 build rc 0, dll exists, PE machine 0x8664 (LabVIEW.exe measured 0x8664)
  A  3000 calls site 7 -> after unload exactly 1 file t0_site07_pid<PID>.bin = freq + 3000 stamps, monotone non-decreasing;
     >= 2048 stamps on disk BEFORE unload (2 full chunks)
  B  2 threads interleaving sites 3 and 9 (1500 each) -> exactly 2 files, each monotone, counts == calls;
     site 64 -> return 1, no file (and site -1 -> return 1)
  C  process handle count flat (+-10) over 10 load-stamp-unload rounds
  D  per-call cost of stamp() from Python (ctypes overhead dominates; the number is a ceiling, reported not gated)
Each round uses its own T0STAMP_DIR under %TEMP% so files are attributable; the DLL is unloaded with FreeLibrary.
"""
import ctypes, ctypes.wintypes as W, glob, os, struct, subprocess, sys, threading, time, hashlib, shutil, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                             # noqa: E402
DLL = os.path.join(HERE, "t0stamp.dll")
CLAUDEDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
K32 = ctypes.WinDLL("kernel32", use_last_error=True)
K32.LoadLibraryW.restype = W.HMODULE; K32.LoadLibraryW.argtypes = [W.LPCWSTR]
K32.FreeLibrary.argtypes = [W.HMODULE]; K32.GetProcAddress.restype = ctypes.c_void_p; K32.GetProcAddress.argtypes = [W.HMODULE, ctypes.c_char_p]
K32.GetProcessHandleCount.argtypes = [W.HANDLE, ctypes.POINTER(W.DWORD)]
STAMP_T = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.c_int32, ctypes.c_void_p)
GATES = {}; FACTS = []


def gate(k, ok, detail=""):
    GATES[k] = bool(ok); print("GATE %s %s %s" % (k, "PASS" if ok else "FAIL", detail), flush=True)


def handles():
    n = W.DWORD(0); K32.GetProcessHandleCount(K32.GetCurrentProcess(), ctypes.byref(n)); return n.value


def load(outdir):
    os.environ["T0STAMP_DIR"] = outdir; os.makedirs(outdir, exist_ok=True)
    h = K32.LoadLibraryW(DLL)
    if not h:
        raise OSError("LoadLibrary failed %d" % ctypes.get_last_error())
    fn = STAMP_T(K32.GetProcAddress(h, b"stamp"))
    return h, fn


def unload(h):
    ok = K32.FreeLibrary(h)
    if not ok:
        raise OSError("FreeLibrary failed")


def read(path):
    b = open(path, "rb").read(); n = len(b) // 8
    v = struct.unpack("<%dq" % n, b[:n * 8]); return v[0], list(v[1:])


def monotone(v):
    return all(b >= a for a, b in zip(v, v[1:]))


def build():
    r = subprocess.run(["cmd", "/c", os.path.join(HERE, "build.bat")], capture_output=True, text=True, cwd=HERE)
    print(r.stdout[-1500:], r.stderr[-500:], flush=True)
    b = open(DLL, "rb").read(); pe = struct.unpack_from("<I", b, 60)[0]; mach = struct.unpack_from("<H", b, pe + 4)[0]
    gate("S0", r.returncode == 0 and os.path.isfile(DLL) and mach == 0x8664, "rc=%d machine=0x%X size=%d" % (r.returncode, mach, len(b)))
    FACTS.append("dll md5=%s size=%d machine=0x%X compiler=MSVC 14.44.35207 x64 (BuildTools 2022) /O2 /MT /LD" % (hashlib.md5(b).hexdigest(), len(b), mach))


def test_a(tmp):
    d = os.path.join(tmp, "A"); h, fn = load(d); pid = os.getpid()
    t0 = time.perf_counter()
    for _ in range(3000):
        fn(7, None)
    dt = time.perf_counter() - t0
    before = glob.glob(os.path.join(d, "*.bin")); pre = read(before[0])[1] if before else []
    unload(h)
    files = glob.glob(os.path.join(d, "*.bin")); exp = os.path.join(d, "t0_site07_pid%d.bin" % pid)
    freq, v = read(files[0]) if files else (0, [])
    gate("A", len(files) == 1 and os.path.normcase(files[0]) == os.path.normcase(exp) and len(v) == 3000 and monotone(v) and len(pre) >= 2048 and freq > 0,
         "files=%d n=%d mono=%s before_unload=%d freq=%d" % (len(files), len(v), monotone(v), len(pre), freq))
    FACTS.append("A: 3000 ctypes calls %.1f us/call (ctypes ceiling); stamps span %.3f ms by QPC" % (dt / 3000 * 1e6, (v[-1] - v[0]) / freq * 1e3 if v else -1))


def test_b(tmp):
    d = os.path.join(tmp, "B"); h, fn = load(d); rc = {}

    def worker(site):
        r = 0
        for _ in range(1500):
            r |= fn(site, None)
        rc[site] = r
    ts = [threading.Thread(target=worker, args=(s,)) for s in (3, 9)]
    [t.start() for t in ts]; [t.join() for t in ts]
    r64 = fn(64, None); rm1 = fn(-1, None)
    unload(h)
    files = sorted(glob.glob(os.path.join(d, "*.bin"))); ok = len(files) == 2 and rc == {3: 0, 9: 0} and r64 != 0 and rm1 != 0
    det = []
    for f in files:
        freq, v = read(f); ok = ok and len(v) == 1500 and monotone(v); det.append("%s n=%d mono=%s" % (os.path.basename(f), len(v), monotone(v)))
    ok = ok and not glob.glob(os.path.join(d, "t0_site64*"))
    gate("B", ok, "files=%d rc=%s r64=%d r-1=%d %s" % (len(files), rc, r64, rm1, det))


def test_c(tmp):
    hs = []
    for i in range(10):
        d = os.path.join(tmp, "C%d" % i); h, fn = load(d)
        for _ in range(1100):
            fn(5, None)
        unload(h); hs.append(handles())
    gate("C", max(hs) - min(hs) <= 10, "handles per round %s" % hs)


def test_d(tmp):
    d = os.path.join(tmp, "D"); h, fn = load(d); buf = (ctypes.c_uint16 * (1024 * 1280))()
    ts = []
    for _ in range(2000):
        a = time.perf_counter_ns(); fn(11, buf); ts.append(time.perf_counter_ns() - a)
    unload(h); ts.sort()
    FACTS.append("D: ctypes stamp(11, 2.6MB ptr) median %.2f us p99 %.2f us (Python ceiling, not the CLFN cost)" % (ts[len(ts) // 2] / 1e3, ts[int(len(ts) * 0.99)] / 1e3))


def main():
    tmp = tempfile.mkdtemp(prefix="t0stamp_st_"); print("tmp", tmp, flush=True)
    build()
    if GATES.get("S0"):
        test_a(tmp); test_b(tmp); test_c(tmp); test_d(tmp)
    if "--install" in sys.argv and all(GATES.values()):
        dst = os.path.join(CLAUDEDEV, "t0stamp.dll"); shutil.copyfile(DLL, dst)
        FACTS.append("installed %s md5=%s" % (dst, hashlib.md5(open(dst, "rb").read()).hexdigest()))
    shutil.rmtree(tmp, ignore_errors=True)
    for f in FACTS:
        print("FACT", f, flush=True)
    npass = sum(GATES.values()); nfail = len(GATES) - npass
    arte = [{"path": DLL, "md5": hashlib.md5(open(DLL, "rb").read()).hexdigest()}] if os.path.isfile(DLL) else []
    print(P.result_line(P.make_result(npass, nfail, next((k for k, v in GATES.items() if not v), None), arte)), flush=True)
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
