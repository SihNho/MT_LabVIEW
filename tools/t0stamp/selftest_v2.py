r"""selftest_v2.py - card 93-2 (2), PD200(c)(2): build + self-test t0stamp v2 OUTSIDE LabVIEW, then --install.
FOUND FIRST: selftest.py (v1: build/load/read/handles helpers, reused by import); bench.c is new (per-call cost in C, no
ctypes, which is what the card's MAX / p99.9 needs). v1 source/dll kept as t0stamp_v1.c / t0stamp_v1.dll.
PREDICTION CONTRACT:
  S0 dll + bench.exe build rc 0, dll PE 0x8664   S1 stamp() body in t0stamp.c has no WriteFile/Flush/CreateFile/lock
  B  v2 bench 6 sites x 20000 calls: 6 files, 20000 stamps each, every stamp inside its own call's [before, after] QPC
     window (=> contents match call order); site 64 and -1 return 1; no site64 file; meta lines "s 20000 20000 0"
  O  site 5 x 70000: file holds 65536, meta "5 70000 65536 4464"   C handles flat (+-10) over 10 load/unload rounds
  V  v1 bench (same shape) reported for comparison, not gated.  Call-time median / p99.9 / MAX reported for both.
  I  (--install) the t0at VI's CLFN path(s) to t0stamp.dll read from the VI bytes resolve to claudeDev\t0stamp.dll;
     claudeDev\t0stamp.dll md5 1ea78380... -> byte copy t0stamp_v1.dll (md5 equal), then v2 copied over, md5 == local.
"""
import ctypes, glob, hashlib, os, re, shutil, struct, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import selftest as V1                                                          # noqa: E402  (helpers; its main is not run)
P = V1.P; CD = V1.CLAUDEDEV; DLL = V1.DLL; V1DLL = os.path.join(HERE, "t0stamp_v1.dll"); BENCH = os.path.join(HERE, "bench.exe")
T0AT = os.path.join(CD, "D1_s1_t0at_20260926_090833.vi"); V1MD5 = "1ea78380"
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                   # noqa: E731
gate, GATES, FACTS = V1.gate, V1.GATES, V1.FACTS


