r"""diag_c122_mtime - card 122-5: the offline discriminating test named by archive/peer/2026-10-01-c122-hyg-h6.md:75-80.
Lists every file under claudeDev (recursive, any extension) whose mtime falls inside the diag_c122_hyg.py run window
(2026-10-01 13:01:50 .. 13:05:30). No LabVIEW.
PREDICTION: exactly one file, DonorRingConst_v0.vi.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c122_mtime.log -- py -u tools/bench/diag_c122_mtime.py"""
import datetime as D, os, sys                                                      # noqa: E401
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import protocol                                                                     # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
t0, t1 = D.datetime(2026, 10, 1, 13, 1, 50).timestamp(), D.datetime(2026, 10, 1, 13, 5, 30).timestamp()
hits, n = [], 0
for d, _s, fs in os.walk(CD):
    for f in fs:
        n += 1
        p = os.path.join(d, f)
        m = os.path.getmtime(p)
        if t0 <= m <= t1:
            hits.append((D.datetime.fromtimestamp(m).isoformat(), os.path.relpath(p, CD)))
for h in hits:
    print("  FACT HIT {0} {1}".format(*h), flush=True)
ok = [os.path.basename(h[1]) for h in hits] == ["DonorRingConst_v0.vi"]
print("  GATE {0}  M exactly one file in the window == DonorRingConst_v0.vi ({1} files scanned)".format("PASS" if ok else "FAIL", n), flush=True)
print(protocol.result_line(protocol.make_result(int(ok), int(not ok), None if ok else "M window files != [DonorRingConst_v0.vi]")), flush=True)
sys.exit(0 if ok else 1)