def bench(dll, d, iters=20000):
    os.makedirs(d, exist_ok=True); env = dict(os.environ, T0STAMP_DIR=d); ob = os.path.join(d, "bench.bin")
    r = subprocess.run([BENCH, dll, str(iters), ob], capture_output=True, text=True, env=env); print(r.stdout.strip(), r.stderr.strip(), flush=True)
    b = open(ob, "rb").read(); v = struct.unpack("<%dq" % (len(b) // 8), b); f, n = v[0], v[1]
    ab = [(v[2 + 2 * k], v[3 + 2 * k]) for k in range(n)]; ns = sorted((y - x) * 1e9 / f for x, y in ab)
    st = {"n": n, "qpc_hz": f, "median_ns": round(ns[n // 2]), "p99_9_ns": round(ns[int(n * 0.999)]), "max_ns": round(ns[-1]), "calls_over_10us": sum(1 for x in ns if x > 1e4)}
    m = re.search(r"r64=(-?\d+) rm1=(-?\d+)", r.stdout)
    return st, ab, (int(m.group(1)), int(m.group(2))) if m else (None, None)


def test_b(tmp):
    d = os.path.join(tmp, "B"); st, ab, (r64, rm1) = bench(DLL, d); files = sorted(glob.glob(os.path.join(d, "t0_site*.bin"))); ok, det = True, []
    for j, s in enumerate((0, 2, 3, 4, 6, 8)):
        p = [f for f in files if "site%02d_" % s in f]; v = V1.read(p[0])[1] if p else []
        win = all(ab[6 * i + j][0] <= t <= ab[6 * i + j][1] for i, t in enumerate(v)); ok = ok and len(v) == 20000 and win; det.append("s%02d n=%d inwin=%s" % (s, len(v), win))
    meta = open(glob.glob(os.path.join(d, "t0_meta_pid*.txt"))[0]).read().splitlines() if glob.glob(os.path.join(d, "t0_meta_pid*.txt")) else []
    ok = ok and len(files) == 6 and (r64, rm1) == (1, 1) and sorted(x for x in meta if x) == sorted("%d 20000 20000 0" % s for s in (0, 2, 3, 4, 6, 8))
    gate("B", ok, "files=%d r64=%s rm1=%s %s meta=%s" % (len(files), r64, rm1, det, [x for x in meta if x]))
    FACTS.append("v2 C-bench 6 sites x 20000 calls: %s" % st); return st


def test_o(tmp):
    d = os.path.join(tmp, "O"); h, fn = V1.load(d); rc = [fn(5, None) for _ in range(70000)]; V1.unload(h)
    f = glob.glob(os.path.join(d, "t0_site05_*.bin")); v = V1.read(f[0])[1] if f else []; mt = glob.glob(os.path.join(d, "t0_meta_pid*.txt"))
    meta = open(mt[0]).read().strip() if mt else ""
    gate("O", len(v) == 65536 and V1.monotone(v) and meta == "5 70000 65536 4464" and rc.count(2) == 4464, "stored=%d meta=%r rc2=%d" % (len(v), meta, rc.count(2)))


def vi_paths(p):
    b = open(p, "rb").read(); out = []
    for m in re.finditer(rb"PTH[0-9]", b):
        k = m.start(); ln, tp, cnt = struct.unpack_from(">IHH", b, k + 4); j, comps = k + 12, []
        for _ in range(min(cnt, 40)):
            L = b[j]; comps.append(b[j + 1:j + 1 + L].decode("latin-1")); j += 1 + L
        if any("t0stamp" in c.lower() for c in comps): out.append({"type": tp, "comps": comps})
    return out, b.count(b"t0stamp.dll")


def install():
    paths, nraw = vi_paths(T0AT); FACTS.append("t0at VI CLFN library paths (read from VI bytes): %s; raw 't0stamp.dll' occurrences %d" % (paths, nraw))
    good = bool(paths) and all(x["comps"][-1] == "t0stamp.dll" and (x["comps"][-2:-1] == ["claudeDev"] or len(x["comps"]) == 1) for x in paths)
    gate("I1 CLFN path(s) resolve to claudeDev\\t0stamp.dll", good, str(paths))
    dst, bak = os.path.join(CD, "t0stamp.dll"), os.path.join(CD, "t0stamp_v1.dll"); cur = md5(dst)
    gate("I2 installed dll is v1 (1ea78380...) or already this v2", cur.startswith(V1MD5) or cur == md5(DLL), cur)
    if not (good and GATES["I2 installed dll is v1 (1ea78380...) or already this v2"]): return
    if not os.path.isfile(bak): shutil.copyfile(dst, bak)
    gate("I3 claudeDev t0stamp_v1.dll byte copy md5 1ea78380...", md5(bak).startswith(V1MD5), md5(bak))
    if GATES["I3 claudeDev t0stamp_v1.dll byte copy md5 1ea78380..."]:
        shutil.copyfile(DLL, dst); gate("I4 v2 installed md5 == local build", md5(dst) == md5(DLL), md5(dst))


def main():
    tmp = tempfile.mkdtemp(prefix="t0stamp_v2_"); V1.build()
    r = subprocess.run(["cmd", "/c", os.path.join(HERE, "build_bench.bat")], capture_output=True, text=True, cwd=HERE); print(r.stdout[-600:], flush=True)
    GATES["S0"] = GATES.get("S0", False) and r.returncode == 0 and os.path.isfile(BENCH)
    src = open(os.path.join(HERE, "t0stamp.c")).read(); body = src[src.index("int32_t __cdecl stamp("):]; body = body[:body.index("\n}\n")]
    gate("S1 stamp() has no file I/O or lock", not re.search(r"WriteFile|Flush|CreateFile|EnterCritical|fopen", body), "%d chars" % len(body))
    if all(GATES.values()):
        st2 = test_b(tmp); test_o(tmp); V1.test_c(tmp)
        st1 = bench(V1DLL, os.path.join(tmp, "V"))[0]; FACTS.append("v1 C-bench same shape (comparison, not gated): %s" % st1)
    if "--install" in sys.argv and all(GATES.values()): install()
    shutil.rmtree(tmp, ignore_errors=True)
    for f in FACTS: print("FACT", f, flush=True)
    bad = [k for k, v in GATES.items() if not v]
    print(P.result_line(P.make_result(len(GATES) - len(bad), len(bad), bad[0] if bad else None, [{"path": DLL, "md5": md5(DLL)}])), flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
